"""Bounded local text tables; string identities are never inferred or normalized."""

import csv
import io
from pathlib import Path

import pandas as pd

from neurocvguard.config import AuditConfig
from neurocvguard.errors import InputValidationError
from neurocvguard.identity import _missing, _valid_label


def _headers(names: list[object]) -> None:
    if not names or any(not isinstance(name, str) or not name.strip() for name in names):
        raise InputValidationError("Table requires nonempty string column headers.")
    if len(names) != len(set(names)):
        raise InputValidationError("Duplicate table headers; give each column a unique name.")


def _dimensions(rows: int, config: AuditConfig, feature_count: int | None) -> None:
    if rows > config.limits.max_rows:
        raise InputValidationError(
            "Table rows exceed limits.max_rows; review the limit explicitly."
        )
    if feature_count is not None:
        if feature_count > config.limits.max_features:
            raise InputValidationError("Selected features exceed limits.max_features.")
        if rows * feature_count * 8 > config.limits.max_dense_mb * 1024 * 1024:
            raise InputValidationError(
                "Selected dense feature matrix exceeds limits.max_dense_mb; "
                "review dimensions before explicitly increasing the guardrail."
            )


def read_table(
    source: str | Path | pd.DataFrame, config: AuditConfig, *, feature_count: int | None = None
) -> pd.DataFrame:
    """Read UTF-8 CSV/TSV or copy a scalar DataFrame after resource checks."""
    if isinstance(source, pd.DataFrame):
        _headers(list(source.columns))
        _dimensions(len(source), config, feature_count)
        if any(
            not pd.api.types.is_scalar(value)
            for row in source.itertuples(index=False)
            for value in row
        ):
            raise InputValidationError("Table cells must be scalars, not nested objects.")
        return source.copy(deep=True)
    if not isinstance(source, (str, Path)):
        raise InputValidationError("Supply a local CSV/TSV path or pandas DataFrame.")
    path = Path(source)
    if (
        "://" in str(source)
        or str(source).startswith(("\\\\", "//"))
        or path.suffix.lower() not in {".csv", ".tsv"}
    ):
        raise InputValidationError(
            "Use a local uncompressed .csv or .tsv table; "
            "remote and binary sources are unsupported."
        )
    limit = config.limits.max_input_mb * 1024 * 1024
    try:
        if not path.is_file() or path.stat().st_size > limit:
            raise InputValidationError("Table file is missing or exceeds limits.max_input_mb.")
        with path.open("rb") as handle:
            content = handle.read(limit + 1)
        if len(content) > limit:
            raise InputValidationError("Table exceeds limits.max_input_mb.")
        reader = csv.reader(
            io.StringIO(content.decode("utf-8-sig"), newline=""),
            delimiter="\t" if path.suffix.lower() == ".tsv" else ",",
            strict=True,
        )
        header = next(reader, [])
        _headers(list(header))
        rows: list[list[str | None]] = []
        for count, row in enumerate(reader, 1):
            _dimensions(count, config, feature_count)
            if len(row) != len(header):
                raise InputValidationError(
                    f"Malformed table record {count}; "
                    "match the header field count without dropping rows."
                )
            rows.append([None if cell in {"", "n/a"} else cell for cell in row])
        _dimensions(len(rows), config, feature_count)
        return pd.DataFrame(rows, columns=header, dtype=object)
    except (OSError, UnicodeError, csv.Error):
        raise InputValidationError(
            "Cannot parse local UTF-8 table; check encoding, quoting and file permissions."
        ) from None


def validate_identity(frame: pd.DataFrame, column: str, role: str, *, unique: bool = False) -> None:
    if column not in frame:
        raise InputValidationError(f"Missing {role} column; correct the explicit columns mapping.")
    invalid = sum(not _valid_label(value) for value in frame[column])
    if invalid:
        raise InputValidationError(
            f"Invalid {role} in {invalid} rows; provide non-missing strings without "
            "surrounding whitespace or control characters. No automatic conversion or trimming."
        )
    if unique and frame[column].duplicated().any():
        raise InputValidationError("Duplicate observation_id; supply one row per observation key.")


def read_metadata(source: str | Path | pd.DataFrame, config: AuditConfig) -> pd.DataFrame:
    data = read_table(source, config)
    if data.empty:
        raise InputValidationError(
            "Cohort has no observations; provide a nonempty explicit manifest."
        )
    for role in ("observation_id", "subject_id"):
        validate_identity(
            data, getattr(config.columns, role), role, unique=role == "observation_id"
        )
    names = {value for value in config.columns.to_dict().values() if isinstance(value, str)}
    names.update(config.columns.independence)
    names.update(config.columns.categorical_covariates)
    for name in names & set(data.columns):
        if any(not _missing(value) and not isinstance(value, str) for value in data[name]):
            raise InputValidationError(
                "Mapped categorical roles require strings or missing scalars; "
                "convert explicitly upstream."
            )
        data[name] = pd.Series(
            [None if _missing(value) else value for value in data[name]],
            index=data.index,
            dtype=object,
        )
    return data.reset_index(drop=True)
