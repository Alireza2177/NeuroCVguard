"""S05 sensitive plan exports, provenance and deterministic integrity."""

import json
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest
from test_generation import configuration, family_cohort

from neurocvguard import load_split_plan, make_splits
from neurocvguard.config import Objective, SplitConfig, SplitScheme, StudyConfig
from neurocvguard.errors import (
    ConfigurationError,
    InputValidationError,
    PlanningError,
    SplitValidationError,
    UnsupportedDesignError,
)
from neurocvguard.io import write_rejected_plan
from neurocvguard.models import AuditReport, SplitPlan
from neurocvguard.rules import PLAN_RULES
from neurocvguard.serialization import canonical_json, json_digest


def test_canonical_plan_and_sensitive_assignment_export(tmp_path):
    cohort = family_cohort()
    config = configuration(cohort)
    plan = make_splits(cohort, config=config)
    paths = plan.write(tmp_path / "first")
    assert set(paths) == {"plan", "assignments", "notice", "generation_report"}
    assert all(p.is_file() for p in paths.values())
    assert "SENSITIVE" in paths["notice"].read_text()
    assert paths["plan"].read_text() == canonical_json(plan.to_operational_dict()) + "\n"
    assert load_split_plan(paths["plan"], cohort=cohort, config=config) == plan
    imported = load_split_plan(paths["assignments"], cohort=cohort, config=config)
    assert imported.folds == plan.folds and imported.origin == "imported"
    assert imported.cohort_digest == plan.cohort_digest
    assert (
        paths["assignments"].read_text().splitlines()[0]
        == "repeat_id\tfold_id\trole\tobservation_id"
    )
    payload = json.loads(paths["plan"].read_text())
    plan_id = payload.pop("plan_id")
    assert plan_id == json_digest(payload)
    report = AuditReport.from_json(paths["generation_report"].read_text())
    assert report.provenance["sensitive_details"] is True
    assert report.provenance["versions"]["numpy"]
    assert any(c.evidence.get("plan_id") == plan.plan_id for c in report.checks)
    other = plan.write(tmp_path / "second")
    assert all(paths[name].read_bytes() == other[name].read_bytes() for name in paths)
    assert not any(p.name.startswith(".neurocvguard-") for p in paths["plan"].parent.iterdir())


@pytest.mark.parametrize(
    "collision", ["plan.json", "assignments.tsv", "README.SENSITIVE.txt", "generation.private.json"]
)
def test_all_output_conflicts_preflight_before_writes(tmp_path, collision):
    cohort = family_cohort()
    plan = make_splits(cohort, config=configuration(cohort))
    (tmp_path / collision).write_text("keep-existing")
    (tmp_path / "unrelated.txt").write_text("keep-unrelated")
    with pytest.raises(InputValidationError, match="already exists"):
        plan.write(tmp_path)
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted([collision, "unrelated.txt"])
    assert (tmp_path / collision).read_text() == "keep-existing"
    plan.write(tmp_path, overwrite=True)
    assert (tmp_path / "unrelated.txt").read_text() == "keep-unrelated"
    assert (tmp_path / collision).read_text() != "keep-existing"


def test_rejected_diagnostics_are_separate_and_public_safe(tmp_path):
    cohort = family_cohort((2, 2, 2))
    with pytest.raises(PlanningError) as caught:
        make_splits(cohort, config=configuration(cohort, n_splits=5))
    error = caught.value
    paths = write_rejected_plan(error.report, output_dir=tmp_path / "rejected")
    assert "rejected-plan.private.json" in paths
    assert not (tmp_path / "rejected/plan.json").exists()
    assert not (tmp_path / "rejected/assignments.tsv").exists()
    public = json.dumps(error.report.to_dict())
    assert all(person not in public for person in cohort.metadata.subject_id)
    report = AuditReport.from_json(paths["rejected-plan.private.json"].read_text())
    assert report.execution_status == "blocked"
    with pytest.raises(InputValidationError):
        write_rejected_plan(error.report, output_dir=tmp_path / "rejected")
    write_rejected_plan(error.report, output_dir=tmp_path / "rejected", overwrite=True)
    plan = make_splits(cohort, config=configuration(cohort))
    with pytest.raises(InputValidationError, match="separate directory"):
        plan.write(tmp_path / "rejected", overwrite=True)
    plan.write(tmp_path / "accepted")
    with pytest.raises(InputValidationError, match="separate directory"):
        write_rejected_plan(error.report, output_dir=tmp_path / "accepted")


def test_loaded_plan_never_acquires_current_generation_versions(tmp_path):
    cohort = family_cohort()
    plan = make_splits(cohort, config=configuration(cohort))
    loaded = SplitPlan.from_dict(plan.to_operational_dict())
    paths = loaded.write(tmp_path / "loaded")
    assert set(paths) == {"plan", "assignments", "notice"}
    plan.write(tmp_path / "with-history")
    with pytest.raises(InputValidationError, match="provenance cannot be attributed"):
        loaded.write(tmp_path / "with-history", overwrite=True)
    with pytest.raises(SplitValidationError, match="generation_report"):
        SplitPlan.from_dict({**plan.to_operational_dict(), "generation_report": {}})


def test_inner_folds_retained_only_in_json(clean_cohort, tmp_path):
    from test_split_audit import nested_plan

    plan = nested_plan(clean_cohort)
    paths = plan.write(tmp_path)
    restored = SplitPlan.from_json(paths["plan"].read_text())
    assert restored == plan and restored.folds[0].inner_folds
    assert all(
        line.split("\t")[2] in ("train", "test")
        for line in paths["assignments"].read_text().splitlines()[1:]
    )


def test_no_file_io_or_input_mutation_during_generation(tmp_path, monkeypatch):
    cohort = family_cohort()
    config = configuration(cohort)
    before = cohort.metadata
    settings = config.to_dict()
    monkeypatch.chdir(tmp_path)
    make_splits(cohort, config=config)
    assert list(tmp_path.iterdir()) == []
    pd.testing.assert_frame_equal(cohort.metadata, before)
    assert config.to_dict() == settings


def test_invalid_generated_training_no_seed_search(monkeypatch):
    import neurocvguard.splitting as module

    cohort = family_cohort()
    data = cohort.metadata
    data["diagnosis"] = ["rare" if f == "g-00" else "common" for f in data.family]
    cohort = type(cohort)(data, None, cohort.columns, tuple(data.observation_id))
    calls = []
    original = module.StratifiedGroupKFold

    class Spy(original):
        def __init__(self, **kwargs):
            calls.append(kwargs)
            super().__init__(**kwargs)

    monkeypatch.setattr(module, "StratifiedGroupKFold", Spy)
    config = configuration(cohort, seed=42)
    with pytest.raises(PlanningError) as caught:
        make_splits(cohort, config=config)
    assert calls == [dict(n_splits=3, shuffle=True, random_state=42)]
    assert any(
        c.rule_id == "NCG-SPLIT-005" and c.status == "fail" for c in caught.value.report.checks
    )
    limitation = next(c for c in caught.value.report.checks if c.rule_id == "NCG-PLAN-003")
    assert limitation.status == "fail" and limitation.severity == "warning"
    assert limitation.evidence["class_has_fewer_than_two_components"] is True


def test_plan_catalog_matches_normative_definitions():
    catalog = json.loads((Path(__file__).parent.parent / "qa/rule_catalog.json").read_text())
    expected = [row for row in catalog if row["stage"] == "S05"]
    assert [
        dict(
            id=r.id,
            name=r.name,
            trigger_severity=r.trigger_severity.value,
            evidence_kind=r.evidence_kind.value,
            meaning=r.meaning,
            stage=r.stage,
        )
        for r in PLAN_RULES
    ] == expected


@pytest.mark.parametrize("kind", ["audit_only", "imported", "huge_seed", "mapping"])
def test_unsupported_or_mismatched_requests(kind):
    cohort = family_cohort()
    config = configuration(cohort)
    if kind == "audit_only":
        config = replace(config, study=StudyConfig(Objective.AUDIT_ONLY))
    if kind == "imported":
        config = replace(config, split=SplitConfig(SplitScheme.IMPORTED, None))
    if kind == "huge_seed":
        with pytest.raises(ConfigurationError, match="seed"):
            replace(config.split, seed=2**32)
        return
    if kind == "mapping":
        config = replace(config, columns=replace(config.columns, session="different"))
    with pytest.raises((ConfigurationError, UnsupportedDesignError)):
        make_splits(cohort, config=config)


def test_output_validation(tmp_path):
    cohort = family_cohort()
    plan = make_splits(cohort, config=configuration(cohort))
    with pytest.raises(InputValidationError, match="boolean"):
        plan.write(tmp_path, overwrite=1)
    with pytest.raises(InputValidationError, match="local directory"):
        plan.write("https://example.invalid/output")
    with pytest.raises(InputValidationError, match="blocked"):
        write_rejected_plan(plan.generation_report, output_dir=tmp_path)
    bad = replace(
        plan, origin="imported", plan_id="bad", folds=(replace(plan.folds[0], repeat_id=" r0"),)
    )
    with pytest.raises(InputValidationError, match="identities"):
        bad.write(tmp_path)
    assert not list(tmp_path.iterdir())


def test_no_overwrite_race_preserves_competing_file(tmp_path, monkeypatch):
    import neurocvguard.io as module

    cohort = family_cohort()
    plan = make_splits(cohort, config=configuration(cohort))
    original = module.os.open

    def race(path, flags, *args, **kwargs):
        if Path(path).name == "assignments.tsv" and flags & module.os.O_EXCL:
            Path(path).write_text("competing writer")
        return original(path, flags, *args, **kwargs)

    monkeypatch.setattr(module.os, "open", race)
    with pytest.raises(InputValidationError, match="destination conflicts"):
        plan.write(tmp_path)
    assert [p.name for p in tmp_path.iterdir()] == ["assignments.tsv"]
    assert (tmp_path / "assignments.tsv").read_text() == "competing writer"


def test_staging_failure_does_not_replace_existing_artifacts(tmp_path, monkeypatch):
    cohort = family_cohort()
    plan = make_splits(cohort, config=configuration(cohort))
    (tmp_path / "plan.json").write_text("original")
    original = Path.open

    def fail(path, *args, **kwargs):
        if path.name == "assignments.tsv" and path.parent.name.startswith(".neurocvguard-"):
            raise OSError("simulated storage failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail)
    with pytest.raises(InputValidationError, match="storage failure"):
        plan.write(tmp_path, overwrite=True)
    assert [p.name for p in tmp_path.iterdir()] == ["plan.json"]
    assert (tmp_path / "plan.json").read_text() == "original"


def test_documented_planning_example(tmp_path, monkeypatch):
    text = (Path(__file__).parent.parent / "docs/split_generation.md").read_text()
    source = text.split("```python\n", 1)[1].split("```", 1)[0]
    monkeypatch.chdir(tmp_path)
    exec(compile(source, "docs/split_generation.md", "exec"), {})
    assert (tmp_path / "local-splits/plan.json").is_file()
