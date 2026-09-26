"""S09.A real command handlers, module/console entry points and local files."""

import json
import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest

from neurocvguard.cli import main
from neurocvguard.config import load_config

FIXTURES = Path(__file__).parents[1] / "fixtures"


def inputs(command="audit"):
    return [
        command,
        "--cohort",
        str(FIXTURES / "cohort_clean.tsv"),
        "--config",
        str(FIXTURES / "config.json"),
    ]


def process(args, directory, entry="module"):
    executable = Path(sysconfig.get_path("scripts")) / (
        "neurocvguard.exe" if sys.platform == "win32" else "neurocvguard"
    )
    command = (
        [sys.executable, "-I", "-m", "neurocvguard"] if entry == "module" else [str(executable)]
    )
    return subprocess.run(
        [*command, *args], cwd=directory, capture_output=True, text=True, encoding="utf-8"
    )


@pytest.mark.parametrize("args", [["--help"], ["--version"], [], ["audit", "--help"], ["audit"]])
def test_at_s09_01_cli_module_parity(tmp_path, args):
    module, console = process(args, tmp_path), process(args, tmp_path, "console")
    assert (module.returncode, module.stdout, module.stderr) == (
        console.returncode,
        console.stdout,
        console.stderr,
    )


def test_at_s09_02_init_editable(tmp_path, capsys):
    destination = tmp_path / "config.json"
    assert main(["init", "--out", str(destination)]) == 0
    config = load_config(destination)
    assert config.columns.observation_id == "observation_id"
    assert "no columns were inferred" in capsys.readouterr().out
    document = json.loads(destination.read_text())
    document["columns"]["subject_id"] = "participant_id"
    destination.write_text(json.dumps(document))
    assert load_config(destination).columns.subject_id == "participant_id"
    before = destination.read_bytes()
    assert main(["init", "--out", str(destination)]) == 2
    assert destination.read_bytes() == before


def test_at_s09_08_unimplemented_commands(tmp_path):
    help_result = process(["--help"], tmp_path)
    assert "{init,validate,audit,split,evaluate,compare,report}" in help_result.stdout
    # S12 compare requires records; S13 demo is still unimplemented.
    for command in ("compare", "demo"):
        assert process([command], tmp_path).returncode == 2


def test_audit_and_report_commands(tmp_path):
    destination = tmp_path / "audit"
    assert main([*inputs(), "--out", str(destination)]) == 0
    assert (
        main(
            [
                "report",
                "--input",
                str(destination / "report.json"),
                "--out",
                str(tmp_path / "render"),
            ]
        )
        == 0
    )
    assert (destination / "report.json").read_bytes() == (
        tmp_path / "render/report.json"
    ).read_bytes()
    assert (destination / "report.html").read_bytes() == (
        tmp_path / "render/report.html"
    ).read_bytes()


def test_validate_and_split_commands(tmp_path):
    assert main(inputs("validate")) == 0
    destination = tmp_path / "splits"
    assert main([*inputs("split"), "--out", str(destination)]) == 0
    assert (destination / "plan.json").is_file()
    assert (destination / "assignments.tsv").is_file()
    assert main([*inputs("validate"), "--splits", str(destination / "plan.json")]) == 0
