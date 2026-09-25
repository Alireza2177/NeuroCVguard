"""S07.B evidence labels, declared boundaries and persistent limitations."""

import json
from pathlib import Path

import pytest
from test_ledger import declaration
from test_split_audit import nested_plan

from neurocvguard import audit_cohort
from neurocvguard.checks.preprocessing import check_preprocessing
from neurocvguard.config import AuditConfig
from neurocvguard.models import AuditReport, CheckStatus, EvidenceKind, Severity
from neurocvguard.rules import PROVENANCE_RULES


def check(cohort, ledger=None, plan=None):
    return check_preprocessing(cohort, config=AuditConfig(), ledger=ledger, plan=plan)


def rule(results, number):
    return [item for item in results if item.rule_id == f"NCG-PROV-{number:03}"]


def test_at_s07_01_no_ledger(clean_cohort):
    result = check(clean_cohort)
    assert len(result) == 1
    assert result[0].status == CheckStatus.NOT_ASSESSABLE
    assert result[0].evidence_kind == EvidenceKind.UNASSESSABLE
    assert result[0].severity == Severity.WARNING
    report = audit_cohort(clean_cohort, config=AuditConfig())
    assert report.provenance["upstream_preprocessing_verified"] is False
    assert report.execution_status.value == "partial"
    assert "fit_events" not in report.to_dict(sensitive_details=True)


def test_at_s07_02_declared_global_fit(clean_cohort):
    results = check(clean_cohort, declaration())
    item = rule(results, 2)[0]
    assert item.status == CheckStatus.FAIL and item.severity == Severity.WARNING
    assert item.evidence_kind == EvidenceKind.DECLARED
    assert "declared global-fit warning" in item.message
    assert "not observed historical proof" in item.to_dict()["message"]
    assert rule(results, 1)[0].status == CheckStatus.NOT_ASSESSABLE


@pytest.mark.parametrize("nested", [False, True])
def test_at_s07_03_declared_outside_training_ids(clean_cohort, nested):
    plan = nested_plan(clean_cohort)
    outer = plan.folds[0]
    inner = outer.inner_folds[0]
    ids = [inner.validation_ids[0], outer.test_ids[0]] if nested else [outer.test_ids[0]]
    ledger = declaration(
        fit_scope="inner_train" if nested else "outer_train",
        repeat_id=outer.repeat_id,
        fold_id=outer.fold_id,
        inner_fold_id=inner.inner_fold_id if nested else None,
        fit_ids=ids,
    )
    item = rule(check(clean_cohort, ledger, plan), 3)[0]
    assert item.status == CheckStatus.FAIL and item.severity == Severity.ERROR
    assert item.evidence_kind == EvidenceKind.DECLARED
    assert set(item.evidence["outside_training_ids"]) == set(ids)
    assert "does not prove historical execution" in item.to_dict()["message"]
    assert item.to_dict()["evidence"] == {"execution_verified": False}


def test_at_s07_05_fixed_conversion(clean_cohort):
    results = check(clean_cohort, declaration(transform="fixed units", data_dependent=False))
    fixed = rule(results, 5)[0]
    assert fixed.status == CheckStatus.NOT_APPLICABLE and fixed.severity == Severity.INFO
    assert fixed.evidence_kind == EvidenceKind.DECLARED
    assert "not verified" in fixed.message
    assert not rule(results, 2) and not rule(results, 3)
    assert rule(results, 1)[0].status == CheckStatus.NOT_ASSESSABLE


def test_at_s07_06_external_learned_transform(clean_cohort):
    results = check(clean_cohort, declaration(fit_scope="external"))
    assert len(results) == 2
    assert all(item.status == CheckStatus.NOT_ASSESSABLE for item in results)
    assert all(item.evidence_kind == EvidenceKind.UNASSESSABLE for item in results)
    assert results[1].evidence["reason"] == "external_provenance_unverified"


@pytest.mark.parametrize("missing", ["plan", "ids"])
def test_declared_scope_without_comparison_inputs_is_unassessable(clean_cohort, missing):
    plan = nested_plan(clean_cohort)
    outer = plan.folds[0]
    ledger = declaration(
        fit_scope="outer_train",
        repeat_id=outer.repeat_id,
        fold_id=outer.fold_id,
        fit_ids=None if missing == "ids" else list(outer.train_ids),
    )
    result = rule(check(clean_cohort, ledger, None if missing == "plan" else plan), 1)[1]
    assert result.status == CheckStatus.NOT_ASSESSABLE
    assert "unassessable" in result.to_dict()["message"]
    assert result.evidence["reason"] == (
        "split_context_missing" if missing == "plan" else "fit_ids_missing"
    )


def test_inside_training_is_declared_pass_not_verified_upstream(clean_cohort):
    plan = nested_plan(clean_cohort)
    outer = plan.folds[0]
    ledger = declaration(
        fit_scope="outer_train",
        repeat_id=outer.repeat_id,
        fold_id=outer.fold_id,
        fit_ids=list(outer.train_ids),
    )
    results = check(clean_cohort, ledger, plan)
    result = rule(results, 3)[0]
    assert result.status == CheckStatus.PASS and result.evidence_kind == EvidenceKind.DECLARED
    assert "execution is not verified" in result.to_dict()["message"]
    assert rule(results, 1)[0].status == CheckStatus.NOT_ASSESSABLE


def test_empty_and_unknown_scope_are_not_verified(clean_cohort):
    ledger = declaration(fit_scope="unknown")
    assert len(rule(check(clean_cohort, ledger), 1)) == 2
    ledger["events"] = []
    assert len(check(clean_cohort, ledger)) == 1


def test_report_privacy_and_duplicate_scopes_preserved(clean_cohort):
    ledger = declaration(transform="<script>PRIVATE-transform</script>", event_id="PRIVATE-event")
    second = declaration(event_id="second", transform="another-PCA")["events"][0]
    ledger["events"].append(second)
    report = audit_cohort(clean_cohort, config=AuditConfig(), ledger=ledger)
    assert len(rule(report.checks, 2)) == 2
    public = report.to_dict()
    private = report.to_dict(sensitive_details=True)
    assert "PRIVATE" not in json.dumps(public)
    assert "PRIVATE" in json.dumps(private)
    assert AuditReport.from_dict(public).to_dict() == public
    assert all(
        item.evidence_kind != EvidenceKind.OBSERVED
        for item in report.checks
        if item.rule_id.startswith("NCG-PROV")
    )
    assert any(item.rule_id.startswith("NCG-ASSOC") for item in report.checks)
    assert any(item.rule_id.startswith("NCG-COHORT") for item in report.checks)


def test_event_order_invariance_and_registry(clean_cohort):
    data = declaration()
    data["events"].append(declaration(event_id="another")["events"][0])
    first = check(clean_cohort, data)
    data["events"].reverse()
    assert first == check(clean_cohort, data)
    catalog = json.loads((Path(__file__).parent.parent / "qa/rule_catalog.json").read_text())
    expected = [row for row in catalog if row["stage"] == "S07"]
    assert [
        {key: getattr(item, key) for key in row}
        for item, row in zip(PROVENANCE_RULES, expected, strict=True)
    ] == expected


def test_documented_provenance_example():
    document = (Path(__file__).parent.parent / "docs/preprocessing_provenance.md").read_text(
        encoding="utf-8"
    )
    example = document.split("```python\n", 1)[1].split("```", 1)[0]
    # Fixed repository example only, never executable user input.
    exec(compile(example, "docs/preprocessing_provenance.md", "exec"), {})
