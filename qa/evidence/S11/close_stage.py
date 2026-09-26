"""Map actual passing stage tests and verify the stage's preservation boundary."""

import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

evidence = Path(__file__).parent
root = evidence.resolve().parents[2]
stage = evidence.name
number = int(stage[1:])
baseline = json.loads((evidence / "baseline.json").read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if sys.argv[1] == "finish":
    for name in ("pytest-final", "lint-final", "format-verified", "mypy-final"):
        assert json.loads((evidence / f"{name}.json").read_text())["exit_code"] == 0
    tree = ET.parse(evidence / "pytest-final.xml")
    for suite in tree.iter("testsuite"):
        suite.attrib.pop("hostname", None)
    tree.write(evidence / "pytest-final.xml", encoding="utf-8", xml_declaration=True)
    nodes = []
    for case in tree.iter("testcase"):
        assert all(case.find(tag) is None for tag in ("failure", "error", "skipped"))
        nodes.append(case.attrib["classname"].replace(".", "/") + ".py::" + case.attrib["name"])
    path = root / "qa/case_to_test_map.json"
    mapping = json.loads(path.read_text())
    assert not any(row["stage"] == stage for row in mapping["mappings"])
    cases = json.loads((root / "qa/acceptance_cases.json").read_text())
    for case in cases:
        if case["stage"] != stage:
            continue
        prefix = "::test_" + case["id"].lower().replace("-", "_") + "_"
        matched = [node for node in nodes if prefix in node]
        assert matched, case["id"]
        mapping["mappings"].append(
            {
                "case_id": case["id"],
                "test_node_ids": matched,
                "evidence": [
                    f"qa/evidence/{stage}/pytest-final.json",
                    f"qa/evidence/{stage}/pytest-final.xml",
                ],
                "verification_type": "automated",
                "stage": stage,
                "requirement_id": f"REQ-{stage}",
                "execution_status": "PASSED",
                "human_accepted": False,
            }
        )
        case.update(implementation_status="IMPLEMENTED", execution_status="PASSED")
    save(path, mapping)
    save(root / "qa/acceptance_cases.json", cases)
    requirements = json.loads((root / "qa/requirements.json").read_text())
    for row in requirements:
        if row["stage"] == stage:
            row["status"] = "IMPLEMENTED"
    save(root / "qa/requirements.json", requirements)
    path = root / "state/PROJECT_STATUS.json"
    status = json.loads(path.read_text())
    assert status["current_stage"] == stage
    status["stages"][number]["status"] = "READY_FOR_REVIEW"
    save(path, status)
    print(
        f"{stage}: mapped acceptance cases from {len(nodes)} passing tests; human review pending."
    )
elif sys.argv[1] == "verify":
    allowed = set(json.loads((evidence / "allowed_changes.json").read_text()))
    changed = []
    for name, digest in baseline["files"].items():
        path = root / name
        assert path.is_file(), name
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            changed.append(name)
    assert set(changed) <= allowed, changed
    status = json.loads((root / "state/PROJECT_STATUS.json").read_text())
    assert status["stages"][number]["status"] == "READY_FOR_REVIEW"
    for before, after in zip(baseline["project_status"]["stages"], status["stages"], strict=True):
        assert not after["human_accepted"]
        if before["id"] != stage:
            assert before == after
    for name in ("qa/acceptance_cases.json", "qa/requirements.json"):
        rows = json.loads((root / name).read_text())
        for before, after in zip(baseline["registers"][name], rows, strict=True):
            expected = dict(before)
            if before["stage"] == stage:
                if "execution_status" in expected:
                    expected.update(implementation_status="IMPLEMENTED", execution_status="PASSED")
                else:
                    expected["status"] = "IMPLEMENTED"
            assert expected == after
    rows = json.loads((root / "qa/case_to_test_map.json").read_text())["mappings"]
    assert [row for row in rows if row["stage"] != stage] == baseline["registers"][
        "qa/case_to_test_map.json"
    ]["mappings"]
    print(
        json.dumps(
            {
                "retained": len(baseline["files"]),
                "unchanged": len(baseline["files"]) - len(changed),
                "changed": changed,
                "other_stage_status_and_normative_definitions_preserved": True,
            },
            indent=2,
        )
    )
elif sys.argv[1] == "index":
    records = []
    for path in evidence.glob("*.json"):
        item = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(item, dict) and "command" in item:
            records.append((path, item))
    lines = [
        f"# {stage} command evidence",
        "",
        "Exact argument vectors, exit codes, environment and outputs are in each record.",
        "",
        "| Evidence | Command | Exit |",
        "|---|---|---:|",
    ]
    for path, item in sorted(records, key=lambda row: row[1]["started_at_utc"]):
        command = subprocess.list2cmdline(item["command"]).replace("|", "\\|")
        lines.append(f"| [{path.stem}]({path.name}) | `{command}` | {item['exit_code']} |")
    (evidence / "commands.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Indexed {len(records)} checks.")
else:
    raise ValueError("Choose finish, verify or index")
