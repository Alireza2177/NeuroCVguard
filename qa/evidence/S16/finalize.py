"""Reconcile actual S16 evidence and update only the authorized stage."""

import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write(path, value, *, exclusive=False):
    with (ROOT / path).open("x" if exclusive else "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def nodes(name):
    passed, failed = set(), set()
    tree = ET.parse(HERE / (name + ".xml"))
    assert not list(tree.iter("error")) and not list(tree.iter("skipped")), name
    for case in tree.iter("testcase"):
        node = case.attrib["classname"].replace(".", "/") + ".py::" + case.attrib["name"]
        target = failed if case.find("failure") is not None else passed
        assert node not in passed | failed
        target.add(node)
    return passed, failed


def main():
    for name in (
        "build-final",
        "metadata-final",
        "archive-final",
        "distribution-tests-final",
        "linux-matrix",
        "linux-packaging-matrix",
        "windows-catalog-corrected",
        "minimum-catalog-corrected",
        "windows-final-install",
        "linux-final-install",
        "minimum-final-install",
        "minimum-pip-check",
        "minimum-final-probe",
        "lint-close",
        "format-close",
        "types",
        "docs",
        "privacy-scan",
    ):
        assert read(f"qa/evidence/S16/{name}.json")["exit_code"] == 0, name
    records = read("qa/evidence/S16/distributions.json")
    assert records["version"] == "0.1.0"
    for artifact in records["artifacts"]:
        path = ROOT / "dist/s16" / artifact["file"]
        assert path.stat().st_size == artifact["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact["sha256"]
    wheel = next(a for a in records["artifacts"] if a["file"].endswith(".whl"))
    with zipfile.ZipFile(ROOT / "dist/s16-initial" / wheel["file"]) as old:
        with zipfile.ZipFile(ROOT / "dist/s16" / wheel["file"]) as new:
            for name in records["source_payload_hashes"]:
                assert old.read(name) == new.read(name), name
    for platform in ("windows", "linux", "minimum"):
        record = read(f"qa/evidence/S16/{platform}-final-wheel.json")
        assert record["wheel_sha256"] == wheel["sha256"]
        assert record["installed_payloads_match_wheel"] == 53
        assert record["installed_under_environment"] and not record["editable"]
        assert record["demo"] == "completed"

    matrix = []
    previous = None
    for version in ("311", "312", "313"):
        full, failed = nodes("linux-" + version)
        added, added_failed = nodes("linux-" + version + "-packaging")
        assert len(full) == 712 and len(added) == 9 and not failed | added_failed
        assert not full & added
        assert previous is None or previous == full
        previous = full
        matrix.append(
            {
                "environment": "linux-" + version,
                "existing_passed": len(full),
                "separate_packaging_passed": len(added),
                "unique_passed": len(full | added),
                "installation": "isolated editable source snapshot",
            }
        )
    runtime = {
        n
        for n in previous
        if not n.startswith(
            ("tests/test_documentation.py::", "tests/test_foundation_validator.py::")
        )
        and n != "tests/test_bootstrap.py::test_editable_install_points_to_source"
    }
    assert len(runtime) == 678
    for first, corrected in (
        ("windows-wheel-core", "windows-catalog-corrected"),
        ("minimum-tests", "minimum-catalog-corrected"),
    ):
        passed, failed = nodes(first)
        fixed, remaining = nodes(corrected)
        assert len(passed) == 672 and len(fixed) == 6 and not remaining
        assert fixed <= failed and passed | fixed == runtime
        expected = (
            {"tests/test_bootstrap.py::test_editable_install_points_to_source"}
            if first == "minimum-tests"
            else set()
        )
        assert failed - fixed == expected
        matrix.append(
            {
                "environment": first,
                "initial_passed": len(passed),
                "initial_failed": len(failed),
                "corrective_passed": len(fixed),
                "unique_runtime_passed": len(passed | fixed),
                "outside_wheel_scope": sorted(expected),
                "installation": "non-editable initial wheel; runtime bytes equal final",
            }
        )
    matrix.extend({"environment": name, "status": "NOT_RUN"} for name in ("macOS", "hosted CI"))
    write("qa/evidence/S16/platform-matrix.json", matrix, exclusive=True)

    selected = {f"AT-S16-{i:02}": [] for i in range(1, 9)}
    evidence = {
        "01": ["build-final.json", "metadata-final.json", "distributions.json"],
        "02": ["archive-final.json", "distributions.json", "distribution-tests-final.xml"],
        "03": [
            "windows-final-install.json",
            "linux-final-install.json",
            "windows-final-wheel.json",
            "linux-final-wheel.json",
        ],
        "04": ["platform-matrix.json", "linux-matrix.json", "windows-catalog-corrected.xml"],
        "05": [
            "minimum-tests.xml",
            "minimum-catalog-corrected.xml",
            "minimum-final-wheel.json",
            "minimum-pip-check.json",
        ],
        "06": ["distributions.json", "preservation.json"],
        "07": ["review.md", "platform-matrix.json"],
        "08": ["review.md", "preservation.json"],
    }
    package_nodes, failed = nodes("distribution-tests-final")
    assert len(package_nodes) == 9 and not failed
    cases = read("qa/acceptance_cases.json")
    mapping = read("qa/case_to_test_map.json")
    mapping["mappings"] = [m for m in mapping["mappings"] if m["case_id"] not in selected]
    for case in cases:
        if case["id"] not in selected:
            continue
        case.update(implementation_status="IMPLEMENTED", execution_status="PASSED")
        suffix = case["id"][-2:]
        mapping["mappings"].append(
            {
                "case_id": case["id"],
                "stage": "S16",
                "requirement_id": "REQ-S16",
                "execution_status": "PASSED",
                "human_accepted": False,
                "verification_type": "automated_and_implementing_ai_review",
                "test_node_ids": sorted(package_nodes) if suffix in {"01", "02", "06"} else [],
                "evidence": ["qa/evidence/S16/" + n for n in evidence[suffix]]
                + ["state/release/S16_DOSSIER.md", "state/release/S16_CHECKLIST.md"],
                "scope_note": "Local S16 criterion passed; human/public gates remain pending. "
                "AT-S16-04 records unavailable platforms as NOT RUN.",
            }
        )
    write("qa/acceptance_cases.json", cases)
    write("qa/case_to_test_map.json", mapping)
    requirements = read("qa/requirements.json")
    for requirement in requirements:
        if requirement["stage"] == "S16":
            requirement["status"] = "IMPLEMENTED"
    write("qa/requirements.json", requirements)
    status = read("state/PROJECT_STATUS.json")
    assert status["current_stage"] == "S16" and not status["public_release_authorized"]
    for stage in status["stages"]:
        if stage["id"] == "S16":
            stage.update(status="READY_FOR_REVIEW", evidence_path="qa/evidence/S16/")
        assert not stage["human_accepted"]
    write("state/PROJECT_STATUS.json", status)

    baseline = read("qa/evidence/S16/baseline.json")
    changed = []
    for name, digest in baseline["files"].items():
        path = ROOT / name
        assert path.is_file(), name
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            changed.append(name)
    allowed = {
        "AI_ASSISTANCE.md",
        "CHANGELOG.md",
        "docs/installation.md",
        "docs/release.md",
        "pyproject.toml",
        "state/PROJECT_STATUS.json",
        "qa/acceptance_cases.json",
        "qa/case_to_test_map.json",
        "qa/requirements.json",
    }
    assert set(changed) <= allowed, set(changed) - allowed
    for old, new in zip(baseline["status"]["stages"], status["stages"], strict=True):
        if old["id"] != "S16":
            assert old == new
    old_cases = json.loads(
        subprocess.check_output(
            ["git", "show", baseline["revision"] + ":qa/acceptance_cases.json"], cwd=ROOT
        )
    )
    for old, new in zip(old_cases, cases, strict=True):
        if old["stage"] != "S16":
            assert old == new
    assert (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        == (baseline["revision"])
    )
    inputs = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in ("pyproject.toml", "README.md", "LICENSE", ".gitignore")
    }
    write(
        "qa/evidence/S16/preservation.json",
        {
            "base_revision": baseline["revision"],
            "tracked_paths_preserved": len(baseline["files"]),
            "changed_tracked_files": sorted(changed),
            "unchanged_runtime_and_examples": True,
            "non_S16_stages_and_cases_preserved": True,
            "public_release_authorized": False,
            "candidate_metadata_hashes": inputs,
            "payload_hashes": records["source_payload_hashes"],
            "initial_and_final_wheel_runtime_bytes_equal": True,
        },
        exclusive=True,
    )
    print("S16 evidence reconciled; READY_FOR_REVIEW; human acceptance pending; S17 untouched.")


if __name__ == "__main__":
    main()
