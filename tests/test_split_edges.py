"""Additional S04 identity, privacy and no-repair boundaries."""

import json
from dataclasses import replace

import pandas as pd
import pytest
from test_partitions import findings, objective_config, plan_fixture
from test_split_audit import nested_plan, summary

from neurocvguard import audit_splits, load_split_plan
from neurocvguard.config import AuditConfig, Objective
from neurocvguard.errors import SplitValidationError
from neurocvguard.models import CheckStatus, Cohort, PlanOrigin, SplitPlan
from neurocvguard.serialization import json_digest


def test_inner_participant_crossing_without_observation_overlap(clean_cohort):
    plan = nested_plan(clean_cohort)
    outer = plan.folds[0]
    inner = outer.inner_folds[0]
    moved = inner.train_ids[0]
    changed = replace(
        inner, train_ids=inner.train_ids[1:], validation_ids=(*inner.validation_ids, moved)
    )
    # Preserve exactly-once inner validation across both folds as well.
    reverse = replace(
        outer.inner_folds[1], train_ids=changed.validation_ids, validation_ids=changed.train_ids
    )
    plan = replace(plan, folds=(replace(outer, inner_folds=(changed, reverse)),))
    report = audit_splits(clean_cohort, plan, config=AuditConfig())
    assert any(
        check.status == CheckStatus.FAIL
        for check in findings(report.checks, 2)
        if "inner_fold_id" in check.scope
    )
    assert all(check.status == CheckStatus.PASS for check in findings(report.checks, 10))
    assert summary(report)["valid_for_objective"] is False


def test_missing_target_or_relationship_blocks_summary_without_dropping(clean_cohort):
    data = clean_cohort.metadata
    data.loc[0, "diagnosis"] = None
    columns = replace(clean_cohort.columns, independence=("family",))
    cohort = Cohort(data, None, columns, clean_cohort.observation_order)
    report = audit_splits(cohort, plan_fixture(), config=AuditConfig(columns=columns))
    assert summary(report)["valid_for_objective"] is False
    assert summary(report)["evaluation_permitted"] is False
    assert report.input_summary["n_observations"] == 36
    assert any(check.status == CheckStatus.NOT_ASSESSABLE for check in findings(report.checks, 3))
    assert all(check.status == CheckStatus.NOT_ASSESSABLE for check in findings(report.checks, 5))


def test_known_domain_violation_not_hidden_by_incomplete_coverage(clean_cohort):
    data = clean_cohort.metadata
    data.loc[0, "site"] = None
    cohort = Cohort(data, None, clean_cohort.columns, clean_cohort.observation_order)
    report = audit_splits(
        cohort,
        replace(plan_fixture(), objective=Objective.UNSEEN_SITE),
        config=objective_config(Objective.UNSEEN_SITE),
    )
    domains = findings(report.checks, 4)
    assert any(check.status == CheckStatus.FAIL for check in domains)
    assert any(check.status == CheckStatus.NOT_ASSESSABLE for check in domains)
    assert summary(report)["valid_for_objective"] is False


def test_row_and_fold_order_do_not_change_audit(clean_cohort):
    plan = plan_fixture()
    before = audit_splits(clean_cohort, plan, config=AuditConfig()).to_dict(sensitive_details=True)
    data = clean_cohort.metadata.iloc[::-1]
    cohort = Cohort(data, None, clean_cohort.columns, tuple(data.observation_id))
    after = audit_splits(
        cohort, replace(plan, folds=plan.folds[::-1]), config=AuditConfig()
    ).to_dict(sensitive_details=True)
    assert before == after


def test_private_fold_labels_and_summary_type_confusion_not_exported(clean_cohort):
    plan = plan_fixture()
    private_text = "private-person@example.invalid"
    plan = replace(
        plan,
        folds=tuple(
            replace(fold, repeat_id=private_text, fold_id=private_text + str(index))
            for index, fold in enumerate(plan.folds)
        ),
    )
    report = audit_splits(clean_cohort, plan, config=AuditConfig())
    assert private_text not in json.dumps(report.to_dict())
    assert private_text in json.dumps(report.to_dict(sensitive_details=True))
    check = next(check for check in report.checks if check.scope.get("field") == "split_summary")
    forged = replace(
        check,
        evidence={"valid_for_objective": private_text, "n_outer_folds": True, "n_repeats": -1},
    )
    assert forged.to_dict()["evidence"] == {}


def test_generated_hash_integrity_retained_on_import(clean_cohort):
    plan = load_split_plan(
        plan_fixture().to_operational_dict(), cohort=clean_cohort, config=AuditConfig()
    )
    payload = plan.to_operational_dict()
    payload["origin"] = "generated"
    del payload["plan_id"]
    payload["plan_id"] = json_digest(payload)
    generated = load_split_plan(payload, cohort=clean_cohort, config=AuditConfig())
    assert generated.origin == PlanOrigin.GENERATED
    assert generated.cohort_digest == plan.cohort_digest
    corrupted = generated.to_operational_dict()
    corrupted["seed"] = 5
    with pytest.raises(SplitValidationError, match="Generated plan_id"):
        SplitPlan.from_dict(corrupted)


def test_library_audit_does_not_write_or_read_tables(clean_cohort, monkeypatch, tmp_path):
    plan = plan_fixture()

    def fail(*args, **kwargs):
        raise AssertionError("split audits must not read or write tables")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pd, "read_csv", fail)
    monkeypatch.setattr(pd.DataFrame, "to_csv", fail)
    assert summary(audit_splits(clean_cohort, plan, config=AuditConfig()))["complete_cv"]
    assert list(tmp_path.iterdir()) == []


def test_documented_split_example():
    from pathlib import Path

    text = (Path(__file__).parent.parent / "docs/split_audits.md").read_text()
    example = text.split("```python\n", 1)[1].split("```", 1)[0]
    # Fixed, repository-owned example only; the application never runs user code.
    exec(compile(example, "docs/split_audits.md", "exec"), {})
