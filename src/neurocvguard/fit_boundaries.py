"""Preparation and validation for future controlled fits; never executes or logs fits."""

import math
from dataclasses import dataclass, field

from neurocvguard.config import AuditConfig
from neurocvguard.errors import EvaluationError
from neurocvguard.identity import _valid_label
from neurocvguard.models import Cohort, FitEvent, SplitPlan
from neurocvguard.provenance import _training_ids, _validate_context


@dataclass(frozen=True)
class FitBoundary:
    """A planned training boundary, with no execution status or evidence claim.

    ``C`` describes the prescribed logistic baseline candidate. Observation IDs
    are sensitive. This object is not a FitEvent and cannot authenticate execution.
    Use prepare_fit_boundary to derive it from validated cohort/plan context.
    """

    event_id: str
    repeat_id: str
    fold_id: str
    inner_fold_id: str | None
    C: float
    allowed_ids: tuple[str, ...] = field(repr=False)

    def __post_init__(self) -> None:
        labels = (self.event_id, self.repeat_id, self.fold_id)
        if any(not _valid_label(value) for value in labels) or (
            self.inner_fold_id is not None and not _valid_label(self.inner_fold_id)
        ):
            raise EvaluationError("Fit boundary identifiers must be valid nonempty labels.")
        if type(self.C) not in (int, float) or not math.isfinite(self.C) or self.C <= 0:
            raise EvaluationError("Fit boundary C must be finite and positive.")
        ids = tuple(self.allowed_ids)
        if not ids or len(ids) != len(set(ids)) or any(not _valid_label(key) for key in ids):
            raise EvaluationError("Fit boundary requires unique nonempty observation IDs.")
        object.__setattr__(self, "allowed_ids", tuple(sorted(ids)))

    @property
    def scope(self) -> str:
        """Return outer_train or inner_train, without claiming a fit occurred."""
        return "outer_train" if self.inner_fold_id is None else "inner_train"


def prepare_fit_boundary(
    cohort: Cohort,
    plan: SplitPlan,
    *,
    config: AuditConfig,
    event_id: str,
    repeat_id: str,
    fold_id: str,
    C: float,
    inner_fold_id: str | None = None,
) -> FitBoundary:
    """Prepare an outer/inner training boundary without creating a runtime event.

    Parameters
    ----------
    cohort, plan, config : Cohort, SplitPlan, AuditConfig
        Matching identity context and disjoint complete memberships. This helper
        does not replace the evaluator's prerequisite scientific split audit.
    event_id, repeat_id, fold_id : str
        Planned event identity and explicit outer fold reference.
    C : float
        Positive finite logistic baseline parameter.
    inner_fold_id : str or None, optional
        Inner candidate context; None denotes outer fitting.

    Returns
    -------
    FitBoundary
        Planning data only. No estimator is constructed, called or serialized.

    Examples
    --------
    ``boundary = prepare_fit_boundary(cohort, plan, config=config,
    event_id="fit-1", repeat_id="r0", fold_id="f0", C=1.0)``
    """
    _validate_context(cohort, config, plan)
    ids = _training_ids(plan, repeat_id, fold_id, inner_fold_id)
    return FitBoundary(event_id, repeat_id, fold_id, inner_fold_id, C, ids)


def validate_fit_ids(boundary: FitBoundary, fit_ids: tuple[str, ...]) -> None:
    """Reject empty, duplicate or outside-training IDs before a future fit call.

    A strict subset is permitted. This validation is not an observed fit event;
    the future runner must record actual call completion/failure separately.
    """
    if (
        not fit_ids
        or any(not _valid_label(key) for key in fit_ids)
        or len(fit_ids) != len(set(fit_ids))
    ):
        raise EvaluationError("Actual fit IDs must be unique nonempty observation keys.")
    if not set(fit_ids) <= set(boundary.allowed_ids):
        raise EvaluationError("Fit boundary violation: IDs outside the current training subset.")


def validate_fit_event(event: FitEvent, *, boundary: FitBoundary) -> None:
    """Validate a recorded event's context and IDs; never authenticate its origin.

    Both failed and completed FitEvent records can be checked. Parsing or manually
    constructing such a record proves no fit occurred. S07 creates no observed
    events; the future runner must capture the actual call and its outcome.
    """
    expected = (
        boundary.event_id,
        boundary.repeat_id,
        boundary.fold_id,
        boundary.inner_fold_id,
        boundary.C,
        boundary.scope,
    )
    actual = (
        event.event_id,
        event.repeat_id,
        event.fold_id,
        event.inner_fold_id,
        event.C,
        event.scope,
    )
    if actual != expected:
        raise EvaluationError("Recorded fit event does not match the planned fold/model context.")
    validate_fit_ids(boundary, event.fit_ids)
