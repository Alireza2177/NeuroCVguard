"""Participant inventory and scoped cohort checks; no fitting or file I/O."""

import math
from collections import Counter
from dataclasses import dataclass, field
from numbers import Real

import pandas as pd

from neurocvguard.errors import InputValidationError, UnsupportedDesignError
from neurocvguard.identity import (
    ProtectedComponents,
    _missing,
    _scalar_missing,
    _valid_label,
    _validated_metadata,
    build_components,
)
from neurocvguard.models import CheckResult, CheckStatus, Cohort, EvidenceKind, Severity
from neurocvguard.rules import get_rule
from neurocvguard.serialization import FrozenJSONValue, json_digest


@dataclass(frozen=True)
class ParticipantValues:
    """Sensitive participant-local distinct values and incomplete row counts."""

    participant_id: str = field(repr=False)
    values: tuple[str, ...] = field(repr=False)
    missing_observations: int
    invalid_observations: int


@dataclass(frozen=True)
class FieldInventory:
    """Mapped field coverage and counts before any display suppression.

    Participant counts are nonexclusive for multivalued fields. Missing and
    invalid values are excluded from label counts, never from the cohort.
    """

    role: str
    column: str | None
    available: bool
    missing_observations: int
    invalid_observations: int
    observation_counts: tuple[tuple[str, int], ...] = field(repr=False)
    participant_counts: tuple[tuple[str, int], ...] = field(repr=False)
    participants: tuple[ParticipantValues, ...] = field(repr=False)

    @property
    def complete(self) -> bool:
        """Whether every observation has a usable value for this mapped field."""
        return self.available and not (self.missing_observations or self.invalid_observations)

    @property
    def varying_participants(self) -> tuple[str, ...]:
        """Sensitive IDs with two or more observed values, even if coverage is partial."""
        return tuple(item.participant_id for item in self.participants if len(item.values) > 1)


@dataclass(frozen=True)
class CohortInventory:
    """Sensitive in-memory inventory; not a public report or full design verdict.

    Class counts include only participants with one target and complete target
    coverage. Other participants remain in total counts and field coverage.
    """

    n_observations: int
    n_participants: int
    observations_per_participant: tuple[tuple[str, int], ...] = field(repr=False)
    fields: tuple[FieldInventory, ...] = field(repr=False)
    participant_class_counts: tuple[tuple[str, int], ...] = field(repr=False)
    constant_target_eligible: bool

    def field_for(self, role: str) -> FieldInventory:
        """Return one recorded field without inferring a role.

        Parameters
        ----------
        role : str
            Scalar role name or indexed independence/covariate role.

        Returns
        -------
        FieldInventory
            Immutable sensitive field coverage and values.

        Raises
        ------
        KeyError
            The role is not present in this inventory.

        Examples
        --------
        ``inventory.field_for("session").participants`` is participant-local.
        """
        for item in self.fields:
            if item.role == role:
                return item
        raise KeyError(role)

    def require_constant_target(self) -> None:
        """Enforce this prerequisite only; other planning/evaluation checks remain.

        Raises
        ------
        UnsupportedDesignError
            Targets are missing, malformed, changing, or the cohort is empty.

        Examples
        --------
        ``inventory_cohort(cohort).require_constant_target()`` before a baseline.
        """
        if not self.constant_target_eligible:
            raise UnsupportedDesignError(
                "Constant-target planning/evaluation requires one complete target per participant. "
                "Changing targets may be meaningful; explicitly curate a supported cohort upstream."
            )


def _field_inventory(
    data: pd.DataFrame,
    subjects: tuple[str, ...],
    subject_column: str,
    role: str,
    column: str | None,
) -> FieldInventory:
    available = column is not None and column in data
    labels: dict[str, set[str]] = {subject: set() for subject in subjects}
    missing: Counter[str] = Counter()
    invalid: Counter[str] = Counter()
    observations: Counter[str] = Counter()
    values = data[column].tolist() if available else [None] * len(data)
    for subject, value in zip(data[subject_column], values, strict=True):
        if _missing(value):
            missing[subject] += 1
        elif not _valid_label(value):
            invalid[subject] += 1
        else:
            # _valid_label has established a string without modifying it.
            assert isinstance(value, str)
            labels[subject].add(value)
            observations[value] += 1
    people = Counter(value for values in labels.values() for value in values)
    return FieldInventory(
        role,
        column,
        available,
        sum(missing.values()),
        sum(invalid.values()),
        tuple(sorted(observations.items())),
        tuple(sorted(people.items())),
        tuple(
            ParticipantValues(
                subject, tuple(sorted(labels[subject])), missing[subject], invalid[subject]
            )
            for subject in subjects
        ),
    )


def inventory_cohort(cohort: Cohort) -> CohortInventory:
    """Count people, observations, local sessions, domains and target coverage.

    Parameters
    ----------
    cohort : Cohort
        Already validated in-memory tables with explicit roles. No rows are dropped.

    Returns
    -------
    CohortInventory
        Immutable sensitive inventory, including partial optional-field coverage.

    Raises
    ------
    InputValidationError
        Mandatory identities cannot support trustworthy set-based conclusions.

    Examples
    --------
    ``inventory = inventory_cohort(cohort); inventory.n_participants``

    Notes
    -----
    Session values are distinct within each person. A participant/session pair
    may contain several observations. Repeated visits are not a split violation.
    """
    data = _validated_metadata(cohort)
    columns = cohort.columns
    counts = Counter(data[columns.subject_id])
    subjects = tuple(sorted(counts))
    mapped = [
        (role, getattr(columns, role))
        for role in ("observation_id", "subject_id", "target", "session", "site", "phase")
    ]
    mapped += [(f"independence:{index}", name) for index, name in enumerate(columns.independence)]
    mapped += [
        (f"categorical_covariates:{index}", name)
        for index, name in enumerate(columns.categorical_covariates)
    ]
    fields = tuple(
        _field_inventory(data, subjects, columns.subject_id, role, column)
        for role, column in mapped
    )
    target = next(item for item in fields if item.role == "target")
    classes = Counter(
        item.values[0]
        for item in target.participants
        if len(item.values) == 1 and not (item.missing_observations or item.invalid_observations)
    )
    return CohortInventory(
        len(data),
        len(subjects),
        tuple(sorted(counts.items())),
        fields,
        tuple((label, classes[label]) for label, _ in target.observation_counts),
        bool(subjects) and target.complete and not target.varying_participants,
    )


def _finding(
    number: int,
    scope: str,
    status: CheckStatus,
    evidence: dict[str, FrozenJSONValue],
    *,
    triggered: bool = False,
) -> CheckResult:
    rule = get_rule(f"NCG-COHORT-{number:03d}")
    message = rule.trigger_message if triggered else rule.clear_message
    if status == CheckStatus.NOT_ASSESSABLE and number not in (5, 6):
        message = "Input coverage for this cohort check is incomplete; inspect the field coverage."
    if status == CheckStatus.NOT_APPLICABLE and number == 4:
        message = "Exact-feature equality was not requested."
    return CheckResult(
        instance_id=f"{rule.id}:{scope}",
        rule_id=rule.id,
        status=status,
        severity=rule.trigger_severity if triggered else Severity.INFO,
        evidence_kind=(
            EvidenceKind.UNASSESSABLE
            if status == CheckStatus.NOT_ASSESSABLE
            else rule.evidence_kind
        ),
        scope={"field": scope},
        message=message,
        recommendation=rule.recommendation,
        evidence=evidence,
    )


def inventory_checks(inventory: CohortInventory) -> tuple[CheckResult, ...]:
    """Create inventory findings in stable rule/field order, without split conclusions.

    Parameters
    ----------
    inventory : CohortInventory
        Result from inventory_cohort; internal counts are not privacy-suppressed.

    Returns
    -------
    tuple of CheckResult
        Observed descriptions and explicit unassessable optional-field notices.

    Examples
    --------
    ``checks = inventory_checks(inventory_cohort(cohort))``
    """
    repeated = sum(count > 1 for _, count in inventory.observations_per_participant)
    checks = [
        _finding(
            1,
            "subject_id",
            CheckStatus.PASS if repeated else CheckStatus.NOT_APPLICABLE,
            {
                "repeated_participants": repeated,
                "n_observations": inventory.n_observations,
                "n_participants": inventory.n_participants,
            },
            triggered=bool(repeated),
        )
    ]
    target = inventory.field_for("target")
    varying = len(target.varying_participants)
    target_status = (
        CheckStatus.FAIL
        if varying
        else CheckStatus.PASS
        if inventory.constant_target_eligible
        else CheckStatus.NOT_ASSESSABLE
    )
    checks.append(
        _finding(
            2,
            "target",
            target_status,
            {
                "varying_participants": varying,
                "constant_target_eligible": inventory.constant_target_eligible,
            },
            triggered=bool(varying),
        )
    )
    for role in ("site", "phase"):
        domain = inventory.field_for(role)
        varying = len(domain.varying_participants)
        checks.append(
            _finding(
                3,
                role,
                CheckStatus.PASS if domain.complete or varying else CheckStatus.NOT_ASSESSABLE,
                {"varying_participants": varying, "coverage_complete": domain.complete},
                triggered=bool(varying),
            )
        )
    for item in inventory.fields:
        if item.role not in {"observation_id", "subject_id"} and not item.complete:
            protected = item.role.startswith("independence:")
            checks.append(
                _finding(
                    6 if protected else 5,
                    item.role,
                    CheckStatus.NOT_ASSESSABLE,
                    {
                        "column": item.column,
                        "available": item.available,
                        "missing_observations": item.missing_observations,
                        "invalid_observations": item.invalid_observations,
                    },
                    triggered=True,
                )
            )
    return tuple(sorted(checks, key=lambda check: (check.rule_id, str(check.scope["field"]))))


@dataclass(frozen=True)
class EqualityGroup:
    """Sensitive row membership with exact equality across at least two participants."""

    observation_ids: tuple[str, ...] = field(repr=False)
    participant_ids: tuple[str, ...] = field(repr=False)


@dataclass(frozen=True)
class FeatureEquality:
    """Heuristic equality groups and explicit coverage; no verified identity links."""

    groups: tuple[EqualityGroup, ...] = field(repr=False)
    assessed_observations: int
    skipped_all_missing: int
    reason: str | None


def _feature_digest(vector: tuple[float | None, ...]) -> str:
    return json_digest(vector)


def _numeric_vector(values: tuple[object, ...]) -> tuple[float | None, ...]:
    vector: list[float | None] = []
    for value in values:
        if _scalar_missing(value):
            vector.append(None)
        elif isinstance(value, bool) or not isinstance(value, Real):
            raise InputValidationError(
                "Selected features must contain validated finite numeric scalars or missing values."
            )
        else:
            try:
                number = float(value)
            except (OverflowError, ValueError) as error:
                raise InputValidationError(
                    "Selected numeric feature exceeds finite float range."
                ) from error
            if not math.isfinite(number) or value != number:
                raise InputValidationError(
                    "Selected features must be finite and exactly representable "
                    "as validated floats; "
                    "do not silently round values for equality checks."
                )
            vector.append(0.0 if number == 0 else number)
    return tuple(vector)


def exact_feature_equality(
    cohort: Cohort,
    feature_columns: tuple[str, ...],
    *,
    enabled: bool = True,
) -> FeatureEquality:
    """Find exact selected-vector groups, with hash collision confirmation.

    Parameters
    ----------
    cohort : Cohort
        Already validated and explicitly aligned numeric features and identities.
    feature_columns : tuple of str
        Explicit selected predictor names; never inferred from numeric dtypes.
    enabled : bool, optional
        Disable this optional check explicitly, recording not_requested.

    Returns
    -------
    FeatureEquality
        Sensitive equality groups, assessed count and all-missing skip coverage.

    Raises
    ------
    InputValidationError
        Identities, selected names or numeric cells violate the input boundary.

    Examples
    --------
    ``equality = exact_feature_equality(cohort, ("feature_1", "feature_2"))``

    Notes
    -----
    SHA-256 buckets are further keyed by full canonical numeric tuples, so hash
    collisions cannot imply equality. Dictionary lookup confirms complete tuple
    equality without an all-pairs scan, even if all primary hashes collide.
    Missing positions compare equal, signed zero is canonicalized, all-missing
    vectors are skipped. No rounding, identity merge or row removal is performed.
    """
    if type(enabled) is not bool:
        raise InputValidationError("enabled must be an explicit boolean.")
    if not enabled:
        return FeatureEquality((), 0, 0, "not_requested")
    data = _validated_metadata(cohort)
    features = cohort.features
    if features is None:
        return FeatureEquality((), 0, 0, "features_not_supplied")
    if (
        not isinstance(feature_columns, (tuple, list))
        or not feature_columns
        or any(not isinstance(name, str) or not name for name in feature_columns)
        or len(set(feature_columns)) != len(feature_columns)
    ):
        raise InputValidationError("Select an explicit non-empty list of unique feature columns.")
    roles = cohort.columns.to_dict()
    forbidden = {value for value in roles.values() if isinstance(value, str)}
    forbidden.update(cohort.columns.independence)
    forbidden.update(cohort.columns.categorical_covariates)
    if forbidden.intersection(feature_columns):
        raise InputValidationError(
            "Selected features include a mapped role or protected/covariate field."
        )
    if any(name not in features for name in feature_columns):
        raise InputValidationError(
            "A selected feature column is absent; supply the explicit predictors."
        )
    # No join occurs here: the Cohort constructor already enforces explicit-key alignment.
    buckets: dict[str, dict[tuple[float | None, ...], list[tuple[str, str]]]] = {}
    skipped = 0
    for observation, subject, values in zip(
        cohort.observation_order,
        data[cohort.columns.subject_id],
        features.loc[:, list(feature_columns)].itertuples(index=False, name=None),
        strict=True,
    ):
        vector = _numeric_vector(values)
        if all(value is None for value in vector):
            skipped += 1
            continue
        exact_groups = buckets.setdefault(_feature_digest(vector), {})
        exact_groups.setdefault(vector, []).append((observation, subject))
    groups = []
    for bucket in buckets.values():
        for rows in bucket.values():
            people = tuple(sorted({subject for _, subject in rows}))
            if len(people) > 1:
                groups.append(EqualityGroup(tuple(sorted(key for key, _ in rows)), people))
    assessed = len(data) - skipped
    reason = ("all_missing_vectors" if skipped else "no_observations") if not assessed else None
    return FeatureEquality(
        tuple(sorted(groups, key=lambda group: group.observation_ids)), assessed, skipped, reason
    )


@dataclass(frozen=True)
class CohortAudit:
    """S03 category results, not an overall audit report or design-validity verdict.

    Identity-bearing detail stays in immutable local records; serialize individual
    CheckResult objects through their explicit public/sensitive projections.
    """

    inventory: CohortInventory
    components: ProtectedComponents = field(repr=False)
    feature_equality: FeatureEquality = field(repr=False)
    checks: tuple[CheckResult, ...] = field(repr=False)


def check_cohort(
    cohort: Cohort,
    feature_columns: tuple[str, ...] = (),
    *,
    check_features: bool = True,
) -> CohortAudit:
    """Run only the S03 cohort checks in rule-ID then field order.

    Parameters
    ----------
    cohort : Cohort
        Already constructed validated input; no files, models or partitions are used.
    feature_columns : tuple of str, optional
        Required explicit selection when features are supplied and checked.
    check_features : bool, optional
        Whether to run optional exact-feature equality; absence remains unassessable.

    Returns
    -------
    CohortAudit
        Inventory, observed components, equality and evidence-aware checks. A pass
        is scoped to its check; it cannot establish upstream preprocessing or design validity.

    Raises
    ------
    InputValidationError
        Mandatory identity or feature structure is corrupt.

    Examples
    --------
    ``result = check_cohort(cohort, ("feature_1", "feature_2"))``
    """
    inventory = inventory_cohort(cohort)
    components = build_components(cohort)
    equality = exact_feature_equality(cohort, feature_columns, enabled=check_features)
    checks = list(inventory_checks(inventory))
    equality_status = (
        CheckStatus.NOT_APPLICABLE
        if equality.reason == "not_requested"
        else CheckStatus.NOT_ASSESSABLE
        if equality.reason
        else CheckStatus.FAIL
        if equality.groups
        else CheckStatus.PASS
    )
    checks.append(
        _finding(
            4,
            "features",
            equality_status,
            {
                "cross_participant_groups": len(equality.groups),
                "assessed_observations": equality.assessed_observations,
                "skipped_all_missing": equality.skipped_all_missing,
                "skip_reason": "all_missing_vectors" if equality.skipped_all_missing else None,
                "reason": equality.reason,
            },
            triggered=bool(equality.groups),
        )
    )
    ordered = tuple(sorted(checks, key=lambda check: (check.rule_id, str(check.scope["field"]))))
    return CohortAudit(inventory, components, equality, ordered)
