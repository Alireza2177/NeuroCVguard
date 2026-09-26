"""Participant classification with isolated fits and optional nested C selection."""

import platform
from dataclasses import replace
from importlib.metadata import version

import numpy as np
import numpy.typing as npt

from neurocvguard import __version__
from neurocvguard._evaluation_fits import FitOutcome, evaluation_check, fit_outer
from neurocvguard._evaluation_inputs import fixed_pipeline, preflight
from neurocvguard._tuning import TUNING_POLICY, tune_C
from neurocvguard.config import AuditConfig
from neurocvguard.io import cohort_digest, feature_digest
from neurocvguard.metrics import aggregate_participants, participant_metrics
from neurocvguard.models import (
    CandidateScore,
    CheckResult,
    Cohort,
    EvaluationFold,
    EvaluationResult,
    EvaluationStatus,
    FitEvent,
    FoldStatus,
    MetricSet,
    SplitPlan,
)
from neurocvguard.serialization import json_digest


def _undefined_checks(metrics: MetricSet, scope: dict[str, str | int | None]) -> list[CheckResult]:
    checks = []
    for name in ("accuracy", "balanced_accuracy", "macro_f1", "roc_auc"):
        value = getattr(metrics, name)
        if value.value is None:
            checks.append(
                evaluation_check(
                    "NCG-EVAL-002", {**scope, "field": name}, {"reason": value.reason, "n": value.n}
                )
            )
    return checks


def evaluate_baseline(cohort: Cohort, plan: SplitPlan, *, config: AuditConfig) -> EvaluationResult:
    """Run the controlled baseline, optionally tuning C; never serializes models.

    Parameters
    ----------
    cohort : Cohort
        Explicitly keyed metadata and selected numeric features.
    plan : SplitPlan
        Complete, objective-valid outer CV with exactly one repeat.
    config : AuditConfig
        Fixed C or an explicit nested C grid, seed and iteration limit.

    Returns
    -------
    EvaluationResult
        Sensitive fit records and plan, participant metrics and prerequisite checks.
        A failed fold leaves the result incomplete with pooled_metrics=None.

    Raises
    ------
    UnsupportedDesignError
        A validly described request is infeasible or outside classification scope.
    InputValidationError, ConfigurationError, SplitValidationError
        Malformed inputs or mismatched context. Unexpected execution defects propagate.

    Notes
    -----
    Each training participant has total classifier loss weight one. Imputation
    and scaling use training observations, not participant-weighted statistics.
    Controlled fitting cannot authenticate or repair upstream preprocessing.

    Examples
    --------
    ``result = evaluate_baseline(cohort, plan, config=config)``
    """
    inputs = preflight(cohort, plan, config)
    template = fixed_pipeline(config)
    folds: list[EvaluationFold] = []
    events: list[FitEvent] = []
    checks = [
        replace(check, evidence={**check.evidence, "input_summary": inputs.audit.input_summary})
        if check.rule_id == "NCG-COHORT-001"
        else check
        for check in inputs.audit.checks
    ]
    people: list[str] = []
    truths: list[str] = []
    probabilities: list[npt.NDArray[np.float64]] = []
    for fold in sorted(inputs.plan.folds, key=lambda item: (item.repeat_id, item.fold_id)):
        selected_C: float | None = config.evaluation.C
        candidate_scores: tuple[CandidateScore, ...] = ()
        fit_config = config
        if config.evaluation.tune:
            selection = tune_C(inputs, fold, config, template)
            events.extend(selection.events)
            checks.extend(selection.checks)
            candidate_scores = selection.scores
            selected_C = selection.selected_C
            if selected_C is not None:
                fit_config = replace(config, evaluation=replace(config.evaluation, C=selected_C))
        outcome = (
            fit_outer(inputs, fold, fit_config, template)
            if selected_C is not None
            else FitOutcome(fold, None, None, "inner_tuning_failed", ())
        )
        checks.extend(outcome.checks)
        if outcome.event is not None:
            events.append(outcome.event)
        train_people = set(inputs.participants.loc[list(fold.train_ids)])
        test_people = tuple(inputs.participants.loc[list(fold.test_ids)])
        metrics = None
        if outcome.reason is None:
            assert outcome.probabilities is not None
            ids, labels, means = aggregate_participants(
                test_people, tuple(inputs.targets.loc[list(fold.test_ids)]), outcome.probabilities
            )
            metrics = participant_metrics(
                labels,
                means,
                class_order=inputs.classes,
                positive_class=config.evaluation.positive_class,
            )
            people.extend(ids)
            truths.extend(labels)
            probabilities.append(means)
            checks.extend(
                _undefined_checks(metrics, {"repeat_id": fold.repeat_id, "fold_id": fold.fold_id})
            )
        folds.append(
            EvaluationFold(
                fold.repeat_id,
                fold.fold_id,
                FoldStatus.FAILED if outcome.reason else FoldStatus.COMPLETED,
                outcome.reason,
                len(train_people),
                len(set(test_people)),
                selected_C,
                metrics,
                candidate_scores,
            )
        )
    complete = all(fold.status == FoldStatus.COMPLETED for fold in folds)
    pooled = None
    if complete:
        if len(people) != len(set(people)) or set(people) != set(inputs.participants):
            raise RuntimeError("Internal participant out-of-fold coverage defect.")
        pooled = participant_metrics(
            tuple(truths),
            np.concatenate(probabilities),
            class_order=inputs.classes,
            positive_class=config.evaluation.positive_class,
        )
        checks.extend(_undefined_checks(pooled, {"field": "pooled"}))
    checks.sort(
        key=lambda item: (
            item.rule_id,
            str(item.scope.get("repeat_id", "")),
            str(item.scope.get("fold_id", "")),
            str(item.scope.get("field", "")),
            item.instance_id,
        )
    )
    return EvaluationResult(
        format="neurocvguard.evaluation.private",
        schema_version="1.0",
        tool_version=__version__,
        sensitive=True,
        execution_status=EvaluationStatus.COMPLETED if complete else EvaluationStatus.INCOMPLETE,
        objective=config.study.objective,
        diagnostic_only=False,
        cohort_digest=cohort_digest(inputs.cohort),
        feature_digest=feature_digest(inputs.cohort),
        config_digest=json_digest(config.to_dict()),
        class_order=inputs.classes,
        positive_class=config.evaluation.positive_class,
        feature_columns=config.evaluation.feature_columns,
        metric_unit="participant",
        n_observations=len(inputs.cohort.observation_order),
        n_participants=len(set(inputs.participants)),
        folds=tuple(folds),
        fit_events=tuple(events),
        pooled_metrics=pooled,
        preflight_checks=tuple(checks),
        limitations=(
            *inputs.audit.limitations,
            *((TUNING_POLICY,) if config.evaluation.tune else ()),
            "Research baseline only; no clinical validity or inferential confidence interval.",
            "Classifier loss weights balance participants within each fit; imputation and "
            "scaling use training-observation statistics.",
            "Undefined metrics retain null values; "
            "failed folds prevent a pooled complete-CV score.",
        ),
        provenance={
            "seed": config.split.seed,
            "versions": {
                "python": platform.python_version(),
                "neurocvguard": __version__,
                **{name: version(name) for name in ("numpy", "pandas", "scipy", "scikit-learn")},
            },
            "upstream_preprocessing_verified": False,
        },
        actual_plan=inputs.plan,
        plan_digest=json_digest(inputs.plan.to_operational_dict()),
    )
