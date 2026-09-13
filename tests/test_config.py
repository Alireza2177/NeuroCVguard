"""S01.A configuration and strict JSON acceptance cases."""

import copy
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from neurocvguard.config import AuditConfig, Objective, load_config
from neurocvguard.errors import ConfigurationError, InputValidationError
from neurocvguard.serialization import canonical_json, strict_json_loads

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_at_s01_01_unknown_key() -> None:
    with pytest.raises(ConfigurationError, match="secret_magic"):
        load_config(FIXTURES / "config_invalid_unknown_key.json")


@pytest.mark.parametrize(
    "text", ['{"schema_version":"1.0","schema_version":"1.0"}', '{"x":{"n":1,"n":2}}']
)
def test_at_s01_02_duplicate_keys(text: str) -> None:
    with pytest.raises(ConfigurationError, match="Duplicate JSON key"):
        AuditConfig.from_json(text)


@pytest.mark.parametrize(
    ("section", "key"),
    [
        ("split", "n_splits"),
        ("split", "seed"),
        ("limits", "max_rows"),
        ("evaluation", "max_iter"),
        ("association", "review_threshold"),
    ],
)
def test_at_s01_03_boolean_number(section: str, key: str) -> None:
    data = AuditConfig().to_dict()
    data[section][key] = True
    with pytest.raises(ConfigurationError):
        AuditConfig.from_dict(data)


def test_at_s01_04_optional_defaults() -> None:
    data = AuditConfig().to_dict()
    del data["evaluation"]["positive_class"]
    del data["limits"]["max_input_mb"]
    data["columns"]["site"] = None
    result = AuditConfig.from_dict(data)
    assert result.evaluation.positive_class is None
    assert result.limits.max_input_mb == 128
    assert result.columns.site is None
    del data["columns"]["session"]
    with pytest.raises(ConfigurationError):
        AuditConfig.from_dict(data)


@pytest.mark.parametrize("version", ["2.0", "1.1", 1, True, None])
def test_at_s01_05_version(version: object) -> None:
    data = AuditConfig().to_dict()
    data["schema_version"] = version
    with pytest.raises(ConfigurationError, match="Incompatible schema_version"):
        AuditConfig.from_dict(data)


@pytest.mark.parametrize("number", ["NaN", "Infinity", "-Infinity", "1e9999"])
def test_at_s01_07_nonfinite_input(number: str) -> None:
    with pytest.raises(InputValidationError):
        strict_json_loads('{"x":' + number + "}")


@given(st.integers(min_value=0, max_value=2**32 - 1), st.sampled_from([None, "site", "scanner"]))
def test_at_s01_10_config_no_mutation(seed: int, site: str | None) -> None:
    data = AuditConfig().to_dict()
    data["split"]["seed"] = seed
    data["columns"]["site"] = site
    before = copy.deepcopy(data)
    result = AuditConfig.from_dict(data)
    assert result.study.objective is Objective.UNSEEN_PARTICIPANT
    assert data == before
    data["evaluation"]["feature_columns"].append("later")
    assert result.evaluation.feature_columns == ("feature_1", "feature_2")
    exported = result.to_dict()
    exported["evaluation"]["C_grid"].append(100)
    assert result.evaluation.C_grid == (0.1, 1.0, 10.0)
    with pytest.raises(FrozenInstanceError):
        result.split.seed = 9


def test_config_cross_fields_and_audit_only() -> None:
    data = AuditConfig().to_dict()
    data["study"]["objective"] = "unseen_site"
    with pytest.raises(ConfigurationError, match="does not match"):
        AuditConfig.from_dict(data)
    data["study"]["objective"] = "audit_only"
    data["evaluation"]["feature_columns"] = []
    data["columns"]["target"] = None
    assert AuditConfig.from_dict(data).study.objective == Objective.AUDIT_ONLY


@pytest.mark.parametrize(
    "feature", ["observation_id", "subject_id", "diagnosis", "site", "family", "covariate"]
)
def test_predictors_exclude_roles(feature: str) -> None:
    data = AuditConfig().to_dict()
    data["columns"]["independence"] = ["family"]
    data["columns"]["categorical_covariates"] = ["covariate"]
    data["evaluation"]["feature_columns"] = [feature]
    with pytest.raises(ConfigurationError, match="feature_columns"):
        AuditConfig.from_dict(data)


def test_role_collision() -> None:
    data = AuditConfig().to_dict()
    data["columns"]["observation_id"] = data["columns"]["subject_id"]
    with pytest.raises(ConfigurationError, match="collide"):
        AuditConfig.from_dict(data)


def test_load_config_bom_and_local_path(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(canonical_json(AuditConfig().to_dict()), encoding="utf-8-sig")
    assert load_config(path) == AuditConfig()
    for invalid in (
        "https://example.invalid/config.json",
        tmp_path / "missing.json",
        tmp_path / "file.pkl",
    ):
        with pytest.raises(ConfigurationError):
            load_config(invalid)
    with pytest.raises(ConfigurationError):
        load_config(path, max_input_mb=True)
    path.write_bytes(b" " * (1024 * 1024 + 1))
    with pytest.raises(ConfigurationError, match="exceeds"):
        load_config(path, max_input_mb=1)
