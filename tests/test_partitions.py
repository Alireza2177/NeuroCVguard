"""S04.B literal-set oracles for outer partition checks."""

import json
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st

from neurocvguard.checks.partitions import outer_checks
from neurocvguard.config import AuditConfig, ColumnMap, Objective, SplitScheme, StudyConfig
from neurocvguard.models import (
    CheckStatus,
    Cohort,
    EvidenceKind,
    PlanOrigin,
    Severity,
    SplitFold,
    SplitPlan,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"


def plan_fixture(name="splits_clean.json"):
    return SplitPlan.from_json((FIXTURES / name).read_text())


def imported_plan(train, test, *, objective=Objective.UNSEEN_PARTICIPANT, inner=None):
    return SplitPlan(
        "1.0",
        "test-plan",
        PlanOrigin.IMPORTED,
        None,
        objective,
        "imported",
        None,
        (SplitFold("r", "f", tuple(train), tuple(test), inner),),
    )


def objective_config(objective, *, columns=None):
    default = AuditConfig()
    return replace(
        default,
        columns=columns or default.columns,
        study=StudyConfig(objective),
        split=replace(default.split, scheme=SplitScheme.IMPORTED, n_splits=None),
    )


def findings(checks, number):
    return [check for check in checks if check.rule_id == f"NCG-SPLIT-{number:03d}"]


def test_at_s04_01_participant_overlap_without_observation_overlap(clean_cohort):
    checks = outer_checks(
        clean_cohort, plan_fixture("splits_participant_overlap.json"), config=AuditConfig()
    )
    assert all(check.status == CheckStatus.PASS for check in findings(checks, 1))
    assert all(
        check.status == CheckStatus.FAIL
        and check.severity == Severity.ERROR
        and check.evidence["overlap_count"] == 18
        for check in findings(checks, 2)
    )
    assert all(check.evidence["session_overlap_count"] == 0 for check in findings(checks, 2))


def test_at_s04_02_clean_repeated_cohort(clean_cohort):
    checks = outer_checks(clean_cohort, plan_fixture(), config=AuditConfig())
    assert all(
        check.status == CheckStatus.PASS for number in (2, 3) for check in findings(checks, number)
    )
    assert all(
        check.message == "No participant overlap detected in this supplied split."
        for check in findings(checks, 2)
    )


@pytest.mark.parametrize("diagnostic", [False, True])
def test_at_s04_03_observation_overlap_never_waived(clean_cohort, diagnostic):
    plan = plan_fixture()
    fold = plan.folds[0]
    plan = replace(plan, folds=(replace(fold, train_ids=(*fold.train_ids, fold.test_ids[0])),))
    config = replace(
        AuditConfig(),
        evaluation=replace(AuditConfig().evaluation, diagnostic_allow_subject_overlap=diagnostic),
    )
    violation = findings(outer_checks(clean_cohort, plan, config=config), 1)[0]
    assert violation.status == CheckStatus.FAIL and violation.severity == Severity.ERROR
    assert violation.evidence["overlap_count"] == 1


def test_at_s04_04_train_reuse_is_ordinary(clean_cohort):
    plan = plan_fixture()
    assert set(plan.folds[0].train_ids) & set(plan.folds[1].train_ids)
    checks = outer_checks(clean_cohort, plan, config=AuditConfig())
    assert not any(check.status == CheckStatus.FAIL for check in checks)


def test_at_s04_05_sites_allowed_for_unseen_people(clean_cohort):
    domains = findings(outer_checks(clean_cohort, plan_fixture(), config=AuditConfig()), 4)
    assert all(check.status == CheckStatus.NOT_APPLICABLE for check in domains)
    assert all(check.evidence["observed_shared_domain_counts"]["site"] == 3 for check in domains)


@pytest.mark.parametrize("objective", [Objective.UNSEEN_SITE, Objective.UNSEEN_PHASE])
def test_at_s04_06_requested_domain_is_separate(clean_cohort, objective):
    data = clean_cohort.metadata
    columns = clean_cohort.columns
    if objective == Objective.UNSEEN_PHASE:
        data["phase"] = data.site
        columns = replace(columns, phase="phase")
    cohort = Cohort(data, None, columns, clean_cohort.observation_order)
    plan = replace(plan_fixture(), objective=objective)
    checks = outer_checks(cohort, plan, config=objective_config(objective, columns=columns))
    assert all(
        check.status == CheckStatus.FAIL
        and check.severity == Severity.ERROR
        and check.evidence["overlap_count"] == 3
        for check in findings(checks, 4)
    )


def test_at_s04_07_unknown_fold_retains_independent_results(clean_cohort):
    plan = plan_fixture()
    corrupted = replace(plan.folds[0], test_ids=(*plan.folds[0].test_ids, "unknown-sensitive-id"))
    plan = replace(plan, folds=(corrupted, *plan.folds[1:]))
    checks = outer_checks(clean_cohort, plan, config=AuditConfig())
    assert findings(checks, 7)[0].status == CheckStatus.FAIL
    for number in (2, 3, 5, 6):
        assert findings(checks, number)[0].status == CheckStatus.NOT_ASSESSABLE
        assert findings(checks, number)[0].evidence_kind == EvidenceKind.UNASSESSABLE
        assert all(check.status == CheckStatus.PASS for check in findings(checks, number)[1:])
    public = json.dumps([check.to_dict() for check in checks])
    assert "unknown-sensitive-id" not in public


def test_at_s04_08_missing_row_is_coverage_failure(clean_cohort):
    plan = plan_fixture()
    plan = replace(plan, folds=(replace(plan.folds[0], train_ids=plan.folds[0].train_ids[1:]),))
    check = findings(outer_checks(clean_cohort, plan, config=AuditConfig()), 8)[0]
    assert check.status == CheckStatus.FAIL and check.evidence["missing_count"] == 1


def test_at_s04_10_missing_training_class_blocks(clean_cohort):
    frame = clean_cohort.metadata
    train = tuple(frame.loc[frame.diagnosis == "CN", "observation_id"])
    test = tuple(frame.loc[frame.diagnosis == "AD", "observation_id"])
    checks = outer_checks(clean_cohort, imported_plan(train, test), config=AuditConfig())
    training = findings(checks, 5)[0]
    assert training.status == CheckStatus.FAIL and training.severity == Severity.ERROR
    assert training.evidence["class_order"] == ("AD", "CN")
    assert training.evidence["participant_support"] == (("AD", 0), ("CN", 9))
    assert training.evidence["missing_classes"] == ("AD",)


def test_at_s04_11_missing_test_class_is_warning(clean_cohort):
    test = ("obs-001-1", "obs-001-2")
    train = tuple(sorted(set(clean_cohort.observation_order) - set(test)))
    checks = outer_checks(clean_cohort, imported_plan(train, test), config=AuditConfig())
    assert findings(checks, 5)[0].status == CheckStatus.PASS
    missing = findings(checks, 6)[0]
    assert missing.status == CheckStatus.FAIL and missing.severity == Severity.WARNING
    assert missing.evidence["class_complete_metrics_available"] is False
    assert "undefined, not zero" in missing.message


def test_audit_only_overlap_is_warning(clean_cohort):
    plan = replace(plan_fixture("splits_participant_overlap.json"), objective=Objective.AUDIT_ONLY)
    checks = outer_checks(clean_cohort, plan, config=objective_config(Objective.AUDIT_ONLY))
    assert all(
        check.severity == Severity.WARNING
        for number in (2, 3)
        for check in findings(checks, number)
    )


def test_missing_required_domain_and_relationship_are_unassessable(clean_cohort):
    data = clean_cohort.metadata
    data.loc[0, "site"] = None
    columns = replace(clean_cohort.columns, independence=("absent_family",))
    cohort = Cohort(data, None, columns, clean_cohort.observation_order)
    checks = outer_checks(
        cohort,
        replace(plan_fixture(), objective=Objective.UNSEEN_SITE),
        config=objective_config(Objective.UNSEEN_SITE, columns=columns),
    )
    assert all(
        check.status == CheckStatus.NOT_ASSESSABLE
        for check in findings(checks, 4)
        if check.scope["field"] == "site"
    )
    assert all(
        check.status == CheckStatus.FAIL
        for check in findings(checks, 4)
        if check.scope["field"] == "site_observed_overlap"
    )
    assert all(check.status == CheckStatus.NOT_ASSESSABLE for check in findings(checks, 3))
    assert all(check.status == CheckStatus.PASS for check in findings(checks, 2))


@given(st.permutations(range(12)), st.integers(1, 11))
def test_participant_component_sets_match_literal_oracle(order, cut):
    rows = [
        {
            "observation_id": f"o{i}",
            "subject_id": f"p{i // 2}",
            "family": f"family{i // 4}",
            "diagnosis": "A" if i // 2 % 2 else "B",
        }
        for i in range(12)
    ]
    data = pd.DataFrame(rows)
    columns = ColumnMap(independence=("family",))
    cohort = Cohort(data, None, columns, tuple(data.observation_id))
    train = [rows[i]["observation_id"] for i in order[:cut]]
    test = [rows[i]["observation_id"] for i in order[cut:]]
    checks = outer_checks(cohort, imported_plan(train, test), config=AuditConfig(columns=columns))
    expected_people = {rows[i]["subject_id"] for i in order[:cut]} & {
        rows[i]["subject_id"] for i in order[cut:]
    }
    expected_families = {rows[i]["family"] for i in order[:cut]} & {
        rows[i]["family"] for i in order[cut:]
    }
    assert findings(checks, 2)[0].evidence["overlap_count"] == len(expected_people)
    assert findings(checks, 3)[0].evidence["overlap_count"] == len(expected_families)
