"""S03.A known-answer inventory and scientific scope checks."""

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pandas as pd
import pytest

from neurocvguard.checks.cohort import inventory_checks, inventory_cohort
from neurocvguard.errors import InputValidationError, UnsupportedDesignError
from neurocvguard.models import CheckStatus, EvidenceKind, Severity


def test_at_s03_01_people_and_observations(clean_cohort):
    inventory = inventory_cohort(clean_cohort)
    assert inventory.n_participants == 18
    assert inventory.n_observations == 36
    assert {count for _, count in inventory.observations_per_participant} == {2}
    assert inventory.field_for("target").observation_counts == (("AD", 18), ("CN", 18))
    assert inventory.participant_class_counts == (("AD", 9), ("CN", 9))
    assert len(inventory.field_for("site").observation_counts) == 3
    assert inventory.constant_target_eligible
    inventory.require_constant_target()


def test_at_s03_02_repetition_is_informational(clean_cohort):
    checks = inventory_checks(inventory_cohort(clean_cohort))
    repeated = next(check for check in checks if check.rule_id == "NCG-COHORT-001")
    assert repeated.status == CheckStatus.PASS
    assert repeated.severity == Severity.INFO
    assert repeated.evidence_kind == EvidenceKind.OBSERVED
    assert "evaluate separation in the actual splits" in repeated.message
    assert not any(check.status == CheckStatus.FAIL for check in checks)
    assert not any(check.rule_id.startswith("NCG-SPLIT") for check in checks)
    # Independent known-answer assertion, not a production S04 partition audit.
    plan = json.loads((Path(__file__).parent.parent / "fixtures/splits_clean.json").read_text())
    subjects = dict(
        zip(clean_cohort.observation_order, clean_cohort.metadata.subject_id, strict=True)
    )
    for fold in plan["folds"]:
        assert {subjects[key] for key in fold["train_ids"]}.isdisjoint(
            {subjects[key] for key in fold["test_ids"]}
        )


def test_at_s03_03_sessions_are_participant_local(clean_cohort, make_cohort):
    inventory = inventory_cohort(clean_cohort)
    sessions = inventory.field_for("session")
    assert len(sessions.participants) == 18
    assert all(item.values == ("ses-01", "ses-02") for item in sessions.participants)
    rows = clean_cohort.metadata.to_dict("records")
    rows[1]["session_id"] = "ses-01"
    changed = inventory_cohort(make_cohort(rows))
    assert changed.n_participants == 18 and changed.n_observations == 36
    assert changed.field_for("session").participants[0].values == ("ses-01",)
    assert not any(check.status == CheckStatus.FAIL for check in inventory_checks(changed))


def test_at_s03_04_target_variation_not_relabeling(make_cohort):
    cohort = make_cohort(fixture="cohort_changing_target.tsv")
    original = cohort.metadata
    inventory = inventory_cohort(cohort)
    assert inventory.field_for("target").varying_participants == ("sub-001",)
    assert sum(count for _, count in inventory.participant_class_counts) == 17
    assert not inventory.constant_target_eligible
    with pytest.raises(UnsupportedDesignError, match="Changing targets may be meaningful"):
        inventory.require_constant_target()
    check = next(item for item in inventory_checks(inventory) if item.rule_id == "NCG-COHORT-002")
    assert check.status == CheckStatus.FAIL and check.severity == Severity.WARNING
    assert "may be meaningful" in check.message
    pd.testing.assert_frame_equal(cohort.metadata, original)


def test_at_s03_08_cross_site_inventory(make_cohort):
    inventory = inventory_cohort(make_cohort(fixture="cohort_cross_site.tsv"))
    assert inventory.n_participants == 18
    assert inventory.field_for("site").varying_participants == ("sub-001",)
    check = next(
        item
        for item in inventory_checks(inventory)
        if item.rule_id == "NCG-COHORT-003" and item.scope["field"] == "site"
    )
    assert check.status == CheckStatus.PASS and check.severity == Severity.INFO
    assert "preserving participant identity" in check.message


def test_missing_and_malformed_optional_fields_keep_independent_counts(make_cohort):
    cohort = make_cohort(
        [
            {"observation_id": "o1", "subject_id": "p1", "diagnosis": "CN", "site": 123},
            {"observation_id": "o2", "subject_id": "p1", "diagnosis": None, "site": "s"},
        ]
    )
    inventory = inventory_cohort(cohort)
    assert (inventory.n_observations, inventory.n_participants) == (2, 1)
    assert inventory.field_for("site").invalid_observations == 1
    assert inventory.field_for("target").missing_observations == 1
    assert inventory.participant_class_counts == (("CN", 0),)
    assert not inventory.field_for("session").available
    assert not inventory.constant_target_eligible
    checks = inventory_checks(inventory)
    gaps = [check for check in checks if check.rule_id == "NCG-COHORT-005"]
    assert {check.scope["field"] for check in gaps} == {"site", "target", "session", "phase"}
    assert all(
        check.status == CheckStatus.NOT_ASSESSABLE
        and check.evidence_kind == EvidenceKind.UNASSESSABLE
        for check in gaps
    )


@pytest.mark.parametrize("subject", [None, "", " person", "person\n", 1, ["person"]])
def test_corrupt_identity_stops_conclusions(make_cohort, subject):
    cohort = make_cohort([{"observation_id": "o1", "subject_id": subject}])
    with pytest.raises(InputValidationError, match="Invalid subject_id in 1 rows"):
        inventory_cohort(cohort)


def test_inventory_owns_immutable_results(clean_cohort):
    original = clean_cohort.metadata
    inventory = inventory_cohort(clean_cohort)
    with pytest.raises(FrozenInstanceError):
        inventory.n_participants = 0
    pd.testing.assert_frame_equal(clean_cohort.metadata, original)
    assert "sub-001" not in repr(inventory)
