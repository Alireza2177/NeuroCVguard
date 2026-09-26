"""S12.B explicit overlap exception never changes the audit's validity judgment."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline
from test_cli_commands import FIXTURES
from test_evaluation_preflight import evaluation_inputs

from neurocvguard import audit_splits, evaluate_baseline, load_cohort, load_split_plan
from neurocvguard._evaluation_inputs import preflight
from neurocvguard.config import Objective, SplitConfig, SplitScheme
from neurocvguard.errors import NeuroCVguardError, UnsupportedDesignError
from neurocvguard.models import EvaluationResult, InnerFold, SplitFold


def diagnostic_inputs():
    cohort, _, config = evaluation_inputs()
    config = replace(
        config, evaluation=replace(config.evaluation, diagnostic_allow_subject_overlap=True)
    )
    plan = load_split_plan(
        FIXTURES / "splits_participant_overlap.json", cohort=cohort, config=config
    )
    return cohort, plan, config


def test_at_s12_04_default_off_refuses_before_fit(monkeypatch):
    cohort, plan, config = diagnostic_inputs()
    config = replace(
        config, evaluation=replace(config.evaluation, diagnostic_allow_subject_overlap=False)
    )
    monkeypatch.setattr(Pipeline, "fit", lambda *a, **k: pytest.fail("default allowed overlap"))
    with pytest.raises(UnsupportedDesignError):
        evaluate_baseline(cohort, plan, config=config)


@pytest.mark.parametrize("tune", [False, True])
def test_at_s12_05_narrow_permit_preserves_audit_and_row_fit_boundaries(monkeypatch, tune):
    cohort, plan, config = diagnostic_inputs()
    config = replace(config, evaluation=replace(config.evaluation, tune=tune))
    original, seen = Pipeline.fit, []

    def spy(self, X, y, **kwargs):
        seen.append((self, tuple(X.index)))
        return original(self, X, y, **kwargs)

    monkeypatch.setattr(Pipeline, "fit", spy)
    result = evaluate_baseline(cohort, plan, config=config)
    assert result.execution_status == "completed" and result.diagnostic_only
    assert result.pooled_metrics.n_participants == result.n_participants == 18
    assert sum(f.test_participants for f in result.folds) == 36
    summary = next(c for c in result.preflight_checks if c.scope.get("field") == "split_summary")
    assert summary.evidence["valid_for_objective"] is False
    assert summary.evidence["evaluation_permitted"] is False
    assert any(c.rule_id == "NCG-EVAL-003" and c.status == "fail" for c in result.preflight_checks)
    assert any(c.rule_id == "NCG-SPLIT-002" and c.status == "fail" for c in result.preflight_checks)
    assert len(seen) == len(result.fit_events)
    for event, (_, actual) in zip(result.fit_events, seen, strict=True):
        outer = next(f for f in result.actual_plan.folds if f.fold_id == event.fold_id)
        assert actual == event.fit_ids and set(actual).isdisjoint(outer.test_ids)
        if event.inner_fold_id:
            inner = next(f for f in outer.inner_folds if f.inner_fold_id == event.inner_fold_id)
            assert actual == inner.train_ids and set(actual).isdisjoint(inner.validation_ids)
    assert EvaluationResult.from_dict(result.to_operational_dict()) == result
    assert result.to_dict()["evaluation_summary"]["diagnostic_only"] is True
    assert "Do not report as evidence for unseen-participant" in str(result.to_dict())
    assert any("does not remove" in item for item in result.limitations)
    assert any(
        c.evidence.get("valid_for_objective") is False
        for c in audit_splits(cohort, plan, config=config).checks
    )


@pytest.mark.parametrize(
    "problem", ["observation_overlap", "unknown", "coverage", "repeat", "holdout", "training_class"]
)
def test_at_s12_06_structural_and_class_constraints_never_waived(monkeypatch, problem):
    cohort, plan, config = diagnostic_inputs()
    first = plan.folds[0]
    if problem == "observation_overlap":
        first = replace(first, train_ids=first.train_ids + first.test_ids[:1])
        plan = replace(plan, folds=(first, *plan.folds[1:]))
    elif problem == "unknown":
        first = replace(first, train_ids=first.train_ids + ("unknown",))
        plan = replace(plan, folds=(first, *plan.folds[1:]))
    elif problem == "coverage":
        plan = replace(plan, folds=(first, replace(first, fold_id="other")))
    elif problem == "repeat":
        plan = replace(plan, folds=(first, replace(plan.folds[1], repeat_id="other")))
    elif problem == "holdout":
        plan = replace(plan, folds=(first,))
    else:
        metadata = cohort.metadata.set_index("observation_id")
        a = tuple(metadata.index[metadata.diagnosis == "AD"])
        b = tuple(metadata.index[metadata.diagnosis == "CN"])
        plan = replace(plan, folds=(SplitFold("0", "a", a, b), SplitFold("0", "b", b, a)))
    monkeypatch.setattr(Pipeline, "fit", lambda *a, **k: pytest.fail("invalid fit"))
    with pytest.raises(NeuroCVguardError):
        evaluate_baseline(cohort, plan, config=config)


@pytest.mark.parametrize("objective", [Objective.UNSEEN_SITE, Objective.UNSEEN_PHASE])
def test_at_s12_07_domain_objective_never_waived(monkeypatch, objective):
    cohort, plan, config = diagnostic_inputs()
    config = replace(
        config,
        study=replace(config.study, objective=objective),
        split=SplitConfig(SplitScheme.IMPORTED, None, config.split.seed),
    )
    plan = replace(plan, objective=objective)
    monkeypatch.setattr(Pipeline, "fit", lambda *a, **k: pytest.fail("domain waiver"))
    with pytest.raises(UnsupportedDesignError, match="cannot waive family, site or phase"):
        evaluate_baseline(cohort, plan, config=config)


@pytest.mark.parametrize("complete", [True, False])
def test_at_s12_07_declared_family_fields_never_waived(monkeypatch, complete):
    cohort, plan, config = diagnostic_inputs()
    metadata = cohort.metadata
    metadata["family"] = "shared-family" if complete else None
    config = replace(config, columns=replace(config.columns, independence=("family",)))
    cohort = load_cohort(metadata, config=config, features=cohort.features)
    monkeypatch.setattr(Pipeline, "fit", lambda *a, **k: pytest.fail("family waiver"))
    with pytest.raises(UnsupportedDesignError, match="no extra independence columns"):
        evaluate_baseline(cohort, replace(plan, cohort_digest=None), config=config)


def test_inner_participant_overlap_never_waived(monkeypatch):
    cohort, plan, config = diagnostic_inputs()
    # Outer-disjoint ordinary plan with an intentionally observation-random inner partition.
    _, ordinary, _ = evaluation_inputs()
    outer = ordinary.folds[0]
    left = tuple(i for i in outer.train_ids if i.endswith("-1"))
    right = tuple(i for i in outer.train_ids if i.endswith("-2"))
    outer = replace(outer, inner_folds=(InnerFold("a", left, right), InnerFold("b", right, left)))
    plan = replace(ordinary, folds=(outer, *ordinary.folds[1:]))
    monkeypatch.setattr(Pipeline, "fit", lambda *a, **k: pytest.fail("inner waiver"))
    with pytest.raises(UnsupportedDesignError):
        evaluate_baseline(cohort, plan, config=config)


def test_at_s12_05_pool_all_observations_not_fold_means(monkeypatch):
    _, template, config = diagnostic_inputs()
    metadata = pd.DataFrame(
        [
            {
                "observation_id": f"o-{p}-{v}",
                "subject_id": f"p-{p}",
                "diagnosis": "AD" if p < 2 else "CN",
            }
            for p in range(4)
            for v in range(4)
        ]
    )
    features = metadata[["observation_id"]].assign(feature_1=np.arange(16), feature_2=1.0)
    cohort = load_cohort(metadata, config=config, features=features)
    small = tuple(i for i in cohort.observation_order if i.endswith("-3"))
    large = tuple(i for i in cohort.observation_order if i not in small)
    plan = replace(
        template,
        cohort_digest=None,
        folds=(SplitFold("0", "a", small, large), SplitFold("0", "b", large, small)),
    )
    truth = metadata.set_index("observation_id").diagnosis

    def probabilities(pipe, frame, classes):
        result = []
        for key in frame.index:
            correct = 0.0 if key.endswith("-3") else 0.9
            result.append([correct if c == truth[key] else 1 - correct for c in classes])
        return np.asarray(result)

    monkeypatch.setattr("neurocvguard._evaluation_fits.ordered_probabilities", probabilities)
    result = evaluate_baseline(cohort, plan, config=config)
    assert [f.metrics.accuracy.value for f in result.folds] == [1.0, 0.0]
    assert result.pooled_metrics.accuracy.value == 1.0
    assert result.pooled_metrics.confusion_matrix == ((2, 0), (0, 2))
    # (.9*3 + 0)/4 = .675 correct, whereas mean of fold means = .45 wrong.
    assert result.pooled_metrics.n_participants == 4


def test_diagnostic_expected_failure_stays_incomplete(monkeypatch):
    cohort, plan, config = diagnostic_inputs()
    monkeypatch.setattr(
        Pipeline, "fit", lambda *a, **k: (_ for _ in ()).throw(ValueError("synthetic"))
    )
    result = evaluate_baseline(cohort, plan, config=config)
    assert result.diagnostic_only and result.execution_status == "incomplete"
    assert result.pooled_metrics is None and all(f.status == "failed" for f in result.folds)


def test_flag_does_not_mislabel_a_participant_disjoint_plan():
    cohort, plan, config = evaluation_inputs()
    config = replace(
        config, evaluation=replace(config.evaluation, diagnostic_allow_subject_overlap=True)
    )
    assert preflight(cohort, plan, config).diagnostic_only is False
