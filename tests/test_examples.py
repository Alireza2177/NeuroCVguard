"""Run every self-contained tutorial outside the source working directory."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from neurocvguard import load_cohort, load_config

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = sorted((ROOT / "examples").glob("[0-9][0-9]_*.py"))


@pytest.fixture(scope="module")
def outputs(tmp_path_factory):
    root = tmp_path_factory.mktemp("all-tutorials")
    assert len(SCRIPTS) == 5
    for script in SCRIPTS:
        destination = root / script.stem
        result = subprocess.run(
            [sys.executable, "-I", str(script), "--out", str(destination), "--sensitive-details"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        assert result.returncode == 0, result.stderr
        assert "synthetic" in result.stdout.lower() and "no patient data" in result.stderr
    return root


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.stem)
def test_at_s13_05_every_script_complete_with_no_hidden_inputs(outputs, script):
    directory = outputs / script.stem
    manifest = json.loads((directory / "demo.private.json").read_text(encoding="utf-8"))
    assert manifest["example"] == int(script.name[:2])
    assert manifest["execution_status"] == "completed"
    assert str(script) in manifest["command"]
    assert (directory / "report.html").is_file()


def test_site_example_domain_constraints_and_missing_class_metrics(outputs):
    directory = outputs / "03_site_held_out"
    data = json.loads((directory / "site-held-out.evaluation.private.json").read_text())
    assert data["objective"] == "unseen_site"
    assert any(
        f["metrics"]["balanced_accuracy"]["reason"] == "missing_true_class" for f in data["folds"]
    )
    metadata = pd.read_csv(directory / "cohort.tsv", sep="\t").set_index("observation_id")
    for fold in data["actual_plan"]["folds"]:
        assert set(metadata.loc[fold["train_ids"], "site"]).isdisjoint(
            metadata.loc[fold["test_ids"], "site"]
        )
        assert set(metadata.loc[fold["train_ids"], "subject_id"]).isdisjoint(
            metadata.loc[fold["test_ids"], "subject_id"]
        )
        assert metadata.loc[fold["train_ids"], "target"].nunique() == 2


def test_provenance_example_never_authenticates_declaration(outputs):
    directory = outputs / "04_preprocessing_provenance"
    declared = json.loads((directory / "report.json").read_text())
    unknown = json.loads((directory / "unknown.report.json").read_text())
    assert any(
        c["rule_id"] == "NCG-PROV-002" and c["evidence_kind"] == "declared"
        for c in declared["checks"]
    )
    assert any(
        c["rule_id"] == "NCG-PROV-001" and c["status"] == "not_assessable"
        for c in unknown["checks"]
    )
    assert not declared["provenance"]["upstream_preprocessing_verified"]
    assert not list(directory.glob("*.evaluation.private.json"))


def test_feature_example_uses_explicit_keys_not_row_order(outputs):
    directory = outputs / "05_explicit_feature_join"
    config = load_config(directory / "config.json")
    meta = pd.read_csv(directory / "cohort.tsv", sep="\t")
    features = pd.read_csv(directory / "features.tsv", sep="\t")
    assert meta.scan_key.tolist() == list(reversed(features.scan_key.tolist()))
    cohort = load_cohort(
        directory / "cohort.tsv", features=directory / "features.tsv", config=config
    )
    actual = cohort.features.set_index("scan_key")
    expected = features.set_index("scan_key").loc[actual.index]
    pd.testing.assert_frame_equal(actual, expected)
