"""Validate executed evidence, update only authorized case statuses and retain history."""

import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def test_nodes(paths):
    nodes = set()
    for path in paths:
        tree = ET.parse(ROOT / path)
        assert (
            not list(tree.iter("failure")) + list(tree.iter("error")) + list(tree.iter("skipped"))
        )
        for case in tree.iter("testcase"):
            node = case.attrib["classname"].replace(".", "/") + ".py::" + case.attrib["name"]
            assert node not in nodes, node
            nodes.add(node)
    return nodes


def main():
    shards = read("qa/evidence/S15/shards.json")
    files = [name for group in shards.values() for name in group]
    assert len(files) == len(set(files))
    assert set(files) == {
        p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("test_*.py")
    }
    final_xml = [f"qa/evidence/S15/verified-{i}.xml" for i in range(4)]
    nodes = test_nodes(final_xml)
    baseline = test_nodes(["qa/evidence/S15/baseline.xml"])
    assert baseline <= nodes
    assert read("qa/evidence/S15/coverage-gate.json")["passed"]
    for name in (
        "verified-0",
        "verified-1",
        "verified-2",
        "verified-3",
        "docs",
        "lint-close",
        "format-close",
        "types-final",
        "mutations",
        "benchmarks",
        "doctests",
        "security-record-check",
    ):
        assert read(f"qa/evidence/S15/{name}.json")["exit_code"] == 0, name
    mutation = read("qa/evidence/S15/mutation-results.json")
    assert len(mutation) == 10 and all(
        r["mutant_exit"] == 1 and r["restored_exit"] == 0 and r["restored_identically"]
        for r in mutation
    )
    mapping = read("qa/case_to_test_map.json")
    # Two S00 mappings still pointed to six pre-CLI parameter display names.
    # Preserve them explicitly as historical evidence; refresh only current IDs.
    refreshed = []
    for entry in mapping["mappings"]:
        old = entry.get("test_node_ids", [])
        missing = [node for node in old if node not in nodes]
        if missing:
            assert entry["case_id"] in {"AT-S00-02", "AT-S00-04"}
            entry["historical_test_node_ids"] = old.copy()
            updated = []
            for node in old:
                if node in nodes:
                    updated.append(node)
                    continue
                prefix = node.split("-", 1)[0]
                suffix = node.rsplit("-", 1)[1]
                candidates = [
                    n for n in nodes if n.startswith(prefix + "-") and n.endswith("-" + suffix)
                ]
                assert len(candidates) == 1, (node, candidates)
                updated.append(candidates[0])
            entry["test_node_ids"] = updated
            entry["evidence"] = [*entry["evidence"], *final_xml]
            refreshed.append(entry["case_id"])
    selected = {
        "AT-S14-01": ("test_at_s14_01",),
        "AT-S14-02": ("test_at_s14_02",),
        "AT-S14-03": ("test_at_s14_03",),
        "AT-S14-04": ("test_at_s14_04",),
        "AT-S14-05": ("test_rule_catalog_and_limitations",),
        "AT-S14-06": ("test_at_s14_06",),
        "AT-S14-07": (),
        "AT-S14-08": (),
        "AT-S15-01": (),
        "AT-S15-02": (
            "test_at_s15_02",
            "test_components_match_independent_graph_oracle",
            "test_at_s06_",
        ),
        "AT-S15-03": (),
        "AT-S15-04": ("test_at_s15_04", "test_remote_spellings"),
        "AT-S15-05": (),
        "AT-S15-06": ("test_at_s15_06", "test_at_s02_16"),
        "AT-S15-07": ("test_at_s15_07",),
        "AT-S15-08": (),
        "AT-S15-09": (),
    }
    mapping["mappings"] = [r for r in mapping["mappings"] if r["case_id"] not in selected]
    cases = read("qa/acceptance_cases.json")
    for case in cases:
        if case["id"] not in selected:
            continue
        case_id = case["id"]
        pending = case_id == "AT-S14-08"
        case.update(
            implementation_status="IMPLEMENTED", execution_status="NOT_RUN" if pending else "PASSED"
        )
        stage = case["stage"]
        matches = sorted(
            n
            for n in nodes
            if any(n.split("::", 1)[1].startswith(prefix) for prefix in selected[case_id])
        )
        evidence = [f"qa/evidence/{stage}/review.md", *final_xml]
        if stage == "S15":
            evidence += [
                "qa/evidence/S15/coverage-gate.json",
                "qa/evidence/S15/mutation-results.json",
                "qa/evidence/S15/benchmark-results.json",
                "state/decisions/ADR-S15-001-cold-dependency-rng.md",
            ]
        if pending:
            evidence = ["docs/ownership.md", "state/handoffs/S14.md"]
        mapping["mappings"].append(
            {
                "case_id": case_id,
                "test_node_ids": matches,
                "evidence": evidence,
                "verification_type": "human_pending" if pending else "automated_and_ai_review",
                "stage": stage,
                "requirement_id": "REQ-" + stage,
                "execution_status": case["execution_status"],
                "human_accepted": False,
            }
        )
    mapping["note"] = (
        "Current test IDs and actual evidence are mapped per case. Historical "
        "S00 parameter IDs are retained separately. Human acceptance remains separate; "
        "S14 walkthrough pending; S15 first-import exception explicitly approved."
    )
    write("qa/case_to_test_map.json", mapping)
    write("qa/acceptance_cases.json", cases)
    requirements = read("qa/requirements.json")
    for requirement in requirements:
        if requirement["stage"] in ("S14", "S15"):
            requirement["status"] = "IMPLEMENTED"
    write("qa/requirements.json", requirements)
    status = read("state/PROJECT_STATUS.json")
    status["current_stage"] = "S15"
    for stage in status["stages"]:
        if stage["id"] in ("S14", "S15"):
            stage.update(status="READY_FOR_REVIEW", evidence_path=f"qa/evidence/{stage['id']}/")
        assert not stage["human_accepted"]
    assert all(s["status"] == "NOT_STARTED" for s in status["stages"] if s["id"] in ("S16", "S17"))
    write("state/PROJECT_STATUS.json", status)
    original = read("qa/evidence/S14/baseline.json")
    retained, changed = [], []
    for name, digest in original["files"].items():
        path = ROOT / name
        assert path.is_file(), name
        (retained if hashlib.sha256(path.read_bytes()).hexdigest() == digest else changed).append(
            name
        )
    allowed = {
        ".gitignore",
        "AI_ASSISTANCE.md",
        "README.md",
        "pyproject.toml",
        "state/PROJECT_STATUS.json",
        "qa/case_to_test_map.json",
        "qa/acceptance_cases.json",
        "qa/requirements.json",
        "tests/test_bootstrap.py",
    }
    allowed.update(
        "docs/" + name + ".md"
        for name in (
            "association_diagnostics",
            "cohort_checks",
            "comparison",
            "contracts",
            "evaluation",
            "preprocessing_provenance",
            "reporting",
            "split_audits",
            "split_generation",
            "synthetic_examples",
        )
    )
    allowed.update(
        "src/neurocvguard/" + name + ".py"
        for name in (
            "_projection",
            "_report_writes",
            "_tables",
            "cli",
            "comparison",
            "config",
            "demo",
            "io",
            "provenance",
        )
    )
    assert set(changed) <= allowed, set(changed) - allowed
    for old, new in zip(original["status"]["stages"], status["stages"], strict=True):
        if old["id"] not in ("S14", "S15"):
            assert old == new
    before_cases = json.loads(
        subprocess.check_output(
            ["git", "show", original["revision"] + ":qa/acceptance_cases.json"], cwd=ROOT
        )
    )
    for old, new in zip(before_cases, cases, strict=True):
        if old["stage"] not in ("S14", "S15"):
            assert old == new
        else:
            assert {
                k: v
                for k, v in old.items()
                if k not in ("implementation_status", "execution_status")
            } == {
                k: v
                for k, v in new.items()
                if k not in ("implementation_status", "execution_status")
            }
    report = {
        "baseline_files": len(original["files"]),
        "unchanged": len(retained),
        "allowed_existing_changes": changed,
        "baseline_tests_retained": len(baseline),
        "final_tests": len(nodes),
        "new_tests_since_baseline": len(nodes - baseline),
        "refreshed_historical_mappings": refreshed,
        "stages": "S14/S15 READY_FOR_REVIEW",
        "human_acceptance": "pending",
        "S16_S17": "NOT_STARTED",
    }
    write("qa/evidence/S15/preservation.json", report)
    for stage_name in ("S14", "S15"):
        directory = ROOT / "qa/evidence" / stage_name
        lines = [
            f"# {stage_name} recorded commands",
            "",
            "Exact argument vectors, environments, timestamps and outputs are in the linked JSON.",
            "Failed attempts are retained; later correction does not change their exit status.",
            "",
            "| Record | Exit | Command argument vector |",
            "|---|---:|---|",
        ]
        for path in sorted(directory.glob("*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, dict) and {"command", "exit_code"} <= value.keys():
                command = json.dumps(value["command"]).replace("|", "&#124;")
                lines.append(f"| [{path.name}]({path.name}) | {value['exit_code']} | `{command}` |")
        (directory / "commands.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
