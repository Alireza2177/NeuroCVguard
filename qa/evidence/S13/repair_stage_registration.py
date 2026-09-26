"""Correct the copied stage-preparation index, preserving captured predecessor state."""

import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
baseline = json.loads(Path(__file__).with_name("baseline.json").read_text())
path = root / "state/PROJECT_STATUS.json"
status = json.loads(path.read_text())
assert status["current_stage"] == "S13"
assert status["stages"][12] == {
    "id": "S12",
    "status": "IN_PROGRESS",
    "human_accepted": False,
    "evidence_path": "qa/evidence/S13/",
}
assert baseline["project_status"]["stages"][12]["status"] == "READY_FOR_REVIEW"
status["stages"][12] = baseline["project_status"]["stages"][12]
assert status["stages"][13]["id"] == "S13"
status["stages"][13]["evidence_path"] = "qa/evidence/S13/"
path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
print("Restored exact baseline S12 metadata and assigned evidence to S13; no acceptance changed.")
