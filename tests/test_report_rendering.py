"""S08.B offline content, coverage and precomputed-only rendering."""

import json
from html.parser import HTMLParser
from pathlib import Path

from test_contracts import evaluation, fixture
from test_report_projection import association_report

from neurocvguard.models import AuditReport, ComparisonResult, EvaluationResult
from neurocvguard.reporting import render_report, write_report


def test_reporting_guide_example(tmp_path, monkeypatch):
    document = (Path(__file__).parents[1] / "docs/reporting.md").read_text(encoding="utf-8")
    code = document.split("```python\n", 1)[1].split("```", 1)[0]
    monkeypatch.chdir(tmp_path)
    exec(compile(code, "docs/reporting.md", "exec"), {})
    assert list(tmp_path.iterdir()) == []


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.ids = set()
        self.links = []
        self.text = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if "href" in attributes:
            self.links.append(attributes["href"])

    def handle_data(self, data):
        self.text.append(data)


def test_at_s08_08_no_network_render(monkeypatch):
    import socket

    def prohibited(*args, **kwargs):
        raise AssertionError("Rendering may not open network connections")

    monkeypatch.setattr(socket, "socket", prohibited)
    html = render_report(association_report())
    page = Page(html)
    assert not any(
        tag in {"script", "iframe", "img", "link", "object", "embed"} for tag, _ in page.tags
    )
    assert all(link.startswith("#") and link[1:] in page.ids for link in page.links)
    assert "@media print" in html and "default-src &#39;" not in html
    assert "default-src 'none'" in html and "style-src" in html
    assert "<style>" in html and "font-family: system-ui" in html


def test_at_s08_12_coverage_visibility():
    page = Page(render_report(association_report()))
    text = " ".join(page.text)
    assert "Incomplete assessment coverage" in text
    assert "Not assessable" in text and "unassessable" in text
    assert text.index("Incomplete assessment coverage") < text.index("3. Actionable findings")
    assert "Your experiment is leakage-free" not in text
    assert {
        "scope",
        "coverage",
        "findings",
        "cohort",
        "partitions",
        "associations",
        "results",
        "provenance",
        "limitations",
        "actions",
        "references",
    } <= page.ids


def test_at_s08_13_rendering_does_not_recompute(monkeypatch):
    import neurocvguard.audit as audit
    import neurocvguard.checks.associations as associations
    import neurocvguard.checks.cohort as cohort

    report = association_report()

    def prohibited(*args, **kwargs):
        raise AssertionError("Rendering must consume precomputed data")

    monkeypatch.setattr(associations, "association", prohibited)
    monkeypatch.setattr(associations, "check_associations", prohibited)
    monkeypatch.setattr(cohort, "inventory_cohort", prohibited)
    monkeypatch.setattr(audit, "audit_cohort", prohibited)
    assert "Site 001" in render_report(report)


def test_json_html_share_projection_and_manifest(tmp_path):
    result = association_report()
    paths = write_report(result, output_dir=tmp_path)
    assert json.loads(paths["json"].read_text()) == result.to_dict()
    assert paths["html"].read_text(encoding="utf-8") == render_report(result)
    manifest = json.loads(paths["manifest"].read_text())
    assert manifest["schema_version"] == "1.0"
    assert manifest["operational_records_included"] is False
    assert set(p.name for p in tmp_path.iterdir()) == {
        "report.json",
        "report.html",
        "report.manifest.json",
    }


def test_public_json_can_render_again_without_private_inputs():
    report = association_report()
    assert render_report(AuditReport.from_dict(report.to_dict())) == render_report(report)


def test_comparison_has_version_manifest_without_invented_inventory(tmp_path):
    record = ComparisonResult.from_dict(fixture("comparison_schema_example"))
    paths = write_report(record, output_dir=tmp_path)
    assert json.loads(paths["json"].read_text()) == record.to_dict()
    assert json.loads(paths["manifest"].read_text())["result_schema"] == "comparison-summary"
    assert "No cohort inventory supplied" in paths["html"].read_text(encoding="utf-8")


def test_evaluation_keeps_failed_fold_and_privacy_nulls(tmp_path):
    data = evaluation(small=True)
    data["execution_status"] = "incomplete"
    data["pooled_metrics"] = None
    data["folds"][1].update(status="failed", reason="synthetic failure", metrics=None)
    result = EvaluationResult.from_dict(data)
    paths = write_report(result, output_dir=tmp_path)
    output = json.loads(paths["json"].read_text())
    assert len(output["evaluation_summary"]["fold_metrics"]) == 2
    assert output["evaluation_summary"]["fold_metrics"][1]["status"] == "failed"
    assert "privacy_small_cells" in paths["html"].read_text(encoding="utf-8")
