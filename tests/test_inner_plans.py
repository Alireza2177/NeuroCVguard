"""S11.A generated and supplied inner assignments are independently audited."""

from dataclasses import replace

import pytest
from sklearn.pipeline import Pipeline
from test_evaluation_preflight import evaluation_inputs

from neurocvguard import load_cohort, make_splits
from neurocvguard._evaluation_inputs import preflight
from neurocvguard.config import Objective, SplitConfig, SplitScheme
from neurocvguard.errors import UnsupportedDesignError
from neurocvguard.identity import build_components
from neurocvguard.models import SplitPlan


def tuning_inputs():
    cohort, plan, config = evaluation_inputs()
    return cohort, plan, replace(config, evaluation=replace(config.evaluation, tune=True))


def test_at_s11_09_generated_plan_is_detached_and_roundtrips():
    cohort, plan, config = tuning_inputs()
    before = plan.to_operational_dict()
    derived = preflight(cohort, plan, config).plan
    assert plan.to_operational_dict() == before
    assert all(not f.inner_folds for f in plan.folds)
    assert derived.plan_id != plan.plan_id
    assert SplitPlan.from_dict(derived.to_operational_dict()) == derived
    assert preflight(cohort, plan, config).plan == derived
    for outer in derived.folds:
        validation = []
        for inner in outer.inner_folds:
            assert set(inner.train_ids).isdisjoint(inner.validation_ids)
            assert set(inner.train_ids) | set(inner.validation_ids) == set(outer.train_ids)
            assert set(inner.train_ids + inner.validation_ids).isdisjoint(outer.test_ids)
            validation.extend(inner.validation_ids)
        assert sorted(validation) == sorted(outer.train_ids)


def test_supplied_inner_folds_retained_without_regeneration(monkeypatch):
    cohort, plan, config = tuning_inputs()
    derived = preflight(cohort, plan, config).plan
    monkeypatch.setattr(
        "neurocvguard._inner_plans.make_splits",
        lambda *a, **k: pytest.fail("generated supplied folds"),
    )
    assert preflight(cohort, derived, config).plan == derived


def test_partial_inner_plan_only_generates_absent_memberships():
    cohort, plan, config = tuning_inputs()
    generated = preflight(cohort, plan, config).plan
    supplied = replace(
        generated,
        folds=(generated.folds[0], *[replace(f, inner_folds=()) for f in generated.folds[1:]]),
    )
    before = supplied.to_operational_dict()
    result = preflight(cohort, supplied, config)
    assert result.plan.folds == generated.folds
    assert supplied.to_operational_dict() == before


def test_at_s11_07_missing_inner_training_class_blocks_every_fit(monkeypatch):
    from neurocvguard.models import InnerFold

    cohort, plan, config = tuning_inputs()
    metadata = cohort.metadata.set_index("observation_id")
    outer = plan.folds[0]
    first = tuple(i for i in outer.train_ids if metadata.loc[i, "diagnosis"] == "AD")
    second = tuple(i for i in outer.train_ids if i not in first)
    invalid = replace(
        plan,
        folds=(
            replace(
                outer,
                inner_folds=(InnerFold("one", first, second), InnerFold("two", second, first)),
            ),
            *plan.folds[1:],
        ),
    )
    monkeypatch.setattr(Pipeline, "fit", lambda *a, **k: pytest.fail("missing-class fit"))
    with pytest.raises(UnsupportedDesignError, match="training classes"):
        preflight(cohort, invalid, config)


def test_invalid_supplied_inner_is_rejected_not_replaced(monkeypatch):
    cohort, plan, config = tuning_inputs()
    derived = preflight(cohort, plan, config).plan
    outer = derived.folds[0]
    inner = replace(
        outer.inner_folds[0], train_ids=outer.inner_folds[0].train_ids + outer.test_ids[:1]
    )
    broken = replace(
        derived,
        folds=(replace(outer, inner_folds=(inner, *outer.inner_folds[1:])), *derived.folds[1:]),
    )
    monkeypatch.setattr(Pipeline, "fit", lambda *a, **k: pytest.fail("fit before validation"))
    with pytest.raises(UnsupportedDesignError, match="objective-valid"):
        preflight(cohort, broken, config)


def test_at_s11_07_infeasible_inner_count_fails_without_fitting(monkeypatch):
    cohort, plan, config = tuning_inputs()
    metadata = cohort.metadata
    people = {p: i for i, p in enumerate(sorted(metadata.subject_id.unique()))}
    metadata["family"] = metadata.subject_id.map(lambda p: f"family{people[p] // 2}")
    config = replace(
        config,
        columns=replace(config.columns, independence=("family",)),
        evaluation=replace(config.evaluation, tune=False, inner_splits=10),
    )
    cohort = load_cohort(metadata, config=config, features=cohort.features)
    plan = make_splits(cohort, config=config)
    config = replace(config, evaluation=replace(config.evaluation, tune=True))
    monkeypatch.setattr(Pipeline, "fit", lambda *a, **k: pytest.fail("fit on infeasible plan"))
    with pytest.raises(UnsupportedDesignError, match="independent components"):
        preflight(cohort, plan, config)


@pytest.mark.parametrize(
    "objective,scheme,role",
    [
        (Objective.UNSEEN_PARTICIPANT, SplitScheme.SUBJECT_KFOLD, None),
        (Objective.UNSEEN_SITE, SplitScheme.LEAVE_ONE_SITE_OUT, "site"),
        (Objective.UNSEEN_PHASE, SplitScheme.LEAVE_ONE_PHASE_OUT, "phase"),
    ],
)
def test_inner_protects_transitive_components_and_has_participant_objective(
    objective, scheme, role
):
    cohort, _, config = tuning_inputs()
    metadata = cohort.metadata
    people = sorted(metadata.subject_id.unique())
    # Three-person chains via two declared relationships; all chains stay in a domain.
    index = {p: i for i, p in enumerate(people)}
    metadata["family"] = metadata.subject_id.map(
        lambda p: f"f{index[p] // 3}" if index[p] % 3 < 2 else f"single{index[p]}"
    )
    metadata["duplicate"] = metadata.subject_id.map(
        lambda p: f"d{index[p] // 3}" if index[p] % 3 > 0 else f"single{index[p]}"
    )
    if role:
        metadata[role] = metadata.subject_id.map(lambda p: f"domain{index[p] // 6}")
    config = replace(
        config,
        columns=replace(
            config.columns,
            independence=("family", "duplicate"),
            phase="phase" if role == "phase" else None,
        ),
        study=replace(config.study, objective=objective),
        split=SplitConfig(scheme, 3 if role is None else None, config.split.seed),
        evaluation=replace(config.evaluation, tune=False, inner_splits=2),
    )
    cohort = load_cohort(metadata, config=config, features=cohort.features)
    plan = make_splits(cohort, config=config)
    config = replace(config, evaluation=replace(config.evaluation, tune=True))
    inputs = preflight(cohort, plan, config)
    components = build_components(cohort).participant_to_component
    for outer in inputs.plan.folds:
        for inner in outer.inner_folds:
            left = {components[p] for p in inputs.participants.loc[list(inner.train_ids)]}
            right = {components[p] for p in inputs.participants.loc[list(inner.validation_ids)]}
            assert left.isdisjoint(right)
    assert any(
        c.evidence.get("inner_objective") == "unseen_participant" for c in inputs.audit.checks
    )
