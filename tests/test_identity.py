"""S03.B protected identity tests with independent graph and ordering oracles."""

import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st

from neurocvguard.checks.cohort import inventory_checks, inventory_cohort
from neurocvguard.config import ColumnMap
from neurocvguard.errors import ConfigurationError, SplitValidationError
from neurocvguard.identity import build_components
from neurocvguard.models import CheckStatus, Cohort, EvidenceKind, Severity


def linked_cohort(rows):
    frame = pd.DataFrame(rows)
    return Cohort(
        frame, None, ColumnMap(independence=("family", "duplicate")), tuple(frame.observation_id)
    )


LINKS = [
    {"observation_id": "a", "subject_id": "A", "family": "f1", "duplicate": "d1"},
    {"observation_id": "b", "subject_id": "B", "family": "f1", "duplicate": "d2"},
    {"observation_id": "c", "subject_id": "C", "family": "f2", "duplicate": "d2"},
    {"observation_id": "d", "subject_id": "D", "family": "f3", "duplicate": "d3"},
]


def test_at_s03_05_transitive_components():
    result = build_components(linked_cohort(LINKS))
    assert tuple(group.participant_ids for group in result.components) == (("A", "B", "C"), ("D",))
    assert result.complete
    result.require_complete()
    assert len(set(result.participant_to_component.values())) == 2


def test_at_s03_06_field_namespaces_and_real_bridges():
    rows = [
        {"observation_id": "a", "subject_id": "A", "family": "X", "duplicate": "d1"},
        {"observation_id": "b", "subject_id": "B", "family": "f2", "duplicate": "X"},
    ]
    assert len(build_components(linked_cohort(rows)).components) == 2
    bridge = {"observation_id": "c", "subject_id": "C", "family": "X", "duplicate": "X"}
    assert len(build_components(linked_cohort([*rows, bridge])).components) == 1


@pytest.mark.parametrize("missing", [None, pd.NA, float("nan"), "", "n/a"])
def test_at_s03_07_missing_values_are_not_links(missing):
    rows = [dict(row, family=missing) for row in LINKS]
    cohort = linked_cohort(rows)
    result = build_components(cohort)
    assert tuple(group.participant_ids for group in result.components) == (
        ("A",),
        ("B", "C"),
        ("D",),
    )
    assert not result.complete
    assert result.coverage[0].missing_observations == 4
    with pytest.raises(SplitValidationError, match="before strict planning/evaluation"):
        result.require_complete()
    check = next(
        item
        for item in inventory_checks(inventory_cohort(cohort))
        if item.rule_id == "NCG-COHORT-006"
    )
    assert (check.status, check.severity, check.evidence_kind) == (
        CheckStatus.NOT_ASSESSABLE,
        Severity.ERROR,
        EvidenceKind.UNASSESSABLE,
    )


def test_at_s03_07_missing_declared_column_blocks():
    result = build_components(
        linked_cohort(
            [{key: value for key, value in row.items() if key != "family"} for row in LINKS]
        )
    )
    assert not result.coverage[0].available
    with pytest.raises(SplitValidationError):
        result.require_complete()


def test_at_s03_08_cross_site_identity_preserved(make_cohort):
    cohort = make_cohort(fixture="cohort_cross_site.tsv")
    result = build_components(cohort)
    assert len(result.components) == 18
    assert len(result.participant_to_component) == 18
    assert any(component.participant_ids == ("sub-001",) for component in result.components)


def test_at_s03_03_sessions_do_not_link_people(clean_cohort):
    assert len(build_components(clean_cohort).components) == 18


def test_at_s03_03_session_cannot_be_global_relationship(clean_cohort):
    cohort = Cohort(
        clean_cohort.metadata,
        None,
        ColumnMap(independence=("session_id",)),
        clean_cohort.observation_order,
    )
    with pytest.raises(ConfigurationError, match="participant-local session"):
        build_components(cohort)


@given(st.permutations(LINKS))
def test_at_s03_11_row_order_invariant(rows):
    assert build_components(linked_cohort(rows)) == build_components(linked_cohort(LINKS))


@given(
    st.lists(
        st.tuples(st.integers(0, 4), st.integers(0, 3), st.integers(0, 3)), min_size=1, max_size=25
    )
)
def test_components_match_independent_graph_oracle(assignments):
    rows = [
        {
            "observation_id": f"o{i}",
            "subject_id": f"p{person}",
            "family": f"v{family}",
            "duplicate": f"v{duplicate}",
        }
        for i, (person, family, duplicate) in enumerate(assignments)
    ]
    # Independent small-fixture adjacency traversal, deliberately not union-find.
    graph = {row["subject_id"]: set() for row in rows}
    for left in rows:
        for right in rows:
            if any(left[field] == right[field] for field in ("family", "duplicate")):
                graph[left["subject_id"]].add(right["subject_id"])
    remaining = set(graph)
    expected = []
    while remaining:
        reached, pending = set(), {min(remaining)}
        while pending:
            person = pending.pop()
            reached.add(person)
            pending.update(graph[person] - reached)
        expected.append(tuple(sorted(reached)))
        remaining -= reached
    actual = build_components(linked_cohort(rows))
    assert tuple(group.participant_ids for group in actual.components) == tuple(sorted(expected))


def test_component_values_and_outputs_not_normalized_or_mutated():
    rows = [
        {"observation_id": f"o{i}", "subject_id": subject, "family": subject, "duplicate": subject}
        for i, subject in enumerate(("001", "1", "NA", "é", "e\u0301"))
    ]
    cohort = linked_cohort(rows)
    before = cohort.metadata
    result = build_components(cohort)
    assert len(result.components) == 5
    with pytest.raises(TypeError):
        result.participant_to_component["001"] = "new"
    pd.testing.assert_frame_equal(cohort.metadata, before)
    assert "component-" not in repr(result)


def test_multiple_values_of_same_participant_bridge_relationship_groups():
    rows = [dict(LINKS[0], family="f2", observation_id="a2"), *LINKS]
    result = build_components(linked_cohort(rows))
    assert result.components[0].participant_ids == ("A", "B", "C")
    assert sum(len(group.participant_ids) for group in result.components) == 4


def test_malformed_relationship_does_not_link_and_explains_block():
    cohort = linked_cohort([dict(row, family=["bad"]) for row in LINKS])
    result = build_components(cohort)
    assert not result.complete and result.coverage[0].invalid_observations == 4
    finding = next(
        check
        for check in inventory_checks(inventory_cohort(cohort))
        if check.rule_id == "NCG-COHORT-006"
    )
    assert "Strict planning/evaluation is blocked" in finding.message
    assert "blocked" in finding.to_dict()["message"]
