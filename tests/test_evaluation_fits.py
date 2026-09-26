"""S10.B independent spies observe real fit inputs, state and failure boundaries."""

import warnings
from dataclasses import replace

import numpy as np
import pytest
from sklearn.exceptions import ConvergenceWarning
from sklearn.pipeline import Pipeline
from test_evaluation_preflight import evaluation_inputs

from neurocvguard._evaluation_fits import fit_outer, ordered_probabilities
from neurocvguard._evaluation_inputs import fixed_pipeline, preflight
from neurocvguard.models import Cohort


def execute(monkeypatch, before_fit=None):
    cohort, plan, config = evaluation_inputs()
    prepared = preflight(cohort, plan, config)
    original = Pipeline.fit
    observed = []

    def spy(self, X, y, **kwargs):
        observed.append((self, X.copy(), y.copy(), kwargs["classifier__sample_weight"].copy()))
        if before_fit:
            before_fit(len(observed), X)
        return original(self, X, y, **kwargs)

    monkeypatch.setattr(Pipeline, "fit", spy)
    template = fixed_pipeline(config)
    outcomes = [fit_outer(prepared, fold, config, template) for fold in prepared.plan.folds]
    return outcomes, observed, prepared, template


def test_at_s10_01_training_only_scaler(monkeypatch):
    outcomes, observed, prepared, _ = execute(monkeypatch)
    for outcome, (pipeline, training, _, _) in zip(outcomes, observed, strict=True):
        assert outcome.reason is None
        reference = training.fillna(training.median()).fillna(0).mean().to_numpy()
        np.testing.assert_allclose(pipeline.named_steps["scaler"].mean_, reference)
        assert not np.allclose(reference, prepared.features.mean().to_numpy())


def test_at_s10_02_actual_fit_ids(monkeypatch):
    outcomes, observed, prepared, _ = execute(monkeypatch)
    for outcome, (_, training, targets, weights) in zip(outcomes, observed, strict=True):
        assert tuple(training.index) == outcome.fold.train_ids == outcome.event.fit_ids
        assert set(training.index).isdisjoint(outcome.fold.test_ids)
        assert list(targets.index) == list(training.index)
        people = prepared.participants.loc[training.index]
        for person in set(people):
            assert weights[people == person].sum() == pytest.approx(1)


def test_at_s10_03_fresh_objects(monkeypatch):
    _, observed, _, template = execute(monkeypatch)
    assert len({id(row[0]) for row in observed}) == len(observed)
    for step in template.named_steps:
        assert len({id(row[0].named_steps[step]) for row in observed}) == len(observed)
    assert not hasattr(template.named_steps["scaler"], "mean_")


def test_at_s10_07_all_missing_training_feature(monkeypatch):
    cohort, plan, config = evaluation_inputs()
    features = cohort.features
    first = plan.folds[0]
    features.loc[features.observation_id.isin(first.train_ids), "feature_1"] = np.nan
    features.loc[features.observation_id.isin(first.test_ids), "feature_1"] = 12345
    changed = Cohort(cohort.metadata, features, cohort.columns, cohort.observation_order)
    prepared = preflight(changed, plan, config)
    captured = []
    original = Pipeline.fit

    def spy(self, X, y, **kwargs):
        result = original(self, X, y, **kwargs)
        captured.append(self)
        return result

    monkeypatch.setattr(Pipeline, "fit", spy)
    result = fit_outer(prepared, first, config, fixed_pipeline(config))
    assert result.reason is None
    assert any(check.rule_id == "NCG-EVAL-004" for check in result.checks)
    assert captured[0].named_steps["imputer"].statistics_[0] == 0
    assert captured[0].named_steps["scaler"].mean_[0] == 0
    assert captured[0].named_steps["scaler"].n_features_in_ == 2


def test_at_s10_06_explicit_class_mapping():
    class Reversed:
        classes_ = np.array(["CN", "AD"])

        def predict_proba(self, frame):
            return np.array([[0.8, 0.2]] * len(frame))

    cohort, plan, config = evaluation_inputs()
    prepared = preflight(cohort, plan, config)
    mapped = ordered_probabilities(Reversed(), prepared.features.iloc[:1], prepared.classes)
    np.testing.assert_allclose(mapped, [[0.2, 0.8]])


def test_at_s10_12_convergence_failure(monkeypatch):
    def warning(number, frame):
        warnings.warn("synthetic nonconvergence", ConvergenceWarning, stacklevel=2)

    outcomes, observed, _, _ = execute(monkeypatch, warning)
    assert len(outcomes) == len(observed)
    assert all(
        outcome.event.status == "failed" and outcome.reason == "fit_did_not_converge"
        for outcome in outcomes
    )
    assert all(outcome.probabilities is None for outcome in outcomes)


def test_internal_boundary_defect_has_no_fabricated_event(monkeypatch):
    import neurocvguard._evaluation_fits as fits

    cohort, plan, config = evaluation_inputs()
    prepared = preflight(cohort, plan, config)
    monkeypatch.setattr(fits, "_training_frame", lambda inputs, fold: inputs.features)

    def prohibited(*args, **kwargs):
        pytest.fail("Boundary violation reached fit")

    monkeypatch.setattr(Pipeline, "fit", prohibited)
    outcome = fit_outer(prepared, plan.folds[0], config, fixed_pipeline(config))
    assert outcome.event is None and outcome.reason == "internal_fit_boundary_violation"
    assert outcome.checks[0].rule_id == "NCG-PROV-004"


def test_unexpected_errors_propagate(monkeypatch):
    def broken(number, frame):
        raise RuntimeError("unexpected implementation defect")

    with pytest.raises(RuntimeError, match="implementation defect"):
        execute(monkeypatch, broken)


def test_real_iteration_limit_fails():
    cohort, plan, config = evaluation_inputs()
    config = replace(config, evaluation=replace(config.evaluation, max_iter=1))
    prepared = preflight(cohort, plan, config)
    result = fit_outer(prepared, plan.folds[0], config, fixed_pipeline(config))
    assert result.reason == "fit_did_not_converge"
