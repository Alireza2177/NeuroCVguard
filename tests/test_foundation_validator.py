"""AT-S15-09: artifact checks cannot masquerade as application or human acceptance."""

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path, PureWindowsPath

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/validate_foundation.py"


@pytest.fixture
def validator():
    spec = importlib.util.spec_from_file_location("foundation_validator_probe", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_report(validator, tmp_path, mode):
    output = tmp_path / f"{mode}.json"
    code = validator.main(["--mode", mode, "--output", str(output)])
    return code, json.loads(output.read_text(encoding="utf-8"))


def test_artifacts_pass_without_claiming_application_acceptance(validator, tmp_path):
    code, report = run_report(validator, tmp_path, "artifacts")
    assert code == 0 and report["checks_failed"] == 0
    assert report["application_tests_executed"] == 0
    status = json.loads((ROOT / "state/PROJECT_STATUS.json").read_text(encoding="utf-8"))
    assert report["reported_software_status"] == status["software_status"]
    assert len(report["snapshot_checks_not_applied"]) == 3
    assert "human acceptance" in report["scope"]
    assert "software-not-claimed" not in {row["check"] for row in report["checks"]}


def test_default_foundation_gate_still_rejects_implemented_repository(tmp_path):
    output = tmp_path / "foundation.json"
    result = subprocess.run(
        [sys.executable, str(TOOL), "--output", str(output)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    report = json.loads(output.read_text(encoding="utf-8"))
    assert result.returncode == 1 and report["mode"] == "foundation"
    assert report["snapshot_checks_not_applied"] == []
    assert {r["check"] for r in report["checks"] if not r["passed"]} == {
        "all-required-cases-unrun",
        "software-not-claimed",
        "no-invented-stage-passes",
    }
    assert "KeyError" not in result.stderr


@pytest.mark.parametrize("mode", ["foundation", "artifacts"])
def test_both_modes_reject_corrupted_known_answer_fixture(validator, tmp_path, monkeypatch, mode):
    read = validator.read_json

    def damaged(path):
        value = copy.deepcopy(read(path))
        if path == "fixtures/splits_clean.json":
            value["folds"][0]["test_ids"] = ["NOT-IN-COHORT"]
        return value

    monkeypatch.setattr(validator, "read_json", damaged)
    code, report = run_report(validator, tmp_path, mode)
    assert code == 1
    assert any(
        r["check"].startswith("splits_clean.json:coverage:") and not r["passed"]
        for r in report["checks"]
    )


def test_windows_schema_keys_use_manifest_spelling(validator, tmp_path, monkeypatch):
    original = Path.relative_to

    def windows_relative(self, *args, **kwargs):
        # Force Windows spelling even when this regression runs on Linux/macOS.
        return PureWindowsPath(original(self, *args, **kwargs))

    monkeypatch.setattr(Path, "relative_to", windows_relative)
    code, report = run_report(validator, tmp_path, "artifacts")
    assert code == 0
    assert any(
        r["check"] == "fixture:fixtures/config.json" and r["passed"] for r in report["checks"]
    )


def test_existing_evidence_is_never_overwritten(validator, tmp_path):
    output = tmp_path / "existing.json"
    output.write_bytes(b"original evidence")
    with pytest.raises(SystemExit) as error:
        validator.main(["--mode", "artifacts", "--output", str(output)])
    assert error.value.code == 2
    assert output.read_bytes() == b"original evidence"


def test_no_output_means_no_record_write(validator, monkeypatch):
    original = Path.open

    def no_writes(self, mode="r", *args, **kwargs):
        assert not any(flag in mode for flag in "wax+"), self
        return original(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", no_writes)
    assert validator.main(["--mode", "artifacts"]) == 0


def test_repeated_calls_do_not_accumulate_checks(validator, tmp_path):
    _, first = run_report(validator, tmp_path, "foundation")
    _, second = run_report(validator, tmp_path, "artifacts")
    assert first["checks_total"] == second["checks_total"] + 3


def test_original_snapshot_conditions_still_pass(validator, tmp_path, monkeypatch):
    read = validator.read_json

    def original_snapshot(path):
        value = copy.deepcopy(read(path))
        if path == "state/PROJECT_STATUS.json":
            value["software_status"] = "NOT_IMPLEMENTED"
            value["public_release_authorized"] = False
            for stage in value["stages"]:
                stage.update(status="NOT_STARTED", human_accepted=False)
        elif path == "qa/acceptance_cases.json":
            for case in value:
                case["execution_status"] = "NOT_RUN"
        return value

    monkeypatch.setattr(validator, "read_json", original_snapshot)
    code, report = run_report(validator, tmp_path, "foundation")
    assert code == 0 and report["checks_failed"] == 0
    assert report["snapshot_checks_not_applied"] == []
