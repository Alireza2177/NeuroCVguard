"""S05 participant-level splitter oracles and no-repair boundaries."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from sklearn.model_selection import StratifiedGroupKFold

from neurocvguard.config import AuditConfig, ColumnMap, SplitConfig
from neurocvguard.errors import PlanningError, UnsupportedDesignError
from neurocvguard.models import CheckStatus, Cohort, SplitPlan
from neurocvguard.splitting import make_splits


def family_cohort(sizes=(2, 2, 2, 2, 2, 2), visits=1):
    rows = []
    for group, size in enumerate(sizes):
        for person in range(size):
            for visit in range(visits if isinstance(visits, int) else visits[group]):
                rows.append(
                    dict(
                        observation_id=f"o-{group:02}-{person:02}-{visit:03}",
                        subject_id=f"p-{group:02}-{person:02}",
                        diagnosis="A" if person % 2 else "B",
                        family=f"g-{group:02}",
                        site=f"s-{group:02}",
                        phase=f"h-{group:02}",
                    )
                )
    data = pd.DataFrame(rows)
    columns = ColumnMap(session=None, phase="phase", independence=("family",))
    return Cohort(data, None, columns, tuple(data.observation_id))


def configuration(cohort, **split):
    return AuditConfig(columns=cohort.columns, split=SplitConfig(**split))


def people_by_fold(cohort, plan):
    people = cohort.metadata.set_index(cohort.columns.observation_id)[
        cohort.columns.subject_id
    ].to_dict()
    return tuple(
        (frozenset(people[o] for o in fold.train_ids), frozenset(people[o] for o in fold.test_ids))
        for fold in plan.folds
    )


def test_at_s05_01_participant_stratification_unit(monkeypatch):
    import neurocvguard.splitting as module

    original = module.StratifiedGroupKFold
    seen = []

    class Spy(original):
        def split(self, X, y, groups):
            seen.append((len(X), tuple(y), tuple(groups)))
            return super().split(X, y, groups)

    monkeypatch.setattr(module, "StratifiedGroupKFold", Spy)
    once = family_cohort()
    uneven = family_cohort(visits=(1, 2, 40, 3, 1, 12))
    first = make_splits(once, config=configuration(once))
    second = make_splits(uneven, config=configuration(uneven))
    assert seen[0] == seen[1] and seen[0][0] == 12
    assert people_by_fold(once, first) == people_by_fold(uneven, second)
    assert first.cohort_digest != second.cohort_digest


@given(st.lists(st.integers(2, 5), min_size=3, max_size=8))
@settings(max_examples=15, deadline=None)
def test_at_s05_02_protected_group_disjointness(sizes):
    cohort = family_cohort(sizes)
    plan = make_splits(cohort, config=configuration(cohort))
    data = cohort.metadata.set_index("observation_id")
    for fold in plan.folds:
        assert set(data.loc[list(fold.train_ids), "family"]).isdisjoint(
            data.loc[list(fold.test_ids), "family"]
        )
        assert set(fold.train_ids) | set(fold.test_ids) == set(cohort.observation_order)
    # Families contain both classes: no component-level guessed target.
    support = next(c.evidence for c in plan.generation_report.checks if c.rule_id == "NCG-PLAN-003")
    assert support["class_component_support"] == (("A", len(sizes)), ("B", len(sizes)))


def test_at_s05_03_too_few_groups(monkeypatch):
    import neurocvguard.splitting as module

    cohort = family_cohort((2, 2, 2))

    def fail(*args, **kwargs):
        pytest.fail("no splitter should run after infeasible group count")

    monkeypatch.setattr(module, "StratifiedGroupKFold", fail)
    with pytest.raises(PlanningError, match="5 folds.*3 independent") as caught:
        make_splits(cohort, config=configuration(cohort, n_splits=5))
    assert caught.value.report.execution_status == "blocked"
    assert any(
        c.rule_id == "NCG-PLAN-001" and c.status == "fail" for c in caught.value.report.checks
    )


def test_at_s05_04_approximate_stratification():
    cohort = family_cohort((2, 3, 7, 2, 5, 2))
    plan = make_splits(cohort, config=configuration(cohort))
    report = plan.generation_report
    assert any("approximate" in text for text in report.limitations)
    data = cohort.metadata.set_index("observation_id")
    for fold in plan.folds:
        checks = [
            c
            for c in report.checks
            if c.rule_id == "NCG-SPLIT-006" and c.scope.get("fold_id") == fold.fold_id
        ]
        expected = (
            data.loc[list(fold.test_ids)].drop_duplicates("subject_id").diagnosis.value_counts()
        )
        assert checks[0].evidence["participant_support"] == tuple(
            (c, int(expected.get(c, 0))) for c in ("A", "B")
        )


def test_at_s05_07_no_hidden_repair():
    cohort = family_cohort((2, 2, 2))
    config = configuration(cohort, n_splits=5, seed=33)
    before, settings_before = cohort.metadata, config.to_dict()
    with pytest.raises(PlanningError):
        make_splits(cohort, config=config)
    pd.testing.assert_frame_equal(cohort.metadata, before)
    assert config.to_dict() == settings_before


def test_at_s05_08_independent_post_audit(monkeypatch):
    import neurocvguard.splitting as module

    original = module._subject_folds
    called = []
    audit = module.audit_splits

    def bad(*args):
        folds = original(*args)
        fold = folds[0]
        return (replace(fold, test_ids=(*fold.test_ids, fold.train_ids[0])), *folds[1:])

    def spy(*args, **kwargs):
        called.append(True)
        return audit(*args, **kwargs)

    monkeypatch.setattr(module, "_subject_folds", bad)
    monkeypatch.setattr(module, "audit_splits", spy)
    cohort = family_cohort()
    with pytest.raises(PlanningError, match="independent audit") as caught:
        make_splits(cohort, config=configuration(cohort))
    assert called == [True]
    assert any(
        c.rule_id == "NCG-SPLIT-001" and c.status == CheckStatus.FAIL
        for c in caught.value.report.checks
    )


@given(st.integers(0, 100000))
@settings(max_examples=8, deadline=None)
def test_at_s05_09_seed_and_order_stability(seed):
    cohort = family_cohort(visits=2)
    config = configuration(cohort, seed=seed)
    first = make_splits(cohort, config=config)
    data = cohort.metadata.iloc[::-1]
    reverse = Cohort(data, None, cohort.columns, tuple(data.observation_id))
    second = make_splits(reverse, config=config)
    assert first.to_operational_dict() == second.to_operational_dict()
    assert first.generation_report.to_dict(
        sensitive_details=True
    ) == second.generation_report.to_dict(sensitive_details=True)
    assert tuple(fold.fold_id for fold in first.folds) == ("fold-000", "fold-001", "fold-002")
    assert all(fold.repeat_id == "0" for fold in first.folds)


@given(st.integers(0, 100000))
@settings(max_examples=6, deadline=None)
def test_at_s05_10_global_rng_preservation(seed):
    cohort = family_cohort()
    before = np.random.get_state()
    make_splits(cohort, config=configuration(cohort, seed=seed))
    after = np.random.get_state()
    assert before[0] == after[0] and np.array_equal(before[1], after[1]) and before[2:] == after[2:]


def test_assignments_match_standard_participant_splitter():
    cohort = family_cohort((2, 3, 4, 2, 5, 2))
    plan = make_splits(cohort, config=configuration(cohort))
    from neurocvguard.identity import build_components

    data = cohort.metadata.sort_values("subject_id").drop_duplicates("subject_id")
    groups = build_components(cohort).participant_to_component
    expected = StratifiedGroupKFold(3, shuffle=True, random_state=2026).split(
        np.zeros((len(data), 1)), data.diagnosis, [groups[p] for p in data.subject_id]
    )
    actual = people_by_fold(cohort, plan)
    for index, (train, test) in enumerate(expected):
        assert actual[index] == (
            frozenset(data.iloc[train].subject_id),
            frozenset(data.iloc[test].subject_id),
        )


@pytest.mark.parametrize(
    "condition", ["missing_target", "changing_target", "one_class", "missing_family"]
)
def test_planning_prerequisites(condition):
    cohort = family_cohort(visits=2)
    data = cohort.metadata
    if condition == "missing_target":
        data.loc[0, "diagnosis"] = None
    if condition == "changing_target":
        data.loc[0, "diagnosis"] = "A"
    if condition == "one_class":
        data["diagnosis"] = "A"
    if condition == "missing_family":
        data.loc[0, "family"] = None
    cohort = Cohort(data, None, cohort.columns, tuple(data.observation_id))
    with pytest.raises(PlanningError):
        make_splits(cohort, config=configuration(cohort))


def test_runtime_report_separate_from_operational_schema():
    cohort = family_cohort()
    plan = make_splits(cohort, config=configuration(cohort))
    assert "generation_report" not in plan.to_operational_dict()
    restored = SplitPlan.from_dict(plan.to_operational_dict())
    assert restored == plan and restored.generation_report is None
    assert replace(plan).generation_report is None
    assert plan.generation_report.provenance["versions"]["scikit-learn"]


def test_nested_generation_not_silently_enabled():
    cohort = family_cohort()
    config = configuration(cohort)
    with pytest.raises(UnsupportedDesignError, match="outer folds only"):
        make_splits(
            cohort, config=replace(config, evaluation=replace(config.evaluation, tune=True))
        )


def test_insufficient_class_components_can_retain_valid_warning_plan():
    cohort = family_cohort((2, 2, 2, 2))
    data = cohort.metadata
    data.loc[data.family == "g-03", "diagnosis"] = "A"
    cohort = Cohort(data, None, cohort.columns, tuple(data.observation_id))
    plan = make_splits(cohort, config=configuration(cohort, n_splits=4))
    report = plan.generation_report
    limitation = next(c for c in report.checks if c.rule_id == "NCG-PLAN-003")
    assert limitation.status == "fail" and limitation.severity == "warning"
    assert limitation.evidence["class_component_count_sufficient"] is False
    assert all(c.status == "pass" for c in report.checks if c.rule_id == "NCG-SPLIT-005")
    assert any(c.status == "fail" for c in report.checks if c.rule_id == "NCG-SPLIT-006")


@pytest.mark.parametrize("failure", ["value_error", "empty_partition"])
def test_splitter_infeasibility_is_not_input_error_or_fallback(monkeypatch, failure):
    import neurocvguard.splitting as module

    calls = []

    class FailingSplitter:
        def __init__(self, **kwargs):
            calls.append(kwargs)

        def split(self, *args):
            if failure == "value_error":
                raise ValueError("simulated infeasible allocation")
            return [(np.arange(12), np.array([], dtype=int))]

    monkeypatch.setattr(module, "StratifiedGroupKFold", FailingSplitter)
    cohort = family_cohort()
    with pytest.raises(PlanningError) as caught:
        make_splits(cohort, config=configuration(cohort))
    assert len(calls) == 1
    assert caught.value.report.execution_status == "blocked"
    assert any(c.evidence.get("requested_seed") == 2026 for c in caught.value.report.checks)
