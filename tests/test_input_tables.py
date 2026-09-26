"""S02.A strict metadata input using only fictitious identities."""

from dataclasses import replace

import pandas as pd
import pytest

from neurocvguard import load_cohort
from neurocvguard.config import AuditConfig, ColumnMap
from neurocvguard.errors import InputValidationError

CONFIG = AuditConfig(columns=ColumnMap(target=None, session=None, site="site"))


def table(tmp_path, text, suffix=".tsv"):
    path = tmp_path / ("input" + suffix)
    path.write_text(text, encoding="utf-8")
    return path


def test_at_s02_01_leading_zeros(tmp_path):
    result = load_cohort(
        table(tmp_path, "observation_id\tsubject_id\n001\t001\n1\t1\n"), config=CONFIG
    )
    assert result.observation_order == ("001", "1")
    assert list(result.metadata.subject_id) == ["001", "1"]


def test_at_s02_02_duplicate_headers(tmp_path):
    with pytest.raises(InputValidationError, match="Duplicate table headers"):
        load_cohort(
            table(tmp_path, "observation_id,subject_id,subject_id\no,p,q\n", ".csv"), config=CONFIG
        )


def test_at_s02_03_bom_and_unicode(tmp_path):
    result = load_cohort(
        table(tmp_path, "\ufeffobservation_id\tsubject_id\nدیدار-α\tنام-β\n"), config=CONFIG
    )
    assert result.observation_order == ("دیدار-α",)
    assert result.metadata.subject_id.iloc[0] == "نام-β"


@pytest.mark.parametrize("value", [" PRIVATE", "PRIVATE ", "PRIVATE\x01"])
def test_at_s02_04_whitespace_identity(tmp_path, value):
    with pytest.raises(InputValidationError) as error:
        load_cohort(table(tmp_path, f"observation_id\tsubject_id\no\t{value}\n"), config=CONFIG)
    assert "PRIVATE" not in str(error.value)
    assert "strings" in str(error.value)


@pytest.mark.parametrize("row", ["\tp", "o\t", "n/a\tp"])
def test_at_s02_05_missing_critical_id(tmp_path, row):
    with pytest.raises(InputValidationError, match="Invalid"):
        load_cohort(table(tmp_path, "observation_id\tsubject_id\n" + row + "\n"), config=CONFIG)


def test_at_s02_06_na_vocabulary(tmp_path):
    result = load_cohort(
        table(tmp_path, "observation_id\tsubject_id\tsite\nNA\tNA\tn/a\n"), config=CONFIG
    )
    assert result.observation_order == ("NA",)
    assert result.metadata.site.iloc[0] is None


def test_at_s02_07_duplicate_observations(tmp_path):
    with pytest.raises(InputValidationError, match="Duplicate observation_id"):
        load_cohort(table(tmp_path, "observation_id\tsubject_id\no\tp\no\tq\n"), config=CONFIG)


def test_at_s02_13_dataframe_identity_type():
    with pytest.raises(InputValidationError, match="strings"):
        load_cohort(pd.DataFrame({"observation_id": ["o"], "subject_id": [1]}), config=CONFIG)


@pytest.mark.parametrize("body", ["o\tp\textra", "o", '"unterminated\tp'])
def test_malformed_rows_fail_without_silent_drop(tmp_path, body):
    with pytest.raises(InputValidationError):
        load_cohort(table(tmp_path, "observation_id\tsubject_id\n" + body), config=CONFIG)


def test_no_normalization_of_distinct_legitimate_keys(tmp_path):
    keys = ["sub-X", "X", "x", "é", "e\u0301"]
    text = "observation_id\tsubject_id\n" + "\n".join(f"{key}\t{key}" for key in keys)
    result = load_cohort(table(tmp_path, text), config=CONFIG)
    assert result.observation_order == tuple(keys)


def test_missing_optional_field_retains_rows(tmp_path):
    result = load_cohort(table(tmp_path, "observation_id\tsubject_id\no\tp\n"), config=CONFIG)
    assert len(result.metadata) == 1 and "site" not in result.metadata


def test_row_limit(tmp_path):
    config = replace(CONFIG, limits=replace(CONFIG.limits, max_rows=1))
    with pytest.raises(InputValidationError, match="max_rows"):
        load_cohort(table(tmp_path, "observation_id\tsubject_id\no\tp\nr\tq\n"), config=config)
