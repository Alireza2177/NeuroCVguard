"""Shared audit orchestration for Python callers and the local CLI."""

from dataclasses import replace

from neurocvguard.audit import audit_cohort, audit_splits
from neurocvguard.checks.preprocessing import check_preprocessing
from neurocvguard.config import AuditConfig
from neurocvguard.errors import InputValidationError
from neurocvguard.models import AuditReport, Cohort, SplitPlan
from neurocvguard.provenance import _validate_context


def audit_workflow(
    cohort: Cohort,
    *,
    config: AuditConfig,
    plan: SplitPlan | None = None,
    ledger: dict[str, object] | None = None,
) -> AuditReport:
    """Combine cohort, split and declared provenance checks without fitting.

    Parameters
    ----------
    cohort : Cohort
        Validated keyed metadata and optional aligned features.
    config : AuditConfig
        Matching explicit roles and objective.
    plan : SplitPlan or None, optional
        Supplied memberships; observed violations remain reportable findings.
    ledger : dict or None, optional
        User declarations, never authenticated execution history.

    Returns
    -------
    AuditReport
        Combined scopes with unique namespaced instance IDs. Incomplete provenance
        remains prominent; repeated rule IDs in distinct scopes are retained.

    Raises
    ------
    InputValidationError, ConfigurationError, SplitValidationError
        Invalid contracts or inconsistent identity/configuration context.

    Notes
    -----
    Invalid memberships remain split findings and cannot establish a declared
    training boundary. No membership is repaired or discarded.

    Examples
    --------
    ``report = audit_workflow(cohort, config=config, plan=plan)``
    """
    base = audit_cohort(cohort, config=config)
    checks = [
        replace(item, instance_id="cohort:" + item.instance_id)
        for item in base.checks
        if not item.rule_id.startswith("NCG-PROV-")
    ]
    limitations = list(base.limitations)
    context = plan
    if plan is not None:
        partitions = audit_splits(cohort, plan, config=config)
        checks.extend(
            replace(item, instance_id="split:" + item.instance_id)
            for item in partitions.checks
            if not item.rule_id.startswith("NCG-PROV-")
        )
        limitations.extend(partitions.limitations)
        try:
            _validate_context(cohort, config, plan)
        except InputValidationError:
            # Keep every invalid membership finding from the split audit above.
            # Such partitions cannot be used as a valid declared training boundary.
            context = None
            limitations.append(
                "Invalid supplied memberships prevent contextual fit-boundary comparison; "
                "declarations remain unassessable where context is required."
            )
    provenance = check_preprocessing(cohort, config=config, ledger=ledger, plan=context)
    checks.extend(
        replace(item, instance_id="provenance:" + item.instance_id) for item in provenance
    )
    return replace(base, checks=tuple(checks), limitations=tuple(dict.fromkeys(limitations)))
