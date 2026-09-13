"""Participant-level categorical association; no inference, fitting or file I/O."""

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.stats.contingency import association, expected_freq

from neurocvguard.checks.cohort import FieldInventory, inventory_cohort
from neurocvguard.config import AuditConfig
from neurocvguard.errors import ConfigurationError, InputValidationError
from neurocvguard.models import CheckResult, CheckStatus, Cohort, EvidenceKind, Severity
from neurocvguard.rules import get_rule
from neurocvguard.serialization import FrozenJSONValue


@dataclass(frozen=True)
class _PairView:
    role: str
    column: str
    target_column: str | None
    records: tuple[tuple[str, str, str], ...] = field(repr=False)
    n_original: int
    n_missing_field: int
    n_missing_target: int
    n_invalid_field: int
    n_invalid_target: int
    n_unstable_field: int
    n_unstable_target: int
    n_field_levels: int
    n_target_levels: int
    reason: str | None

    @property
    def n_complete(self) -> int:
        return len(self.records)


def _pair_view(covariate: FieldInventory, target: FieldInventory) -> _PairView:
    # Match explicit participant keys, not the relative order of two inventories.
    targets = {person.participant_id: person for person in target.participants}
    records = []
    missing_field = missing_target = invalid_field = invalid_target = 0
    unstable_field = unstable_target = 0
    for person in covariate.participants:
        outcome = targets[person.participant_id]
        missing_field += person.missing_observations > 0
        missing_target += outcome.missing_observations > 0
        invalid_field += person.invalid_observations > 0
        invalid_target += outcome.invalid_observations > 0
        unstable_field += len(person.values) > 1
        unstable_target += len(outcome.values) > 1
        if (
            len(person.values) == len(outcome.values) == 1
            and not (person.missing_observations or outcome.missing_observations)
            and not (person.invalid_observations or outcome.invalid_observations)
        ):
            records.append((person.participant_id, person.values[0], outcome.values[0]))
    reason = (
        "unstable_within_participant"
        if unstable_field or unstable_target
        else "invalid_values"
        if invalid_field or invalid_target
        else "missing_field"
        if not covariate.available
        else "missing_target"
        if not target.available
        else "no_complete_pairs"
        if not records
        else "too_many_categories"
        if max(len(covariate.observation_counts), len(target.observation_counts)) > 100
        else None
    )
    assert covariate.column is not None  # Only explicitly mapped fields are requested.
    return _PairView(
        covariate.role,
        covariate.column,
        target.column,
        tuple(sorted(records)),
        len(covariate.participants),
        missing_field,
        missing_target,
        invalid_field,
        invalid_target,
        unstable_field,
        unstable_target,
        len(covariate.observation_counts),
        len(target.observation_counts),
        reason,
    )


def _pair_views(cohort: Cohort, config: AuditConfig) -> tuple[_PairView, ...]:
    if cohort.columns != config.columns:
        raise ConfigurationError(
            "Cohort roles differ from config.columns; use the matching mapping."
        )
    inventory = inventory_cohort(cohort)
    target = inventory.field_for("target")
    fields = [
        item
        for item in inventory.fields
        if item.column is not None
        and (item.role in {"site", "phase"} or item.role.startswith("categorical_covariates:"))
    ]
    return tuple(_pair_view(item, target) for item in fields)


@dataclass(frozen=True)
class _Statistic:
    row_levels: tuple[str, ...] = field(repr=False)
    target_levels: tuple[str, ...] = field(repr=False)
    counts: tuple[tuple[int, ...], ...] | None = field(repr=False)
    expected: tuple[tuple[float, ...], ...] | None = field(repr=False)
    value: float | None
    reason: str | None
    n: int
    sparse_observed_cells: int | None
    sparse_expected_cells: int | None


def _statistic(pair: _PairView, min_cell_count: int) -> _Statistic:
    if pair.reason is not None:
        return _Statistic((), (), None, None, None, pair.reason, 0, None, None)
    rows = tuple(sorted({covariate for _, covariate, _ in pair.records}))
    targets = tuple(sorted({target for _, _, target in pair.records}))
    row_indices = {level: index for index, level in enumerate(rows)}
    target_indices = {level: index for index, level in enumerate(targets)}
    table = np.zeros((len(rows), len(targets)), dtype=np.int64)
    for _, covariate, target in pair.records:
        table[row_indices[covariate], target_indices[target]] += 1
    # Levels come only from complete observed records: zero marginal levels are
    # absent, but the full Cartesian table retains observed zero cells.
    expected = np.asarray(expected_freq(table), dtype=float)
    if not np.isfinite(expected).all():
        raise InputValidationError("Non-finite expected counts; investigate association inputs.")
    reason = "constant_variable" if min(table.shape) < 2 else None
    value = None
    if reason is None:
        value = float(association(table, method="cramer", correction=False))
        if not math.isfinite(value):
            raise InputValidationError("Non-finite Cramer's V; investigate association inputs.")
    return _Statistic(
        rows,
        targets,
        tuple(tuple(int(cell) for cell in row) for row in table),
        tuple(tuple(float(cell) for cell in row) for row in expected),
        value,
        reason,
        pair.n_complete,
        int(np.count_nonzero(table < min_cell_count)),
        int(np.count_nonzero(expected < min_cell_count)),
    )


def _evidence(
    pair: _PairView, result: _Statistic, config: AuditConfig
) -> dict[str, FrozenJSONValue]:
    return {
        "counting_unit": "participant",
        "field_column": pair.column,
        "target_column": pair.target_column,
        "objective": config.study.objective.value,
        "n_original": pair.n_original,
        "n_complete": pair.n_complete,
        "n_excluded": pair.n_original - pair.n_complete,
        "n_in_table": result.n,
        "missing_field_participants": pair.n_missing_field,
        "missing_target_participants": pair.n_missing_target,
        "invalid_field_participants": pair.n_invalid_field,
        "invalid_target_participants": pair.n_invalid_target,
        "unstable_field_participants": pair.n_unstable_field,
        "unstable_target_participants": pair.n_unstable_target,
        "observed_field_levels": pair.n_field_levels,
        "observed_target_levels": pair.n_target_levels,
        "row_levels": result.row_levels,
        "target_levels": result.target_levels,
        "table": result.counts,
        "expected_counts": result.expected,
        "statistic": {"value": result.value, "reason": result.reason, "n": result.n},
        "estimator": "Cramer's V; uncorrected Pearson chi-square; correction=False",
        "review_threshold": config.association.review_threshold,
        "min_cell_count": config.association.min_cell_count,
        "sparse_observed_cells": result.sparse_observed_cells,
        "sparse_expected_cells": result.sparse_expected_cells,
        "interpretation": "Descriptive participant counts, not independent-sample inference. "
        "Association is not proof of causal confounding or model shortcut use.",
    }


def check_associations(cohort: Cohort, *, config: AuditConfig) -> tuple[CheckResult, ...]:
    """Describe acquisition/target association once per participant for each mapped pair.

    Parameters
    ----------
    cohort : Cohort
        Constructed keyed metadata. Site, phase and explicitly mapped categorical
        covariates are assessed against the target; features are not used.
    config : AuditConfig
        Matching column roles and explicit review/sparse-count thresholds.

    Returns
    -------
    tuple of CheckResult
        Stable scoped checks with sensitive table/support evidence. Undefined
        statistics are null with reasons. to_dict() omits numeric table details;
        to_dict(sensitive_details=True) retains the original local evidence.

    Raises
    ------
    ConfigurationError, InputValidationError
        Invalid identity/mapping or non-finite statistic/expected counts.

    Examples
    --------
    ``checks = check_associations(cohort, config=config)`` performs no fitting or writes.

    Notes
    -----
    Any within-person change blocks that entire pair. A participant with any
    missing visit value is excluded only from the complete-pair diagnostic, with
    counts recorded; the main cohort is unchanged. No p-value or causal verdict
    is returned. Related participants are not asserted to be independent samples.
    """
    checks = []
    for pair in _pair_views(cohort, config):
        result = _statistic(pair, config.association.min_cell_count)
        evidence = _evidence(pair, result, config)
        outcomes = []
        if result.value is None:
            outcomes.append((3, CheckStatus.NOT_ASSESSABLE))
        else:
            outcomes.append(
                (
                    1,
                    CheckStatus.FAIL
                    if result.value >= config.association.review_threshold
                    else CheckStatus.PASS,
                )
            )
        if result.counts is not None:
            outcomes.append(
                (
                    2,
                    CheckStatus.FAIL
                    if result.sparse_observed_cells or result.sparse_expected_cells
                    else CheckStatus.PASS,
                )
            )
        for number, status in outcomes:
            rule = get_rule(f"NCG-ASSOC-{number:03}")
            checks.append(
                CheckResult(
                    f"assoc-{number:03}-{pair.role.replace(':', '-')}",
                    rule.id,
                    status,
                    Severity.INFO if status == CheckStatus.PASS else Severity.WARNING,
                    EvidenceKind.UNASSESSABLE
                    if status == CheckStatus.NOT_ASSESSABLE
                    else EvidenceKind.OBSERVED,
                    {"field": pair.role},
                    rule.clear_message if status == CheckStatus.PASS else rule.trigger_message,
                    rule.recommendation,
                    evidence,
                )
            )
    return tuple(sorted(checks, key=lambda check: (check.rule_id, str(check.scope["field"]))))
