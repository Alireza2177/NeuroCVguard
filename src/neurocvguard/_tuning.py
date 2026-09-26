"""Explicit nested C selection from pooled inner participant predictions only."""

from dataclasses import dataclass, replace

import numpy as np
import numpy.typing as npt
from sklearn.pipeline import Pipeline

from neurocvguard._evaluation_fits import fit_inner
from neurocvguard._evaluation_inputs import EvaluationInputs
from neurocvguard.config import AuditConfig
from neurocvguard.metrics import aggregate_participants, participant_metrics
from neurocvguard.models import CandidateScore, CheckResult, FitEvent, SplitFold

TUNING_POLICY = (
    "Inner tuning protects participants and declared dependence components, including "
    "under site/phase-held-out outer evaluation; its objective is unseen participants. "
    "Selection maximizes pooled inner participant balanced accuracy; scores within "
    "1e-12 of the maximum tie and the smallest C wins. Candidate scores and selected_C "
    "record the resolution. Any required inner failure prevents outer refitting."
)


@dataclass(frozen=True)
class Selection:
    selected_C: float | None
    scores: tuple[CandidateScore, ...]
    events: tuple[FitEvent, ...]
    checks: tuple[CheckResult, ...]
    reason: str | None


def select_C(scores: tuple[CandidateScore, ...]) -> float | None:
    """Refuse a partial grid; compare ties to the maximum, not pairwise chains."""
    if not scores or any(item.balanced_accuracy is None for item in scores):
        return None
    maximum = max(item.balanced_accuracy for item in scores if item.balanced_accuracy is not None)
    return min(
        item.C
        for item in scores
        if item.balanced_accuracy is not None and maximum - item.balanced_accuracy <= 1e-12
    )


def tune_C(
    inputs: EvaluationInputs, fold: SplitFold, config: AuditConfig, template: Pipeline
) -> Selection:
    """Use each fixed inner membership for every sorted C, retaining all failures."""
    if not fold.inner_folds:
        raise RuntimeError("Tuning requires preflight-validated inner assignments.")
    scores: list[CandidateScore] = []
    events: list[FitEvent] = []
    checks: list[CheckResult] = []
    for C in sorted(set(config.evaluation.C_grid)):
        candidate_config = replace(config, evaluation=replace(config.evaluation, C=C))
        people: list[str] = []
        truths: list[str] = []
        probabilities: list[npt.NDArray[np.float64]] = []
        failure = None
        for inner in sorted(fold.inner_folds, key=lambda item: item.inner_fold_id):
            outcome = fit_inner(inputs, fold, inner, candidate_config, template)
            checks.extend(outcome.checks)
            if outcome.event is not None:
                events.append(outcome.event)
            if outcome.reason is not None:
                failure = failure or outcome.reason
                continue
            assert outcome.probabilities is not None
            ids, labels, means = aggregate_participants(
                tuple(inputs.participants.loc[list(inner.validation_ids)]),
                tuple(inputs.targets.loc[list(inner.validation_ids)]),
                outcome.probabilities,
            )
            people.extend(ids)
            truths.extend(labels)
            probabilities.append(means)
        value = None
        if failure is None:
            expected = set(inputs.participants.loc[list(fold.train_ids)])
            if set(people) != expected or len(people) != len(expected):
                raise RuntimeError("Internal inner participant out-of-fold coverage defect.")
            metric = participant_metrics(
                tuple(truths),
                np.concatenate(probabilities),
                class_order=inputs.classes,
                positive_class=config.evaluation.positive_class,
            ).balanced_accuracy
            value, failure = metric.value, metric.reason
        scores.append(CandidateScore(C, value, failure))
    selected = select_C(tuple(scores))
    return Selection(
        selected,
        tuple(scores),
        tuple(events),
        tuple(checks),
        None if selected is not None else "inner_tuning_failed",
    )
