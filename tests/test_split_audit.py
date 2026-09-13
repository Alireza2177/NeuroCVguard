"""S04.C nested boundaries, CV semantics and public AuditReport contract."""

import json
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest
from test_partitions import findings, objective_config, plan_fixture

from neurocvguard import audit_splits, load_split_plan
from neurocvguard.config import AuditConfig, Objective
from neurocvguard.errors import SplitValidationError
from neurocvguard.models import AuditReport, CheckStatus, Cohort, InnerFold, ReportStatus, Severity
from neurocvguard.rules import SPLIT_RULES, get_rule


def summary(report):
    return next(
        check.evidence
        for check in report.checks
        if check.rule_id == "NCG-SPLIT-011" and check.scope.get("field") == "split_summary"
    )


def nested_plan(cohort):
    people = dict(zip(cohort.observation_order, cohort.metadata.subject_id, strict=True))
    folds = []
    for fold in plan_fixture().folds:
        ordered = sorted({people[key] for key in fold.train_ids})
        half = set(ordered[: len(ordered) // 2])
        left = tuple(key for key in fold.train_ids if people[key] in half)
        right = tuple(key for key in fold.train_ids if people[key] not in half)
        folds.append(
            replace(fold, inner_folds=(InnerFold("i0", left, right), InnerFold("i1", right, left)))
        )
    return replace(plan_fixture(), folds=tuple(folds))


def test_clean_audit_schema_and_independent_summary(clean_cohort):
    report = audit_splits(clean_cohort, plan_fixture(), config=AuditConfig())
    assert isinstance(report, AuditReport)
    assert summary(report)["valid_for_objective"] is True
    assert summary(report)["complete_cv"] is True
    assert summary(report)["evaluation_permitted"] is True
    assert report.execution_status == ReportStatus.PARTIAL
    assert any(
        check.rule_id == "NCG-PROV-001" and check.status == CheckStatus.NOT_ASSESSABLE
        for check in report.checks
    )
    public = report.to_dict()
    projected = [
        check["evidence"]
        for check in public["checks"]
        if "valid_for_objective" in check["evidence"]
    ]
    assert projected[0]["valid_for_objective"] is True
    assert projected[0]["evaluation_permitted"] is True
    assert AuditReport.from_dict(public).to_dict() == public


def test_at_s04_12_outer_test_in_inner_train(clean_cohort):
    plan = nested_plan(clean_cohort)
    outer = plan.folds[0]
    inner = replace(
        outer.inner_folds[0], train_ids=(*outer.inner_folds[0].train_ids, outer.test_ids[0])
    )
    changed = replace(
        plan, folds=(replace(outer, inner_folds=(inner, outer.inner_folds[1])), *plan.folds[1:])
    )
    report = audit_splits(clean_cohort, changed, config=AuditConfig())
    containment = [
        check for check in findings(report.checks, 9) if check.status == CheckStatus.FAIL
    ]
    assert len(containment) == 1
    assert containment[0].evidence["outer_test_count"] == 1
    assert containment[0].evidence["outside_outer_train_count"] == 1
    assert summary(report)["evaluation_permitted"] is False


def test_at_s04_13_inner_protected_overlap(clean_cohort):
    outer = nested_plan(clean_cohort).folds[0]
    data = clean_cohort.metadata
    data["family"] = data.subject_id
    people = dict(zip(data.observation_id, data.subject_id, strict=True))
    pair = {
        people[outer.inner_folds[0].train_ids[0]],
        people[outer.inner_folds[0].validation_ids[0]],
    }
    data.loc[data.subject_id.isin(pair), "family"] = "shared-family"
    columns = replace(clean_cohort.columns, independence=("family",))
    cohort = Cohort(data, None, columns, clean_cohort.observation_order)
    plan = replace(plan_fixture(), folds=(outer,))
    report = audit_splits(cohort, plan, config=AuditConfig(columns=columns))
    component_checks = findings(report.checks, 3)
    assert all(
        check.status == CheckStatus.FAIL
        for check in component_checks
        if "inner_fold_id" in check.scope
    )
    assert all(
        check.status == CheckStatus.PASS
        for check in component_checks
        if "inner_fold_id" not in check.scope
    )
    assert summary(report)["valid_for_objective"] is False


def test_at_s04_14_holdout_is_auditable_not_complete_cv(clean_cohort):
    plan = replace(plan_fixture(), folds=(plan_fixture().folds[0],))
    report = audit_splits(clean_cohort, plan, config=AuditConfig())
    assert summary(report)["valid_for_objective"] is True
    assert summary(report)["complete_cv"] is False
    assert summary(report)["evaluation_permitted"] is False
    assert not any(check.status == CheckStatus.FAIL for check in report.checks)
    assert all(check.status == CheckStatus.NOT_APPLICABLE for check in findings(report.checks, 11))


def test_at_s04_15_repeated_cv_audited_separately(clean_cohort):
    plan = plan_fixture()
    plan = replace(
        plan, folds=(*plan.folds, *(replace(fold, repeat_id="1") for fold in plan.folds))
    )
    report = audit_splits(clean_cohort, plan, config=AuditConfig())
    coverage = [
        check for check in findings(report.checks, 11) if check.scope.get("field") == "complete_cv"
    ]
    assert len(coverage) == 2 and all(check.evidence["complete_cv"] is True for check in coverage)
    assert summary(report)["n_repeats"] == 2
    assert summary(report)["valid_for_objective"] is True
    assert summary(report)["complete_cv"] is False
    assert summary(report)["evaluation_permitted"] is False
    assert not any(check.status == CheckStatus.FAIL for check in report.checks)


def test_invalid_cv_coverage_does_not_become_holdout_exception(clean_cohort):
    plan = plan_fixture()
    changed = replace(plan, folds=(plan.folds[0], replace(plan.folds[0], fold_id="other")))
    report = audit_splits(clean_cohort, changed, config=AuditConfig())
    assert any(check.status == CheckStatus.FAIL for check in findings(report.checks, 11))
    assert summary(report)["complete_cv"] is False
    assert summary(report)["valid_for_objective"] is False


def test_nested_validation_once_and_correct_inner_objective(clean_cohort):
    plan = nested_plan(clean_cohort)
    report = audit_splits(clean_cohort, plan, config=AuditConfig())
    assert summary(report)["evaluation_permitted"] is True
    fold = plan.folds[0]
    broken = replace(
        fold, inner_folds=(fold.inner_folds[0], replace(fold.inner_folds[0], inner_fold_id="other"))
    )
    failed = audit_splits(
        clean_cohort, replace(plan, folds=(broken, *plan.folds[1:])), config=AuditConfig()
    )
    coverage = [
        check
        for check in findings(failed.checks, 10)
        if check.scope["field"] == "validation_coverage"
    ]
    assert any(
        check.status == CheckStatus.FAIL and check.evidence["nonunique_count"] > 0
        for check in coverage
    )
    domain_plan = replace(plan, objective=Objective.UNSEEN_SITE)
    domain_report = audit_splits(
        clean_cohort, domain_plan, config=objective_config(Objective.UNSEEN_SITE)
    )
    inner_domains = [
        check for check in findings(domain_report.checks, 4) if "inner_fold_id" in check.scope
    ]
    assert all(check.status == CheckStatus.NOT_APPLICABLE for check in inner_domains)
    assert all(
        check.evidence["inner_objective"] == "unseen_participant"
        for check in findings(domain_report.checks, 9)
    )


def test_tuning_without_inner_assignments_is_not_generated(clean_cohort):
    config = replace(AuditConfig(), evaluation=replace(AuditConfig().evaluation, tune=True))
    report = audit_splits(clean_cohort, plan_fixture(), config=config)
    assert all(check.status == CheckStatus.NOT_ASSESSABLE for check in findings(report.checks, 10))
    assert summary(report)["evaluation_permitted"] is False


def test_inner_observation_overlap_and_unknown_member(clean_cohort):
    plan = nested_plan(clean_cohort)
    outer = plan.folds[0]
    inner = outer.inner_folds[0]
    bad_inner = replace(
        inner, train_ids=(*inner.train_ids, inner.validation_ids[0], "private-unknown")
    )
    plan = replace(plan, folds=(replace(outer, inner_folds=(bad_inner, outer.inner_folds[1])),))
    report = audit_splits(clean_cohort, plan, config=AuditConfig())
    assert any(check.status == CheckStatus.FAIL for check in findings(report.checks, 9))
    assert any(
        check.status == CheckStatus.FAIL and check.evidence.get("observation_overlap_count") == 1
        for check in findings(report.checks, 10)
    )
    assert any(check.status == CheckStatus.NOT_ASSESSABLE for check in findings(report.checks, 2))
    assert "private-unknown" not in json.dumps(report.to_dict())


def test_diagnostic_and_audit_only_never_grant_objective_validity(clean_cohort):
    config = replace(
        AuditConfig(),
        evaluation=replace(AuditConfig().evaluation, diagnostic_allow_subject_overlap=True),
    )
    report = audit_splits(
        clean_cohort, plan_fixture("splits_participant_overlap.json"), config=config
    )
    assert summary(report)["valid_for_objective"] is False
    assert summary(report)["evaluation_permitted"] is False
    assert all(check.severity == Severity.ERROR for check in findings(report.checks, 2))
    audit_only = audit_splits(
        clean_cohort,
        replace(plan_fixture(), objective=Objective.AUDIT_ONLY),
        config=objective_config(Objective.AUDIT_ONLY),
    )
    assert summary(audit_only)["valid_for_objective"] is False


def test_digest_mismatch_rejected_by_audit_too(clean_cohort):
    plan = load_split_plan(
        plan_fixture().to_operational_dict(), cohort=clean_cohort, config=AuditConfig()
    )
    data = clean_cohort.metadata
    data.loc[0, "site"] = "changed"
    with pytest.raises(SplitValidationError, match="digest mismatch"):
        audit_splits(
            Cohort(data, None, clean_cohort.columns, clean_cohort.observation_order),
            plan,
            config=AuditConfig(),
        )


def test_private_details_and_inputs_preserved(clean_cohort):
    plan = plan_fixture("splits_participant_overlap.json")
    before = plan.to_operational_dict()
    data = clean_cohort.metadata
    report = audit_splits(clean_cohort, plan, config=AuditConfig())
    public, private = report.to_dict(), report.to_dict(sensitive_details=True)
    assert "sub-001" not in json.dumps(public) and "sub-001" in json.dumps(private)
    assert "component-" not in json.dumps(public)
    assert plan.to_operational_dict() == before
    pd.testing.assert_frame_equal(clean_cohort.metadata, data)


def test_split_rules_match_normative_catalog():
    rows = [
        row
        for row in json.loads((Path(__file__).parent.parent / "qa/rule_catalog.json").read_text())
        if row["stage"] == "S04"
    ]
    assert [
        {key: getattr(rule, key) for key in row}
        for rule, row in zip(SPLIT_RULES, rows, strict=True)
    ] == rows
    assert get_rule("NCG-SPLIT-011").stage == "S04"
