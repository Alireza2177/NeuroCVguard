"""S13.B offline journeys, diagnostics, staging and actual report consistency."""

import hashlib
import json
import random
import socket
from dataclasses import replace

import numpy as np
import pytest
from sklearn.pipeline import Pipeline
from test_cli_commands import process
from test_contracts import fixture

from neurocvguard import write_report
from neurocvguard.cli import main
from neurocvguard.demo import run_demo
from neurocvguard.errors import InputValidationError
from neurocvguard.models import AuditReport, EvaluationResult
from neurocvguard.synthetic import SCENARIOS, SYNTHETIC_NOTICE


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def demos(tmp_path_factory):
    root = tmp_path_factory.mktemp("synthetic-demos")
    # Deny Python networking during the complete generation/audit/evaluation/export run.
    with pytest.MonkeyPatch.context() as patch:

        def forbidden(*args, **kwargs):
            pytest.fail("offline demo attempted network access")

        patch.setattr(socket.socket, "connect", forbidden)
        patch.setattr(socket, "create_connection", forbidden)
        for scenario in SCENARIOS:
            result = run_demo(output_dir=root / scenario, scenario=scenario)
            assert result.execution_status == "completed"
    return root


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_at_s13_04_offline_full_workflow_and_provenance(demos, scenario):
    directory = demos / scenario
    manifest = read(directory / "demo.private.json")
    assert manifest["synthetic"] is True and manifest["sensitive"] is True
    assert manifest["parameters"]["seed"] == 2026
    assert manifest["invocation"] == "Python API" and manifest["command"] is None
    assert manifest["versions"]["python"] and manifest["versions"]["scikit-learn"]
    for name, digest in manifest["output_sha256"].items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
    for file in directory.glob("*.manifest.json"):
        assert all((directory / name).is_file() for name in read(file)["artifacts"])
    participant = EvaluationResult.from_dict(
        read(directory / "participant.evaluation.private.json")
    )
    assert not participant.diagnostic_only and participant.pooled_metrics.n_participants == 60
    assert participant.cohort_digest == manifest["cohort_digest"]
    assert participant.feature_digest == manifest["feature_digest"]
    assert AuditReport.from_dict(read(directory / "report.json")).to_dict() == read(
        directory / "report.json"
    )
    if scenario == "repeated":
        diagnostic = EvaluationResult.from_dict(
            read(directory / "observation-diagnostic.evaluation.private.json")
        )
        assert diagnostic.diagnostic_only
        assert diagnostic.pooled_metrics.n_participants == 60
        assert sum(f.test_participants for f in diagnostic.folds) > 60
        text = (directory / "report.html").read_text(encoding="utf-8")
        assert "valid_for_objective=false" in text
        assert "Do not report as evidence for unseen-participant generalization" in text
    elif scenario == "site_shift":
        other = EvaluationResult.from_dict(
            read(directory / "site-held-out.evaluation.private.json")
        )
        assert other.objective == "unseen_site" and not other.diagnostic_only
        assert other.feature_digest == participant.feature_digest


def test_at_s13_02_complete_demo_preserves_rng(demos, tmp_path):
    before, py_before = np.random.get_state(), random.getstate()
    run_demo(output_dir=tmp_path / "again")
    after = np.random.get_state()
    assert before[0] == after[0] and before[2:] == after[2:]
    np.testing.assert_array_equal(before[1], after[1])
    assert py_before == random.getstate()
    for path in (demos / "clean").iterdir():
        assert path.read_bytes() == (tmp_path / "again" / path.name).read_bytes()


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_at_s13_06_public_reports_label_synthetic_without_enabling_details(
    demos, scenario, tmp_path
):
    directory = demos / scenario
    for file in directory.glob("*report.json"):
        data = read(file)
        assert SYNTHETIC_NOTICE in data["limitations"]
        assert data["provenance"]["sensitive_details"] is False
        assert "SYN-person-" not in file.read_text(encoding="utf-8")
        assert "SYN-obs-" not in file.read_text(encoding="utf-8")
    report = AuditReport.from_dict(read(directory / "report.json"))
    paths = write_report(report, output_dir=tmp_path)
    assert paths["json"].read_bytes() == (directory / "report.json").read_bytes()
    assert "Fully synthetic demonstration" in paths["html"].read_text(encoding="utf-8")
    assert "not biologically realistic" in paths["html"].read_text(encoding="utf-8")


def test_only_exact_fixed_synthetic_notice_is_preserved():
    original = AuditReport.from_dict(fixture("report_schema_example"))
    forged = replace(original, limitations=(SYNTHETIC_NOTICE + " <script>private</script>",))
    assert "private" not in str(forged.to_dict()["limitations"])
    labelled = replace(original, limitations=(SYNTHETIC_NOTICE,))
    assert labelled.to_dict()["provenance"]["sensitive_details"] is False


def test_at_s13_07_displayed_values_are_actual_projected_results(demos):
    for scenario in SCENARIOS:
        directory = demos / scenario
        root = read(directory / "report.json")
        html = (directory / "report.html").read_text(encoding="utf-8")
        if scenario == "clean":
            private = EvaluationResult.from_dict(
                read(directory / "participant.evaluation.private.json")
            )
            assert root["evaluation_summary"] == private.to_dict()["evaluation_summary"]
        else:
            for item in root["comparison_summary"]["differences"]:
                assert (
                    str(item["difference"]) if item["difference"] is not None else "Null"
                ) in html
        assert "causal amount of leakage" not in html


def test_demo_cli_module_console_and_no_overwrite(tmp_path):
    args = ["demo", "--out", str(tmp_path / "module")]
    module = process(args, tmp_path)
    console = process(["demo", "--out", str(tmp_path / "console")], tmp_path, "console")
    assert module.returncode == console.returncode == 0
    assert (module.stdout, module.stderr) == (console.stdout, console.stderr)
    assert "synthetic=true" in module.stdout and "no patient data" in module.stderr
    for name in ("report.json", "report.html", "cohort.tsv", "features.tsv"):
        assert (tmp_path / "module" / name).read_bytes() == (
            tmp_path / "console" / name
        ).read_bytes()
    before = {p.name: p.read_bytes() for p in (tmp_path / "module").iterdir()}
    assert main(args) == 2
    assert before == {p.name: p.read_bytes() for p in (tmp_path / "module").iterdir()}
    (tmp_path / "module/unrelated.txt").write_text("retain me")
    assert main(args + ["--overwrite", "--sensitive-details"]) == 0
    assert (tmp_path / "module/unrelated.txt").read_text() == "retain me"
    assert read(tmp_path / "module/report.json")["provenance"]["sensitive_details"] is True


def test_bundle_conflict_preserves_existing_report(tmp_path):
    path = tmp_path / "report.html"
    path.write_text("previous-good-report")
    with pytest.raises(InputValidationError):
        run_demo(output_dir=tmp_path)
    assert path.read_text() == "previous-good-report"
    assert set(p.name for p in tmp_path.iterdir()) == {"report.html"}


def test_failed_fit_retains_incomplete_demo_and_exit_four(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise ValueError("synthetic expected failure")

    monkeypatch.setattr(Pipeline, "fit", fail)
    assert main(["demo", "--out", str(tmp_path)]) == 4
    result = read(tmp_path / "participant.evaluation.private.json")
    assert result["execution_status"] == "incomplete" and result["pooled_metrics"] is None
    assert len(result["folds"]) == 3 and all(f["status"] == "failed" for f in result["folds"])
    assert read(tmp_path / "demo.private.json")["execution_status"] == "incomplete"
