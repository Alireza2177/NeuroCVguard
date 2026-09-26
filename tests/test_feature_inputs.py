"""S02.B exact keyed joins and selected numeric feature boundaries."""

from dataclasses import replace

import pandas as pd
import pytest

from neurocvguard import load_cohort
from neurocvguard.config import AuditConfig, ColumnMap, EvaluationConfig
from neurocvguard.errors import ConfigurationError, InputValidationError
from neurocvguard.io import feature_digest

CONFIG = AuditConfig(
    columns=ColumnMap(target=None, session=None, site=None),
    evaluation=EvaluationConfig(feature_columns=("value",)),
)


def frames():
    metadata = pd.DataFrame(
        {"observation_id": ["001", "1"], "subject_id": ["p", "q"]}, index=[8, 4]
    )
    features = pd.DataFrame(
        {"observation_id": ["1", "001"], "value": ["20", "10"]}, index=[5, 2], dtype=object
    )
    return metadata, features


def test_at_s02_08_shuffled_feature_rows():
    metadata, features = frames()
    cohort = load_cohort(metadata, config=CONFIG, features=features)
    assert list(cohort.features.value) == [10.0, 20.0]
    assert tuple(cohort.features.observation_id) == cohort.observation_order == ("001", "1")


def test_at_s02_09_missing_key():
    metadata, features = frames()
    with pytest.raises(InputValidationError, match="1 missing and 0 extra"):
        load_cohort(metadata, config=CONFIG, features=features.iloc[:1])


def test_at_s02_10_extra_key():
    metadata, features = frames()
    features.loc[9] = ["extra", "12"]
    with pytest.raises(InputValidationError, match="0 missing and 1 extra"):
        load_cohort(metadata, config=CONFIG, features=features)


@pytest.mark.parametrize("name", ["subject_id", "diagnosis", "site", "observation_id"])
def test_at_s02_11_prohibited_predictors(name):
    with pytest.raises(ConfigurationError, match="mapped role"):
        AuditConfig(evaluation=EvaluationConfig(feature_columns=(name,)))


@pytest.mark.parametrize("value", ["PRIVATE-text", "inf", float("inf"), "NaN", True, complex(1, 2)])
def test_at_s02_12_numeric_coercion(value):
    metadata, features = frames()
    features.loc[5, "value"] = value
    with pytest.raises(InputValidationError) as error:
        load_cohort(metadata, config=CONFIG, features=features)
    assert "PRIVATE-text" not in str(error.value)


@pytest.mark.parametrize("value", ["", "n/a", None, pd.NA, float("nan")])
def test_recognized_missing_feature_values_retained(value):
    metadata, features = frames()
    features["value"] = pd.Series([value, value], index=features.index, dtype=object)
    cohort = load_cohort(metadata, config=CONFIG, features=features)
    assert cohort.features.value.isna().all()
    assert len(cohort.metadata) == 2


def test_at_s02_14_no_input_mutation():
    metadata, features = frames()
    before_m, before_f = metadata.copy(deep=True), features.copy(deep=True)
    cohort = load_cohort(metadata, config=CONFIG, features=features)
    returned_metadata, returned_features = cohort.metadata, cohort.features
    returned_metadata.loc[0, "subject_id"] = "changed"
    returned_features.loc[0, "value"] = 999
    pd.testing.assert_frame_equal(metadata, before_m)
    pd.testing.assert_frame_equal(features, before_f)
    assert list(cohort.features.value) == [10, 20]


def test_duplicate_feature_keys_rejected():
    metadata, features = frames()
    features["observation_id"] = ["001", "001"]
    with pytest.raises(InputValidationError, match="Duplicate observation"):
        load_cohort(metadata, config=CONFIG, features=features)


def test_empty_selection_never_infers_numeric_predictors():
    metadata, features = frames()
    config = replace(CONFIG, evaluation=replace(CONFIG.evaluation, feature_columns=()))
    with pytest.raises(ConfigurationError, match="nonempty"):
        load_cohort(metadata, config=config, features=features)


def test_feature_digest_is_keyed_and_value_sensitive():
    metadata, features = frames()
    first = feature_digest(load_cohort(metadata, config=CONFIG, features=features))
    assert first == feature_digest(
        load_cohort(metadata.iloc[::-1], config=CONFIG, features=features.iloc[::-1])
    )
    features.loc[5, "value"] = "21"
    assert first != feature_digest(load_cohort(metadata, config=CONFIG, features=features))
