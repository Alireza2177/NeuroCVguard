"""Capture the S12 preservation baseline before implementation changes."""

import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).parent
names = subprocess.check_output(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root, text=True
).splitlines()
baseline = {
    "files": {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in names
        if not name.startswith("qa/evidence/S12/")
    },
    "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
    "project_status": json.loads((root / "state/PROJECT_STATUS.json").read_text()),
    "registers": {
        name: json.loads((root / name).read_text())
        for name in ("qa/acceptance_cases.json", "qa/requirements.json", "qa/case_to_test_map.json")
    },
}
with (evidence / "baseline.json").open("x", encoding="utf-8") as handle:
    json.dump(baseline, handle, indent=2)
    handle.write("\n")
for name in ("run_check.py", "close_stage.py"):
    source = (root / "qa/evidence/S11" / name).read_text()
    (evidence / name).write_text(
        source.replace("local S11 check", "local S12 check"), encoding="utf-8"
    )
status = baseline["project_status"]
status["current_stage"] = "S12"
status["stages"][12].update(status="IN_PROGRESS", evidence_path="qa/evidence/S12/")
(root / "state/PROJECT_STATUS.json").write_text(
    json.dumps(status, indent=2) + "\n", encoding="utf-8"
)
print(f"Captured {len(baseline['files'])} preexisting files; S12 IN_PROGRESS.")
