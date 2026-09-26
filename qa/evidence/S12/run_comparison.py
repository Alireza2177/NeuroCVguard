"""Exercise installed comparison and diagnostics on fictitious fixtures outside source cwd."""

import json
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from importlib.metadata import version
from pathlib import Path

import neurocvguard
from neurocvguard import compare_designs
from neurocvguard.comparison import load_evaluation

root = Path(__file__).resolve().parents[3]
ordinary = "--ordinary" in sys.argv
if ordinary:
    assert Path(neurocvguard.__file__).is_relative_to(Path(sys.prefix))
console = Path(sysconfig.get_path("scripts")) / (
    "neurocvguard.exe" if sys.platform == "win32" else "neurocvguard"
)
transcript = {
    "python": sys.version.split()[0],
    "dependencies": {name: version(name) for name in ("numpy", "pandas", "scipy", "scikit-learn")},
    "installation": "ordinary" if ordinary else "editable",
    "data": "Only documented fictitious repository fixtures; no patient data",
    "commands": [],
}
with tempfile.TemporaryDirectory(prefix="ncg-s12-") as directory:
    work = Path(directory) / "local comparison ü"
    work.mkdir()
    for filename in (
        "cohort_clean.tsv",
        "features_shuffled.tsv",
        "config.json",
        "splits_clean.json",
        "splits_participant_overlap.json",
    ):
        shutil.copyfile(root / "fixtures" / filename, work / filename)

    def run(args, expected=0, entry="module"):
        command = (
            [sys.executable, "-I", "-m", "neurocvguard"] if entry == "module" else [str(console)]
        )
        result = subprocess.run(
            [*command, *args], cwd=work, capture_output=True, text=True, encoding="utf-8"
        )
        transcript["commands"].append(
            {
                "entry": entry,
                "args": args,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        assert result.returncode == expected, transcript["commands"][-1]
        return result

    def read(path):
        return json.loads((work / path).read_text(encoding="utf-8"))

    run(["compare", "--help"])
    inputs = [
        "--cohort",
        "cohort_clean.tsv",
        "--features",
        "features_shuffled.tsv",
        "--splits",
        "splits_clean.json",
        "--config",
        "config.json",
    ]
    run(["evaluate", *inputs, "--out", "ordinary"])
    diagnostic = read("config.json")
    diagnostic["evaluation"]["diagnostic_allow_subject_overlap"] = True
    (work / "diagnostic.json").write_text(json.dumps(diagnostic), encoding="utf-8")
    diagnostic_inputs = list(inputs)
    diagnostic_inputs[diagnostic_inputs.index("--splits") + 1] = "splits_participant_overlap.json"
    diagnostic_inputs[-1] = "diagnostic.json"
    result = run(["evaluate", *diagnostic_inputs, "--out", "diagnostic"])
    assert "valid_for_objective=false" in result.stderr
    compare = [
        "compare",
        "--result",
        "A=ordinary/evaluation.private.json",
        "--result",
        "B=diagnostic/evaluation.private.json",
    ]
    module = run([*compare, "--out", "module"])
    console_result = run([*compare, "--out", "console"], entry="console")
    assert (module.stdout, module.stderr) == (console_result.stdout, console_result.stderr)
    records = {
        "A": load_evaluation(work / "ordinary/evaluation.private.json"),
        "B": load_evaluation(work / "diagnostic/evaluation.private.json"),
    }
    comparison = compare_designs(records)
    public = read("module/report.json")
    assert public == comparison.to_dict()
    assert (work / "module/report.json").read_bytes() == (work / "console/report.json").read_bytes()
    assert records["B"].diagnostic_only and not records["A"].diagnostic_only
    assert records["B"].pooled_metrics.n_participants == records["B"].n_participants
    for name in ("module", "diagnostic"):
        html = (work / name / "report.html").read_text(encoding="utf-8")
        assert "Do not report as evidence for unseen-participant generalization" in html
        assert "valid_for_objective=false" in html
        assert records["B"].feature_digest not in html
    run(["report", "--input", "module/report.json", "--out", "render"])
    assert (work / "render/report.json").read_bytes() == (work / "module/report.json").read_bytes()
    bad = [*compare]
    bad[2] = "A=ordinary/report.json"
    refused = run([*bad, "--out", "refused"], expected=2)
    assert "operational" in refused.stderr and not (work / "refused").exists()
    before = {p.name: p.read_bytes() for p in (work / "module").iterdir()}
    run([*compare, "--out", "module"], expected=2)
    assert before == {p.name: p.read_bytes() for p in (work / "module").iterdir()}
    failed = read("config.json")
    failed["evaluation"]["max_iter"] = 1
    (work / "incomplete.json").write_text(json.dumps(failed), encoding="utf-8")
    incomplete_inputs = list(inputs)
    incomplete_inputs[-1] = "incomplete.json"
    run(["evaluate", *incomplete_inputs, "--out", "incomplete"], expected=4)
    incomplete_compare = list(compare)
    incomplete_compare[4] = "B=incomplete/evaluation.private.json"
    run([*incomplete_compare, "--out", "incomplete-comparison", "--sensitive-details"])
    nulls = read("incomplete-comparison/report.json")["differences"]
    assert all(d["difference"] is None and "design_b_incomplete" in d["reasons"] for d in nulls)
    transcript.update(
        api_cli_parity=True,
        diagnostic_warning_preserved=True,
        rerender_stable=True,
        public_input_refused=True,
        existing_outputs_preserved=True,
        incomplete_deltas_null=True,
        ordinary_folds=len(records["A"].folds),
        diagnostic_folds=len(records["B"].folds),
        diagnostic_participants=records["B"].n_participants,
    )
print(json.dumps(transcript, indent=2, ensure_ascii=True))
