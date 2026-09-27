"""Check built metadata and install a wheel outside the checkout on each CI OS."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import venv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--constraints", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = args.out.resolve()
    if destination.is_relative_to(root):
        parser.error("The clean wheel environment must be outside the checkout")
    if destination.exists():
        parser.error("Choose a fresh output directory; existing paths are never replaced")
    distributions = sorted(args.dist.resolve().iterdir())
    wheels = [p for p in distributions if p.suffix == ".whl"]
    if len(wheels) != 1:
        parser.error("Expected exactly one wheel")
    subprocess.run(
        [sys.executable, "-m", "twine", "check", "--strict", *map(str, distributions)], check=True
    )
    destination.mkdir(parents=True)
    wheel = destination / wheels[0].name
    shutil.copyfile(wheels[0], wheel)
    probe = destination / "verify_wheel.py"
    shutil.copyfile(root / "tools/verify_wheel.py", probe)
    environment = destination / "environment"
    venv.create(environment, with_pip=True)
    scripts = environment / ("Scripts" if sys.platform == "win32" else "bin")
    python = scripts / ("python.exe" if sys.platform == "win32" else "python")
    console = scripts / ("neurocvguard.exe" if sys.platform == "win32" else "neurocvguard")
    install = [str(python), "-m", "pip", "install", str(wheel)]
    if args.constraints:
        install += ["-c", str(args.constraints.resolve())]
    commands = [
        install,
        [str(python), "-m", "pip", "check"],
        [str(console), "--version"],
        [str(console), "--help"],
        [
            str(python),
            "-I",
            str(probe),
            "--forbid-root",
            str(root),
            "--wheel",
            str(wheel),
            "--out",
            str(destination / "demo"),
        ],
    ]
    for command in commands:
        subprocess.run(command, cwd=destination, check=True)


if __name__ == "__main__":
    main()
