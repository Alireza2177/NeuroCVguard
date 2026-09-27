"""Copy trusted repository test inputs into fresh, owned verification directories."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
paths = json.loads((ROOT / "dist/s16-environments.json").read_text())
if sys.platform == "win32":
    base = Path(paths["windows_root"])
    for name in ("wheel312", "minimum311"):
        target = base / (name + "-checks")
        target.mkdir()
        for directory in ("tests", "fixtures", "contracts", "docs", "examples"):
            shutil.copytree(
                ROOT / directory,
                target / directory,
                ignore=shutil.ignore_patterns("__pycache__", "_build"),
            )
        shutil.copyfile(ROOT / "tools/verify_wheel.py", base / name / "verify_wheel.py")
        (target / "pytest.ini").write_text("[pytest]\naddopts = --strict-markers --strict-config\n")
        assert not (target / "src").exists()
        (target / "qa").mkdir()
        shutil.copyfile(ROOT / "qa/rule_catalog.json", target / "qa/rule_catalog.json")
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    tracked += [str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "tools").glob("*.py")]
    tracked += [
        str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "tests").glob("test_*.py")
    ]
    (ROOT / "dist/s16-source-files.json").write_text(json.dumps(sorted(set(tracked))))
else:
    target = Path(paths["linux_root"]) / "source"
    target.mkdir(parents=True)
    for name in json.loads((ROOT / "dist/s16-source-files.json").read_text()):
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        destination = target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
print("Prepared external test snapshot; original repository remains untouched.")
