"""Check the S00 file inventory without relying on a Git repository."""

import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
baseline = json.loads((Path(__file__).with_name("baseline.json")).read_text())
allowed = {
    "state/PROJECT_STATUS.json",
    "qa/case_to_test_map.json",
    "qa/acceptance_cases.json",
    "qa/requirements.json",
}
changed = []
missing = []
for name, digest in baseline["files"].items():
    path = root / name
    if not path.is_file():
        missing.append(name)
    elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        changed.append(name)
unexpected = sorted(set(changed) - allowed)
assert not missing, missing
assert not unexpected, unexpected
status = json.loads((root / "state/PROJECT_STATUS.json").read_text())
assert status["stages"][1:] == baseline["original_project_status"]["stages"][1:]
assert status["stages"][0]["human_accepted"] is False
assert status["public_release_authorized"] is False
definitions = json.loads(Path(__file__).with_name("register_baseline.json").read_text())
for name, expected in definitions.items():
    rows = json.loads((root / name).read_text())
    actual = {}
    for row in rows:
        definition = {
            key: value
            for key, value in row.items()
            if key not in {"status", "implementation_status", "execution_status"}
        }
        actual[row["id"]] = hashlib.sha256(
            json.dumps(definition, sort_keys=True).encode()
        ).hexdigest()
        if row["stage"] != "S00":
            if "execution_status" in row:
                assert row["execution_status"] == "NOT_RUN"
                assert row["implementation_status"] == "NOT_IMPLEMENTED"
            else:
                assert row["status"] == "NOT_IMPLEMENTED"
    assert actual == expected, name
print(
    json.dumps(
        {
            "original_files": len(baseline["files"]),
            "unchanged_files": len(baseline["files"]) - len(changed),
            "authorized_changed_files": changed,
            "missing_files": missing,
            "unexpected_changes": unexpected,
            "later_stages_unchanged": True,
            "requirement_and_acceptance_definitions_unchanged": True,
            "git_index": "NOT APPLICABLE: no Git repository at baseline",
        },
        indent=2,
    )
)
