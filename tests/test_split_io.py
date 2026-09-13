"""S04.A structural loading and binding tests; no design is repaired."""

import copy
import json
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest

from neurocvguard.config import AuditConfig, ColumnMap, Objective, SplitScheme, StudyConfig
from neurocvguard.errors import ConfigurationError, InputValidationError, SplitValidationError
from neurocvguard.io import cohort_digest, load_split_plan
from neurocvguard.models import Cohort, PlanOrigin, SplitPlan
from neurocvguard.serialization import json_digest

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def clean_plan_dict():
    return json.loads((FIXTURES / "splits_clean.json").read_text())


def test_json_binding_preserves_source_and_imported_origin(clean_cohort, clean_plan_dict):
    before = copy.deepcopy(clean_plan_dict)
    plan = load_split_plan(clean_plan_dict, cohort=clean_cohort, config=AuditConfig())
    assert plan.origin == PlanOrigin.IMPORTED and plan.seed is None
    assert plan.cohort_digest == cohort_digest(clean_cohort)
    assert clean_plan_dict == before and before["cohort_digest"] is None
    assert plan.folds == SplitPlan.from_dict(before).folds
    assert (
        load_split_plan(plan.to_operational_dict(), cohort=clean_cohort, config=AuditConfig())
        == plan
    )


def test_at_s04_16_digest_mismatch_and_metadata_scope(clean_cohort, clean_plan_dict):
    plan = load_split_plan(clean_plan_dict, cohort=clean_cohort, config=AuditConfig())
    metadata = clean_cohort.metadata
    metadata.loc[0, "diagnosis"] = "another-target"
    changed = Cohort(metadata, None, clean_cohort.columns, clean_cohort.observation_order)
    with pytest.raises(SplitValidationError, match="digest mismatch"):
        load_split_plan(plan.to_operational_dict(), cohort=changed, config=AuditConfig())
    metadata = clean_cohort.metadata.iloc[::-1].copy()
    metadata["unmapped"] = "ignored"
    features = pd.DataFrame({"observation_id": metadata.observation_id, "arbitrary": 1.0})
    reordered = Cohort(metadata, features, clean_cohort.columns, tuple(metadata.observation_id))
    assert cohort_digest(reordered) == cohort_digest(clean_cohort)


def test_digest_matches_literal_canonical_mapping(clean_cohort):
    mapping = clean_cohort.columns.to_dict()
    records = clean_cohort.metadata.sort_values("observation_id").to_dict("records")
    assert cohort_digest(clean_cohort) == json_digest({"columns": mapping, "records": records})


def test_at_s04_07_unknown_members_rejected(clean_cohort):
    with pytest.raises(SplitValidationError, match="unknown observation IDs") as caught:
        load_split_plan(
            FIXTURES / "splits_unknown_id.json", cohort=clean_cohort, config=AuditConfig()
        )
    assert "obs-does-not-exist" not in str(caught.value)


def test_at_s04_09_duplicate_json_membership(clean_cohort, clean_plan_dict):
    clean_plan_dict["folds"][0]["train_ids"].append(clean_plan_dict["folds"][0]["train_ids"][0])
    with pytest.raises(SplitValidationError, match="uniqueItems"):
        load_split_plan(clean_plan_dict, cohort=clean_cohort, config=AuditConfig())


def test_at_s04_17_tsv_valid_import(clean_cohort):
    plan = load_split_plan(
        FIXTURES / "assignments_clean.tsv", cohort=clean_cohort, config=AuditConfig()
    )
    expected = SplitPlan.from_json((FIXTURES / "splits_clean.json").read_text())
    # TSV cannot express the JSON fixture's explicit empty inner_folds field.
    assert all(fold.inner_folds == () for fold in expected.folds)
    assert plan.folds == tuple(replace(fold, inner_folds=None) for fold in expected.folds)
    assert plan.origin == PlanOrigin.IMPORTED and plan.seed is None
    assert plan.cohort_digest == cohort_digest(clean_cohort)


@pytest.mark.parametrize("role", ["validation", "Train", "", "train "])
def test_at_s04_17_invalid_tsv_role(clean_cohort, tmp_path, role):
    path = tmp_path / "plan.tsv"
    path.write_text(f"repeat_id\tfold_id\trole\tobservation_id\n0\tf\t{role}\to1\n")
    with pytest.raises(InputValidationError, match="only train and test"):
        load_split_plan(path, cohort=clean_cohort, config=AuditConfig())


def test_at_s04_09_duplicate_tsv_membership(clean_cohort, tmp_path):
    text = (FIXTURES / "assignments_clean.tsv").read_text()
    path = tmp_path / "plan.tsv"
    path.write_text(text + text.splitlines()[1] + "\n")
    with pytest.raises(SplitValidationError, match="Duplicate role/observation"):
        load_split_plan(path, cohort=clean_cohort, config=AuditConfig())


@pytest.mark.parametrize(
    "text",
    [
        "repeat_id\tfold_id\trole\trole\n",
        "repeat_id\tfold_id\trole\tobservation_id\textra\n",
        "repeat_id\tfold_id\trole\tobservation_id\n0\tf\ttrain\n",
        'repeat_id\tfold_id\trole\tobservation_id\n0\tf\ttrain\t"unclosed',
        "repeat_id\tfold_id\trole\tobservation_id\n0\tf\ttrain\t obs-001-1\n",
    ],
)
def test_strict_tsv_structure(clean_cohort, tmp_path, text):
    path = tmp_path / "plan.tsv"
    path.write_text(text)
    with pytest.raises(InputValidationError):
        load_split_plan(path, cohort=clean_cohort, config=AuditConfig())


def test_objective_and_role_mapping_cannot_be_reinterpreted(clean_cohort, clean_plan_dict):
    config = AuditConfig(
        study=StudyConfig(Objective.UNSEEN_SITE),
        split=replace(AuditConfig().split, scheme=SplitScheme.IMPORTED, n_splits=None),
    )
    with pytest.raises(SplitValidationError, match="objective"):
        load_split_plan(clean_plan_dict, cohort=clean_cohort, config=config)
    with pytest.raises(ConfigurationError, match="roles differ"):
        load_split_plan(
            clean_plan_dict,
            cohort=clean_cohort,
            config=AuditConfig(columns=ColumnMap(target="other")),
        )


def test_bom_duplicate_json_keys_and_file_limits(clean_cohort, tmp_path):
    path = tmp_path / "plan.json"
    path.write_text((FIXTURES / "splits_clean.json").read_text(), encoding="utf-8-sig")
    assert load_split_plan(path, cohort=clean_cohort, config=AuditConfig()).cohort_digest
    path.write_text('{"schema_version":"1.0","schema_version":"1.0"}')
    with pytest.raises(InputValidationError, match="Duplicate"):
        load_split_plan(path, cohort=clean_cohort, config=AuditConfig())
    path.write_bytes(b" " * (1024 * 1024 + 1))
    config = replace(AuditConfig(), limits=replace(AuditConfig().limits, max_input_mb=1))
    with pytest.raises(InputValidationError, match="max_input_mb"):
        load_split_plan(path, cohort=clean_cohort, config=config)


def test_tsv_row_guard_and_unsupported_formats(clean_cohort, tmp_path):
    config = replace(AuditConfig(), limits=replace(AuditConfig().limits, max_rows=2))
    with pytest.raises(InputValidationError, match="max_rows"):
        load_split_plan(FIXTURES / "assignments_clean.tsv", cohort=clean_cohort, config=config)
    with pytest.raises(InputValidationError, match="local uncompressed"):
        load_split_plan(tmp_path / "plan.pkl", cohort=clean_cohort, config=AuditConfig())
