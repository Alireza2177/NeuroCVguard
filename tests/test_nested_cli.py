"""Nested CLI produces complete private provenance and failure exit codes."""

import json

import pytest
from sklearn.pipeline import Pipeline
from test_evaluation_cli import arguments
from test_inner_plans import tuning_inputs

from neurocvguard.cli import main
from neurocvguard.models import AuditReport, EvaluationResult


@pytest.mark.parametrize("max_iter,exit_code", [(2000, 0), (1, 4)])
def test_nested_cli_records_and_failure_policy(tmp_path, capsys, max_iter, exit_code):
    _, _, config = tuning_inputs()
    document = config.to_dict()
    document["evaluation"]["max_iter"] = max_iter
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(document), encoding="utf-8")
    output = tmp_path / "output"
    args = arguments(output)
    args[args.index("--config") + 1] = str(config_path)
    assert main(args) == exit_code
    captured = capsys.readouterr()
    assert "obs-" not in captured.out + captured.err
    result = EvaluationResult.from_json((output / "evaluation.private.json").read_text())
    public = json.loads((output / "report.json").read_text())
    assert public == result.to_dict() == AuditReport.from_dict(public).to_dict()
    assert all(f.inner_folds for f in result.actual_plan.folds)
    assert all(len(f.candidate_scores) == 3 for f in result.folds)
    if exit_code == 4:
        assert result.pooled_metrics is None
        assert all(f.selected_C is None and f.reason == "inner_tuning_failed" for f in result.folds)
        assert all(e.scope == "inner_train" for e in result.fit_events)
    else:
        assert len(result.fit_events) == 30 and result.pooled_metrics is not None
    combined = (output / "report.html").read_text() + (output / "report.json").read_text()
    assert all(
        marker not in combined
        for marker in ("obs-001-1", "candidate_scores", "fit_ids", "actual_plan")
    )


def test_at_s11_07_cli_infeasible_inner_request_exits_three(tmp_path, monkeypatch):
    _, _, config = tuning_inputs()
    document = config.to_dict()
    document["evaluation"]["inner_splits"] = 20
    path = tmp_path / "config.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    args = arguments(tmp_path / "out")
    args[args.index("--config") + 1] = str(path)
    monkeypatch.setattr(Pipeline, "fit", lambda *a, **k: pytest.fail("infeasible fit"))
    assert main(args) == 3
    assert not (tmp_path / "out").exists()
