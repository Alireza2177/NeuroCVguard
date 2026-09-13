"""S01 model contracts using synthetic records, never computed research results."""

import copy
import json
import socket
from pathlib import Path

import pandas as pd
import pytest
from jsonschema import Draft202012Validator

from neurocvguard.config import ColumnMap
from neurocvguard.errors import EvaluationError, InputValidationError, SplitValidationError
from neurocvguard.models import (
    AuditReport,
    CheckResult,
    CheckStatus,
    Cohort,
    ComparisonResult,
    EvaluationResult,
    EvidenceKind,
    MetricSet,
    MetricValue,
    PreprocessingLedger,
    SplitPlan,
)
from neurocvguard.schema import SCHEMA_NAMES, load_schema, validate_document
from neurocvguard.serialization import canonical_json, json_digest, strict_json_loads

ROOT = Path(__file__).resolve().parents[1]


def fixture(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / (name + ".json")).read_text())


def metric_set(*, small: bool = False, pooled: bool = False) -> dict:
    """Handwritten synthetic metric contract; values are not experiment outputs."""
    count = 40 if pooled else 20
    table = [[10, 10], [10, 10]] if pooled else ([[9, 1], [0, 10]] if small else [[5, 5], [5, 5]])
    value = {"value": 0.5, "reason": None, "n": count}
    return {
        "accuracy": copy.deepcopy(value),
        "balanced_accuracy": copy.deepcopy(value),
        "macro_f1": copy.deepcopy(value),
        "roc_auc": {"value": None, "reason": "synthetic_undefined", "n": count},
        "n_participants": count,
        "per_class": [
            {"class_label": "AD", "support": count // 2, "recall": 0.5},
            {"class_label": "CN", "support": count // 2, "recall": 0.5},
        ],
        "confusion_matrix": table,
    }


def evaluation(*, small: bool = False) -> dict:
    result = fixture("evaluation_schema_example")
    result.update(
        execution_status="completed",
        n_observations=80,
        n_participants=40,
        pooled_metrics=metric_set(pooled=True),
    )
    result["folds"] = [
        {
            "repeat_id": "private-repeat",
            "fold_id": f"private-fold-{i}",
            "status": "completed",
            "reason": None,
            "train_participants": 20,
            "test_participants": 20,
            "selected_C": 1.0,
            "metrics": metric_set(small=small and i == 0),
            "candidate_scores": [],
        }
        for i in range(2)
    ]
    result["fit_events"] = [
        {
            "event_id": "private-event",
            "repeat_id": "private-repeat",
            "fold_id": "private-fold-0",
            "inner_fold_id": None,
            "C": 1.0,
            "fit_ids": ["private-observation"],
            "status": "completed",
            "scope": "outer_train",
        }
    ]
    result["limitations"] = ["Synthetic only; private-note must not enter a public report."]
    return result


def test_at_s01_06_null_metric() -> None:
    metric = MetricValue(None, "positive_class_unspecified", 12)
    assert strict_json_loads(canonical_json(metric.to_dict())) == {
        "value": None,
        "reason": "positive_class_unspecified",
        "n": 12,
    }
    assert MetricValue(0.0, None, 12).to_dict()["value"] == 0.0
    for reason in (None, "", "   "):
        with pytest.raises(InputValidationError):
            MetricValue(None, reason, 12)
    with pytest.raises(InputValidationError):
        MetricValue(0.0, "undefined", 12)


@pytest.mark.parametrize("number", [float("nan"), float("inf"), -float("inf")])
def test_at_s01_07_reject_nonfinite_output(number: float) -> None:
    with pytest.raises(InputValidationError):
        MetricValue(number, None, 10)
    with pytest.raises(InputValidationError):
        canonical_json({"nested": [number]})
    data = evaluation()
    data["folds"][0]["selected_C"] = number
    with pytest.raises(EvaluationError):
        EvaluationResult.from_dict(data)


def test_at_s01_08_all_packaged_contracts_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def denied(*args: object, **kwargs: object) -> None:
        raise AssertionError("Network attempted during schema validation")

    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    for name in SCHEMA_NAMES:
        schema = load_schema(name)
        Draft202012Validator.check_schema(schema)
        assert schema == json.loads((ROOT / "contracts" / (name + ".schema.json")).read_text())
        schema.clear()
        assert load_schema(name)
    for entry in fixture("manifest"):
        name = Path(entry["schema"]).name.removesuffix(".schema.json")
        data = json.loads((ROOT / entry["path"]).read_text())
        if entry["valid"]:
            assert validate_document(name, data) == data
        else:
            with pytest.raises(InputValidationError):
                validate_document(name, data)


@pytest.mark.parametrize(
    "reference", ["https://example.invalid/schema", "file:///private/schema", "other.schema.json"]
)
def test_external_schema_reference_refused(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, reference: str
) -> None:
    folder = tmp_path / "schemas"
    folder.mkdir()
    (folder / "config.schema.json").write_text(json.dumps({"$ref": reference}))
    monkeypatch.setattr("neurocvguard.schema.files", lambda _: tmp_path)
    with pytest.raises(InputValidationError, match="External schema"):
        load_schema("config")


@pytest.mark.parametrize("name", ["../config", "https://example.invalid/config", "unrecognized"])
def test_unknown_schema_name_refused(name: str) -> None:
    with pytest.raises(InputValidationError, match="Unknown schema"):
        load_schema(name)


@pytest.mark.parametrize(
    ("cls", "name"),
    [
        (SplitPlan, "splits_clean"),
        (SplitPlan, "splits_participant_overlap"),
        (SplitPlan, "splits_unknown_id"),
        (PreprocessingLedger, "ledger_declared_global"),
        (EvaluationResult, "evaluation_schema_example"),
    ],
)
def test_at_s01_09_operational_round_trip(cls: type, name: str) -> None:
    data = fixture(name)
    original = copy.deepcopy(data)
    result = cls.from_dict(data)
    encoded = result.to_operational_dict()
    expected = copy.deepcopy(original)
    if cls is SplitPlan:
        # spec/05 section 5.2 prescribes canonical ID sorting. The intentionally
        # unknown-ID fixture is structurally valid but contains an unsorted list.
        for fold in expected["folds"]:
            fold["train_ids"].sort()
            fold["test_ids"].sort()
    assert encoded == expected
    assert cls.from_json(canonical_json(encoded)).to_operational_dict() == expected
    assert data == original


def test_at_s01_09_report_and_comparison_round_trip() -> None:
    report = AuditReport.from_dict(fixture("report_schema_example"))
    assert report.checks[0].status is CheckStatus.NOT_ASSESSABLE
    assert report.checks[0].evidence_kind is EvidenceKind.UNASSESSABLE
    for sensitive in (False, True):
        projection = report.to_dict(sensitive_details=sensitive)
        assert (
            AuditReport.from_json(canonical_json(projection)).to_dict(sensitive_details=sensitive)
            == projection
        )
    comparison = fixture("comparison_schema_example")
    record = ComparisonResult.from_dict(comparison)
    assert record.to_dict(sensitive_details=True) == comparison
    assert (
        ComparisonResult.from_json(canonical_json(record.to_dict())).to_dict() == record.to_dict()
    )


def test_at_s01_09_memberships_sorted_without_relabeling() -> None:
    data = fixture("splits_clean")
    data["folds"][0]["train_ids"].reverse()
    before = copy.deepcopy(data)
    plan = SplitPlan.from_dict(data)
    assert plan.folds[0].train_ids == tuple(sorted(data["folds"][0]["train_ids"]))
    assert [fold.fold_id for fold in plan.folds] == [fold["fold_id"] for fold in data["folds"]]
    assert data == before


def test_generated_plan_hash_and_unique_folds() -> None:
    data = fixture("splits_clean")
    data.update(origin="generated", cohort_digest="0" * 64)
    with pytest.raises(SplitValidationError, match="Generated plan_id"):
        SplitPlan.from_dict(data)
    data["plan_id"] = json_digest({key: value for key, value in data.items() if key != "plan_id"})
    assert SplitPlan.from_dict(data).origin.value == "generated"
    data["folds"].append(copy.deepcopy(data["folds"][0]))
    with pytest.raises(SplitValidationError, match="unique"):
        SplitPlan.from_dict(data)


def test_at_s01_10_cohort_copy_and_key_alignment() -> None:
    metadata = pd.DataFrame(
        {"observation_id": ["synthetic-a", "synthetic-b"], "subject_id": ["subject-a", "subject-b"]}
    )
    features = pd.DataFrame(
        {"observation_id": ["synthetic-a", "synthetic-b"], "feature_1": [1.0, 2.0]}
    )
    cohort = Cohort(metadata, features, ColumnMap(), ("synthetic-a", "synthetic-b"))
    metadata.loc[0, "subject_id"] = "changed"
    features.loc[0, "feature_1"] = 100
    exported = cohort.metadata
    exported.loc[1, "subject_id"] = "changed"
    assert cohort.metadata["subject_id"].tolist() == ["subject-a", "subject-b"]
    assert cohort.features["feature_1"].tolist() == [1.0, 2.0]
    with pytest.raises(InputValidationError, match="aligned"):
        Cohort(metadata, features.iloc[::-1], ColumnMap(), ("synthetic-a", "synthetic-b"))


def test_at_s01_10_nested_record_ownership() -> None:
    data = evaluation()
    before = copy.deepcopy(data)
    record = EvaluationResult.from_dict(data)
    record.to_dict()
    record.to_operational_dict()["fit_events"].clear()
    assert data == before
    data["fit_events"][0]["fit_ids"].append("changed")
    assert record.fit_events[0].fit_ids == ("private-observation",)
    with pytest.raises(TypeError):
        record.provenance["seed"] = 0


def test_at_s01_11_private_and_public_boundaries() -> None:
    data = evaluation()
    record = EvaluationResult.from_dict(data)
    operational = record.to_operational_dict()
    assert operational["format"] == "neurocvguard.evaluation.private"
    assert operational["sensitive"] is True
    assert operational == data
    public = record.to_dict()
    encoded = canonical_json(public)
    for token in (
        "private-observation",
        "private-event",
        "private-note",
        "private-fold",
        "private-repeat",
        data["cohort_digest"],
        data["feature_digest"],
        data["config_digest"],
    ):
        assert token not in encoded
    assert "fit_events" not in public
    assert "cohort_digest" not in public
    assert public["result_type"] == "evaluation"
    assert public["evaluation_summary"]["class_order"] == ["AD", "CN"]
    assert len(public["evaluation_summary"]["fold_metrics"]) == 2
    assert AuditReport.from_dict(public).result_type == "evaluation"
    with pytest.raises(EvaluationError):
        EvaluationResult.from_dict(public)
    for value in (record, {"nested": record}):
        with pytest.raises(InputValidationError, match="projection|serializer|to_dict"):
            canonical_json(value)


def test_at_s01_11_small_cells_hide_linked_fold_and_pooled_metrics() -> None:
    record = EvaluationResult.from_dict(evaluation(small=True))
    public = record.to_dict()["evaluation_summary"]
    assert public["pooled_metrics"] is None
    assert public["metrics_hidden_reason"] == "privacy_small_cells"
    assert all(
        fold["metrics"] is None and fold["metrics_hidden_reason"] == "privacy_small_cells"
        for fold in public["fold_metrics"]
    )
    assert (
        record.to_dict(sensitive_details=True)["evaluation_summary"]["pooled_metrics"] is not None
    )
    assert record.to_operational_dict()["folds"][0]["metrics"]["confusion_matrix"][0][1] == 1


def test_at_s01_11_report_open_evidence_not_exported() -> None:
    data = fixture("report_schema_example")
    for key in ("message", "recommendation", "instance_id"):
        data["checks"][0][key] = "private-identifier"
    data["checks"][0]["scope"] = {"fold_id": "private-fold", "site": "private-site"}
    data["checks"][0]["evidence"] = {
        "nested": ["private-person"],
        "table": [[1, 99]],
        "email": "synthetic@example.invalid",
    }
    record = AuditReport.from_dict(data)
    public = record.to_dict()
    assert "private-" not in canonical_json(public)
    assert "example.invalid" not in canonical_json(public)
    sensitive = record.to_dict(sensitive_details=True)
    assert sensitive["provenance"]["sensitive_details"] is True
    assert sensitive["checks"][0]["evidence"] == data["checks"][0]["evidence"]
    assert any("Sensitive research output" in text for text in sensitive["limitations"])


def test_at_s01_11_comparison_redacts_dependent_deltas() -> None:
    data = fixture("comparison_schema_example")
    data["designs"][0]["metrics"] = metric_set(small=True)
    data["designs"][1]["metrics"] = metric_set()
    data["differences"][0].update(difference=0.1, reasons=[])
    result = ComparisonResult.from_dict(data)
    public = result.to_dict()
    assert public["designs"][0]["metrics"] is None
    assert public["designs"][1]["metrics"] is not None
    assert public["differences"][0]["difference"] is None
    assert public["differences"][0]["reasons"] == ["privacy_small_cells"]
    assert result.to_dict(sensitive_details=True) == data


@pytest.mark.parametrize(
    ("status", "kind"),
    [("pass", "unassessable"), ("fail", "unassessable"), ("not_assessable", "observed")],
)
def test_illegal_status_evidence_combinations(status: str, kind: str) -> None:
    data = fixture("report_schema_example")["checks"][0]
    data.update(rule_id="NCG-SPLIT-002", status=status, evidence_kind=kind)
    with pytest.raises(InputValidationError):
        CheckResult.from_dict(data)


def test_declared_evidence_not_promoted() -> None:
    data = fixture("report_schema_example")["checks"][0]
    data.update(rule_id="NCG-PROV-003", status="fail", evidence_kind="declared")
    assert CheckResult.from_dict(data).evidence_kind == EvidenceKind.DECLARED
    data["evidence_kind"] = "observed"
    with pytest.raises(InputValidationError, match="declared"):
        CheckResult.from_dict(data)
    ledger = fixture("ledger_declared_global")
    ledger["source"] = "runtime_verified"
    with pytest.raises(InputValidationError):
        PreprocessingLedger.from_dict(ledger)


def test_metric_shape_class_alignment_and_failed_folds() -> None:
    data = metric_set()
    data["confusion_matrix"][0].append(0)
    with pytest.raises(InputValidationError, match="size"):
        MetricSet.from_dict(data)
    data = evaluation()
    data["class_order"].reverse()
    with pytest.raises(EvaluationError, match="class order"):
        EvaluationResult.from_dict(data)
    data = evaluation()
    data["execution_status"] = "incomplete"
    data["folds"][0].update(status="failed", reason="synthetic_fit_failure", metrics=None)
    with pytest.raises(EvaluationError, match="pooled"):
        EvaluationResult.from_dict(data)
    data["pooled_metrics"] = None
    record = EvaluationResult.from_dict(data)
    assert len(record.to_dict()["evaluation_summary"]["fold_metrics"]) == 2
    assert record.to_dict()["evaluation_summary"]["fold_metrics"][0]["status"] == "failed"


def test_standard_json_determinism_and_key_types() -> None:
    assert canonical_json({"z": "é", "a": [None, 0]}) == '{"a":[null,0],"z":"é"}'
    assert json_digest({"b": 2, "a": 1}) == json_digest({"a": 1, "b": 2})
    assert json_digest([1, 2]) != json_digest([2, 1])
    with pytest.raises(InputValidationError):
        canonical_json({1: "invalid"})
