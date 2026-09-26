"""Check the ordinary installed wheel's demo and packaged tutorial assets offline."""

import json
import os
import subprocess
import sys
import sysconfig
import tempfile
from importlib.resources import files
from pathlib import Path

import neurocvguard

assert Path(neurocvguard.__file__).is_relative_to(Path(sys.prefix))
scripts = files("neurocvguard").joinpath("examples")
assert len(list(scripts.iterdir())) >= 5
transcript = {"python": sys.version.split()[0], "installed_import_verified": True, "commands": []}
console = Path(sysconfig.get_path("scripts")) / "neurocvguard.exe"
with tempfile.TemporaryDirectory(prefix="ncg-s13-installed-") as directory:
    work = Path(directory)
    commands = [
        [sys.executable, "-I", "-m", "neurocvguard", "demo", "--out", "module"],
        [str(console), "demo", "--out", "console"],
        *[
            [sys.executable, "-I", str(scripts.joinpath(name)), "--out", name[:-3]]
            for name in (
                "01_cohort_audit.py",
                "02_repeated_observations.py",
                "03_site_held_out.py",
                "04_preprocessing_provenance.py",
                "05_explicit_feature_join.py",
            )
        ],
    ]
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=work,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        row = {
            "command": command,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        transcript["commands"].append(row)
        assert completed.returncode == 0, row
        assert (work / command[-1] / "report.html").is_file()
    assert (work / "module/report.json").read_bytes() == (work / "console/report.json").read_bytes()
    assert (work / "module/report.html").read_bytes() == (work / "console/report.html").read_bytes()
print(json.dumps(transcript, indent=2))
