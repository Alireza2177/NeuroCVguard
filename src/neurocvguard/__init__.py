"""Research-only local cohort/split checks, with lazy public API imports."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neurocvguard.config import AuditConfig
    from neurocvguard.models import AuditReport, Cohort, SplitPlan

__version__ = "0.1.0"


def make_splits(cohort: Cohort, *, config: AuditConfig) -> SplitPlan:
    """Generate and independently audit deterministic outer assignments.

    Parameters
    ----------
    cohort : Cohort
        Constructed keyed cohort with constant targets and complete protected fields.
    config : AuditConfig
        Explicit supported objective, splitter settings and seed.

    Returns
    -------
    SplitPlan
        Sensitive operational plan with separate in-memory generation_report.

    Raises
    ------
    PlanningError, UnsupportedDesignError, ConfigurationError, InputValidationError
        Unsupported inputs, infeasible design or failed independent audit.

    Examples
    --------
    ``plan = make_splits(cohort, config=config)`` writes no files and fits no model.
    """
    from neurocvguard.splitting import make_splits as make

    return make(cohort, config=config)


def load_split_plan(
    source: str | Path | dict[str, object],
    *,
    cohort: Cohort,
    config: AuditConfig,
) -> SplitPlan:
    """Load and bind supplied assignments; see neurocvguard.io.load_split_plan.

    Parameters
    ----------
    source : str, Path or dict
        Local JSON/TSV path or schema-shaped plan dictionary.
    cohort : Cohort
        Already validated, explicitly keyed in-memory data.
    config : AuditConfig
        Matching objective/roles and input limits.

    Returns
    -------
    SplitPlan
        Bound sensitive operational plan, not a design approval.

    Raises
    ------
    InputValidationError, ConfigurationError, SplitValidationError
        Invalid source structure, identities, mapping, objective or digest.

    Examples
    --------
    ``load_split_plan("plan.json", cohort=cohort, config=config)``
    """
    from neurocvguard.io import load_split_plan as load

    return load(source, cohort=cohort, config=config)


def audit_splits(cohort: Cohort, plan: SplitPlan, *, config: AuditConfig) -> AuditReport:
    """Audit supplied partitions; see neurocvguard.audit.audit_splits.

    Parameters
    ----------
    cohort : Cohort
        Validated in-memory input.
    plan : SplitPlan
        Supplied structural plan record.
    config : AuditConfig
        Matching roles/objective; no diagnostic relaxation of invariants.

    Returns
    -------
    AuditReport
        Scoped checks and separate objective/complete-CV eligibility flags.

    Raises
    ------
    InputValidationError, ConfigurationError, SplitValidationError
        Corrupt identities or incompatible objective, mapping or digest.

    Examples
    --------
    ``audit_splits(cohort, plan, config=config).to_dict()`` is privacy-projected.
    """
    from neurocvguard.audit import audit_splits as audit

    return audit(cohort, plan, config=config)
