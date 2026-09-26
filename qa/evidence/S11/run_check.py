"""Run a local S11 check and save an exclusive, privacy-normalized JSON record."""

import datetime
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Record an argument-vector command without invoking a shell."""
    root = Path(__file__).resolve().parents[3]
    name, *command = sys.argv[1:]
    destination = Path(__file__).with_name(name + ".json")
    if destination.exists():
        raise FileExistsError(destination)
    start = datetime.datetime.now(datetime.UTC).isoformat()
    environment = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )

    def redact(value: str) -> str:
        for path, replacement in (
            (str(root), "<PROJECT_ROOT>"),
            (str(Path.home()), "<USER_HOME>"),
            (os.environ.get("TEMP", ""), "<TEMP>"),
        ):
            if path:
                for spelling in (path.replace("\\", "\\\\"), path, path.replace("\\", "/")):
                    value = re.sub(re.escape(spelling), replacement, value, flags=re.I)
        return value

    record = {
        "command": [redact(arg) for arg in command],
        "cwd": "<PROJECT_ROOT>",
        "started_at_utc": start,
        "recorder_python": platform.python_version(),
        "platform": platform.platform(),
        "environment_overrides": {"PYTHONIOENCODING": "utf-8"},
        "exit_code": result.returncode,
        "stdout": redact(result.stdout),
        "stderr": redact(result.stderr),
    }
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    print(json.dumps(record, indent=2))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
