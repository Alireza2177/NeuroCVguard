"""Participant-level standard splitters with independent post-generation auditing."""

import warnings
from dataclasses import dataclass, replace
from typing import NoReturn

import numpy as np
import sklearn
from sklearn.model_selection import LeaveOneGroupOut, StratifiedGroupKFold

from neurocvguard import __version__
from neurocvguard.audit import audit_splits
from neurocvguard.checks.cohort import CohortInventory, inventory_cohort
from neurocvguard.config import AuditConfig, Objective, SplitScheme
from neurocvguard.errors import ConfigurationError, PlanningError, UnsupportedDesignError
from neurocvguard.identity import build_components
from neurocvguard.io import cohort_digest
from neurocvguard.models import (
    AuditReport,
    CheckResult,
    CheckStatus,
    Cohort,
    EvidenceKind,
    ReportStatus,
    Severity,
    SplitFold,
    SplitPlan,
)
from neurocvguard.serialization import FrozenJSONValue, json_digest


@dataclass(frozen=True)
class _Participants:
    people: tuple[str, ...]
    targets: tuple[str, ...]
    components: tuple[str, ...]
    observations: dict[str, tuple[str, ...]]
    inventory: CohortInventory


def _check(
    number: int, status: CheckStatus, message: str, evidence: dict[str, FrozenJSONValue]
) -> CheckResult:
    return CheckResult(
        f"plan-{number:03}",
        f"NCG-PLAN-{number:03}",
        status,
        Severity.WARNING
        if number == 3 and status == CheckStatus.FAIL
        else Severity.ERROR
        if status == CheckStatus.FAIL
        else Severity.INFO,
        EvidenceKind.OBSERVED,
        {"field": "generation"},
        message,
        "Review the requested design and available independent units; no rows, labels, "
        "fold counts or seeds are automatically changed.",
        evidence,
    )


def _report(
    cohort: Cohort,
    config: AuditConfig,
    checks: list[CheckResult],
    *,
    audit: AuditReport | None = None,
    blocked: bool = False,
) -> AuditReport:
    checks = [
        replace(
            check,
            evidence={
                **check.evidence,
                "requested_scheme": config.split.scheme.value,
                "requested_seed": config.split.seed,
                "requested_n_splits": config.split.n_splits,
            },
        )
        for check in checks
    ]
    if audit is None:
        inventory = inventory_cohort(cohort)
        audit = AuditReport(
            "1.0",
            __version__,
            "audit",
            config.study.objective,
            ReportStatus.BLOCKED,
            {
                "n_observations": inventory.n_observations,
                "n_participants": inventory.n_participants,
                "supplied_roles": tuple(
                    sorted({f.role.split(":")[0] for f in inventory.fields if f.available})
                ),
                "missing_roles": tuple(
                    sorted({f.role.split(":")[0] for f in inventory.fields if not f.complete})
                ),
            },
            (
                CheckResult(
                    "upstream-unassessable",
                    "NCG-PROV-001",
                    CheckStatus.NOT_ASSESSABLE,
                    Severity.INFO,
                    EvidenceKind.UNASSESSABLE,
                    {},
                    "Upstream preprocessing remains unassessable.",
                    "Document upstream fitting separately.",
                    {},
                ),
            ),
            (),
            {
                "foundation_version": "1.0.0",
                "versions": {},
                "sensitive_details": False,
                "upstream_preprocessing_verified": False,
            },
        )
    return replace(
        audit,
        checks=(*audit.checks, *checks),
        execution_status=ReportStatus.BLOCKED if blocked else audit.execution_status,
        limitations=(
            *audit.limitations,
            "Stratification is approximate under indivisible protected groups.",
            "Generated outer assignments are reproducible for fixed inputs, seed and versions.",
            "Planning computes no model score and does not verify upstream preprocessing.",
        ),
        provenance={
            **audit.provenance,
            "versions": {
                "neurocvguard": __version__,
                "numpy": np.__version__,
                "scikit-learn": sklearn.__version__,
            },
        },
    )


def _refuse(
    message: str,
    cohort: Cohort,
    config: AuditConfig,
    checks: list[CheckResult],
    *,
    audit: AuditReport | None = None,
) -> NoReturn:
    raise PlanningError(message, report=_report(cohort, config, checks, audit=audit, blocked=True))


def _participants(cohort: Cohort, config: AuditConfig) -> _Participants:
    if config.columns != cohort.columns:
        raise ConfigurationError(
            "Cohort roles differ from config.columns; use the matching mapping."
        )
    inventory = inventory_cohort(cohort)
    if not inventory.constant_target_eligible or len(inventory.participant_class_counts) < 2:
        _refuse(
            "Planning requires complete constant participant targets and at least two classes; "
            "review the supported cohort without automatically relabeling observations.",
            cohort,
            config,
            [
                _check(
                    3,
                    CheckStatus.FAIL,
                    "Constant-target classification is infeasible.",
                    {"reason": "constant_target_or_class_count"},
                )
            ],
        )
    components = build_components(cohort)
    if not components.complete:
        _refuse(
            "Protected relationship coverage is incomplete; resolve declared "
            "fields before planning.",
            cohort,
            config,
            [
                CheckResult(
                    "relationships-unassessable",
                    "NCG-SPLIT-003",
                    CheckStatus.NOT_ASSESSABLE,
                    Severity.ERROR,
                    EvidenceKind.UNASSESSABLE,
                    {"field": "independence"},
                    "Protected relationships are incomplete; separation cannot be established.",
                    "Resolve declared relationship coverage before planning.",
                    {"reason": "incomplete_protected_relationships"},
                )
            ],
        )
    target_rows = inventory.field_for("target").participants
    people = tuple(item.participant_id for item in target_rows)
    data = cohort.metadata
    observations: dict[str, list[str]] = {person: [] for person in people}
    for observation, person in zip(
        data[cohort.columns.observation_id], data[cohort.columns.subject_id], strict=True
    ):
        observations[person].append(observation)
    mapping = components.participant_to_component
    return _Participants(
        people,
        tuple(item.values[0] for item in target_rows),
        tuple(mapping[person] for person in people),
        {person: tuple(sorted(ids)) for person, ids in observations.items()},
        inventory,
    )


def _expand(table: _Participants, positions: object) -> tuple[str, ...]:
    # Splitter outputs are integer positions into this explicit canonical participant table.
    indices = np.asarray(positions, dtype=np.intp)
    return tuple(
        sorted(
            observation
            for index in indices
            for observation in table.observations[table.people[int(index)]]
        )
    )


def _subject_folds(
    table: _Participants, cohort: Cohort, config: AuditConfig, checks: list[CheckResult]
) -> tuple[SplitFold, ...]:
    count = config.split.n_splits
    assert count is not None  # Validated subject_kfold config contract.
    groups = len(set(table.components))
    if groups < count:
        checks.append(
            _check(
                1,
                CheckStatus.FAIL,
                "Too few independent groups for the requested folds.",
                {"n_components": groups, "n_splits": count},
            )
        )
        _refuse(
            f"Requested {count} folds but only {groups} independent components are available; "
            "choose an explicitly justified design. No fallback was attempted.",
            cohort,
            config,
            checks,
        )
    supports = tuple(
        (
            label,
            len(
                {
                    group
                    for target, group in zip(table.targets, table.components, strict=True)
                    if target == label
                }
            ),
        )
        for label in sorted(set(table.targets))
    )
    checks.append(
        _check(
            3,
            CheckStatus.FAIL if any(n < count for _, n in supports) else CheckStatus.PASS,
            "Stratification is approximate; actual fold support is recorded "
            "by the independent audit.",
            {
                "class_component_support": supports,
                "n_splits": count,
                "class_component_count_sufficient": all(n >= count for _, n in supports),
                "class_has_fewer_than_two_components": any(n < 2 for _, n in supports),
            },
        )
    )
    splitter = StratifiedGroupKFold(n_splits=count, shuffle=True, random_state=config.split.seed)
    try:
        with warnings.catch_warnings(record=True) as notices:
            positions = list(
                splitter.split(np.zeros((len(table.people), 1)), table.targets, table.components)
            )
        if notices:
            checks[-1] = replace(
                checks[-1], evidence={**checks[-1].evidence, "splitter_warning_count": len(notices)}
            )
    except ValueError:
        _refuse(
            "StratifiedGroupKFold could not allocate this requested participant/class design; "
            "review class support and n_splits. The seed and scheme were not changed.",
            cohort,
            config,
            checks,
        )
    if any(len(train) == 0 or len(test) == 0 for train, test in positions):
        _refuse(
            "The requested grouped allocation produced an empty partition; review group sizes "
            "and the requested design. No alternate seed or splitter was attempted.",
            cohort,
            config,
            checks,
        )
    return tuple(
        SplitFold("0", f"fold-{index:03}", _expand(table, train), _expand(table, test))
        for index, (train, test) in enumerate(positions)
    )


def _domain_folds(
    table: _Participants, cohort: Cohort, config: AuditConfig, checks: list[CheckResult]
) -> tuple[SplitFold, ...]:
    role = "site" if config.split.scheme == SplitScheme.LEAVE_ONE_SITE_OUT else "phase"
    field = table.inventory.field_for(role)
    if not field.complete:
        _refuse(
            f"Required {role} values are missing or invalid; resolve domain "
            f"coverage before planning.",
            cohort,
            config,
            [
                CheckResult(
                    "domain-unassessable",
                    "NCG-SPLIT-004",
                    CheckStatus.NOT_ASSESSABLE,
                    Severity.ERROR,
                    EvidenceKind.UNASSESSABLE,
                    {"field": role},
                    "Required domain coverage is incomplete.",
                    "Supply complete domain metadata.",
                    {
                        "missing_observations": field.missing_observations,
                        "invalid_observations": field.invalid_observations,
                    },
                )
            ],
        )
    component_domains: dict[str, set[str]] = {}
    for person, component in zip(field.participants, table.components, strict=True):
        component_domains.setdefault(component, set()).update(person.values)
    crossing = sum(len(values) != 1 for values in component_domains.values())
    if crossing:
        checks.append(
            _check(
                2,
                CheckStatus.FAIL,
                "Protected components cross the held-out domain.",
                {
                    "role": role,
                    "crossing_components": crossing,
                    "crossing_participants": len(field.varying_participants),
                },
            )
        )
        _refuse(
            f"Strict held-out-{role} planning is infeasible: participants or protected components "
            "cross domains. Review the objective; no observations were removed or relabeled.",
            cohort,
            config,
            checks,
        )
    domains = tuple(person.values[0] for person in field.participants)
    count = len(set(domains))
    if count < 2:
        checks.append(
            _check(
                1,
                CheckStatus.FAIL,
                "At least two held-out domains are required.",
                {"role": role, "n_domains": count},
            )
        )
        _refuse(
            f"At least two distinct {role} domains are required for leave-one-domain-out planning.",
            cohort,
            config,
            checks,
        )
    positions = LeaveOneGroupOut().split(np.zeros((len(table.people), 1)), table.targets, domains)
    return tuple(
        SplitFold("0", f"fold-{index:03}", _expand(table, train), _expand(table, test))
        for index, (train, test) in enumerate(positions)
    )


def make_splits(cohort: Cohort, *, config: AuditConfig) -> SplitPlan:
    """Generate outer folds with standard splitters and independently audit them.

    Parameters
    ----------
    cohort : Cohort
        Validated keyed in-memory metadata, with complete constant participant targets.
    config : AuditConfig
        Explicit objective, compatible scheme, fold count and integer seed.

    Returns
    -------
    SplitPlan
        Bound sensitive assignments. generation_report retains the independent audit,
        feasibility warnings and dependency versions outside the canonical plan schema.

    Raises
    ------
    PlanningError
        Infeasible design or failed independent audit; report holds separate diagnostics.
    ConfigurationError, InputValidationError, UnsupportedDesignError
        Invalid inputs or unsupported generation request. No automatic repair occurs.

    Examples
    --------
    ``plan = make_splits(cohort, config=config)`` performs no fitting or file writing.

    Notes
    -----
    S05 generates outer folds only. Nested tuning generation belongs to S11.
    Reconstructing a plan from JSON does not authenticate generation provenance.
    """
    if (
        config.study.objective == Objective.AUDIT_ONLY
        or config.split.scheme == SplitScheme.IMPORTED
    ):
        raise UnsupportedDesignError(
            "Choose an explicit supported generation objective and scheme; "
            "imported/audit_only does not generate assignments."
        )
    if config.evaluation.tune:
        raise UnsupportedDesignError(
            "make_splits generates outer folds only. Request outer planning with "
            "evaluation.tune=false; evaluate_baseline can derive inner folds with tune=true."
        )
    table = _participants(cohort, config)
    checks: list[CheckResult] = []
    folds = (
        _subject_folds(table, cohort, config, checks)
        if config.split.scheme == SplitScheme.SUBJECT_KFOLD
        else _domain_folds(table, cohort, config, checks)
    )
    payload = {
        "schema_version": "1.0",
        "origin": "generated",
        "cohort_digest": cohort_digest(cohort),
        "objective": config.study.objective.value,
        "scheme": config.split.scheme.value,
        "seed": config.split.seed,
        "folds": [fold._as_dict() for fold in folds],
    }
    plan = SplitPlan.from_dict({**payload, "plan_id": json_digest(payload)})
    audit = audit_splits(cohort, plan, config=config)
    summary = next(
        check.evidence for check in audit.checks if check.scope.get("field") == "split_summary"
    )
    if summary.get("valid_for_objective") is not True or summary.get("complete_cv") is not True:
        failures = sorted(
            {
                check.rule_id
                for check in audit.checks
                if check.status in (CheckStatus.FAIL, CheckStatus.NOT_ASSESSABLE)
                and check.severity == Severity.ERROR
            }
        )
        _refuse(
            "Generated plan failed independent audit (" + ", ".join(failures) + "); "
            "inspect the diagnostic report. No alternate seed or splitter was attempted.",
            cohort,
            config,
            checks,
            audit=audit,
        )
    if not any(check.rule_id == "NCG-PLAN-003" for check in checks):
        checks.append(
            _check(
                3,
                CheckStatus.PASS,
                "Actual class support is recorded in the independent audit.",
                {},
            )
        )
    checks = [
        replace(
            check,
            evidence={
                **check.evidence,
                "scheme": plan.scheme,
                "seed": plan.seed,
                "plan_id": plan.plan_id,
                "cohort_digest": plan.cohort_digest,
            },
        )
        for check in checks
    ]
    object.__setattr__(plan, "generation_report", _report(cohort, config, checks, audit=audit))
    return plan
