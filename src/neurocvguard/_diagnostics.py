"""Narrow evaluation exception; audit findings and objective validity never change."""

from neurocvguard.config import AuditConfig, Objective
from neurocvguard.errors import UnsupportedDesignError
from neurocvguard.models import AuditReport, CheckStatus

DIAGNOSTIC_LIMITATION = (
    "Diagnostic only; valid_for_objective=false. Do not report as evidence for "
    "unseen-participant generalization. Participant-level aggregation does not remove "
    "the training leakage already present. Every observation has one held-out prediction; "
    "all held-out observation probabilities are averaged once per participant."
)


def validate_diagnostic_request(config: AuditConfig) -> None:
    if config.evaluation.diagnostic_allow_subject_overlap and (
        config.study.objective != Objective.UNSEEN_PARTICIPANT or config.columns.independence
    ):
        raise UnsupportedDesignError(
            "Diagnostic overlap requires unseen_participant and no extra independence columns. "
            "It cannot waive family, site or phase constraints."
        )


def evaluation_eligibility(audit: AuditReport, config: AuditConfig) -> bool:
    """Return whether the narrow outer-overlap exception was actually necessary.

    Inner participant/component overlap is never waived, including during tuning.
    Without extra dependence columns, component overlap is participant overlap.
    All original audit failures remain in the retained report.
    """
    validate_diagnostic_request(config)
    summary = next(c for c in audit.checks if c.scope.get("field") == "split_summary")
    if summary.evidence.get("evaluation_permitted") is True:
        return False
    required = {f"NCG-SPLIT-{n:03d}" for n in (1, 2, 3, 4, 5, 7, 8, 9, 10, 11)}
    failures = [
        c
        for c in audit.checks
        if c.rule_id in required and c.status in (CheckStatus.FAIL, CheckStatus.NOT_ASSESSABLE)
    ]
    if (
        config.evaluation.diagnostic_allow_subject_overlap
        and summary.evidence.get("complete_cv") is True
        and failures
        and all(
            c.status == CheckStatus.FAIL
            and c.rule_id in {"NCG-SPLIT-002", "NCG-SPLIT-003"}
            and c.scope.get("inner_fold_id") is None
            for c in failures
        )
    ):
        return True
    raise UnsupportedDesignError(
        "Evaluation requires complete, protected and objective-valid partitions with all "
        "training classes. Diagnostic permission cannot waive other violations; run audit."
    )
