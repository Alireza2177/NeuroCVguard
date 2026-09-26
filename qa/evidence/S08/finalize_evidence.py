"""Update only S08 mappings/status, or index the completed command evidence."""

import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).parent


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if sys.argv[1] == "map":
    for name in (
        "pytest-verified",
        "mypy-verified",
        "lint-final",
        "format-completed",
        "installed-verified",
        "packaged-final",
        "rendered-verified",
    ):
        assert json.loads((evidence / f"{name}.json").read_text())["exit_code"] == 0
    # Remove machine hostnames, preserving test names, outcomes and real timings.
    for path in evidence.glob("pytest-*.xml"):
        tree = ET.parse(path)
        for suite in tree.iter("testsuite"):
            suite.attrib.pop("hostname", None)
        tree.write(path, encoding="utf-8", xml_declaration=True)
    suite = ET.parse(evidence / "pytest-verified.xml")
    nodes = [
        item.attrib["classname"].replace(".", "/") + ".py::" + item.attrib["name"]
        for item in suite.iter("testcase")
    ]
    path = root / "qa/case_to_test_map.json"
    data = json.loads(path.read_text())
    assert not any(row["stage"] == "S08" for row in data["mappings"])
    for number in range(1, 14):
        prefix = f"::test_at_s08_{number:02}_"
        selected = [node for node in nodes if prefix in node]
        assert selected
        data["mappings"].append(
            {
                "case_id": f"AT-S08-{number:02}",
                "test_node_ids": selected,
                "evidence": [
                    "qa/evidence/S08/pytest-verified.xml",
                    "qa/evidence/S08/pytest-verified.json",
                    "qa/evidence/S08/review.md",
                ],
                "verification_type": "automated",
                "stage": "S08",
                "requirement_id": "REQ-S08",
                "execution_status": "PASSED",
                "human_accepted": False,
            }
        )
    save(path, data)
    for name in ("qa/acceptance_cases.json", "qa/requirements.json"):
        path = root / name
        rows = json.loads(path.read_text())
        for row in rows:
            if row["stage"] == "S08":
                if "execution_status" in row:
                    row.update(implementation_status="IMPLEMENTED", execution_status="PASSED")
                else:
                    row["status"] = "IMPLEMENTED"
        save(path, rows)
    path = root / "state/PROJECT_STATUS.json"
    status = json.loads(path.read_text())
    assert status["current_stage"] == "S08"
    status["stages"][8]["status"] = "READY_FOR_REVIEW"
    assert status["stages"][8]["human_accepted"] is False
    save(path, status)
    print("Mapped 13 S08 cases and marked READY_FOR_REVIEW; human acceptance remains pending.")
elif sys.argv[1] == "index":
    records = []
    for path in evidence.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "command" in data:
            records.append((path, data))
    lines = [
        "# S08 exact command evidence",
        "",
        "Commands were run from the project root through the S08 recorder. Each JSON",
        "contains the exact argument vector, exit code, timestamp, platform and output.",
        "Paths/usernames are normalized. Failures are retained alongside corrections.",
        "",
        "| Evidence | Exact checked command | Exit |",
        "|---|---|---:|",
    ]
    for path, data in sorted(records, key=lambda row: row[1]["started_at_utc"]):
        command = subprocess.list2cmdline(data["command"]).replace("|", "\\|")
        lines.append(f"| [{path.stem}]({path.name}) | `{command}` | {data['exit_code']} |")
    (evidence / "commands.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    baseline = json.loads((evidence / "baseline.json").read_text())
    names = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
    ).splitlines()
    changed = {}
    added = {}
    for name in names:
        path = root / name
        if not path.is_file() or name.endswith("/change_inventory.json"):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if name not in baseline["files"]:
            added[name] = digest
        elif baseline["files"][name] != digest:
            changed[name] = digest
    save(evidence / "change_inventory.json", {"changed": changed, "added": added})
    print(f"Indexed {len(records)} command records and final changed/new artifact hashes.")
else:
    raise ValueError("Choose map or index")
