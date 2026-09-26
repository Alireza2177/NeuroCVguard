"""Selected numeric features aligned by exact observation keys, never row position."""

import math
from numbers import Real
from pathlib import Path

import pandas as pd

from neurocvguard._tables import read_table, validate_identity
from neurocvguard.config import AuditConfig
from neurocvguard.errors import ConfigurationError, InputValidationError
from neurocvguard.identity import _missing


def numeric_value(value: object) -> float:
    if _missing(value):
        return float("nan")
    if isinstance(value, bool) or not isinstance(value, (str, Real)):
        raise InputValidationError(
            "Selected features require finite numbers or recognized missing values."
        )
    try:
        number = float(value)
    except (ValueError, OverflowError):
        raise InputValidationError(
            "Selected feature contains nonnumeric text; repair the source without dropping rows."
        ) from None
    if not math.isfinite(number):
        raise InputValidationError(
            "Selected feature contains infinity or unrecognized missing text; "
            "use finite numbers, empty text or n/a."
        )
    return number


def align_features(
    source: str | Path | pd.DataFrame, config: AuditConfig, order: tuple[str, ...]
) -> pd.DataFrame:
    names = config.evaluation.feature_columns
    if not names:
        raise ConfigurationError(
            "Select an explicit nonempty evaluation.feature_columns list for feature input."
        )
    data = read_table(source, config, feature_count=len(names))
    key = config.columns.observation_id
    validate_identity(data, key, "observation_id", unique=True)
    if any(name not in data for name in names):
        raise InputValidationError(
            "Selected feature columns are missing; correct evaluation.feature_columns."
        )
    keys = set(data[key])
    missing, extra = len(set(order) - keys), len(keys - set(order))
    if missing or extra:
        raise InputValidationError(
            f"Feature key mismatch: {missing} missing and {extra} extra observations; "
            "supply the exact cohort keys, without intersection or positional joins."
        )
    aligned = data.set_index(key).loc[list(order), list(names)].reset_index()
    for name in names:
        aligned[name] = pd.Series([numeric_value(value) for value in aligned[name]], dtype=float)
    return aligned
