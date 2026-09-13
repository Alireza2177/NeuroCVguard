"""Participant identity boundaries for already constructed, sensitive cohorts."""

import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, cast

import pandas as pd

from neurocvguard.errors import ConfigurationError, InputValidationError, SplitValidationError
from neurocvguard.models import Cohort
from neurocvguard.serialization import json_digest


def _scalar_missing(value: object) -> bool:
    if not pd.api.types.is_scalar(value):
        return False
    # pandas' scalar predicate is not a typing TypeGuard. The runtime guard above
    # prevents array-valued results; this cast is confined to that library boundary.
    return bool(pd.isna(cast(Any, value)))


def _missing(value: object) -> bool:
    return _scalar_missing(value) or (isinstance(value, str) and value in {"", "n/a"})


def _valid_label(value: object) -> bool:
    return (
        isinstance(value, str)
        and not _missing(value)
        and value == value.strip()
        and not any(unicodedata.category(char) == "Cc" for char in value)
    )


def _validated_metadata(cohort: Cohort) -> pd.DataFrame:
    """Refuse corrupt identity units before computing set-based conclusions.

    This is a defensive check at the S03 boundary, not S02 file ingestion.
    """
    data = cohort.metadata
    for role in ("observation_id", "subject_id"):
        column = getattr(cohort.columns, role)
        if column not in data:
            raise InputValidationError(f"Missing {role} column; supply validated identities.")
        invalid = sum(not _valid_label(value) for value in data[column])
        if invalid:
            raise InputValidationError(
                f"Invalid {role} in {invalid} rows; supply non-missing string identities "
                "without surrounding whitespace or control characters."
            )
    if data[cohort.columns.observation_id].duplicated().any():
        raise InputValidationError("Duplicate observation_id; repair keys before cohort checks.")
    return data


@dataclass(frozen=True)
class Component:
    """Sensitive deterministic component identifier and sorted participant membership."""

    component_id: str = field(repr=False)
    participant_ids: tuple[str, ...] = field(repr=False)


@dataclass(frozen=True)
class RelationshipCoverage:
    """Availability and incomplete observations for one declared protected column."""

    column: str
    available: bool
    missing_observations: int
    invalid_observations: int

    @property
    def complete(self) -> bool:
        """Whether this declared relationship is known for every observation."""
        return self.available and not (self.missing_observations or self.invalid_observations)


@dataclass(frozen=True)
class ProtectedComponents:
    """Observed links only; incomplete coverage does not establish independence.

    Component labels and membership mappings are sensitive internal data, not
    anonymized IDs. No public serializer is provided for these records.
    """

    components: tuple[Component, ...] = field(repr=False)
    coverage: tuple[RelationshipCoverage, ...]

    @property
    def complete(self) -> bool:
        """Whether all declared relationships have complete usable values."""
        return all(item.complete for item in self.coverage)

    @property
    def participant_to_component(self) -> Mapping[str, str]:
        """Return a read-only sensitive mapping, owned independently by the caller."""
        return MappingProxyType(
            {
                person: component.component_id
                for component in self.components
                for person in component.participant_ids
            }
        )

    def require_complete(self) -> None:
        """Refuse strict planning/evaluation with unknown protected relationships.

        Raises
        ------
        SplitValidationError
            Declared relationship coverage is incomplete; no implicit waiver exists.

        Examples
        --------
        ``build_components(cohort).require_complete()`` before strict planning.
        """
        if not self.complete:
            raise SplitValidationError(
                "Protected relationship coverage is incomplete; resolve the declared fields "
                "before strict planning/evaluation. Unknown values are not independent groups."
            )


class _UnionFind:
    def __init__(self, participants: tuple[str, ...]) -> None:
        self.parent = {person: person for person in participants}
        self.size = dict.fromkeys(participants, 1)

    def find(self, person: str) -> str:
        while self.parent[person] != person:
            self.parent[person] = self.parent[self.parent[person]]
            person = self.parent[person]
        return person

    def union(self, left: str, right: str) -> None:
        left, right = self.find(left), self.find(right)
        if left == right:
            return
        if self.size[left] < self.size[right]:
            left, right = right, left
        self.parent[right] = left
        self.size[left] += self.size[right]


def build_components(cohort: Cohort) -> ProtectedComponents:
    """Union participants sharing any non-missing declared relationship value.

    Parameters
    ----------
    cohort : Cohort
        Already constructed cohort with explicit independence columns.

    Returns
    -------
    ProtectedComponents
        Immutable memberships sorted by participant IDs and partial coverage.

    Raises
    ------
    InputValidationError
        Mandatory identity units are malformed.
    ConfigurationError
        A participant-local session column is declared as a global relationship key.

    Examples
    --------
    ``components = build_components(cohort); components.require_complete()``

    Notes
    -----
    Field namespaces are distinct. Sessions never add global identity links;
    domains do not add links unless explicitly declared protected relationships.
    Feature equality never adds links. Missing/invalid values block strict use.
    SHA-256 labels encode canonical membership; they are not anonymization.
    """
    data = _validated_metadata(cohort)
    if cohort.columns.session in cohort.columns.independence:
        raise ConfigurationError(
            "A participant-local session column cannot be a global protected relationship. "
            "Supply an explicitly scoped relationship column instead."
        )
    subject_column = cohort.columns.subject_id
    participants = tuple(sorted(set(data[subject_column])))
    groups = _UnionFind(participants)
    owners: dict[tuple[str, str], str] = {}
    coverage = []
    for column in cohort.columns.independence:
        available = column in data
        missing = invalid = 0
        values = data[column].tolist() if available else [None] * len(data)
        for person, value in zip(data[subject_column], values, strict=True):
            if _missing(value):
                missing += 1
            elif not _valid_label(value):
                invalid += 1
            else:
                assert isinstance(value, str)
                key = (column, value)
                if key in owners:
                    groups.union(person, owners[key])
                else:
                    owners[key] = person
        coverage.append(RelationshipCoverage(column, available, missing, invalid))
    memberships: dict[str, list[str]] = {}
    for person in participants:
        memberships.setdefault(groups.find(person), []).append(person)
    ordered = sorted(tuple(members) for members in memberships.values())
    return ProtectedComponents(
        tuple(Component("component-" + json_digest(members), members) for members in ordered),
        tuple(coverage),
    )
