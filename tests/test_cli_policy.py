"""S09.B exit decisions, stream privacy and safe local output controls."""

import json
from dataclasses import replace

import pytest
from test_cli_commands import FIXTURES, inputs
from test_report_projection import association_report

from neurocvguard import load_cohort, load_config, load_split_plan
from neurocvguard.cli import main
from neurocvguard.reporting import write_configured_report
from neurocvguard.workflows import audit_workflow


def overlap_args(destination):
    return [
        *inputs(),
        "--splits",
        str(FIXTURES / "splits_participant_overlap.json"),
        "--out",
        str(destination),
    ]


def test_at_s09_03_threshold_after_report(tmp_path):
    assert main(overlap_args(tmp_path)) == 3
    report = json.loads((tmp_path / "report.json").read_text())
    assert any(row["status"] == "fail" and row["severity"] == "error" for row in report["checks"])
    assert (tmp_path / "report.html").is_file()
    assert report["execution_status"] == "partial"


@pytest.mark.parametrize(
    "text",
    [
        '{"PRIVATE-key": 2}',
        '{"schema_version":"99"}',
        '{"schema_version":"1.0","schema_version":"1.0"}',
        "{invalid",
    ],
)
def test_at_s09_04_malformed_config(tmp_path, capsys, text):
    source = tmp_path / "PRIVATE-config.json"
    source.write_text(text)
    args = inputs()
    args[-1] = str(source)
    assert main([*args, "--out", str(tmp_path / "out")]) == 2
    stream = capsys.readouterr()
    assert "strict JSON" in stream.err and "column mappings" in stream.err
    assert "PRIVATE" not in stream.err + stream.out
    assert not (tmp_path / "out").exists()


def test_at_s09_05_none_preserves_findings(tmp_path):
    assert main(overlap_args(tmp_path / "error")) == 3
    assert main([*overlap_args(tmp_path / "none"), "--fail-on", "none"]) == 0
    assert (tmp_path / "error/report.json").read_bytes() == (
        tmp_path / "none/report.json"
    ).read_bytes()


def test_warning_policy_and_validate_report(tmp_path):
    assert main([*inputs("validate"), "--out", str(tmp_path), "--fail-on", "warning"]) == 3
    assert (tmp_path / "report.json").is_file()


def test_at_s09_06_streams_and_overwrite(tmp_path, capsys):
    args = [*inputs(), "--out", str(tmp_path)]
    assert main(args) == 0
    streams = capsys.readouterr()
    assert "INFO: Validating" in streams.err and "Computing scoped" in streams.err
    assert "report.json" in streams.out and "execution=partial" in streams.out
    assert "INFO:" not in streams.out and "Artifacts" not in streams.err
    assert str(tmp_path) not in streams.out + streams.err
    original = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    assert main(args) == 2
    assert original == {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    assert main([*args, "--overwrite"]) == 0


def test_at_s09_07_sensitive_split_announcement(tmp_path, capsys):
    assert main([*inputs("split"), "--out", str(tmp_path)]) == 0
    streams = capsys.readouterr()
    assert "observation IDs" in streams.err and "Do not publish" in streams.err
    assert "obs-001" not in streams.err + streams.out
    assert (tmp_path / "README.SENSITIVE.txt").is_file()


@pytest.mark.parametrize("via_config", [True, False])
def test_sensitive_report_requires_explicit_choice(tmp_path, capsys, via_config):
    document = json.loads((FIXTURES / "config.json").read_text())
    document["report"]["sensitive_details"] = via_config
    source = tmp_path / "config.json"
    source.write_text(json.dumps(document))
    args = inputs()
    args[-1] = str(source)
    args += ["--out", str(tmp_path / "out")]
    if not via_config:
        args += ["--sensitive-details"]
    assert main(args) == 0
    assert "Sensitive report requested" in capsys.readouterr().err
    data = json.loads((tmp_path / "out/report.json").read_text())
    assert data["provenance"]["sensitive_details"] is True


@pytest.mark.parametrize("threshold,cells,visible", [(2, 3, True), (6, 5, False)])
def test_configured_projection_used_once(tmp_path, threshold, cells, visible):
    config = load_config(FIXTURES / "config.json")
    config = replace(config, report=replace(config.report, small_cell_threshold=threshold))
    result = association_report(((cells, cells), (cells, cells)))
    write_configured_report(result, config=config, output_dir=tmp_path)
    data = json.loads((tmp_path / "report.json").read_text())
    assert data == result.to_dict(small_cell_threshold=threshold)
    assert any("display_table" in row["evidence"] for row in data["checks"]) == visible


@pytest.mark.parametrize("debug", [False, True])
def test_unexpected_failure_is_sanitized(tmp_path, capsys, monkeypatch, debug):
    import neurocvguard.workflows as workflows

    def broken(*args, **kwargs):
        raise RuntimeError("PRIVATE-row-value C:/Users/PRIVATE-user/input.tsv")

    monkeypatch.setattr(workflows, "audit_workflow", broken)
    assert main((["--debug"] if debug else []) + [*inputs(), "--out", str(tmp_path)]) == 1
    stream = capsys.readouterr()
    assert "PRIVATE" not in stream.out + stream.err
    assert ("Sanitized traceback" in stream.err) == debug
    assert not list(tmp_path.iterdir())


def test_bad_invocation_no_private_echo(capsys):
    with pytest.raises(SystemExit) as error:
        main(["PRIVATE-command"])
    assert error.value.code == 2
    assert "PRIVATE" not in capsys.readouterr().err


def test_structural_errors_not_suppressed_by_none(tmp_path):
    args = inputs()
    args[2] = str(tmp_path / "missing.tsv")
    assert main([*args, "--out", str(tmp_path / "out"), "--fail-on", "none"]) == 2
    assert not (tmp_path / "out").exists()


def test_infeasible_planning_exit(tmp_path):
    args = inputs("split")
    args[2] = str(FIXTURES / "cohort_changing_target.tsv")
    assert main([*args, "--out", str(tmp_path / "out")]) == 3
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("filename", ["evaluation_schema_example.json", "config.json"])
def test_report_rejects_nonreport_records(tmp_path, filename):
    assert (
        main(["report", "--input", str(FIXTURES / filename), "--out", str(tmp_path / "out")]) == 2
    )
    assert not (tmp_path / "out").exists()


def test_report_version_rejected(tmp_path):
    data = json.loads((FIXTURES / "report_schema_example.json").read_text())
    data["schema_version"] = "99"
    source = tmp_path / "input.json"
    source.write_text(json.dumps(data))
    assert main(["report", "--input", str(source), "--out", str(tmp_path / "out")]) == 2


def test_comparison_manifest_required(tmp_path):
    source = tmp_path / "comparison.json"
    source.write_bytes((FIXTURES / "comparison_schema_example.json").read_bytes())
    args = ["report", "--input", str(source), "--out", str(tmp_path / "out")]
    assert main(args) == 2
    (tmp_path / "report.manifest.json").write_text(
        json.dumps({"schema_version": "1.0", "result_schema": "comparison-summary"})
    )
    assert main(args) == 0


def test_combined_scopes_and_declared_provenance(tmp_path):
    config = load_config(FIXTURES / "config.json")
    cohort = load_cohort(FIXTURES / "cohort_clean.tsv", config=config)
    plan = load_split_plan(
        FIXTURES / "splits_participant_overlap.json", cohort=cohort, config=config
    )
    ledger = json.loads((FIXTURES / "ledger_declared_global.json").read_text())
    report = audit_workflow(cohort, config=config, plan=plan, ledger=ledger)
    ids = [check.instance_id for check in report.checks]
    assert len(ids) == len(set(ids))
    assert {item.split(":")[0] for item in ids} == {"cohort", "split", "provenance"}
    declared = [row for row in report.checks if row.rule_id == "NCG-PROV-002"]
    assert declared and all(row.evidence_kind == "declared" for row in declared)
    assert any(
        row.rule_id == "NCG-PROV-001" and row.status == "not_assessable" for row in report.checks
    )
    args = [*overlap_args(tmp_path), "--ledger", str(FIXTURES / "ledger_declared_global.json")]
    assert main(args) == 3
    assert json.loads((tmp_path / "report.json").read_text()) == report.to_dict()
