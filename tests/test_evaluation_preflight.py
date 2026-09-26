"""S10.A no-fit scope checks, explicit roles and prescribed pipeline settings."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from test_cli_commands import FIXTURES

from neurocvguard import audit_splits, load_cohort, load_config, load_split_plan
from neurocvguard._evaluation_inputs import fixed_pipeline, participant_weights, preflight
from neurocvguard.config import Objective
from neurocvguard.errors import ConfigurationError, InputValidationError, UnsupportedDesignError
from neurocvguard.models import Cohort, SplitFold


def evaluation_inputs():
    config = load_config(FIXTURES / "config.json")
    cohort = load_cohort(
        FIXTURES / "cohort_clean.tsv", config=config, features=FIXTURES / "features_shuffled.tsv"
    )
    plan = load_split_plan(FIXTURES / "splits_clean.json", cohort=cohort, config=config)
    return cohort, plan, config


def test_prescribed_unfitted_pipeline():
    cohort, plan, config = evaluation_inputs()
    validated = preflight(cohort, plan, config)
    assert validated.classes == ("AD", "CN")
    pipe = fixed_pipeline(config)
    assert tuple(pipe.named_steps) == ("imputer", "scaler", "classifier")
    assert pipe.named_steps["imputer"].strategy == "median"
    assert pipe.named_steps["imputer"].keep_empty_features is True
    assert pipe.named_steps["classifier"].solver == "lbfgs"
    assert pipe.named_steps["classifier"].class_weight is None
    assert not hasattr(pipe.named_steps["scaler"], "mean_")


def test_at_s10_04_participant_loss_weights():
    people = pd.Series(["p1", "p2", "p1", "p3", "p1", "p2"])
    weights = participant_weights(people)
    np.testing.assert_allclose(weights, [1 / 3, 1 / 2, 1 / 3, 1, 1 / 3, 1 / 2])
    for person in set(people):
        assert weights[people == person].sum() == pytest.approx(1)
    # Counts are recomputed for the current subset, never imported from the cohort.
    np.testing.assert_allclose(participant_weights(people.iloc[:2]), [1, 1])


def test_at_s10_08_changing_target_refused():
    cohort, plan, config = evaluation_inputs()
    metadata = cohort.metadata
    metadata.loc[0, "diagnosis"] = "AD"
    altered = Cohort(metadata, cohort.features, cohort.columns, cohort.observation_order)
    unbound = replace(plan, cohort_digest=None)
    with pytest.raises(UnsupportedDesignError, match="change within participants"):
        preflight(altered, unbound, config)
    assert audit_splits(altered, unbound, config=config).checks


@pytest.mark.parametrize("scope", ["holdout", "repeats", "audit_only", "tune", "diagnostic"])
def test_at_s10_14_scope_guards(scope):
    cohort, plan, config = evaluation_inputs()
    if scope == "holdout":
        plan = replace(plan, folds=plan.folds[:1])
    elif scope == "repeats":
        plan = replace(
            plan, folds=plan.folds + tuple(replace(f, repeat_id="r2") for f in plan.folds)
        )
    elif scope == "audit_only":
        config = replace(config, study=replace(config.study, objective=Objective.AUDIT_ONLY))
        plan = replace(plan, objective=Objective.AUDIT_ONLY)
    elif scope == "tune":
        # S11 implements this former scope boundary; preserve the regression node.
        config = replace(config, evaluation=replace(config.evaluation, tune=True))
        assert all(f.inner_folds for f in preflight(cohort, plan, config).plan.folds)
        return
    else:
        config = replace(
            config,
            evaluation=replace(
                config.evaluation,
                diagnostic_allow_subject_overlap=True,
            ),
        )
    with pytest.raises(UnsupportedDesignError):
        preflight(cohort, plan, config)
    assert audit_splits(cohort, plan, config=config).checks


def test_overlap_rejected_before_pipeline(monkeypatch):
    cohort, _, config = evaluation_inputs()
    plan = load_split_plan(
        FIXTURES / "splits_participant_overlap.json", cohort=cohort, config=config
    )
    with pytest.raises(UnsupportedDesignError, match="objective-valid"):
        preflight(cohort, plan, config)


@pytest.mark.parametrize("problem", ["features", "infinity", "limit", "positive", "roles"])
def test_preflight_invalid_input(problem):
    cohort, plan, config = evaluation_inputs()
    expected = InputValidationError
    if problem == "features":
        cohort = Cohort(cohort.metadata, None, cohort.columns, cohort.observation_order)
    elif problem == "infinity":
        features = cohort.features
        features.loc[0, "feature_1"] = np.inf
        cohort = Cohort(cohort.metadata, features, cohort.columns, cohort.observation_order)
    elif problem == "limit":
        config = replace(config, limits=replace(config.limits, max_rows=1))
    elif problem == "positive":
        config = replace(config, evaluation=replace(config.evaluation, positive_class="absent"))
        expected = ConfigurationError
    else:
        config = replace(config, columns=replace(config.columns, subject_id="other"))
        expected = ConfigurationError
    with pytest.raises(expected):
        preflight(cohort, plan, config)


def test_probability_allocation_guard_before_fitting():
    _, plan, config = evaluation_inputs()
    config = replace(
        config,
        limits=replace(config.limits, max_dense_mb=1),
        evaluation=replace(config.evaluation, positive_class=None),
    )
    metadata = pd.DataFrame(
        [
            {
                "observation_id": f"o-{i}-{side}",
                "subject_id": f"p-{i}-{side}",
                "diagnosis": f"c-{i}",
            }
            for side in range(2)
            for i in range(400)
        ]
    )
    features = metadata[["observation_id"]].assign(feature_1=1.0, feature_2=2.0)
    cohort = load_cohort(metadata, config=config, features=features)
    first, second = cohort.observation_order[:400], cohort.observation_order[400:]
    plan = replace(
        plan,
        cohort_digest=None,
        folds=(SplitFold("r", "a", first, second), SplitFold("r", "b", second, first)),
    )
    with pytest.raises(InputValidationError, match="probability/confusion"):
        preflight(cohort, plan, config)
