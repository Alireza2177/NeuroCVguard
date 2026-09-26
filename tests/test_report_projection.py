"""S08.A public allowlists, domain aliases and linked suppression."""

import json
from dataclasses import replace

from test_association_checks import checks
from test_association_pairs import pair_cohort
from test_contracts import fixture

from neurocvguard.models import AuditReport
from neurocvguard.reporting import render_report
from neurocvguard.serialization import canonical_json


def association_report(table=((5, 5), (5, 5))):
    report = AuditReport.from_dict(fixture("report_schema_example"))
    return replace(report, checks=report.checks + checks(pair_cohort(table)))


def test_at_s08_01_default_id_redaction():
    report = association_report()
    item = replace(
        report.checks[0],
        instance_id="PRIVATE-person",
        scope={"fold_id": "PRIVATE-observation"},
        message="PRIVATE-person",
        recommendation="PRIVATE-observation",
        evidence={"ids": ["PRIVATE-person"]},
    )
    report = replace(report, checks=(item, *report.checks[1:]))
    assert "PRIVATE" not in canonical_json(report.to_dict())
    assert "PRIVATE" not in render_report(report)
    assert "PRIVATE" in canonical_json(report.to_dict(sensitive_details=True))


def test_at_s08_02_path_redaction():
    report = association_report()
    marker = "C:/Users/PRIVATE-user/data/private.tsv"
    report = replace(
        report,
        tool_version=marker,
        limitations=(marker,),
        provenance=dict(report.provenance, versions={"input": marker}),
    )
    assert "PRIVATE-user" not in canonical_json(report.to_dict())
    assert "PRIVATE-user" not in render_report(report)


def test_path_and_email_target_labels_are_not_public():
    from test_contracts import evaluation

    from neurocvguard.models import EvaluationResult

    data = evaluation()
    data["class_order"] = ["C:/Users/PRIVATE-user/data", "PRIVATE@email.invalid"]
    data["positive_class"] = data["class_order"][0]
    for metric in [data["pooled_metrics"], *[fold["metrics"] for fold in data["folds"]]]:
        for index, row in enumerate(metric["per_class"]):
            row["class_label"] = data["class_order"][index]
    result = EvaluationResult.from_dict(data)
    assert "PRIVATE" not in canonical_json(result.to_dict())
    assert "PRIVATE" in canonical_json(result.to_dict(sensitive_details=True))


def test_at_s08_03_domain_aliasing_and_idempotence():
    report = association_report()
    modified = []
    for item in report.checks:
        if item.scope.get("field") == "site":
            item = replace(
                item,
                evidence=dict(item.evidence, row_levels=("Private Clinic A", "Private Clinic B")),
            )
        modified.append(item)
    report = replace(report, checks=tuple(modified))
    public = report.to_dict()
    text = canonical_json(public)
    assert "Site 001" in text and "Site 002" in text
    assert "Private Clinic" not in text and "reverse" not in text
    assert "Private Clinic" not in render_report(report)
    assert "field_column" not in text and "expected_counts" not in text
    assert AuditReport.from_dict(public).to_dict() == public


def test_at_s08_04_small_cell_suppression():
    report = association_report(((1, 8), (9, 17)))
    original = canonical_json(report.to_dict(sensitive_details=True))
    for item in report.to_dict()["checks"]:
        if item["rule_id"].startswith("NCG-ASSOC"):
            assert item["evidence"] == {"details_omitted": True}
    assert canonical_json(report.to_dict(sensitive_details=True)) == original


def test_whole_report_threshold_is_explicit_and_no_recalculation():
    report = association_report()
    assert any("display_table" in x["evidence"] for x in report.to_dict()["checks"])
    assert not any(
        "display_table" in x["evidence"] for x in report.to_dict(small_cell_threshold=6)["checks"]
    )
    # Existing single-check API intentionally remains conservative.
    assert all("display_table" not in x.to_dict()["evidence"] for x in report.checks)


def test_same_domain_has_same_alias_in_multiple_tables():
    report = association_report()
    site = next(item for item in report.checks if item.scope.get("field") == "site")
    first = replace(
        site,
        instance_id="first",
        scope={"field": "site", "fold_id": "one"},
        evidence=dict(site.evidence, row_levels=("A", "B")),
    )
    second = replace(
        site,
        instance_id="second",
        scope={"field": "site", "fold_id": "two"},
        evidence=dict(site.evidence, row_levels=("B", "C")),
    )
    report = replace(report, checks=(first, second))
    projected = report.to_dict()["checks"]
    assert (
        projected[0]["evidence"]["display_table"]["row_levels"][1]
        == projected[1]["evidence"]["display_table"]["row_levels"][0]
    )


def test_suppressed_table_labels_do_not_shift_public_rerender_aliases():
    report = association_report()
    site = next(item for item in report.checks if item.scope.get("field") == "site")
    suppressed = replace(
        site,
        instance_id="hidden",
        evidence=dict(site.evidence, row_levels=("A", "B"), table=((1, 8), (9, 17))),
    )
    visible = replace(
        site,
        instance_id="visible",
        evidence=dict(site.evidence, row_levels=("Y", "Z")),
    )
    report = replace(report, checks=(suppressed, visible))
    public = report.to_dict()
    assert AuditReport.from_dict(public).to_dict() == public
    assert render_report(AuditReport.from_dict(public)) == render_report(report)


def test_forged_display_table_never_releases_labels_or_unchecked_values():
    report = association_report()
    item = report.checks[1]
    payload = {
        "row_levels": ["PRIVATE"],
        "target_levels": ["PRIVATE-target"],
        "counts": [[5]],
        "statistic": {"value": None, "reason": "constant_variable"},
        "path": "/PRIVATE/path",
        "total": 999,
    }
    item = replace(item, evidence={"display_table": payload})
    public = replace(report, checks=(item,)).to_dict()
    assert "PRIVATE" not in json.dumps(public) and "999" not in json.dumps(public)
    payload["counts"] = [[True]]
    assert (
        "display_table"
        not in replace(
            report, checks=(replace(item, evidence={"display_table": payload}),)
        ).to_dict()["checks"][0]["evidence"]
    )
