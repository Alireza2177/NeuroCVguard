"""Run a local S16 check and save an exclusive, privacy-normalized JSON record."""

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
    working = root
    if command[0] == "--cwd":
        working = Path(command[1]).resolve()
        command = command[2:]
    destination = Path(__file__).with_name(name + ".json")
    if destination.exists():
        raise FileExistsError(destination)
    start = datetime.datetime.now(datetime.UTC).isoformat()
    overrides = {"PYTHONIOENCODING": "utf-8", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
    environment = dict(os.environ, **overrides)
    result = subprocess.run(
        command,
        cwd=working,
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
        "cwd": redact(str(working)),
        "started_at_utc": start,
        "recorder_python": platform.python_version(),
        "platform": platform.platform(),
        "environment_overrides": overrides,
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
