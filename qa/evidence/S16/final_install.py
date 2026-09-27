"""Fresh final-wheel install and guarded demo, with every command printed verbatim."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
paths = json.loads((ROOT / "dist/s16-environments.json").read_text())
windows = sys.platform == "win32"
base = Path(paths["windows_root"] if windows else paths["linux_root"])
uv = shutil.which("uv") if windows else ROOT / "dist/s16-tooling/uv-linux"
bootstrap = base / ("wheel312/Scripts/python.exe" if windows else "linux-312/bin/python")
environment = base / "final-wheel"
interpreter = environment / ("Scripts/python.exe" if windows else "bin/python")
console = environment / ("Scripts/neurocvguard.exe" if windows else "bin/neurocvguard")
wheel = base / "neurocvguard-0.1.0-py3-none-any.whl"
assert not wheel.exists() and not environment.exists()
shutil.copyfile(ROOT / "dist/s16" / wheel.name, wheel)
script = base / "verify_final_wheel.py"
shutil.copyfile(ROOT / "tools/verify_wheel.py", script)
env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
commands = [
    [uv, "venv", "--seed", "--python", bootstrap, environment],
    [uv, "pip", "install", "--python", interpreter, wheel],
    [interpreter, "-m", "pip", "check"],
    [console, "--version"],
    [console, "--help"],
    [
        interpreter,
        "-I",
        script,
        "--forbid-root",
        ROOT,
        "--wheel",
        wheel,
        "--out",
        base / "final-wheel-demo",
    ],
    [interpreter, "-m", "pip", "list", "--format=json"],
]
for command in commands:
    print(json.dumps({"command": [str(x) for x in command], "cwd": str(base)}), flush=True)
    result = subprocess.run(command, cwd=base, env=env)
    print("exit_code:", result.returncode, flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
record = base / "final-wheel-demo/wheel-verification.json"
target = (
    ROOT / "qa/evidence/S16" / ("windows-final-wheel.json" if windows else "linux-final-wheel.json")
)
with target.open("x", encoding="utf-8") as handle:
    handle.write(record.read_text(encoding="utf-8"))
