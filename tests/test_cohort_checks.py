"""S03.C equality, public interpretation, rule catalog and no-mutation checks."""

import json
from pathlib import Path

import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st

import neurocvguard.checks.cohort as module
from neurocvguard.checks.cohort import check_cohort, exact_feature_equality
from neurocvguard.config import ColumnMap
from neurocvguard.errors import InputValidationError
from neurocvguard.identity import build_components
from neurocvguard.models import CheckStatus, Cohort, EvidenceKind, Severity
from neurocvguard.rules import COHORT_RULES


def feature_cohort(vectors, *, subjects=None):
    keys = [f"o{i}" for i in range(len(vectors))]
    metadata = pd.DataFrame(
        {"observation_id": keys, "subject_id": subjects or [f"p{i}" for i in range(len(vectors))]}
    )
    features = pd.DataFrame(vectors, columns=["f1", "f2"])
    features.insert(0, "observation_id", keys)
    return Cohort(metadata, features, ColumnMap(), tuple(keys))


def test_at_s03_09_equality_is_heuristic_not_identity():
    cohort = feature_cohort([(1.0, 2.0), (1.0, 2.0), (3.0, 4.0)])
    original = cohort.metadata, cohort.features
    components = build_components(cohort)
    result = check_cohort(cohort, ("f1", "f2"))
    assert result.feature_equality.groups[0].observation_ids == ("o0", "o1")
    assert result.feature_equality.groups[0].participant_ids == ("p0", "p1")
    assert len(result.feature_equality.groups) == 1
    assert result.components == components
    assert len(result.components.components) == 3
    assert result.inventory.n_observations == 3
    finding = next(check for check in result.checks if check.rule_id == "NCG-COHORT-004")
    assert (finding.status, finding.severity, finding.evidence_kind) == (
        CheckStatus.FAIL,
        Severity.WARNING,
        EvidenceKind.HEURISTIC,
    )
    assert "does not establish duplicate identity" in finding.message
    public = finding.to_dict()
    assert "heuristic" in public["message"]
    assert "violation" not in public["message"]
    assert public["evidence"] == {}
    assert all(key not in json.dumps(public) for key in ("o0", "o1", "p0", "p1"))
    pd.testing.assert_frame_equal(cohort.metadata, original[0])
    pd.testing.assert_frame_equal(cohort.features, original[1])


def test_at_s03_10_all_missing_vectors_skipped():
    cohort = feature_cohort([(None, float("nan")), (float("nan"), None)])
    result = check_cohort(cohort, ("f1", "f2"))
    assert result.feature_equality.groups == ()
    assert result.feature_equality.assessed_observations == 0
    assert result.feature_equality.skipped_all_missing == 2
    finding = next(check for check in result.checks if check.rule_id == "NCG-COHORT-004")
    assert finding.status == CheckStatus.NOT_ASSESSABLE
    assert finding.evidence["skip_reason"] == "all_missing_vectors"
    assert len(result.components.components) == 2


def test_at_s03_10_partial_missing_and_signed_zero():
    cohort = feature_cohort([(0.0, None), (-0.0, None), (None, 0.0), (None, None), (0.0, 0.0)])
    result = check_cohort(cohort, ("f1", "f2"))
    equality = result.feature_equality
    assert equality.groups[0].observation_ids == ("o0", "o1")
    assert len(equality.groups) == 1
    assert equality.assessed_observations == 4 and equality.skipped_all_missing == 1
    assert (
        next(check for check in result.checks if check.rule_id == "NCG-COHORT-004").evidence[
            "skip_reason"
        ]
        == "all_missing_vectors"
    )


def test_at_s03_12_hash_collisions_require_exact_confirmation(monkeypatch):
    calls = []

    def constant_hash(vector):
        calls.append(vector)
        return "collision"

    monkeypatch.setattr(module, "_feature_digest", constant_hash)
    cohort = feature_cohort([(1.0, 2.0), (1.0, 3.0), (1.0, 2.0)])
    result = exact_feature_equality(cohort, ("f1", "f2"))
    assert len(calls) == 3
    assert tuple(group.observation_ids for group in result.groups) == (("o0", "o2"),)
    # Many unequal primary collisions use complete tuple keys, not pairwise scans.
    many = feature_cohort([(float(i), 0.0) for i in range(3000)])
    assert exact_feature_equality(many, ("f1", "f2")).groups == ()
    assert len(calls) == 3003


@given(st.permutations(range(5)))
def test_equality_memberships_invariant_under_row_permutation(order):
    cohort = feature_cohort([(1.0, None), (1.0, None), (2.0, 3.0), (2.0, 3.0), (0.0, 4.0)])
    data = cohort.metadata.iloc[list(order)]
    features = cohort.features.iloc[list(order)]
    permuted = Cohort(data, features, cohort.columns, tuple(data.observation_id))
    assert exact_feature_equality(permuted, ("f1", "f2")) == exact_feature_equality(
        cohort, ("f1", "f2")
    )


def test_no_rounding_or_same_participant_identity_inference():
    cohort = feature_cohort(
        [(1.0, 2.0), (1.0, 2.0), (1.0000000000000002, 2.0)],
        subjects=["person", "person", "another"],
    )
    assert exact_feature_equality(cohort, ("f1", "f2")).groups == ()
    # An explicit one-feature selection is meaningful; unselected columns are ignored.
    selected = feature_cohort([(1.0, 2.0), (1.0, 3.0)])
    assert len(exact_feature_equality(selected, ("f1",)).groups) == 1


@pytest.mark.parametrize("selection", [(), ("f1", "f1"), ("observation_id",), ("missing",), "f1"])
def test_no_feature_selection_inference(selection):
    with pytest.raises(InputValidationError):
        exact_feature_equality(feature_cohort([(1.0, 2.0)]), selection)


@pytest.mark.parametrize("value", [float("inf"), -float("inf"), "1", True, [1.0]])
def test_unvalidated_feature_cells_fail(value):
    with pytest.raises(InputValidationError):
        exact_feature_equality(feature_cohort([(value, 2.0)]), ("f1", "f2"))


def test_missing_disabled_and_empty_feature_coverage(clean_cohort):
    result = check_cohort(clean_cohort)
    assert result.feature_equality.reason == "features_not_supplied"
    disabled = check_cohort(clean_cohort, check_features=False)
    assert disabled.feature_equality.reason == "not_requested"
    assert next(check for check in disabled.checks if check.rule_id == "NCG-COHORT-004").status == (
        CheckStatus.NOT_APPLICABLE
    )
    with pytest.raises(InputValidationError, match="boolean"):
        check_cohort(clean_cohort, check_features="false")


def test_rule_registry_exactly_matches_normative_catalog():
    expected = [
        row
        for row in json.loads((Path(__file__).parent.parent / "qa/rule_catalog.json").read_text())
        if row["stage"] == "S03"
    ]
    actual = [
        {key: getattr(rule, key) for key in row}
        for rule, row in zip(COHORT_RULES, expected, strict=True)
    ]
    assert actual == expected


def test_check_order_public_messages_and_pure_results(clean_cohort, monkeypatch):
    def prohibited(*args, **kwargs):
        raise AssertionError("cohort checks must not read files or use random numbers")

    monkeypatch.setattr(pd, "read_csv", prohibited)
    result = check_cohort(clean_cohort)
    assert result == check_cohort(clean_cohort)
    assert [(check.rule_id, check.scope["field"]) for check in result.checks] == sorted(
        (check.rule_id, check.scope["field"]) for check in result.checks
    )
    repeated = next(check for check in result.checks if check.rule_id == "NCG-COHORT-001")
    assert "evaluate separation in the actual splits" in repeated.to_dict()["message"]
    assert "sub-001" not in repr(result)


def test_documented_synthetic_example():
    document = (Path(__file__).parent.parent / "docs/cohort_checks.md").read_text()
    example = document.split("```python\n", 1)[1].split("```", 1)[0]
    # Execute this repository's fixed example as documentation QA, never user input.
    exec(compile(example, "docs/cohort_checks.md", "exec"), {})


def test_empty_cohort_has_no_constant_target_or_equality_claim():
    data = pd.DataFrame(columns=["observation_id", "subject_id", "diagnosis"])
    features = pd.DataFrame(columns=["observation_id", "f1"])
    result = check_cohort(Cohort(data, features, ColumnMap(), ()), ("f1",))
    assert result.inventory.n_participants == result.inventory.n_observations == 0
    assert not result.inventory.constant_target_eligible
    assert result.feature_equality.reason == "no_observations"


def test_lossy_large_integer_does_not_create_equality():
    cohort = feature_cohort([(2**53, 0), (2**53 + 1, 0)])
    with pytest.raises(InputValidationError, match="do not silently round"):
        exact_feature_equality(cohort, ("f1", "f2"))
