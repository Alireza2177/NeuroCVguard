"""S10.C CLI code 0/2/3/4, private/public separation and non-executable inputs."""

import json
import pickle
from dataclasses import replace

import pytest
from sklearn.pipeline import Pipeline
from test_cli_commands import FIXTURES, process
from test_evaluation_preflight import evaluation_inputs

from neurocvguard import evaluate_baseline
from neurocvguard.cli import main
from neurocvguard.models import AuditReport, EvaluationResult


def arguments(output):
    return [
        "evaluate",
        "--cohort",
        str(FIXTURES / "cohort_clean.tsv"),
        "--features",
        str(FIXTURES / "features_shuffled.tsv"),
        "--splits",
        str(FIXTURES / "splits_clean.json"),
        "--config",
        str(FIXTURES / "config.json"),
        "--out",
        str(output),
    ]


def test_at_s10_15_cli_private_public_and_api(tmp_path, capsys):
    assert main(arguments(tmp_path)) == 0
    output = capsys.readouterr()
    assert "evaluation.private.json contains fit IDs" in output.err
    assert "metric_unit=participant" in output.out
    assert "obs-" not in output.out + output.err
    private = json.loads((tmp_path / "evaluation.private.json").read_text())
    result = EvaluationResult.from_dict(private)
    cohort, plan, config = evaluation_inputs()
    assert result == evaluate_baseline(cohort, plan, config=config)
    public = json.loads((tmp_path / "report.json").read_text())
    assert public == result.to_dict()
    assert public["execution_status"] == "partial"
    assert public["evaluation_summary"]["execution_status"] == "completed"
    assert AuditReport.from_dict(public).to_dict() == public
    assert "subject_id" in public["input_summary"]["supplied_roles"]
    assert "phase" in public["input_summary"]["missing_roles"]
    assert "training-observation statistics" in " ".join(public["limitations"])
    combined = (tmp_path / "report.json").read_text() + (tmp_path / "report.html").read_text()
    for marker in (
        "obs-001-1",
        "sub-001",
        result.feature_digest,
        result.plan_digest,
        "fit_ids",
        "actual_plan",
    ):
        assert marker not in combined
    assert public["evaluation_summary"]["pooled_metrics"] is None
    assert public["evaluation_summary"]["metrics_hidden_reason"] == "privacy_small_cells"
    assert "No fitted model" in (tmp_path / "README.SENSITIVE.txt").read_text()
    rerendered = tmp_path.parent / (tmp_path.name + "-render")
    assert main(["report", "--input", str(tmp_path / "report.json"), "--out", str(rerendered)]) == 0
    assert (rerendered / "report.json").read_bytes() == (tmp_path / "report.json").read_bytes()
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert main(arguments(tmp_path)) == 2
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert main([*arguments(tmp_path), "--overwrite", "--sensitive-details"]) == 0
    assert (
        json.loads((tmp_path / "report.json").read_text())["evaluation_summary"]["pooled_metrics"]
        is not None
    )


def test_evaluation_module_console_parity(tmp_path):
    module = process(arguments(tmp_path / "module"), tmp_path)
    console = process(arguments(tmp_path / "console"), tmp_path, "console")
    assert module.returncode == console.returncode == 0
    assert (module.stdout, module.stderr) == (console.stdout, console.stderr)
    assert (tmp_path / "module/evaluation.private.json").read_bytes() == (
        tmp_path / "console/evaluation.private.json"
    ).read_bytes()


def test_cli_expected_fit_failure_exit_four(tmp_path, monkeypatch, capsys):
    def fail(*args, **kwargs):
        raise ValueError("PRIVATE sensitive error")

    monkeypatch.setattr(Pipeline, "fit", fail)
    assert main(arguments(tmp_path)) == 4
    document = json.loads((tmp_path / "evaluation.private.json").read_text())
    assert document["execution_status"] == "incomplete" and document["pooled_metrics"] is None
    assert all(f["status"] == "failed" for f in document["folds"])
    assert "PRIVATE" not in capsys.readouterr().err
    assert (tmp_path / "report.html").exists()


def test_cli_design_refusal_before_fitting(tmp_path, monkeypatch):
    def prohibited(*args, **kwargs):
        pytest.fail("Design refusal reached fit")

    monkeypatch.setattr(Pipeline, "fit", prohibited)
    args = arguments(tmp_path / "out")
    args[args.index("--splits") + 1] = str(FIXTURES / "splits_participant_overlap.json")
    assert main(args) == 3
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("slot", ["--features", "--config"])
def test_at_s10_16_no_model_deserialization(tmp_path, monkeypatch, slot):
    import joblib

    def prohibited(*args, **kwargs):
        pytest.fail("Executable model deserialization attempted")

    monkeypatch.setattr(pickle, "load", prohibited)
    monkeypatch.setattr(pickle, "loads", prohibited)
    monkeypatch.setattr(joblib, "load", prohibited)
    source = tmp_path / "model.pkl"
    source.write_bytes(pickle.dumps({"estimator": "not executable input"}))
    args = arguments(tmp_path / "out")
    args[args.index(slot) + 1] = str(source)
    assert main(args) == 2
    assert not (tmp_path / "out").exists()


def test_unexpected_fit_defect_exits_one_without_fake_report(tmp_path, monkeypatch, capsys):
    def broken(*args, **kwargs):
        raise RuntimeError("PRIVATE defect")

    monkeypatch.setattr(Pipeline, "fit", broken)
    assert main(["--debug", *arguments(tmp_path / "out")]) == 1
    assert not (tmp_path / "out").exists()
    assert "PRIVATE" not in capsys.readouterr().err


def test_private_conflict_does_not_create_partial_public_output(tmp_path):
    existing = tmp_path / "evaluation.private.json"
    existing.write_text("preserved")
    assert main(arguments(tmp_path)) == 2
    assert [path.name for path in tmp_path.iterdir()] == [existing.name]
    assert existing.read_text() == "preserved"


def test_at_s10_09_real_single_class_fold():
    from neurocvguard import load_cohort

    cohort, plan, config = evaluation_inputs()
    metadata = cohort.metadata
    metadata.loc[metadata.observation_id.isin(plan.folds[0].test_ids), "diagnosis"] = "AD"
    metadata.loc[metadata.observation_id.isin(plan.folds[1].test_ids), "diagnosis"] = "CN"
    changed = load_cohort(metadata, config=config, features=cohort.features)
    result = evaluate_baseline(changed, replace(plan, cohort_digest=None), config=config)
    assert result.execution_status == "completed"
    assert result.folds[0].metrics.accuracy.value is not None
    assert result.folds[0].metrics.roc_auc.reason == "missing_true_class"
    assert result.folds[0].metrics.balanced_accuracy.reason == "missing_true_class"
    assert result.pooled_metrics.balanced_accuracy.value is not None
