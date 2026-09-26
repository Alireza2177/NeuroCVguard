"""Cohort and split audit orchestration; no fitting or output writes."""

from neurocvguard import __version__
from neurocvguard.checks.associations import check_associations
from neurocvguard.checks.cohort import check_cohort
from neurocvguard.checks.partitions import _audit_checks
from neurocvguard.checks.preprocessing import check_preprocessing
from neurocvguard.config import AuditConfig
from neurocvguard.errors import ConfigurationError
from neurocvguard.models import (
    AuditReport,
    Cohort,
    ReportStatus,
    SplitPlan,
)


def audit_cohort(
    cohort: Cohort,
    *,
    config: AuditConfig,
    ledger: dict[str, object] | None = None,
) -> AuditReport:
    """Combine in-memory cohort, association and declared preprocessing checks.

    Parameters
    ----------
    cohort : Cohort
        Explicitly keyed constructed metadata and optional aligned features.
    config : AuditConfig
        Matching column roles and diagnostic settings.
    ledger : dict or None, optional
        Strict user-declaration ledger. Fold-specific boundaries remain unassessable
        here; check_preprocessing accepts the additional plan needed to compare them.

    Returns
    -------
    AuditReport
        Partial coverage with persistent unverified-upstream limitation. No fit
        events or scores are created. Default serialization is privacy-projected.

    Examples
    --------
    ``audit_cohort(cohort, config=config, ledger=data).to_dict()``
    """
    if cohort.columns != config.columns:
        raise ConfigurationError("Cohort roles differ from config.columns; use matching roles.")
    provenance_checks = check_preprocessing(cohort, config=config, ledger=ledger)
    result = check_cohort(cohort, config.evaluation.feature_columns)
    inventory = result.inventory
    roles = {item.role.split(":")[0] for item in inventory.fields if item.available}
    missing = {item.role.split(":")[0] for item in inventory.fields if not item.complete}
    checks = (*result.checks, *check_associations(cohort, config=config), *provenance_checks)
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
        checks=checks,
        limitations=(
            "Imported preprocessing is declared, not authenticated execution history.",
            "Upstream preprocessing remains unverified; "
            "a Pipeline cannot repair earlier global fitting.",
            "Fold-specific declared fit IDs require a matching split plan for comparison.",
            "This cohort audit cannot establish participant/domain separation "
            "without a supplied plan.",
            "Input identity namespaces must be harmonized upstream; "
            "aliases cannot be resolved automatically.",
        ),
        provenance={
            "foundation_version": "1.0.0",
            "versions": {"neurocvguard": __version__},
            "sensitive_details": False,
            "upstream_preprocessing_verified": False,
        },
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
    remains unassessable; this split-only signature does not accept a ledger.
    An audit-only objective never produces valid_for_objective=true. Holdouts and
    multiple repeats remain auditable but outside single-repeat baseline evaluation.
    """
    checks, inventory = _audit_checks(cohort, plan, config)
    upstream = check_preprocessing(cohort, config=config)[0]
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
                "Input identity namespaces must be harmonized upstream; "
                "site prefixes do not establish distinct participant identities."
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
