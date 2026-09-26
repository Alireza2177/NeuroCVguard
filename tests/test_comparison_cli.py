"""S12.C CLI, report context, explicit warnings and linked privacy suppression."""

import json
from dataclasses import replace

import pytest
from sklearn.pipeline import Pipeline
from test_cli_commands import process
from test_comparison import record
from test_diagnostic_evaluation import diagnostic_inputs
from test_evaluation_cli import arguments

from neurocvguard import compare_designs, write_report
from neurocvguard.cli import main
from neurocvguard.models import AuditReport, ComparisonResult
from neurocvguard.reporting import render_report
from neurocvguard.serialization import canonical_json


def files(tmp_path):
    paths = [tmp_path / "a.json", tmp_path / "b.json"]
    results = [record(0.25), record(0.75)]
    for path, result in zip(paths, results, strict=True):
        path.write_text(canonical_json(result.to_operational_dict()), encoding="utf-8")
    return paths, results


def compare_args(paths, output):
    return [
        "compare",
        "--result",
        f"A={paths[0]}",
        "--result",
        f"B={paths[1]}",
        "--out",
        str(output),
    ]


def test_compare_cli_api_parity_no_fit_and_rerender(tmp_path, monkeypatch, capsys):
    paths, results = files(tmp_path)
    monkeypatch.setattr(Pipeline, "fit", lambda *a, **k: pytest.fail("compare fitted a model"))
    output = tmp_path / "out"
    args = compare_args(paths, output)
    assert main(args) == 0
    logged = capsys.readouterr()
    assert "signed score_difference=A-B" in logged.out
    assert "private-observation" not in logged.out + logged.err
    public = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert public == compare_designs(dict(zip(("A", "B"), results, strict=True))).to_dict()
    assert public["differences"][0]["difference"] == -0.5
    assert public["designs"][0]["context"]["training_participants_min"] == 20
    assert not (output / "evaluation.private.json").exists()
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    assert main(args) == 2
    assert before == {p.name: p.read_bytes() for p in output.iterdir()}
    assert main(args + ["--overwrite"]) == 0
    rerender = tmp_path / "render"
    assert main(["report", "--input", str(output / "report.json"), "--out", str(rerender)]) == 0
    assert (output / "report.json").read_bytes() == (rerender / "report.json").read_bytes()
    html = (output / "report.html").read_text(encoding="utf-8")
    for text in (
        "Pooled participant class support",
        "Training participants per fold",
        "Recorded C values",
        "not causal",
        "-0.5",
    ):
        assert text in html
    assert all(result.feature_digest not in html for result in results)


def test_compare_module_console_parity(tmp_path):
    paths, _ = files(tmp_path)
    module = process(compare_args(paths, tmp_path / "module"), tmp_path)
    console = process(compare_args(paths, tmp_path / "console"), tmp_path, "console")
    assert module.returncode == console.returncode == 0
    assert (module.stdout, module.stderr) == (console.stdout, console.stderr)
    assert (tmp_path / "module/report.json").read_bytes() == (
        tmp_path / "console/report.json"
    ).read_bytes()


@pytest.mark.parametrize("kind", ["public", "duplicate", "malformed", "single", "pickle"])
def test_at_s12_08_compare_rejects_invalid_sources_actionably(tmp_path, capsys, kind):
    paths, results = files(tmp_path)
    args = compare_args(paths, tmp_path / "out")
    if kind == "public":
        paths[0].write_text(canonical_json(results[0].to_dict()))
    elif kind == "duplicate":
        args[4] = f"A={paths[1]}"
    elif kind == "malformed":
        args[2] = str(paths[0])
    elif kind == "single":
        del args[3:5]
    else:
        args[2] = "A=model.pkl"
    assert main(args) == 2
    message = capsys.readouterr().err
    assert "evaluation.private.json" in message and "operational" in message
    assert "do not reconstruct" in message
    assert not (tmp_path / "out").exists()


def test_suppression_keeps_mismatch_reasons_and_cannot_recover_cells(tmp_path):
    original = record()
    metrics = replace(original.pooled_metrics, confusion_matrix=((19, 1), (0, 20)))
    a = replace(original, pooled_metrics=metrics)
    b = replace(original, cohort_digest="a" * 64)
    result = compare_designs({"A": a, "B": b})
    public = result.to_dict()
    assert public["designs"][0]["metrics"] is None
    assert public["designs"][1]["metrics"] is not None
    assert all(
        d["difference"] is None and d["reasons"] == ["privacy_small_cells"]
        for d in public["differences"]
    )
    assert ComparisonResult.from_dict(public).to_dict() == public
    assert result.to_dict(sensitive_details=True)["designs"][0]["metrics"] is not None
    assert "cohort_mismatch" in str(result.to_dict(sensitive_details=True)["differences"])
    write_report(result, output_dir=tmp_path)
    assert "privacy_small_cells" in (tmp_path / "report.html").read_text()


def test_context_labels_are_projected_and_sensitive_names_escaped():
    a = record()
    data = a.to_operational_dict()
    data["class_order"] = ["PRIVATE@email.invalid", "C:/PRIVATE/data"]
    data["positive_class"] = data["class_order"][0]
    for metrics in (data["pooled_metrics"], *[f["metrics"] for f in data["folds"]]):
        for i, item in enumerate(metrics["per_class"]):
            item["class_label"] = data["class_order"][i]
    altered = type(a).from_dict(data)
    result = compare_designs({"<script>alert(1)</script>": altered, "second": altered})
    public = result.to_dict()
    assert "PRIVATE" not in canonical_json(public)
    assert ComparisonResult.from_dict(public).to_dict() == public
    html = render_report(result, sensitive_details=True)
    assert "<script>" not in html and "&lt;script&gt;" in html


def test_at_s12_05_diagnostic_cli_and_every_report_keeps_warning(tmp_path, capsys):
    _, _, config = diagnostic_inputs()
    config_path = tmp_path / "diagnostic.json"
    config_path.write_text(canonical_json(config.to_dict()))
    args = arguments(tmp_path / "diagnostic")
    args[args.index("--config") + 1] = str(config_path)
    args[args.index("--splits") + 1] = args[args.index("--splits") + 1].replace(
        "splits_clean", "splits_participant_overlap"
    )
    assert main(args) == 0
    assert "valid_for_objective=false" in capsys.readouterr().err
    private = tmp_path / "diagnostic/evaluation.private.json"
    public = json.loads((private.parent / "report.json").read_text())
    assert AuditReport.from_dict(public).to_dict() == public
    paths, _ = files(tmp_path)
    compared = tmp_path / "comparison"
    assert main(compare_args([private, paths[1]], compared)) == 0
    assert "Diagnostic only" in capsys.readouterr().err
    for directory in (private.parent, compared):
        html = (directory / "report.html").read_text()
        assert "valid_for_objective=false" in html
        assert "Do not report as evidence for unseen-participant generalization" in html
        assert "aggregation does not remove" in html
    rendered = tmp_path / "rerender"
    assert main(["report", "--input", str(compared / "report.json"), "--out", str(rendered)]) == 0
    assert "valid_for_objective=false" in (rendered / "report.html").read_text()


def test_at_s12_09_report_retains_distribution_and_upstream_limits():
    result = compare_designs({"A": record(), "B": record(0.6)})
    html = render_report(result)
    for text in (
        "held-out distributions",
        "training sizes",
        "class coverage",
        "not causal",
        "Upstream preprocessing",
        "No winning scientific design",
    ):
        assert text in html
