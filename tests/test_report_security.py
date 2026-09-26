"""S08.C adversarial text and write-failure preservation."""

import csv
import json
from dataclasses import replace
from pathlib import Path

import pytest
from test_report_projection import association_report
from test_report_rendering import Page

from neurocvguard.errors import InputValidationError
from neurocvguard.reporting import render_report, write_findings_csv, write_report


def test_at_s08_05_no_hidden_payload_leakage(tmp_path):
    report = association_report(((1, 8), (9, 17)))
    paths = write_report(report, output_dir=tmp_path)
    for path in paths.values():
        text = path.read_text(encoding="utf-8")
        assert "expected_counts" not in text and "row_levels" not in text
        assert "n_in_table" not in text and "permitted_training_count" not in text
        assert "<script" not in text and "data-table" not in text
    data = json.loads(paths["json"].read_text())
    assert all(
        item["evidence"] == {"details_omitted": True}
        for item in data["checks"]
        if item["rule_id"].startswith("NCG-ASSOC")
    )


def test_at_s08_06_html_injection():
    malicious = '</style><script>alert(1)</script><img src=x onerror="alert(2)">' + "測試نام" * 200
    report = association_report()
    item = replace(
        report.checks[0],
        message=malicious,
        recommendation=malicious,
        evidence={"payload": malicious},
    )
    report = replace(report, checks=(item, *report.checks[1:]), limitations=(malicious,))
    html = render_report(report, sensitive_details=True)
    page = Page(html)
    assert malicious in " ".join(page.text)
    assert "&lt;script&gt;" in html
    assert not any(
        tag in {"script", "img"} or any(key.startswith("on") for key in attrs)
        for tag, attrs in page.tags
    )


@pytest.mark.parametrize("prefix", ["=", "+", "-", "@", "\t", "\r", "\n", "   =", "\ufeff="])
def test_at_s08_07_formula_export(tmp_path, prefix):
    report = association_report()
    text = prefix + "SUM(1,2)"
    item = replace(report.checks[0], message=text, recommendation=text)
    report = replace(report, checks=(item,))
    path = write_findings_csv(report, path=tmp_path / "findings.csv", sensitive_details=True)
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["message"] == "'" + text
    assert rows[0]["recommendation"] == "'" + text
    assert "SENSITIVE" in rows[0]["sensitivity"]
    assert report.checks[0].message == text


def test_at_s08_09_explicit_sensitive_export(tmp_path):
    report = association_report()
    item = replace(
        report.checks[0], message="PRIVATE-person", evidence={"ids": ["PRIVATE-observation"]}
    )
    report = replace(
        report,
        checks=(item, *report.checks[1:]),
        provenance=dict(report.provenance, sensitive_details=True),
    )
    public = write_report(report, output_dir=tmp_path / "public")
    private = write_report(report, output_dir=tmp_path / "private", sensitive_details=True)
    assert "PRIVATE" not in public["html"].read_text(encoding="utf-8")
    assert "PRIVATE" not in public["json"].read_text()
    assert "PRIVATE" in private["html"].read_text(encoding="utf-8")
    assert "Sensitive research output: do not publish without review" in private["html"].read_text(
        encoding="utf-8"
    )
    assert json.loads(public["manifest"].read_text())["sensitive_details"] is False
    assert json.loads(private["manifest"].read_text())["sensitive_details"] is True


@pytest.mark.parametrize("at_call", [1, 2, 3])
def test_at_s08_10_atomic_write_failure(tmp_path, monkeypatch, at_call):
    import neurocvguard._report_writes as writes

    paths = write_report(association_report(), output_dir=tmp_path)
    (tmp_path / "unrelated.txt").write_text("keep")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    original = writes.os.replace
    calls = 0

    def fail_once(source, target):
        nonlocal calls
        calls += 1
        if calls == at_call:
            raise OSError("injected replacement failure")
        return original(source, target)

    monkeypatch.setattr(writes.os, "replace", fail_once)
    with pytest.raises(InputValidationError):
        write_report(association_report(((8, 8), (8, 8))), output_dir=tmp_path, overwrite=True)
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before
    assert paths["html"].is_file()


def test_staging_failure_preserves_prior_report(tmp_path, monkeypatch):
    write_report(association_report(), output_dir=tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    original = Path.open

    def fail(path, *args, **kwargs):
        if path.parent.name.startswith(".neurocvguard-report-") and path.name == "report.html":
            raise OSError("injected staging failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail)
    with pytest.raises(InputValidationError):
        write_report(association_report(), output_dir=tmp_path, overwrite=True)
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before


def test_at_s08_11_overwrite_refusal(tmp_path):
    paths = write_report(association_report(), output_dir=tmp_path)
    before = paths["html"].read_bytes()
    with pytest.raises(InputValidationError, match="overwrite=True"):
        write_report(association_report(), output_dir=tmp_path)
    assert paths["html"].read_bytes() == before


def test_active_lock_is_not_removed(tmp_path):
    lock = tmp_path / ".neurocvguard-report.lock"
    lock.write_text("another writer")
    with pytest.raises(InputValidationError, match="lock"):
        write_report(association_report(), output_dir=tmp_path)
    assert lock.read_text() == "another writer"
    assert list(tmp_path.iterdir()) == [lock]


def test_new_bundle_failure_removes_only_owned_outputs(tmp_path, monkeypatch):
    import neurocvguard._report_writes as writes

    (tmp_path / "unrelated").write_text("keep")
    original = writes.os.replace

    def fail(source, target):
        if target.name == "report.html":
            raise OSError("injected")
        return original(source, target)

    monkeypatch.setattr(writes.os, "replace", fail)
    with pytest.raises(InputValidationError):
        write_report(association_report(), output_dir=tmp_path)
    assert [p.name for p in tmp_path.iterdir()] == ["unrelated"]


def test_missing_assets_fail_before_writing(tmp_path, monkeypatch):
    import neurocvguard.reporting as reporting

    monkeypatch.setattr(reporting, "files", lambda package: tmp_path / "absent")
    with pytest.raises(InputValidationError, match="assets"):
        write_report(association_report(), output_dir=tmp_path / "output")
    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize("bad", [1, "true", None])
def test_nonboolean_flags_refused(tmp_path, bad):
    with pytest.raises(InputValidationError):
        write_report(association_report(), output_dir=tmp_path, sensitive_details=bad)
    with pytest.raises(InputValidationError):
        write_report(association_report(), output_dir=tmp_path, overwrite=bad)
