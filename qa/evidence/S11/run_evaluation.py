"""Real fictitious-fixture evaluation outside the source working directory."""

import json
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path

import neurocvguard
from neurocvguard import evaluate_baseline, load_cohort, load_config, load_split_plan
from neurocvguard.models import EvaluationResult

root = Path(__file__).resolve().parents[3]
ordinary = "--ordinary" in sys.argv
if ordinary:
    assert Path(neurocvguard.__file__).is_relative_to(Path(sys.prefix))
console = Path(sysconfig.get_path("scripts")) / (
    "neurocvguard.exe" if sys.platform == "win32" else "neurocvguard"
)
transcript = {
    "python": sys.version.split()[0],
    "version": neurocvguard.__version__,
    "installation": "ordinary" if ordinary else "editable",
    "data": "Documented fictitious repository fixtures; no patient data",
    "commands": [],
}
with tempfile.TemporaryDirectory(prefix="ncg-s11-") as directory:
    work = Path(directory) / "local evaluation ü"
    work.mkdir()
    for filename in (
        "cohort_clean.tsv",
        "features_shuffled.tsv",
        "config.json",
        "splits_clean.json",
        "splits_participant_overlap.json",
    ):
        shutil.copyfile(root / "fixtures" / filename, work / filename)
    tuning = json.loads((work / "config.json").read_text())
    tuning["evaluation"]["tune"] = True
    (work / "config.json").write_text(json.dumps(tuning), encoding="utf-8")

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

    run(["evaluate", "--help"])
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
    module = run(["evaluate", *inputs, "--out", "module"])
    console_result = run(["evaluate", *inputs, "--out", "console"], entry="console")
    assert (module.stdout, module.stderr) == (console_result.stdout, console_result.stderr)
    config = load_config(work / "config.json")
    cohort = load_cohort(
        work / "cohort_clean.tsv", config=config, features=work / "features_shuffled.tsv"
    )
    plan = load_split_plan(work / "splits_clean.json", cohort=cohort, config=config)
    api = evaluate_baseline(cohort, plan, config=config)
    assert all(not fold.inner_folds for fold in plan.folds)
    assert all(fold.inner_folds for fold in api.actual_plan.folds)
    assert len(api.fit_events) == 30
    assert all(len(fold.candidate_scores) == 3 for fold in api.folds)
    private = json.loads((work / "module/evaluation.private.json").read_text())
    assert EvaluationResult.from_dict(private) == api
    assert (work / "module/evaluation.private.json").read_bytes() == (
        work / "console/evaluation.private.json"
    ).read_bytes()
    assert json.loads((work / "module/report.json").read_text()) == api.to_dict()
    run(["report", "--input", "module/report.json", "--out", "render"])
    assert (work / "module/report.json").read_bytes() == (work / "render/report.json").read_bytes()
    document = config.to_dict()
    document["evaluation"]["max_iter"] = 1
    (work / "iterations.json").write_text(json.dumps(document), encoding="utf-8")
    limited = [*inputs]
    limited[-1] = "iterations.json"
    run(["evaluate", *limited, "--out", "incomplete"], expected=4)
    failed = json.loads((work / "incomplete/evaluation.private.json").read_text())
    assert failed["execution_status"] == "incomplete" and failed["pooled_metrics"] is None
    assert all(event["scope"] == "inner_train" for event in failed["fit_events"])
    assert all(fold["selected_C"] is None for fold in failed["folds"])
    document["evaluation"]["inner_splits"] = 20
    (work / "infeasible.json").write_text(json.dumps(document), encoding="utf-8")
    infeasible = [*inputs]
    infeasible[-1] = "infeasible.json"
    run(["evaluate", *infeasible, "--out", "infeasible"], expected=3)
    assert not (work / "infeasible").exists()
    overlap = [*inputs]
    overlap[overlap.index("--splits") + 1] = "splits_participant_overlap.json"
    run(["evaluate", *overlap, "--out", "refused"], expected=3)
    assert not (work / "refused").exists()
    transcript["api_cli_private_and_public_equal"] = True
    transcript["failed_folds_retained_without_pooled_score"] = True
    transcript["completed_folds"] = len(api.folds)
    transcript["participant_count"] = api.n_participants
    transcript["fit_events"] = len(api.fit_events)
    transcript["inner_failure_never_refits_outer"] = True
print(json.dumps(transcript, indent=2, ensure_ascii=True))
