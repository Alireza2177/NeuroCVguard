"""S10.C complete/incomplete runs, contract migration and deterministic boundaries."""

import json
import warnings
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from sklearn.exceptions import ConvergenceWarning
from sklearn.pipeline import Pipeline
from test_cli_commands import FIXTURES
from test_evaluation_preflight import evaluation_inputs

from neurocvguard import evaluate_baseline, load_cohort
from neurocvguard.errors import EvaluationError, UnsupportedDesignError
from neurocvguard.models import EvaluationResult
from neurocvguard.serialization import json_digest


def test_completed_run_private_roundtrip_and_input_preservation():
    cohort, plan, config = evaluation_inputs()
    metadata, features, assignments = cohort.metadata, cohort.features, plan.to_operational_dict()
    result = evaluate_baseline(cohort, plan, config=config)
    assert result.execution_status == "completed" and result.metric_unit == "participant"
    assert result.pooled_metrics.n_participants == result.n_participants == 18
    assert len(result.fit_events) == len(plan.folds)
    assert all(event.status == "completed" for event in result.fit_events)
    assert result.provenance["upstream_preprocessing_verified"] is False
    assert result.actual_plan.to_operational_dict() == assignments
    assert result.plan_digest == json_digest(assignments)
    assert EvaluationResult.from_dict(result.to_operational_dict()) == result
    assert any(
        row.rule_id == "NCG-PROV-001" and row.status == "not_assessable"
        for row in result.preflight_checks
    )
    pd.testing.assert_frame_equal(cohort.metadata, metadata)
    pd.testing.assert_frame_equal(cohort.features, features)
    assert plan.to_operational_dict() == assignments


def test_row_and_fold_order_do_not_change_numerical_results():
    cohort, plan, config = evaluation_inputs()
    first = evaluate_baseline(cohort, plan, config=config)
    shuffled = load_cohort(
        cohort.metadata.iloc[::-1], config=config, features=cohort.features.iloc[::-1]
    )
    second = evaluate_baseline(shuffled, replace(plan, folds=plan.folds[::-1]), config=config)
    assert first.pooled_metrics == second.pooled_metrics
    assert first.folds == second.folds and first.fit_events == second.fit_events
    assert (
        first.feature_digest == second.feature_digest
        and first.cohort_digest == second.cohort_digest
    )


@pytest.mark.parametrize("failure", ["value", "convergence"])
def test_at_s10_13_failed_fold_never_easy_fold_average(monkeypatch, failure):
    cohort, plan, config = evaluation_inputs()
    original = Pipeline.fit
    seen = []

    def spy(self, X, y, **kwargs):
        seen.append(tuple(X.index))
        if len(seen) == 2:
            if failure == "value":
                raise ValueError("PRIVATE error content must not enter results")
            warnings.warn("PRIVATE warning content", ConvergenceWarning, stacklevel=2)
        return original(self, X, y, **kwargs)

    monkeypatch.setattr(Pipeline, "fit", spy)
    result = evaluate_baseline(cohort, plan, config=config)
    assert len(result.folds) == len(seen) == 3
    assert result.execution_status == "incomplete" and result.pooled_metrics is None
    assert [fold.status for fold in result.folds] == ["completed", "failed", "completed"]
    assert result.folds[1].metrics is None and result.folds[1].reason
    assert [event.status for event in result.fit_events] == ["completed", "failed", "completed"]
    assert "PRIVATE" not in json.dumps(result.to_operational_dict())
    assert result.to_dict()["evaluation_summary"]["pooled_metrics"] is None


def test_prediction_failure_retains_successful_fit_event(monkeypatch):
    cohort, plan, config = evaluation_inputs()
    monkeypatch.setattr(Pipeline, "predict_proba", lambda self, X: np.zeros((len(X), 2)))
    result = evaluate_baseline(cohort, plan, config=config)
    assert result.execution_status == "incomplete" and result.pooled_metrics is None
    assert all(event.status == "completed" for event in result.fit_events)
    assert all(fold.reason == "prediction_failed_or_invalid" for fold in result.folds)


def test_internal_boundary_violation_blocks_complete_run(monkeypatch):
    import neurocvguard._evaluation_fits as fits

    cohort, plan, config = evaluation_inputs()
    monkeypatch.setattr(fits, "_training_frame", lambda inputs, fold: inputs.features)
    result = evaluate_baseline(cohort, plan, config=config)
    assert not result.fit_events and result.execution_status == "incomplete"
    assert result.pooled_metrics is None
    assert any(check.rule_id == "NCG-PROV-004" for check in result.preflight_checks)


def test_at_s10_02_transformer_fit_spies(monkeypatch):
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler

    cohort, plan, config = evaluation_inputs()
    impute, scale = SimpleImputer.fit, StandardScaler.fit
    imputer_frames, scaler_arrays = [], []

    def imputer_spy(self, X, y=None, **kwargs):
        imputer_frames.append(X.copy())
        return impute(self, X, y, **kwargs)

    def scaler_spy(self, X, y=None, **kwargs):
        scaler_arrays.append(X.copy())
        return scale(self, X, y, **kwargs)

    monkeypatch.setattr(SimpleImputer, "fit", imputer_spy)
    monkeypatch.setattr(StandardScaler, "fit", scaler_spy)
    evaluate_baseline(cohort, plan, config=config)
    for fold, frame, values in zip(
        sorted(plan.folds, key=lambda f: (f.repeat_id, f.fold_id)),
        imputer_frames,
        scaler_arrays,
        strict=True,
    ):
        assert tuple(frame.index) == fold.train_ids
        np.testing.assert_allclose(values, frame.fillna(frame.median()).fillna(0))


def test_schema_extension_legacy_records_remain_readable():
    original = json.loads((FIXTURES / "evaluation_schema_example.json").read_text())
    result = EvaluationResult.from_dict(original)
    assert result.actual_plan is None and result.plan_digest is None
    assert result.to_operational_dict() == original


def test_evaluation_documentation_example():
    from pathlib import Path

    source = (Path(__file__).parents[1] / "docs/evaluation.md").read_text(encoding="utf-8")
    code = source.split("```python\n", 1)[1].split("```", 1)[0]
    exec(compile(code, "docs/evaluation.md", "exec"), {})


def test_s10_rule_catalog_metadata():
    from neurocvguard.rules import EVALUATION_RULES

    catalog = json.loads((FIXTURES.parent / "qa/rule_catalog.json").read_text())
    rows = {item["id"]: item for item in catalog if item["stage"] == "S10"}
    assert set(rows) == {rule.id for rule in EVALUATION_RULES}
    for rule in EVALUATION_RULES:
        assert rule.meaning == rows[rule.id]["meaning"]
        assert rule.trigger_severity == rows[rule.id]["trigger_severity"]
        assert rule.evidence_kind == rows[rule.id]["evidence_kind"]


@pytest.mark.parametrize("corruption", ["digest", "pair", "fold", "fit"])
def test_schema_extension_detects_inconsistent_plan(corruption):
    cohort, plan, config = evaluation_inputs()
    document = evaluate_baseline(cohort, plan, config=config).to_operational_dict()
    if corruption == "digest":
        document["plan_digest"] = "0" * 64
    elif corruption == "pair":
        document.pop("actual_plan")
    elif corruption == "fold":
        document["folds"][0]["fold_id"] = "unknown"
    else:
        document["fit_events"][0]["fit_ids"] = list(plan.folds[0].test_ids)
    with pytest.raises(EvaluationError):
        EvaluationResult.from_dict(document)


def test_training_class_absence_refuses_all_fitting(monkeypatch):
    cohort, plan, config = evaluation_inputs()
    metadata = cohort.metadata
    metadata["diagnosis"] = "CN"
    subject = metadata.loc[metadata.observation_id.isin(plan.folds[0].test_ids), "subject_id"].iloc[
        0
    ]
    metadata.loc[metadata.subject_id == subject, "diagnosis"] = "AD"
    changed = load_cohort(metadata, config=config, features=cohort.features)

    def prohibited(*args, **kwargs):
        pytest.fail("Infeasible class support reached fit")

    monkeypatch.setattr(Pipeline, "fit", prohibited)
    with pytest.raises(UnsupportedDesignError):
        evaluate_baseline(changed, replace(plan, cohort_digest=None), config=config)
