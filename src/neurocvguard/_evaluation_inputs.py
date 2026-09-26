"""Preflight and fixed sklearn pipeline construction; no fitting occurs here."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace

import numpy as np
import numpy.typing as npt
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from neurocvguard._diagnostics import evaluation_eligibility, validate_diagnostic_request
from neurocvguard._inner_plans import with_inner_plans
from neurocvguard._tables import _dimensions
from neurocvguard.config import AuditConfig, Objective
from neurocvguard.errors import ConfigurationError, InputValidationError, UnsupportedDesignError
from neurocvguard.io import load_cohort, load_split_plan
from neurocvguard.models import AuditReport, Cohort, SplitPlan
from neurocvguard.workflows import audit_workflow


@dataclass(frozen=True)
class EvaluationInputs:
    """Validated private inputs; frames are owned by this evaluation call."""

    cohort: Cohort
    plan: SplitPlan
    audit: AuditReport
    features: pd.DataFrame
    targets: pd.Series[str]
    participants: pd.Series[str]
    classes: tuple[str, ...]
    diagnostic_only: bool = False


def preflight(cohort: Cohort, plan: SplitPlan, config: AuditConfig) -> EvaluationInputs:
    """Validate every fold before any fit, without repairing a design or its data."""
    if cohort.columns != config.columns:
        raise ConfigurationError("Cohort roles differ from the evaluation configuration.")
    _dimensions(len(cohort.observation_order), config, len(config.evaluation.feature_columns))
    features = cohort.features
    if features is None or not config.evaluation.feature_columns:
        raise InputValidationError("Evaluation requires explicitly selected numeric features.")
    validated = load_cohort(cohort.metadata, config=config, features=features)
    bound = load_split_plan(dict(plan.to_operational_dict()), cohort=validated, config=config)
    if config.study.objective == Objective.AUDIT_ONLY:
        raise UnsupportedDesignError("audit_only supports partition inspection, not evaluation.")
    validate_diagnostic_request(config)
    if len(bound.folds) < 2 or len({fold.repeat_id for fold in bound.folds}) != 1:
        raise UnsupportedDesignError(
            "Evaluation requires complete CV with two or more folds and one repeat."
        )
    metadata = validated.metadata.set_index(config.columns.observation_id)
    target = config.columns.target
    if target is None or target not in metadata or metadata[target].isna().any():
        raise UnsupportedDesignError(
            "Classification requires a known target for every participant."
        )
    groups = metadata.groupby(config.columns.subject_id)[target].nunique()
    if (groups != 1).any():
        raise UnsupportedDesignError(
            "Targets change within participants; curate a supported cohort explicitly."
        )
    classes = tuple(sorted(metadata[target].unique()))
    if len(classes) < 2:
        raise UnsupportedDesignError("Classification requires at least two global target classes.")
    if (
        max(len(metadata) * len(classes), len(classes) ** 2) * 8
        > config.limits.max_dense_mb * 1024 * 1024
    ):
        raise InputValidationError(
            "Evaluation probability/confusion matrices exceed limits.max_dense_mb; "
            "review the declared class space and memory limit explicitly."
        )
    if (
        config.evaluation.positive_class is not None
        and config.evaluation.positive_class not in classes
    ):
        raise ConfigurationError("evaluation.positive_class must name a global target class.")
    # First validate outer and any supplied inner partitions. Only absent inner
    # assignments are allowed here; invalid supplied assignments are never replaced.
    outer_config = replace(config, evaluation=replace(config.evaluation, tune=False))
    audit = audit_workflow(validated, config=outer_config, plan=bound)
    diagnostic = evaluation_eligibility(audit, config)
    # Independently require exactly one test fold per participant, not just per row.
    participants = metadata[config.columns.subject_id]
    tested = Counter(
        person for fold in bound.folds for person in set(participants.loc[list(fold.test_ids)])
    )
    if set(tested) != set(participants) or (
        not diagnostic and any(count != 1 for count in tested.values())
    ):
        raise UnsupportedDesignError("Each participant must be tested in exactly one outer fold.")
    if config.evaluation.tune:
        bound = with_inner_plans(validated, bound, config)
        audit = audit_workflow(validated, config=config, plan=bound)
        diagnostic = evaluation_eligibility(audit, config)
    selected = validated.features
    assert selected is not None
    return EvaluationInputs(
        validated,
        bound,
        audit,
        selected.set_index(config.columns.observation_id),
        metadata[target],
        participants,
        classes,
        diagnostic,
    )


def participant_weights(participants: pd.Series[str]) -> npt.NDArray[np.float64]:
    """Current-subset classifier weights; every participant contributes total one."""
    counts = Counter(participants)
    return np.asarray([1.0 / counts[person] for person in participants], dtype=np.float64)


def fixed_pipeline(config: AuditConfig) -> Pipeline:
    """Construct an unfitted standard pipeline using the supported installed API."""
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    C=config.evaluation.C,
                    solver="lbfgs",
                    max_iter=config.evaluation.max_iter,
                    random_state=config.split.seed,
                ),
            ),
        ]
    )
