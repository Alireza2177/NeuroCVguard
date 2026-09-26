"""Observed outer/inner fitting and held-out prediction; no model export."""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import pandas as pd
from sklearn.base import clone
from sklearn.exceptions import ConvergenceWarning
from sklearn.pipeline import Pipeline

from neurocvguard._evaluation_inputs import EvaluationInputs, participant_weights
from neurocvguard.config import AuditConfig
from neurocvguard.errors import EvaluationError
from neurocvguard.fit_boundaries import prepare_fit_boundary, validate_fit_event, validate_fit_ids
from neurocvguard.models import (
    CheckResult,
    CheckStatus,
    EvidenceKind,
    FitEvent,
    FoldStatus,
    InnerFold,
    SplitFold,
)
from neurocvguard.serialization import FrozenJSONValue, json_digest


@dataclass(frozen=True)
class FitOutcome:
    """Private execution data; an absent event means no fit call happened."""

    fold: SplitFold
    event: FitEvent | None
    probabilities: npt.NDArray[np.float64] | None
    reason: str | None
    checks: tuple[CheckResult, ...]


def evaluation_check(
    rule: str, scope: dict[str, str | int | None], evidence: dict[str, FrozenJSONValue]
) -> CheckResult:
    from neurocvguard.rules import get_rule

    definition = get_rule(rule)
    return CheckResult(
        instance_id="evaluation-" + json_digest({"rule": rule, "scope": scope}),
        rule_id=rule,
        status=CheckStatus.FAIL,
        severity=definition.trigger_severity,
        evidence_kind=EvidenceKind.OBSERVED,
        scope=scope,
        message=definition.trigger_message,
        recommendation=definition.recommendation,
        evidence=evidence,
    )


def _training_frame(inputs: EvaluationInputs, fold: SplitFold) -> pd.DataFrame:
    return inputs.features.loc[list(fold.train_ids)].copy()


def ordered_probabilities(
    pipeline: Pipeline, test: pd.DataFrame, classes: tuple[str, ...]
) -> npt.NDArray[np.float64]:
    """Explicit estimator-to-global ordering; refuse invalid probability output."""
    local = tuple(pipeline.classes_)
    raw = np.asarray(pipeline.predict_proba(test), dtype=np.float64)
    if len(local) != len(set(local)) or set(local) != set(classes):
        raise ValueError("prediction_class_mismatch")
    if (
        raw.shape != (len(test), len(classes))
        or not np.isfinite(raw).all()
        or (raw < 0).any()
        or (raw > 1).any()
        or not np.allclose(raw.sum(axis=1), 1.0, atol=1e-8, rtol=0)
    ):
        raise ValueError("invalid_prediction_probabilities")
    return raw[:, [local.index(label) for label in classes]]


def fit_outer(
    inputs: EvaluationInputs, fold: SplitFold, config: AuditConfig, template: Pipeline
) -> FitOutcome:
    return _fit_partition(inputs, fold, config, template)


def fit_inner(
    inputs: EvaluationInputs,
    fold: SplitFold,
    inner: InnerFold,
    config: AuditConfig,
    template: Pipeline,
) -> FitOutcome:
    return _fit_partition(inputs, fold, config, template, inner=inner)


def _fit_partition(
    inputs: EvaluationInputs,
    fold: SplitFold,
    config: AuditConfig,
    template: Pipeline,
    *,
    inner: InnerFold | None = None,
) -> FitOutcome:
    """Clone once; record only actual fit calls and their observed outcomes."""
    scope: dict[str, str | int | None] = {"repeat_id": fold.repeat_id, "fold_id": fold.fold_id}
    if inner is not None:
        scope.update(inner_fold_id=inner.inner_fold_id, candidate_C=str(config.evaluation.C))
    boundary = prepare_fit_boundary(
        inputs.cohort,
        inputs.plan,
        config=config,
        event_id=("outer-" if inner is None else "inner-") + json_digest(scope),
        repeat_id=fold.repeat_id,
        fold_id=fold.fold_id,
        C=config.evaluation.C,
        inner_fold_id=None if inner is None else inner.inner_fold_id,
    )
    training = (
        _training_frame(inputs, fold)
        if inner is None
        else inputs.features.loc[list(inner.train_ids)].copy()
    )
    held_out = fold.test_ids if inner is None else inner.validation_ids
    actual_ids = tuple(training.index)
    try:
        validate_fit_ids(boundary, actual_ids)
        if set(actual_ids) != set(boundary.allowed_ids):
            raise EvaluationError("The fixed baseline must fit the entire current training set.")
    except EvaluationError:
        finding = evaluation_check(
            "NCG-PROV-004", scope, {"reason": "internal_fit_boundary_violation"}
        )
        return FitOutcome(fold, None, None, "internal_fit_boundary_violation", (finding,))
    pipeline = clone(template)
    pipeline.set_params(classifier__C=config.evaluation.C)
    checks = []
    missing = tuple(str(name) for name in training if training[name].isna().all())
    if missing:
        checks.append(
            evaluation_check(
                "NCG-EVAL-004",
                scope,
                {"feature_names": missing, "handling": "fold_local_zero_fill"},
            )
        )
    targets = inputs.targets.loc[list(actual_ids)]
    weights = participant_weights(inputs.participants.loc[list(actual_ids)])
    reason = None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ConvergenceWarning)
            pipeline.fit(training, targets, classifier__sample_weight=weights)
    except ConvergenceWarning:
        reason = "fit_did_not_converge"
    except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
        reason = {
            ValueError: "fit_value_error",
            FloatingPointError: "fit_floating_point_error",
            np.linalg.LinAlgError: "fit_linear_algebra_error",
        }.get(type(error), "fit_value_error")
    event = FitEvent(
        boundary.event_id,
        fold.repeat_id,
        fold.fold_id,
        None if inner is None else inner.inner_fold_id,
        config.evaluation.C,
        actual_ids,
        FoldStatus.FAILED if reason else FoldStatus.COMPLETED,
        boundary.scope,
    )
    validate_fit_event(event, boundary=boundary)
    probabilities = None
    if reason is None:
        try:
            probabilities = ordered_probabilities(
                pipeline, inputs.features.loc[list(held_out)], inputs.classes
            )
        except (ValueError, FloatingPointError, np.linalg.LinAlgError):
            reason = "prediction_failed_or_invalid"
    if reason:
        checks.append(evaluation_check("NCG-EVAL-001", scope, {"reason": reason}))
    return FitOutcome(fold, event, probabilities, reason, tuple(checks))
