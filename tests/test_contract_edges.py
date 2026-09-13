"""Contract boundary regressions beyond the bundled minimal examples."""

import copy

import pytest
from test_contracts import evaluation, fixture, metric_set

from neurocvguard.config import AuditConfig
from neurocvguard.errors import EvaluationError, InputValidationError, SplitValidationError
from neurocvguard.models import AuditReport, EvaluationResult, MetricSet, SplitPlan
from neurocvguard.serialization import canonical_json


def test_at_s01_09_twelve_fold_public_projection_is_idempotent() -> None:
    data = evaluation()
    public = EvaluationResult.from_dict(data).to_dict()
    summary = public["evaluation_summary"]
    template = summary["fold_metrics"][0]
    summary["fold_metrics"] = [
        dict(copy.deepcopy(template), fold_id=f"fold-{i:02d}") for i in range(12)
    ]
    report = AuditReport.from_dict(public)
    projected = report.to_dict()
    assert AuditReport.from_dict(projected).to_dict() == projected
    assert len({fold["fold_id"] for fold in projected["evaluation_summary"]["fold_metrics"]}) == 12


def test_at_s01_08_remote_dynamic_reference_refused(monkeypatch, tmp_path) -> None:
    import json

    from neurocvguard.schema import load_schema

    folder = tmp_path / "schemas"
    folder.mkdir()
    (folder / "config.schema.json").write_text(
        json.dumps({"properties": {"x": {"$dynamicRef": "https://example.invalid/remote"}}})
    )
    monkeypatch.setattr("neurocvguard.schema.files", lambda _: tmp_path)
    with pytest.raises(InputValidationError, match="External schema"):
        load_schema("config")


@pytest.mark.parametrize("option", [1, "true", None])
def test_at_s01_11_sensitive_access_requires_boolean(option: object) -> None:
    record = EvaluationResult.from_dict(evaluation())
    with pytest.raises(InputValidationError):
        record.to_dict(sensitive_details=option)
    check = AuditReport.from_dict(fixture("report_schema_example")).checks[0]
    with pytest.raises(InputValidationError):
        check.to_dict(sensitive_details=option)


def test_completed_status_cannot_hide_incomplete_execution() -> None:
    report = fixture("report_schema_example")
    report["execution_status"] = "completed"
    with pytest.raises(InputValidationError, match="unassessable"):
        AuditReport.from_dict(report)
    data = evaluation()
    data["folds"] = data["folds"][:1]
    with pytest.raises(EvaluationError):
        EvaluationResult.from_dict(data)
    data = evaluation()
    data["folds"][1]["repeat_id"] = "different-repeat"
    with pytest.raises(EvaluationError, match="one repeat"):
        EvaluationResult.from_dict(data)


def test_public_summary_enforces_metric_shape_and_class_order() -> None:
    data = EvaluationResult.from_dict(evaluation()).to_dict()
    data["evaluation_summary"]["pooled_metrics"]["per_class"].reverse()
    with pytest.raises(InputValidationError, match="class order"):
        AuditReport.from_dict(data)
    data = metric_set()
    data["per_class"][0]["support"] = 99
    with pytest.raises(InputValidationError, match="support"):
        MetricSet.from_dict(data)


def test_at_s01_09_inner_folds_and_optional_presence() -> None:
    data = fixture("splits_clean")
    del data["folds"][1]["inner_folds"]
    train = data["folds"][0]["train_ids"]
    data["folds"][0]["inner_folds"] = [
        {"inner_fold_id": "inner", "train_ids": train[:12], "validation_ids": train[12:]}
    ]
    record = SplitPlan.from_dict(data)
    assert record.to_operational_dict() == data
    data["folds"][0]["inner_folds"] *= 2
    with pytest.raises(SplitValidationError, match="unique"):
        SplitPlan.from_dict(data)


def test_at_s01_10_helpers_do_not_mutate_config() -> None:
    from neurocvguard.schema import validate_document
    from neurocvguard.serialization import json_digest

    config = AuditConfig()
    before = config.to_dict()
    validate_document("config", config.to_dict())
    json_digest(config.to_dict())
    canonical_json(config.to_dict())
    assert config.to_dict() == before
