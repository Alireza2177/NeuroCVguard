"""Independent literal-membership audits; never generate or repair a partition."""

from collections import Counter
from dataclasses import dataclass

from neurocvguard.checks.cohort import CohortInventory, inventory_cohort
from neurocvguard.config import AuditConfig, Objective
from neurocvguard.identity import ProtectedComponents, _valid_label, build_components
from neurocvguard.io import _plan_context
from neurocvguard.models import (
    CheckResult,
    CheckStatus,
    Cohort,
    EvidenceKind,
    Severity,
    SplitFold,
    SplitPlan,
)
from neurocvguard.serialization import FrozenJSONValue, json_digest


@dataclass(frozen=True)
class _Context:
    inventory: CohortInventory
    components: ProtectedComponents
    people: dict[str, str]
    labels: dict[str, dict[str, str | None]]
    classes: tuple[str, ...]
    targets: dict[str, str]


def _context(cohort: Cohort) -> _Context:
    inventory = inventory_cohort(cohort)
    data = cohort.metadata
    people = dict(zip(cohort.observation_order, data[cohort.columns.subject_id], strict=True))
    labels = {}
    for role in ("session", "site", "phase"):
        column = getattr(cohort.columns, role)
        values = data[column].tolist() if column in data else [None] * len(data)
        labels[role] = {
            key: value if _valid_label(value) else None
            for key, value in zip(cohort.observation_order, values, strict=True)
        }
    target = inventory.field_for("target")
    targets = {
        item.participant_id: item.values[0]
        for item in target.participants
        if len(item.values) == 1 and not (item.missing_observations or item.invalid_observations)
    }
    return _Context(
        inventory,
        build_components(cohort),
        people,
        labels,
        tuple(label for label, _ in target.observation_counts),
        targets,
    )


def _finding(
    number: int,
    scope: dict[str, str | int | None],
    status: CheckStatus,
    message: str,
    evidence: dict[str, FrozenJSONValue],
    *,
    severity: Severity = Severity.ERROR,
) -> CheckResult:
    rule = f"NCG-SPLIT-{number:03d}"
    return CheckResult(
        instance_id="split-" + json_digest({"rule": rule, "scope": scope}),
        rule_id=rule,
        status=status,
        severity=severity
        if status in (CheckStatus.FAIL, CheckStatus.NOT_ASSESSABLE)
        else Severity.INFO,
        evidence_kind=EvidenceKind.UNASSESSABLE
        if status == CheckStatus.NOT_ASSESSABLE
        else EvidenceKind.OBSERVED,
        scope=scope,
        message=message,
        recommendation="Review the supplied assignments and explicit objective; "
        "correct the source plan without dropping, relabeling or automatically repairing rows.",
        evidence=evidence,
    )


def _status(failed: bool) -> CheckStatus:
    return CheckStatus.FAIL if failed else CheckStatus.PASS


def _identity_checks(
    context: _Context,
    train: set[str],
    test: set[str],
    scope: dict[str, str | int | None],
    objective: Objective,
) -> list[CheckResult]:
    train_people = {context.people[key] for key in train}
    test_people = {context.people[key] for key in test}
    overlap = train_people & test_people
    severity = Severity.WARNING if objective == Objective.AUDIT_ONLY else Severity.ERROR
    sessions = context.labels["session"]
    train_sessions = {
        (context.people[key], sessions[key]) for key in train if sessions[key] is not None
    }
    test_sessions = {
        (context.people[key], sessions[key]) for key in test if sessions[key] is not None
    }
    checks = [
        _finding(
            2,
            {**scope, "field": "subject_id"},
            _status(bool(overlap)),
            "Participant overlap detected in this supplied split."
            if overlap
            else "No participant overlap detected in this supplied split.",
            {
                "overlap_count": len(overlap),
                "participant_ids": tuple(sorted(overlap)),
                "train_participants": len(train_people),
                "test_participants": len(test_people),
                "session_overlap_count": len(train_sessions & test_sessions),
                "missing_session_observations": sum(sessions[key] is None for key in train | test),
            },
            severity=severity,
        )
    ]
    components = context.components.participant_to_component
    shared = {components[person] for person in train_people} & {
        components[person] for person in test_people
    }
    complete = context.components.complete
    status = _status(bool(shared)) if shared or complete else CheckStatus.NOT_ASSESSABLE
    checks.append(
        _finding(
            3,
            {**scope, "field": "component"},
            status,
            "Protected components cross this split."
            if shared
            else "No protected component overlap detected."
            if complete
            else "Protected relationship coverage is incomplete; separation is unassessable.",
            {
                "overlap_count": len(shared),
                "component_ids": tuple(sorted(shared)),
                "relationship_coverage_complete": complete,
            },
            severity=severity,
        )
    )
    if shared and not complete:
        checks.append(
            _finding(
                3,
                {**scope, "field": "independence"},
                CheckStatus.NOT_ASSESSABLE,
                "Known overlap was observed, but additional protected relationships are unknown.",
                {"relationship_coverage_complete": False},
            )
        )
    return checks


def _class_checks(
    context: _Context,
    train: set[str],
    test: set[str],
    scope: dict[str, str | int | None],
) -> list[CheckResult]:
    checks = []
    for number, side, keys in ((5, "train", train), (6, "test", test)):
        valid_targets = context.inventory.constant_target_eligible
        counts = Counter(
            context.targets[person]
            for person in {context.people[key] for key in keys}
            if person in context.targets
        )
        missing = tuple(label for label in context.classes if counts[label] == 0)
        failed = bool(missing) or (number == 5 and len(context.classes) < 2)
        status = _status(failed) if valid_targets else CheckStatus.NOT_ASSESSABLE
        message = (
            "Classification requires complete constant participant targets; no labels "
            "were selected "
            "from changing or missing observations."
            if not valid_targets
            else "Training lacks the full requested class space; evaluation is blocked "
            "for this fold."
            if number == 5 and failed
            else "Test lacks a global class; class-complete metrics are undefined, not zero."
            if failed
            else "All global classes are represented in this partition."
        )
        checks.append(
            _finding(
                number,
                {**scope, "field": side + "_classes"},
                status,
                message,
                {
                    "class_order": context.classes,
                    "participant_support": tuple(
                        (label, counts[label]) for label in context.classes
                    ),
                    "missing_classes": missing,
                    "constant_target_eligible": valid_targets,
                    "class_complete_metrics_available": valid_targets and not missing,
                },
                severity=Severity.ERROR if number == 5 else Severity.WARNING,
            )
        )
    return checks


def _domain_check(
    context: _Context,
    train: set[str],
    test: set[str],
    scope: dict[str, str | int | None],
    objective: Objective,
) -> CheckResult:
    role = {Objective.UNSEEN_SITE: "site", Objective.UNSEEN_PHASE: "phase"}.get(objective)
    if role is None:
        shared = {}
        for name in ("site", "phase"):
            values = context.labels[name]
            shared[name] = len(
                {values[key] for key in train if values[key] is not None}
                & {values[key] for key in test if values[key] is not None}
            )
        return _finding(
            4,
            {**scope, "field": "domain"},
            CheckStatus.NOT_APPLICABLE,
            "Domain separation is not required by this objective; shared sites are not leakage.",
            {"required": False, "observed_shared_domain_counts": shared},
        )
    values = context.labels[role]
    missing = sum(values[key] is None for key in train | test)
    shared_values = {values[key] for key in train if values[key] is not None} & {
        values[key] for key in test if values[key] is not None
    }
    # Missing domains prevent a complete assessment; observed overlap is still retained as evidence.
    status = CheckStatus.NOT_ASSESSABLE if missing else _status(bool(shared_values))
    return _finding(
        4,
        {**scope, "field": role},
        status,
        "Required domain values are missing; strict domain evaluation is blocked."
        if missing
        else "The requested held-out domain appears on both sides."
        if shared_values
        else "No overlap detected for the requested held-out domain.",
        {
            "required": True,
            "missing_observations": missing,
            "overlap_count": len(shared_values),
            "domain_labels": tuple(sorted(value for value in shared_values if value is not None)),
        },
    )


def _partition_checks(
    context: _Context,
    train: set[str],
    test: set[str],
    expected: set[str],
    scope: dict[str, str | int | None],
    objective: Objective,
    *,
    inner: bool = False,
) -> list[CheckResult]:
    all_known = set(context.people)
    unknown = (train | test) - all_known
    overlap = train & test
    missing, extra = expected - (train | test), (train | test) - expected
    checks = [
        _finding(
            7,
            {**scope, "field": "membership"},
            _status(bool(unknown)),
            "Unknown observation IDs prevent trustworthy identity mapping."
            if unknown
            else "All observation memberships refer to explicit cohort keys.",
            {"unknown_count": len(unknown), "unknown_ids": tuple(sorted(unknown))},
        )
    ]
    if inner:
        checks.append(
            _finding(
                10,
                {**scope, "field": "partition"},
                _status(bool(overlap or missing or extra)),
                "Inner train/validation must be disjoint and cover exactly outer training.",
                {
                    "observation_overlap_count": len(overlap),
                    "missing_count": len(missing),
                    "extra_count": len(extra),
                },
            )
        )
    else:
        checks.extend(
            [
                _finding(
                    1,
                    {**scope, "field": "observation_id"},
                    _status(bool(overlap)),
                    "Observation train/test overlap is invalid, including diagnostic runs."
                    if overlap
                    else "No observation train/test overlap detected.",
                    {"overlap_count": len(overlap), "observation_ids": tuple(sorted(overlap))},
                ),
                _finding(
                    8,
                    {**scope, "field": "coverage"},
                    _status(bool(missing or extra)),
                    "Outer train and test must jointly cover the complete supplied cohort.",
                    {
                        "missing_count": len(missing),
                        "extra_count": len(extra),
                        "missing_ids": tuple(sorted(missing)),
                        "extra_ids": tuple(sorted(extra)),
                    },
                ),
            ]
        )
    if unknown:
        for number, field in (
            (2, "subject_id"),
            (3, "component"),
            (4, "domain"),
            (5, "train_classes"),
            (6, "test_classes"),
        ):
            checks.append(
                _finding(
                    number,
                    {**scope, "field": field},
                    CheckStatus.NOT_ASSESSABLE,
                    "Unknown observation membership blocks this scoped check; no partial "
                    "join was used.",
                    {"reason": "unknown_observation_membership"},
                )
            )
    else:
        checks.extend(_identity_checks(context, train, test, scope, objective))
        checks.extend(_class_checks(context, train, test, scope))
        domain = _domain_check(context, train, test, scope, objective)
        checks.append(domain)
        observed_overlap = domain.evidence.get("overlap_count")
        if (
            domain.status == CheckStatus.NOT_ASSESSABLE
            and isinstance(observed_overlap, int)
            and observed_overlap
        ):
            checks.append(
                _finding(
                    4,
                    {**scope, "field": str(domain.scope["field"]) + "_observed_overlap"},
                    CheckStatus.FAIL,
                    "Known domain overlap is observed despite incomplete domain coverage.",
                    {"overlap_count": observed_overlap},
                )
            )
    return checks


def outer_checks(
    cohort: Cohort, plan: SplitPlan, *, config: AuditConfig
) -> tuple[CheckResult, ...]:
    """Audit independent outer-fold invariants without interpreting across-fold train reuse.

    Parameters
    ----------
    cohort : Cohort
        Validated keyed cohort, including declared protected relationships.
    plan : SplitPlan
        Structurally valid plan; unknown members produce scoped failures.
    config : AuditConfig
        Matching objective and role mapping. Diagnostic settings waive no audit invariant.

    Returns
    -------
    tuple of CheckResult
        All meaningful scoped checks. Internal evidence remains sensitive until projected.

    Raises
    ------
    SplitValidationError, ConfigurationError, InputValidationError
        Global structure, objective, metadata binding or identities are invalid.

    Examples
    --------
    ``checks = outer_checks(cohort, plan, config=config)``
    """
    _plan_context(cohort, plan, config)
    context = _context(cohort)
    checks = []
    for fold in plan.folds:
        checks.extend(
            _partition_checks(
                context,
                set(fold.train_ids),
                set(fold.test_ids),
                set(cohort.observation_order),
                {"repeat_id": fold.repeat_id, "fold_id": fold.fold_id},
                config.study.objective,
            )
        )
    return tuple(
        sorted(
            checks,
            key=lambda item: (
                item.rule_id,
                str(item.scope["repeat_id"]),
                str(item.scope["fold_id"]),
                str(item.scope["field"]),
            ),
        )
    )


def _inner_checks(context: _Context, fold: SplitFold, config: AuditConfig) -> list[CheckResult]:
    scope: dict[str, str | int | None] = {"repeat_id": fold.repeat_id, "fold_id": fold.fold_id}
    if not fold.inner_folds:
        return (
            [
                _finding(
                    10,
                    {**scope, "field": "validation_coverage"},
                    CheckStatus.NOT_ASSESSABLE,
                    "Tuning was requested but inner assignments were not supplied; no "
                    "splits were generated.",
                    {
                        "inner_objective": "unseen_participant",
                        "reason": "inner_assignments_missing",
                    },
                )
            ]
            if config.evaluation.tune
            else []
        )
    checks = []
    expected = set(fold.train_ids)
    validation_counts: Counter[str] = Counter()
    objective = (
        Objective.AUDIT_ONLY
        if config.study.objective == Objective.AUDIT_ONLY
        else Objective.UNSEEN_PARTICIPANT
    )
    for inner in fold.inner_folds:
        train, validation = set(inner.train_ids), set(inner.validation_ids)
        inner_scope = {**scope, "inner_fold_id": inner.inner_fold_id}
        escaped = (train | validation) - expected
        outer_test = (train | validation) & set(fold.test_ids)
        checks.append(
            _finding(
                9,
                {**inner_scope, "field": "containment"},
                _status(bool(escaped or outer_test)),
                "Every inner membership must stay within outer training and exclude outer test.",
                {
                    "outside_outer_train_count": len(escaped),
                    "outer_test_count": len(outer_test),
                    "escaped_ids": tuple(sorted(escaped)),
                    "inner_objective": objective.value,
                },
            )
        )
        checks.extend(
            _partition_checks(
                context, train, validation, expected, inner_scope, objective, inner=True
            )
        )
        validation_counts.update(validation)
    missing = expected - set(validation_counts)
    extra = set(validation_counts) - expected
    repeated = sum(count != 1 for key, count in validation_counts.items() if key in expected)
    checks.append(
        _finding(
            10,
            {**scope, "field": "validation_coverage"},
            _status(bool(missing or extra or repeated)),
            "Inner validation must cover each outer-training observation exactly once.",
            {
                "missing_count": len(missing),
                "extra_count": len(extra),
                "nonunique_count": repeated,
                "inner_objective": objective.value,
            },
        )
    )
    return checks


def _audit_checks(
    cohort: Cohort,
    plan: SplitPlan,
    config: AuditConfig,
) -> tuple[tuple[CheckResult, ...], CohortInventory]:
    _plan_context(cohort, plan, config)
    context = _context(cohort)
    expected = set(cohort.observation_order)
    checks = []
    repeats: dict[str, list[SplitFold]] = {}
    for fold in plan.folds:
        scope: dict[str, str | int | None] = {"repeat_id": fold.repeat_id, "fold_id": fold.fold_id}
        checks.extend(
            _partition_checks(
                context,
                set(fold.train_ids),
                set(fold.test_ids),
                expected,
                scope,
                config.study.objective,
            )
        )
        checks.extend(_inner_checks(context, fold, config))
        repeats.setdefault(fold.repeat_id, []).append(fold)
    repeat_complete = []
    for repeat, folds in sorted(repeats.items()):
        counts = Counter(key for fold in folds for key in fold.test_ids)
        missing, extra = expected - set(counts), set(counts) - expected
        repeated = sum(count != 1 for key, count in counts.items() if key in expected)
        complete = len(folds) >= 2 and not (missing or extra or repeated)
        repeat_complete.append(complete)
        status = CheckStatus.NOT_APPLICABLE if len(folds) == 1 else _status(not complete)
        checks.append(
            _finding(
                11,
                {"repeat_id": repeat, "field": "complete_cv"},
                status,
                "One-fold holdout is auditable but is not complete CV."
                if len(folds) == 1
                else "Test membership must cover each cohort observation exactly once "
                "within this repeat.",
                {
                    "complete_cv": complete,
                    "n_outer_folds": len(folds),
                    "missing_count": len(missing),
                    "extra_count": len(extra),
                    "nonunique_count": repeated,
                },
                severity=Severity.WARNING,
            )
        )
    complete_cv = len(repeats) == 1 and all(repeat_complete)
    required = {f"NCG-SPLIT-{number:03d}" for number in (1, 2, 3, 4, 5, 7, 8, 9, 10, 11)}
    valid = config.study.objective != Objective.AUDIT_ONLY and not any(
        check.rule_id in required and check.status in (CheckStatus.FAIL, CheckStatus.NOT_ASSESSABLE)
        for check in checks
    )
    evaluation_permitted = valid and complete_cv and context.inventory.constant_target_eligible
    checks.append(
        _finding(
            11,
            {"field": "split_summary"},
            CheckStatus.PASS if complete_cv else CheckStatus.NOT_APPLICABLE,
            "Complete-CV eligibility is separate from objective validity; diagnostics "
            "waive no audit check.",
            {
                "complete_cv": complete_cv,
                "valid_for_objective": valid,
                "evaluation_permitted": evaluation_permitted,
                "n_repeats": len(repeats),
                "n_outer_folds": len(plan.folds),
                "diagnostic_requested": config.evaluation.diagnostic_allow_subject_overlap,
                "class_order": context.classes,
            },
        )
    )
    return tuple(
        sorted(
            checks,
            key=lambda item: (
                item.rule_id,
                str(item.scope.get("repeat_id", "")),
                str(item.scope.get("fold_id", "")),
                str(item.scope.get("inner_fold_id", "")),
                str(item.scope.get("field", "")),
            ),
        )
    ), context.inventory
