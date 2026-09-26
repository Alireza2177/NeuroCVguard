"""Run the installed CLI outside the repository and print a sanitized real transcript."""

import json
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path

import neurocvguard
from neurocvguard import load_cohort, load_config, load_split_plan
from neurocvguard.workflows import audit_workflow

root = Path(__file__).resolve().parents[3]
console = Path(sysconfig.get_path("scripts")) / (
    "neurocvguard.exe" if sys.platform == "win32" else "neurocvguard"
)
module = [sys.executable, "-I", "-m", "neurocvguard"]
if "--ordinary" in sys.argv:
    assert Path(neurocvguard.__file__).is_relative_to(Path(sys.prefix))
transcript = {
    "version": neurocvguard.__version__,
    "python": sys.version.split()[0],
    "installation": "ordinary" if "--ordinary" in sys.argv else "editable",
    "working_directory": "<TEMP>/local journey ü",
    "commands": [],
}
with tempfile.TemporaryDirectory(prefix="ncg-s09-") as directory:
    work = Path(directory) / "local journey ü"
    work.mkdir()
    for filename in (
        "config.json",
        "cohort_clean.tsv",
        "features_shuffled.tsv",
        "ledger_declared_global.json",
        "splits_participant_overlap.json",
    ):
        shutil.copyfile(root / "fixtures" / filename, work / filename)

    def run(args, expected=0, entry="module"):
        prefix = module if entry == "module" else [str(console)]
        completed = subprocess.run(
            [*prefix, *args], cwd=work, capture_output=True, text=True, encoding="utf-8"
        )
        transcript["commands"].append(
            {
                "entry": entry,
                "args": args,
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
        assert completed.returncode == expected, transcript["commands"][-1]
        return completed

    run(["--version"])
    run(["init", "--out", "starter.json"])
    shared = ["--cohort", "cohort_clean.tsv", "--config", "config.json"]
    features = ["--features", "features_shuffled.tsv"]
    run(["validate", *shared, *features])
    run(["audit", *shared, *features, "--out", "cohort-audit"])
    run(["split", *shared, "--out", "splits"])
    run(["validate", *shared, "--splits", "splits/assignments.tsv"])
    args = [
        "audit",
        *shared,
        *features,
        "--splits",
        "splits/plan.json",
        "--ledger",
        "ledger_declared_global.json",
        "--fail-on",
        "warning",
        "--out",
    ]
    first = run([*args, "combined"], expected=3)
    second = run([*args, "console"], expected=3, entry="console")
    assert (first.stdout, first.stderr) == (second.stdout, second.stderr)
    config = load_config(work / "config.json")
    cohort = load_cohort(
        work / "cohort_clean.tsv", config=config, features=work / "features_shuffled.tsv"
    )
    plan = load_split_plan(work / "splits/plan.json", cohort=cohort, config=config)
    ledger = json.loads((work / "ledger_declared_global.json").read_text())
    expected = audit_workflow(cohort, config=config, plan=plan, ledger=ledger).to_dict()
    assert json.loads((work / "combined/report.json").read_text()) == expected
    assert (work / "combined/report.json").read_bytes() == (
        work / "console/report.json"
    ).read_bytes()
    run(["report", "--input", "combined/report.json", "--out", "render"])
    assert (work / "combined/report.json").read_bytes() == (
        work / "render/report.json"
    ).read_bytes()
    run([*args, "no-threshold", "--fail-on", "none"])
    assert (work / "combined/report.json").read_bytes() == (
        work / "no-threshold/report.json"
    ).read_bytes()
    run(
        ["audit", *shared, "--splits", "splits_participant_overlap.json", "--out", "overlap"],
        expected=3,
    )
    transcript["api_cli_projection_equal"] = True
    transcript["threshold_does_not_change_findings"] = True
# Isolated Python ignores PYTHONIOENCODING; ASCII JSON preserves Unicode paths
# losslessly even when Windows redirects stdout with a legacy code page.
print(json.dumps(transcript, indent=2, ensure_ascii=True))
