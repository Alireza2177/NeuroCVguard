"""S14 executable documentation, API/config/rule coverage and local links."""

import importlib
import inspect
import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from neurocvguard.config import AuditConfig

ROOT = Path(__file__).resolve().parents[1]


def test_at_s14_02_every_public_export_documented():
    reference = (ROOT / "docs/api.rst").read_text(encoding="utf-8")
    inventory = json.loads((ROOT / "qa/evidence/S14/api_inventory.json").read_text())
    for module_name, names in inventory.items():
        module = importlib.import_module(module_name)
        actual = {
            name
            for name, value in vars(module).items()
            if not name.startswith("_")
            and (inspect.isclass(value) or inspect.isfunction(value))
            and value.__module__ == module_name
        }
        assert actual == set(names)
        for name in actual:
            assert f":: {module_name}.{name}\n" in reference


def test_at_s14_03_configuration_reference_matches_contract():
    schema = json.loads((ROOT / "contracts/config.schema.json").read_text())
    defaults = AuditConfig().to_dict()
    reference = (ROOT / "docs/configuration.md").read_text(encoding="utf-8")
    for section, definition in schema["properties"].items():
        for key, rules in definition.get("properties", {"": definition}).items():
            name = f"{section}.{key}" if key else section
            default = defaults[section][key] if key else defaults[section]
            required = key in definition.get("required", []) if key else True
            assert (
                f"| `{name}` | `{json.dumps(default)}` | `{json.dumps(rules)}` | {required} |"
            ) in reference


def test_rule_catalog_and_limitations_discoverable():
    reference = (ROOT / "docs/rules.md").read_text(encoding="utf-8")
    for rule in json.loads((ROOT / "qa/rule_catalog.json").read_text()):
        assert rule["id"] in reference and rule["meaning"] in reference
    for name in ("index.md", "quickstart.md", "limitations.md"):
        page = (ROOT / "docs" / name).read_text(encoding="utf-8").lower()
        assert "upstream preprocessing" in page and "unassessable" in page


def test_at_s14_01_local_markdown_links_exist():
    for page in [ROOT / "README.md", *(ROOT / "docs").glob("*.md")]:
        for target in re.findall(r"\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            assert (page.parent / target.split("#", 1)[0]).is_file(), (page.name, target)


def test_at_s14_04_quickstart_commands_verbatim(tmp_path):
    """Every copyable quickstart command runs in a fresh Unicode/space directory."""
    directory = tmp_path / "fictitious study Δ"
    directory.mkdir()
    page = (ROOT / "docs/quickstart.md").read_text(encoding="utf-8")
    commands = re.findall(r"^python -m neurocvguard .+$", page, re.M)
    assert len(commands) == 8
    for line in commands:
        result = subprocess.run(
            [sys.executable, *shlex.split(line)[1:]],
            cwd=directory,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0, (line, result.stderr)
    assert (directory / "local_outputs/rendered/report.html").is_file()


@pytest.mark.parametrize(
    "command", ["init", "validate", "audit", "split", "evaluate", "compare", "report", "demo"]
)
def test_at_s14_04_documented_subcommands_help(command):
    result = subprocess.run(
        [sys.executable, "-m", "neurocvguard", command, "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0 and "--help" in result.stdout


def test_at_s14_06_08_metadata_and_human_review_remain_honest():
    assert not (ROOT / "CITATION.cff").exists()
    assert "NOT FINALIZED" in (ROOT / "LICENSE").read_text()
    assert "Public release is blocked" in (ROOT / "SECURITY.md").read_text()
    ownership = (ROOT / "docs/ownership.md").read_text()
    assert "Human walkthrough: pending" in ownership
    assert "External-user trial: not performed" in ownership


@pytest.mark.parametrize(
    "page",
    [
        "association_diagnostics",
        "cohort_checks",
        "comparison",
        "evaluation",
        "input_tables",
        "preprocessing_provenance",
        "reporting",
        "split_audits",
        "split_generation",
        "synthetic_examples",
    ],
)
def test_at_s14_04_all_python_guide_blocks(page, tmp_path):
    """Run authored source examples, never arbitrary user/data-supplied code."""
    shutil.copytree(ROOT / "fixtures", tmp_path / "fixtures")
    text = (ROOT / "docs" / (page + ".md")).read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", text, re.S)
    assert blocks
    preparation = ""
    if page == "comparison":
        # The guide explicitly requires existing private results. Build those
        # prerequisites from synthetic fixtures; no undocumented user file.
        preparation = """
from pathlib import Path
from neurocvguard import load_config, load_cohort, load_split_plan, evaluate_baseline
from neurocvguard.serialization import canonical_json
c = load_config("fixtures/config.json")
x = load_cohort("fixtures/cohort_clean.tsv", config=c, features="fixtures/features_shuffled.tsv")
p = load_split_plan("fixtures/splits_clean.json", cohort=x, config=c)
r = evaluate_baseline(x, p, config=c)
for name in ("a", "b"):
    d = Path("local_outputs") / name
    d.mkdir(parents=True)
    (d / "evaluation.private.json").write_text(canonical_json(r.to_operational_dict()))
"""
    script = tmp_path / "guide.py"
    script.write_text(preparation + "\n".join(blocks), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, (page, result.stderr)
