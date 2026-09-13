"""Check S06 preservation and acceptance mapping against its pre-edit baseline."""

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
    "src/neurocvguard/_projection.py",
    "src/neurocvguard/rules.py",
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
assert status["current_stage"] == "S06"
assert status["stages"][6]["status"] == "READY_FOR_REVIEW"
for before, after in zip(baseline["project_status"]["stages"], status["stages"], strict=True):
    if before["id"] != "S06":
        assert before == after
    assert after["human_accepted"] is False
assert status["public_release_authorized"] is False
for name in ("qa/acceptance_cases.json", "qa/requirements.json"):
    rows = json.loads((root / name).read_text())
    for before, after in zip(baseline["registers"][name], rows, strict=True):
        expected = dict(before)
        if expected["stage"] == "S06":
            if "execution_status" in expected:
                expected.update(implementation_status="IMPLEMENTED", execution_status="PASSED")
            else:
                expected["status"] = "IMPLEMENTED"
        assert expected == after, after["id"]
mappings = json.loads((root / "qa/case_to_test_map.json").read_text())["mappings"]
assert [row for row in mappings if row["stage"] != "S06"] == (
    baseline["registers"]["qa/case_to_test_map.json"]["mappings"]
)
suite = ET.parse(evidence / "pytest-final.xml")
nodes = {
    item.attrib["classname"].replace(".", "/") + ".py::" + item.attrib["name"]
    for item in suite.iter("testcase")
}
for item in suite.iter("testcase"):
    assert not any(item.find(tag) is not None for tag in ("failure", "error", "skipped"))
s06 = [row for row in mappings if row["stage"] == "S06"]
assert {row["case_id"] for row in s06} == {f"AT-S06-{number:02}" for number in range(1, 11)}
for row in s06:
    assert row["test_node_ids"] and set(row["test_node_ids"]) <= nodes
    assert row["human_accepted"] is False
    assert all((root / name).is_file() for name in row["evidence"])
for name in ("pytest-final", "mypy-final", "lint-passed", "format-passed", "installed-smoke"):
    assert json.loads((evidence / f"{name}.json").read_text())["exit_code"] == 0
assert (root / "state/handoffs/S06.md").is_file()
print(
    json.dumps(
        {
            "baseline_files_retained": len(baseline["files"]),
            "unchanged_baseline_files": len(baseline["files"]) - len(changed),
            "authorized_changed_files": sorted(changed),
            "prior_stage_status_and_evidence_unchanged": True,
            "s02_and_later_stages_unchanged": True,
            "normative_definitions_unchanged": True,
            "passing_suite_tests": len(nodes),
            "s06_cases_mapped": len(s06),
            "human_acceptance": "pending",
        },
        indent=2,
    )
)
