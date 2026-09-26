"""S11.C adversarial fitting boundaries, untouched test data and run provenance."""

import warnings
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from test_inner_plans import tuning_inputs

from neurocvguard import evaluate_baseline, load_cohort
from neurocvguard._evaluation_inputs import preflight
from neurocvguard._tuning import TUNING_POLICY
from neurocvguard.models import EvaluationResult
from neurocvguard.serialization import json_digest


@pytest.fixture(scope="module")
def run():
    cohort, plan, config = tuning_inputs()
    original_fit = Pipeline.fit
    original_imputer = SimpleImputer.fit
    original_scaler = StandardScaler.fit
    observed, imputers, scalers = [], [], []
    metadata, features, memberships = cohort.metadata, cohort.features, plan.to_operational_dict()

    def spy(self, X, y, **kwargs):
        assert not hasattr(self.named_steps["classifier"], "coef_")
        observed.append((self, X.copy(), y.copy(), kwargs["classifier__sample_weight"].copy()))
        return original_fit(self, X, y, **kwargs)

    def imputer(self, X, y=None):
        imputers.append((self, X.copy()))
        return original_imputer(self, X, y)

    def scaler(self, X, y=None, sample_weight=None):
        scalers.append((self, X.copy()))
        return original_scaler(self, X, y, sample_weight)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Pipeline, "fit", spy)
        patch.setattr(SimpleImputer, "fit", imputer)
        patch.setattr(StandardScaler, "fit", scaler)
        result = evaluate_baseline(cohort, plan, config=config)
    pd.testing.assert_frame_equal(cohort.metadata, metadata)
    pd.testing.assert_frame_equal(cohort.features, features)
    assert plan.to_operational_dict() == memberships
    assert result.execution_status == "completed"
    return cohort, plan, config, result, observed, imputers, scalers


def test_at_s11_01_actual_imputer_scaler_and_pipeline_inputs(run):
    cohort, _, _, result, observed, imputers, scalers = run
    assert len(observed) == len(imputers) == len(scalers) == len(result.fit_events) == 30
    for event, (pipe, frame, targets, weights), (imputer, seen), (scaler, values) in zip(
        result.fit_events, observed, imputers, scalers, strict=True
    ):
        outer = next(f for f in result.actual_plan.folds if f.fold_id == event.fold_id)
        allowed = outer.train_ids
        if event.inner_fold_id is not None:
            inner = next(f for f in outer.inner_folds if f.inner_fold_id == event.inner_fold_id)
            allowed = inner.train_ids
            assert set(frame.index).isdisjoint(inner.validation_ids)
        assert tuple(frame.index) == tuple(seen.index) == event.fit_ids == allowed
        assert set(frame.index).isdisjoint(outer.test_ids)
        assert tuple(targets.index) == allowed
        assert imputer is pipe.named_steps["imputer"]
        assert scaler is pipe.named_steps["scaler"]
        expected = frame.fillna(frame.median()).fillna(0).to_numpy()
        np.testing.assert_allclose(values, expected)
        np.testing.assert_allclose(scaler.mean_, expected.mean(axis=0))
        people = cohort.metadata.set_index("observation_id").loc[list(allowed), "subject_id"]
        for person in set(people):
            assert weights[people == person].sum() == pytest.approx(1)


def test_at_s11_08_refit_fresh_on_entire_outer_train_at_selected_C(run):
    _, _, config, result, observed, _, _ = run
    assert len({id(row[0]) for row in observed}) == len(observed)
    for step in ("imputer", "scaler", "classifier"):
        assert len({id(row[0].named_steps[step]) for row in observed}) == len(observed)
    for fold in result.folds:
        indexed = [
            (i, event) for i, event in enumerate(result.fit_events) if event.fold_id == fold.fold_id
        ]
        outer_events = [(i, event) for i, event in indexed if event.scope == "outer_train"]
        assert len(outer_events) == 1
        index, event = outer_events[0]
        assert index == max(i for i, _ in indexed)
        assert event.C == fold.selected_C == observed[index][0].named_steps["classifier"].C
        assert [s.C for s in fold.candidate_scores] == sorted(config.evaluation.C_grid)
        maximum = max(s.balanced_accuracy for s in fold.candidate_scores)
        assert fold.selected_C == min(
            s.C for s in fold.candidate_scores if maximum - s.balanced_accuracy <= 1e-12
        )


def test_at_s11_09_derived_private_plan_and_public_projection(run):
    _, plan, _, result, _, _, _ = run
    assert all(not fold.inner_folds for fold in plan.folds)
    assert all(fold.inner_folds for fold in result.actual_plan.folds)
    assert result.plan_digest == json_digest(result.actual_plan.to_operational_dict())
    assert EvaluationResult.from_dict(result.to_operational_dict()) == result
    assert TUNING_POLICY in result.limitations
    public = result.to_dict()
    assert "actual_plan" not in public and "fit_events" not in public
    text = str(public)
    assert "candidate_scores" not in text
    assert all(key not in text for fold in plan.folds for key in fold.train_ids)


@pytest.mark.parametrize("change", ["labels", "features"])
def test_at_s11_02_outer_test_changes_cannot_choose_C(change, run):
    cohort, plan, config, baseline, _, _, _ = run
    outer = plan.folds[0]
    metadata, features = cohort.metadata, cohort.features
    if change == "labels":
        mask = metadata.observation_id.isin(outer.test_ids)
        metadata.loc[mask, "diagnosis"] = metadata.loc[mask, "diagnosis"].map(
            {"AD": "CN", "CN": "AD"}
        )
    else:
        features.loc[features.observation_id.isin(outer.test_ids), ["feature_1", "feature_2"]] = 1e6
    changed = load_cohort(metadata, config=config, features=features)
    result = evaluate_baseline(changed, replace(plan, cohort_digest=None), config=config)
    before = next(f for f in baseline.folds if f.fold_id == outer.fold_id)
    after = next(f for f in result.folds if f.fold_id == outer.fold_id)
    assert before.selected_C == after.selected_C
    assert before.candidate_scores == after.candidate_scores
    assert baseline.actual_plan.folds[0].inner_folds == result.actual_plan.folds[0].inner_folds


def test_at_s11_07_inner_failure_retained_and_no_outer_fallback(monkeypatch):
    cohort, plan, config = tuning_inputs()
    # Fail one inner candidate in the first outer fold only; retain all outer folds.
    prepared = preflight(cohort, plan, config)
    failed_outer = prepared.plan.folds[0]
    doomed = set(failed_outer.inner_folds[0].train_ids)
    original = Pipeline.fit

    def fail(self, X, y, **kwargs):
        if set(X.index) == doomed and self.named_steps["classifier"].C == 0.1:
            warnings.warn("synthetic inner failure", ConvergenceWarning, stacklevel=2)
        return original(self, X, y, **kwargs)

    monkeypatch.setattr(Pipeline, "fit", fail)
    result = evaluate_baseline(cohort, prepared.plan, config=config)
    assert result.execution_status == "incomplete" and result.pooled_metrics is None
    failed = [f for f in result.folds if f.status == "failed"]
    assert len(failed) == 1 and len(result.folds) == 3
    assert failed[0].selected_C is None and failed[0].reason == "inner_tuning_failed"
    assert failed[0].candidate_scores[0].balanced_accuracy is None
    assert len(failed[0].candidate_scores) == 3
    assert all(
        e.scope == "inner_train" for e in result.fit_events if e.fold_id == failed_outer.fold_id
    )
    assert EvaluationResult.from_dict(result.to_operational_dict()) == result


def test_tune_false_performs_no_inner_fits_or_selection(monkeypatch):
    cohort, plan, config = tuning_inputs()
    nested = preflight(cohort, plan, config).plan
    monkeypatch.setattr(
        "neurocvguard.evaluation.tune_C", lambda *a: pytest.fail("tune=false selected")
    )
    config = replace(config, evaluation=replace(config.evaluation, tune=False))
    result = evaluate_baseline(cohort, nested, config=config)
    assert len(result.fit_events) == 3
    assert all(e.inner_fold_id is None for e in result.fit_events)
    assert all(not f.candidate_scores and f.selected_C == config.evaluation.C for f in result.folds)


def test_nested_numerics_invariant_to_row_fold_and_grid_order(run):
    cohort, plan, config, baseline, _, _, _ = run
    reordered = load_cohort(
        cohort.metadata.iloc[::-1], config=config, features=cohort.features.iloc[::-1]
    )
    config = replace(
        config,
        evaluation=replace(config.evaluation, C_grid=tuple(reversed(config.evaluation.C_grid))),
    )
    result = evaluate_baseline(
        reordered, replace(plan, folds=tuple(reversed(plan.folds))), config=config
    )
    assert result.folds == baseline.folds
    assert result.fit_events == baseline.fit_events
    assert result.actual_plan == baseline.actual_plan
    assert result.pooled_metrics == baseline.pooled_metrics
