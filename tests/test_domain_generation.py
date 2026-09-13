"""S05 strict domain holdout and training-feasibility tests."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from test_generation import family_cohort

from neurocvguard.config import AuditConfig, Objective, SplitConfig, SplitScheme, StudyConfig
from neurocvguard.errors import PlanningError
from neurocvguard.models import Cohort
from neurocvguard.splitting import make_splits


def domain_config(cohort, role="site", seed=2026):
    return AuditConfig(
        columns=cohort.columns,
        study=StudyConfig(Objective.UNSEEN_SITE if role == "site" else Objective.UNSEEN_PHASE),
        split=SplitConfig(
            SplitScheme.LEAVE_ONE_SITE_OUT if role == "site" else SplitScheme.LEAVE_ONE_PHASE_OUT,
            None,
            seed,
        ),
    )


@pytest.mark.parametrize("crossing", ["person", "family"])
def test_at_s05_05_crossing_domain_group(crossing):
    cohort = family_cohort(visits=2)
    data = cohort.metadata
    if crossing == "person":
        data.loc[0, "site"] = "crossing-site"
    else:
        data.loc[data.subject_id == "p-00-00", "site"] = "crossing-site"
    cohort = Cohort(data, None, cohort.columns, tuple(data.observation_id))
    before = cohort.metadata
    with pytest.raises(PlanningError, match="cross domains") as caught:
        make_splits(cohort, config=domain_config(cohort))
    assert any(
        c.rule_id == "NCG-PLAN-002" and c.status == "fail" for c in caught.value.report.checks
    )
    pd.testing.assert_frame_equal(cohort.metadata, before)
    assert "crossing-site" not in str(caught.value)


@pytest.mark.parametrize("role", ["site", "phase"])
def test_at_s05_06_held_out_phase(role):
    cohort = family_cohort(visits=2)
    plan = make_splits(cohort, config=domain_config(cohort, role))
    data = cohort.metadata.set_index("observation_id")
    held = []
    for fold in plan.folds:
        train, test = data.loc[list(fold.train_ids)], data.loc[list(fold.test_ids)]
        assert train[role].isin(test[role]).sum() == 0
        assert set(train.subject_id).isdisjoint(test.subject_id)
        assert set(train.family).isdisjoint(test.family)
        assert test[role].nunique() == 1
        held.extend(test[role].unique())
    assert sorted(held) == sorted(data[role].unique())
    assert len(plan.folds) == 6 and plan.seed == 2026


@pytest.mark.parametrize("problem", ["missing", "absent", "one_domain"])
def test_required_domain_coverage(problem):
    cohort = family_cohort()
    data = cohort.metadata
    if problem == "missing":
        data.loc[0, "site"] = None
    if problem == "absent":
        data = data.drop(columns="site")
    if problem == "one_domain":
        data["site"] = "same"
    cohort = Cohort(data, None, cohort.columns, tuple(data.observation_id))
    with pytest.raises(PlanningError):
        make_splits(cohort, config=domain_config(cohort))


def test_missing_training_class_blocks_every_requested_plan():
    cohort = family_cohort()
    data = cohort.metadata
    data["diagnosis"] = ["rare" if family == "g-00" else "common" for family in data.family]
    cohort = Cohort(data, None, cohort.columns, tuple(data.observation_id))
    with pytest.raises(PlanningError, match="NCG-SPLIT-005") as caught:
        make_splits(cohort, config=domain_config(cohort))
    assert len([c for c in caught.value.report.checks if c.rule_id == "NCG-SPLIT-005"]) == 6
    assert any(
        c.rule_id == "NCG-SPLIT-005" and c.status == "fail" for c in caught.value.report.checks
    )


def test_missing_test_class_is_warning_when_training_supported():
    cohort = family_cohort()
    data = cohort.metadata
    data["diagnosis"] = ["A" if int(family[-2:]) % 2 else "B" for family in data.family]
    cohort = Cohort(data, None, cohort.columns, tuple(data.observation_id))
    plan = make_splits(cohort, config=domain_config(cohort))
    checks = plan.generation_report.checks
    assert all(c.status == "pass" for c in checks if c.rule_id == "NCG-SPLIT-005")
    assert all(
        c.status == "fail" and c.severity == "warning"
        for c in checks
        if c.rule_id == "NCG-SPLIT-006"
    )


def test_domain_order_and_rng_stability():
    cohort = family_cohort()
    config = domain_config(cohort)
    before = np.random.get_state()
    first = make_splits(cohort, config=config)
    data = cohort.metadata.iloc[::-1]
    second = make_splits(
        Cohort(data, None, cohort.columns, tuple(data.observation_id)), config=config
    )
    after = np.random.get_state()
    assert first.to_operational_dict() == second.to_operational_dict()
    assert before[0] == after[0] and np.array_equal(before[1], after[1]) and before[2:] == after[2:]
    changed_seed = make_splits(cohort, config=replace(config, split=replace(config.split, seed=11)))
    assert first.folds == changed_seed.folds  # LOGO does not use randomness.
    assert first.plan_id != changed_seed.plan_id  # Explicit requested seed is still recorded.
