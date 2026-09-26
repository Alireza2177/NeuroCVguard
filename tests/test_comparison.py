"""S12.A comparison algebra, compatibility and private-record loading."""

import json
from dataclasses import replace

import pytest
from test_contracts import evaluation, fixture

from neurocvguard import compare_designs
from neurocvguard.comparison import load_evaluation
from neurocvguard.config import Objective
from neurocvguard.errors import EvaluationError, InputValidationError
from neurocvguard.models import AuditReport, ComparisonResult, EvaluationResult, EvaluationStatus


def record(score=0.5):
    data = evaluation()
    for metric in ("accuracy", "balanced_accuracy", "macro_f1"):
        data["pooled_metrics"][metric]["value"] = score
    return EvaluationResult.from_dict(data)


def test_at_s12_01_signed_difference_and_determinism():
    a, b = record(0.25), record(0.75)
    result = compare_designs({"B": b, "A": a})
    assert result == compare_designs({"A": a, "B": b})
    assert [d.name for d in result.designs] == ["A", "B"]
    assert [d.difference for d in result.differences[:3]] == [-0.5] * 3
    assert all(d.design_a == "A" and d.design_b == "B" for d in result.differences)
    assert result.differences[-1].difference is None
    assert result.differences[-1].reasons == ("metric_undefined_a", "metric_undefined_b")
    assert a.pooled_metrics.accuracy.value == 0.25


def test_at_s12_02_cohort_mismatch_is_null_with_reason():
    a = record()
    b = replace(a, cohort_digest="a" * 64)
    result = compare_designs({"A": a, "B": b})
    assert all(d.difference is None and "cohort_mismatch" in d.reasons for d in result.differences)
    assert result.designs[0].context.cohort_reference != result.designs[1].context.cohort_reference
    assert "cohort_mismatch" in str(result.to_dict())


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("feature_digest", "b" * 64, "feature_mismatch"),
        ("feature_columns", ("different",), "feature_mismatch"),
        ("positive_class", "CN", "class_definitions_mismatch"),
        ("n_observations", 81, "cohort_counts_mismatch"),
    ],
)
def test_at_s12_03_incompatible_inputs_no_delta(field, value, reason):
    a = record()
    b = replace(a, **{field: value})
    assert all(
        d.difference is None and reason in d.reasons
        for d in compare_designs({"A": a, "B": b}).differences
    )


def test_at_s12_03_unsupported_metric_unit_refused_before_comparison():
    # v1 private schema permits participant only; no row-unit result is invented.
    a = record()
    object.__setattr__(a, "metric_unit", "observation")
    with pytest.raises(EvaluationError, match="metric_unit"):
        compare_designs({"A": a, "B": record()})


def test_incomplete_kept_without_easy_fold_delta():
    a = record()
    incomplete = replace(a, execution_status=EvaluationStatus.INCOMPLETE, pooled_metrics=None)
    result = compare_designs({"A": incomplete, "B": a})
    assert result.designs[0].metrics is None
    assert result.designs[0].context.execution_status == "incomplete"
    assert all(
        d.difference is None and "design_a_incomplete" in d.reasons for d in result.differences
    )


def test_at_s12_08_private_load_and_public_refusal(tmp_path):
    path = tmp_path / "evaluation.private.json"
    path.write_text(json.dumps(record().to_operational_dict()), encoding="utf-8")
    assert load_evaluation(path) == record()
    path.write_text(json.dumps(record().to_dict()), encoding="utf-8")
    with pytest.raises(InputValidationError, match="Compare requires evaluation.private.json"):
        load_evaluation(path)


@pytest.mark.parametrize("text", ['{"format":1,"format":2}', '{"value":NaN}', "[]", "{}"])
def test_strict_private_json(tmp_path, text):
    path = tmp_path / "input.json"
    path.write_text(text)
    with pytest.raises(InputValidationError):
        load_evaluation(path)


def test_no_unsafe_formats_or_oversized_inputs(tmp_path):
    for path in ("https://example.invalid/file.json", "\\\\server\\file.json", "model.pkl"):
        with pytest.raises(InputValidationError):
            load_evaluation(path)
    path = tmp_path / "large.json"
    path.write_bytes(b" " * (1024 * 1024 + 1))
    with pytest.raises(InputValidationError, match="limit"):
        load_evaluation(path, max_input_mb=1)


def test_at_s12_09_different_objectives_are_descriptive_not_causal():
    a = record()
    result = compare_designs({"A": a, "B": replace(a, objective=Objective.UNSEEN_SITE)})
    assert result.differences[0].difference == 0
    assert result.designs[1].objective == "unseen_site"
    for phrase in (
        "not causal",
        "held-out distributions",
        "training sizes",
        "class coverage",
        "No winning",
    ):
        assert phrase in result.interpretation
        assert phrase in result.to_dict()["interpretation"]


def test_context_schema_legacy_and_public_roundtrip():
    old = fixture("comparison_schema_example")
    assert ComparisonResult.from_dict(old).to_dict(sensitive_details=True) == old
    result = compare_designs({"A": record(), "B": record()})
    public = result.to_dict()
    context = public["designs"][0]["context"]
    assert context["n_folds"] == context["n_completed_folds"] == 2
    assert context["n_participants"] == 40 and context["n_observations"] == 80
    assert context["training_participants_min"] == context["training_participants_max"] == 20
    assert context["recorded_C_values"] == [1.0]
    assert ComparisonResult.from_dict(public).to_dict() == public
    assert record().cohort_digest not in str(public)
    assert record().feature_digest not in str(public)
    context["unapproved"] = True
    with pytest.raises(InputValidationError):
        ComparisonResult.from_dict(public)


def test_minimum_two_records_and_named_input_type():
    for results in (
        {},
        {"one": record()},
        {"": record(), "two": record()},
        {"a": {}, "b": record()},
    ):
        with pytest.raises(InputValidationError):
            compare_designs(results)


def test_extended_context_in_embedded_report_and_legacy_migration():
    data = fixture("report_schema_example")
    data["result_type"] = "comparison"
    data["comparison_summary"] = compare_designs({"A": record(), "B": record()}).to_dict()
    report = AuditReport.from_dict(data)
    public = report.to_dict()
    assert public["comparison_summary"] == data["comparison_summary"]
    assert AuditReport.from_dict(public).to_dict() == public
    data["comparison_summary"] = fixture("comparison_schema_example")
    assert all(
        "context" not in d
        for d in AuditReport.from_dict(data).to_dict()["comparison_summary"]["designs"]
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("n_completed_folds", 3),
        ("training_participants_min", 21),
        ("training_participants_max", 41),
        ("positive_class", "unknown"),
        ("n_participants", 41),
        ("class_order", ["CN", "AD"]),
    ],
)
def test_context_consistency_refuses_contradictory_record(field, value):
    data = compare_designs({"A": record(), "B": record()}).to_dict()
    data["designs"][0]["context"][field] = value
    with pytest.raises(InputValidationError):
        ComparisonResult.from_dict(data)
