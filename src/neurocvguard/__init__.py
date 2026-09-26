"""Research-only local cohort/split checks, with lazy public API imports."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

    from neurocvguard.config import AuditConfig
    from neurocvguard.models import (
        AuditReport,
        Cohort,
        ComparisonResult,
        EvaluationResult,
        SplitPlan,
    )

__version__ = "0.1.0"


def compare_designs(results: dict[str, EvaluationResult]) -> ComparisonResult:
    """Compare private records descriptively; see neurocvguard.comparison.compare_designs."""
    from neurocvguard.comparison import compare_designs as compare

    return compare(results)


def evaluate_baseline(cohort: Cohort, plan: SplitPlan, *, config: AuditConfig) -> EvaluationResult:
    """Run classification with optional nested C selection; see evaluation.evaluate_baseline."""
    from neurocvguard.evaluation import evaluate_baseline as evaluate

    return evaluate(cohort, plan, config=config)


def load_config(path: str | Path) -> AuditConfig:
    """Read strict local JSON settings; see neurocvguard.config.load_config."""
    from neurocvguard.config import load_config as load

    return load(path)


def load_cohort(
    metadata: str | Path | pd.DataFrame,
    *,
    config: AuditConfig,
    features: str | Path | pd.DataFrame | None = None,
) -> Cohort:
    """Load strict local tables; see neurocvguard.io.load_cohort for the input contract."""
    from neurocvguard.io import load_cohort as load

    return load(metadata, config=config, features=features)


def audit_cohort(
    cohort: Cohort,
    *,
    config: AuditConfig,
    ledger: dict[str, object] | None = None,
) -> AuditReport:
    """Audit constructed cohort data and declarations without fitting or writing.

    Parameters
    ----------
    cohort : Cohort
        Explicitly keyed in-memory metadata and optional aligned features.
    config : AuditConfig
        Matching roles and diagnostic settings.
    ledger : dict or None, optional
        Strict user-declaration contract; it cannot authenticate historical fitting.

    Returns
    -------
    AuditReport
        Scoped findings and persistent upstream limitations; see neurocvguard.audit.

    Examples
    --------
    ``audit_cohort(cohort, config=config).to_dict()`` returns the public projection.
    """
    from neurocvguard.audit import audit_cohort as audit

    return audit(cohort, config=config, ledger=ledger)


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


def write_report(
    result: AuditReport | EvaluationResult | ComparisonResult,
    *,
    output_dir: str | Path,
    sensitive_details: bool = False,
    overwrite: bool = False,
) -> dict[str, Path]:
    """Write local projected JSON/HTML; see neurocvguard.reporting.write_report.

    Safe defaults omit private evidence and refuse overwriting. Sensitive output
    requires an explicit argument; no operational evaluation or split file is written.
    """
    from neurocvguard.reporting import write_report as write

    return write(
        result, output_dir=output_dir, sensitive_details=sensitive_details, overwrite=overwrite
    )
