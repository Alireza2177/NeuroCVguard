"""Strict standard JSON and deterministic UTF-8 integrity utilities."""

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import TypeAlias, cast

from neurocvguard.errors import InputValidationError

JSONValue: TypeAlias = None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]
JSONObject: TypeAlias = dict[str, JSONValue]
FrozenJSONValue: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | tuple["FrozenJSONValue", ...]
    | Mapping[str, "FrozenJSONValue"]
)


def _json_value(value: object, *, allow_records: bool = False) -> JSONValue:
    if isinstance(value, Enum):
        return _json_value(value.value)
    if value is None or type(value) in (bool, int, str):
        return cast(JSONValue, value)
    if type(value) is float:
        if not math.isfinite(value):
            raise InputValidationError("Non-finite number: use a null metric with a reason.")
        return value
    if is_dataclass(value) and not isinstance(value, type):
        if not allow_records:
            raise InputValidationError("Select an explicit record projection before JSON encoding.")
        omit = getattr(value, "_omit_none", ())
        return {
            field.name: _json_value(getattr(value, field.name), allow_records=True)
            for field in fields(value)
            if field.metadata.get("serialize", True)
            and not (field.name in omit and getattr(value, field.name) is None)
        }
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise InputValidationError("JSON object keys must be strings.")
        return {key: _json_value(item, allow_records=allow_records) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item, allow_records=allow_records) for item in value]
    raise InputValidationError("Unsupported JSON value; use standard JSON types only.")


def canonical_json(value: object) -> str:
    """Encode finite JSON with sorted keys, compact separators and preserved array order.

    Parameters
    ----------
    value : object
        Standard JSON data, or a typed NeuroCVguard record's explicit projection.

    Returns
    -------
    str
        Deterministic text, without display rounding or Unicode normalization.

    Raises
    ------
    InputValidationError
        Non-finite numbers, unsupported values, or invalid Unicode were supplied.

    Examples
    --------
    >>> canonical_json({"b": None, "a": 0})
    '{"a":0,"b":null}'
    """
    # Callers must deliberately select public or operational serialization first.
    if is_dataclass(value):
        raise InputValidationError(
            "Select to_dict() or to_operational_dict() before JSON encoding."
        )
    try:
        text = json.dumps(
            _json_value(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        text.encode("utf-8")
        return text
    except InputValidationError:
        raise
    except (ValueError, UnicodeError, RecursionError) as error:
        raise InputValidationError(
            "Cannot encode finite UTF-8 JSON; check the supplied structure."
        ) from error


def _unique_object(pairs: list[tuple[str, JSONValue]]) -> JSONObject:
    result: JSONObject = {}
    for key, value in pairs:
        if key in result:
            raise InputValidationError("Duplicate JSON key; remove repeated keys before loading.")
        result[key] = value
    return result


def _reject_constant(value: str) -> JSONValue:
    raise InputValidationError("NaN and Infinity are not standard JSON numbers.")


def strict_json_loads(text: str) -> JSONValue:
    """Decode JSON without duplicate-key or non-finite-number coercion.

    Parameters
    ----------
    text : str
        JSON document; an initial UTF-8 BOM is accepted.

    Returns
    -------
    JSONValue
        A fresh standard JSON value; object keys and array order are preserved.

    Raises
    ------
    InputValidationError
        Syntax, duplicate keys, non-finite values or invalid Unicode are present.

    Examples
    --------
    >>> strict_json_loads('{"value": null}')
    {'value': None}
    """
    try:
        data = json.loads(
            text.removeprefix("\ufeff"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
        canonical_json(data)  # Also catches numeric exponent overflow and lone surrogates.
        return cast(JSONValue, data)
    except (json.JSONDecodeError, UnicodeError, RecursionError) as error:
        raise InputValidationError(
            "Invalid JSON syntax or encoding; supply a UTF-8 JSON document."
        ) from error


def json_digest(value: object) -> str:
    """Return SHA-256 of canonical JSON, an integrity aid rather than anonymization.

    Parameters
    ----------
    value : object
        An explicitly selected JSON projection.

    Returns
    -------
    str
        A 64-character lowercase hexadecimal digest.

    Raises
    ------
    InputValidationError
        The value cannot be encoded as finite JSON.

    Examples
    --------
    >>> len(json_digest({"schema_version": "1.0"}))
    64
    """
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
