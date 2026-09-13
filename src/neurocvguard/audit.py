"""Split-only audit orchestration over validated records; no fitting or output writes."""

from neurocvguard import __version__
from neurocvguard.checks.partitions import _audit_checks
from neurocvguard.config import AuditConfig
from neurocvguard.models import (
    AuditReport,
    CheckResult,
    CheckStatus,
    Cohort,
    EvidenceKind,
    ReportStatus,
    Severity,
    SplitPlan,
)


def audit_splits(cohort: Cohort, plan: SplitPlan, *, config: AuditConfig) -> AuditReport:
    """Audit supplied outer/inner memberships without generating or repairing assignments.

    Parameters
    ----------
    cohort : Cohort
        Validated in-memory cohort with explicit observation keys and roles.
    plan : SplitPlan
        Structurally valid JSON contract record. Unknown IDs become scoped diagnostics.
    config : AuditConfig
        Matching roles/objective. Diagnostic options do not relax audit findings.

    Returns
    -------
    AuditReport
        Schema-backed scoped checks. NCG-SPLIT-011 with field=split_summary carries
        complete_cv, valid_for_objective and ordinary evaluation_permitted flags.
        Public projection retains these flags while omitting private memberships.

    Raises
    ------
    InputValidationError, ConfigurationError, SplitValidationError
        Corrupt mandatory identities, objective/mapping mismatch or changed cohort digest.

    Examples
    --------
    ``report = audit_splits(cohort, plan, config=config); public = report.to_dict()``

    Notes
    -----
    Completion is distinct from design validity. A fixed unknown-upstream check
    remains unassessable; this stage does not implement declaration-ledger auditing.
    An audit-only objective never produces valid_for_objective=true. Holdouts and
    multiple repeats remain auditable but outside single-repeat baseline evaluation.
    """
    checks, inventory = _audit_checks(cohort, plan, config)
    upstream = CheckResult(
        "upstream-unassessable",
        "NCG-PROV-001",
        CheckStatus.NOT_ASSESSABLE,
        Severity.INFO,
        EvidenceKind.UNASSESSABLE,
        {},
        "Upstream preprocessing remains unassessable.",
        (
            "Document upstream fitting separately; a split audit cannot verify earlier "
            "transformations."
        ),
        {"reason": "upstream_history_unknown"},
    )
    roles = {item.role.split(":")[0] for item in inventory.fields if item.available}
    missing = {item.role.split(":")[0] for item in inventory.fields if not item.complete}
    return AuditReport(
        schema_version="1.0",
        tool_version=__version__,
        result_type="audit",
        objective=config.study.objective,
        execution_status=ReportStatus.PARTIAL,
        input_summary={
            "n_observations": inventory.n_observations,
            "n_participants": inventory.n_participants,
            "supplied_roles": tuple(sorted(roles)),
            "missing_roles": tuple(sorted(missing)),
        },
        checks=(*checks, upstream),
        limitations=(
            "This audit checks supplied memberships, not how an external experiment ran.",
            (
                "Unknown upstream preprocessing is unassessable; no global leakage-free "
                "verdict is issued."
            ),
            (
                "S02 cohort/feature file ingestion is not implemented; this API consumes "
                "in-memory Cohort records."
            ),
            (
                "Only one complete repeat with at least two outer folds is within ordinary "
                "baseline scope."
            ),
            "Missing test classes leave class-complete metrics undefined; no scores were computed.",
            (
                "Diagnostic requests do not waive audit violations or approve "
                "unseen-participant generalization."
            ),
        ),
        provenance={
            "foundation_version": "1.0.0",
            "versions": {"neurocvguard": __version__},
            "sensitive_details": False,
            "upstream_preprocessing_verified": False,
        },
    )
