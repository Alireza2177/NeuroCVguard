"""Verify S01 preservation, stage boundaries, acceptance links and recorded checks."""

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).parent
baseline = json.loads((evidence / "baseline.json").read_text())
allowed = {
    "AI_ASSISTANCE.md",
    "README.md",
    "pyproject.toml",
    "src/neurocvguard/__init__.py",
    "state/PROJECT_STATUS.json",
    "qa/case_to_test_map.json",
    "qa/acceptance_cases.json",
    "qa/requirements.json",
}
changed = []
for name, digest in baseline["files"].items():
    path = root / name
    assert path.is_file(), name
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        changed.append(name)
assert set(changed) <= allowed, changed
status = json.loads((root / "state/PROJECT_STATUS.json").read_text())
assert status["current_stage"] == "S01"
assert status["stages"][0] == baseline["project_status"]["stages"][0]
assert status["stages"][2:] == baseline["project_status"]["stages"][2:]
assert status["stages"][1]["status"] == "READY_FOR_REVIEW"
assert all(row["human_accepted"] is False for row in status["stages"])
assert status["public_release_authorized"] is False

definitions = json.loads((root / "qa/evidence/S00/register_baseline.json").read_text())
for name, expected in definitions.items():
    actual = {}
    for row in json.loads((root / name).read_text()):
        definition = {
            key: value
            for key, value in row.items()
            if key not in {"status", "implementation_status", "execution_status"}
        }
        actual[row["id"]] = hashlib.sha256(
            json.dumps(definition, sort_keys=True).encode()
        ).hexdigest()
        if "execution_status" in row:
            assert row["execution_status"] == (
                "PASSED" if row["stage"] in {"S00", "S01"} else "NOT_RUN"
            )
            assert row["implementation_status"] == (
                "IMPLEMENTED" if row["stage"] in {"S00", "S01"} else "NOT_IMPLEMENTED"
            )
        else:
            assert row["status"] == (
                "IMPLEMENTED" if row["stage"] in {"S00", "S01"} else "NOT_IMPLEMENTED"
            )
    assert actual == expected, name

suite = ET.parse(evidence / "pytest-final.xml")
nodes = {
    item.attrib["classname"].replace(".", "/") + ".py::" + item.attrib["name"]
    for item in suite.iter("testcase")
}
assert len(nodes) == 79
for item in suite.iter("testcase"):
    assert not any(item.find(tag) is not None for tag in ("failure", "error", "skipped"))
mappings = json.loads((root / "qa/case_to_test_map.json").read_text())["mappings"]
s01 = [row for row in mappings if row["stage"] == "S01"]
assert {row["case_id"] for row in s01} == {f"AT-S01-{number:02}" for number in range(1, 12)}
for row in s01:
    assert row["test_node_ids"] and set(row["test_node_ids"]) <= nodes
    assert row["human_accepted"] is False
    assert all((root / name).is_file() for name in row["evidence"])

checks = (
    "pytest-final",
    "doctests",
    "mypy-final",
    "ruff-passed",
    "format-passed",
    "install-editable-final",
    "install-ordinary-final",
    "installed-resources",
    "pip-check",
)
for name in checks:
    assert json.loads((evidence / (name + ".json")).read_text())["exit_code"] == 0, name
schemas = list((root / "contracts").glob("*.schema.json"))
assert len(schemas) == 6
for path in schemas:
    assert path.read_bytes() == (root / "src/neurocvguard/schemas" / path.name).read_bytes()
assert (root / "state/handoffs/S01.md").is_file()
print(
    json.dumps(
        {
            "baseline_files_retained": len(baseline["files"]),
            "unchanged_baseline_files": len(baseline["files"]) - len(changed),
            "authorized_changed_files": sorted(changed),
            "s00_status_and_historical_evidence_unchanged": True,
            "normative_definitions_unchanged": True,
            "later_stages_unchanged": True,
            "packaged_schemas_identical": len(schemas),
            "passing_suite_tests": len(nodes),
            "s01_cases_mapped": len(s01),
            "human_acceptance": "pending",
        },
        indent=2,
    )
)
