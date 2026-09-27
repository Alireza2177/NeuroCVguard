"""Execute the required Linux interpreter matrix in isolated local source copies."""

import concurrent.futures
import datetime
import json
import os
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "qa/evidence/S16"
BASE = Path(json.loads((ROOT / "dist/s16-environments.json").read_text())["linux_root"])
SOURCE = BASE / "source"
UV = ROOT / "dist/s16-tooling/uv-linux"


def run(name, command, cwd, env):
    destination = EVIDENCE / (name + ".json")
    assert not destination.exists(), name
    # The WSL bootstrap interpreter is Python 3.10, before datetime.UTC exists.
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()  # noqa: UP017
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    record = {
        "command": [str(x) for x in command],
        "cwd": str(cwd),
        "started_at_utc": started,
        "platform": platform.platform(),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "environment_overrides": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"},
    }
    text = (
        json.dumps(record, indent=2)
        .replace(str(ROOT), "<PROJECT_ROOT>")
        .replace(str(BASE), "<LINUX_WORK>")
    )
    destination.write_text(text + "\n", encoding="utf-8")
    print(name, result.returncode, flush=True)
    if result.returncode:
        raise RuntimeError(name + " failed; see its retained command record")


def check(version):
    name = "linux-" + version.replace(".", "")
    python = next((BASE / "pythons").glob(f"cpython-{version}.*-linux-*/bin/python{version}"))
    environment = BASE / name
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    run(name + "-venv", [UV, "venv", "--seed", "--python", python, environment], BASE, env)
    interpreter = environment / "bin/python"
    run(
        name + "-install",
        [UV, "pip", "install", "--python", interpreter, "-e", str(SOURCE) + "[dev,docs]"],
        SOURCE,
        env,
    )
    run(name + "-environment", [interpreter, "-m", "pip", "list", "--format=json"], SOURCE, env)
    run(
        name + "-tests",
        [
            interpreter,
            "-m",
            "pytest",
            "-q",
            "--strict-markers",
            "--strict-config",
            f"--junitxml={EVIDENCE / (name + '.xml')}",
        ],
        SOURCE,
        env,
    )


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(check, ("3.11", "3.12", "3.13")))
