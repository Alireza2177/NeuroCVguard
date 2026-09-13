"""Allowlisted packaged JSON schemas; external reference resolution is prohibited."""

from importlib.resources import files

from jsonschema import Draft202012Validator

from neurocvguard.errors import InputValidationError
from neurocvguard.serialization import JSONObject, JSONValue, _json_value, strict_json_loads

SCHEMA_NAMES = (
    "config",
    "split-plan",
    "preprocessing-ledger",
    "audit-report",
    "evaluation-result",
    "comparison-summary",
)


def _check_references(value: JSONValue) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"$ref", "$dynamicRef", "$recursiveRef"}:
                if not isinstance(item, str) or not item.startswith("#"):
                    raise InputValidationError(
                        "External schema references are prohibited; use packaged contracts."
                    )
            _check_references(item)
    elif isinstance(value, list):
        for item in value:
            _check_references(item)


def load_schema(name: str) -> JSONObject:
    """Read a fresh standalone schema from package resources, without network access.

    Parameters
    ----------
    name : str
        One of SCHEMA_NAMES, without a path or suffix.

    Returns
    -------
    JSONObject
        A caller-owned schema copy.

    Raises
    ------
    InputValidationError
        The name or a packaged reference is unsupported.

    Examples
    --------
    >>> load_schema("config")["title"]
    'NeuroCVguard config contract 1.0'
    """
    if name not in SCHEMA_NAMES:
        raise InputValidationError("Unknown schema name; select a packaged contract.")
    data = strict_json_loads(
        files("neurocvguard").joinpath("schemas", name + ".schema.json").read_text(encoding="utf-8")
    )
    if not isinstance(data, dict):
        raise InputValidationError("Packaged schema must be a JSON object.")
    _check_references(data)
    return data


def validate_document(
    name: str, document: object, *, path: tuple[str | int, ...] = ()
) -> JSONObject:
    """Validate a finite JSON object against a local contract or its structural fragment.

    Parameters
    ----------
    name : str
        Allowlisted schema name.
    document : object
        JSON-compatible mapping, never an executable schema.
    path : tuple, optional
        Internal fragment path for component records.

    Returns
    -------
    JSONObject
        A detached, structurally validated copy. Cohort/design audits are separate.

    Raises
    ------
    InputValidationError
        Invalid fields, schema version, JSON data or fragment path.

    Examples
    --------
    Use ``validate_document("config", config.to_dict())`` on an AuditConfig.
    """
    data = _json_value(document)
    if not isinstance(data, dict):
        raise InputValidationError("Contract document must be a JSON object.")
    if "schema_version" in data and data["schema_version"] != "1.0":
        raise InputValidationError(
            "Incompatible schema_version; migrate explicitly to contract 1.0."
        )
    schema: JSONValue = load_schema(name)
    try:
        for part in path:
            if isinstance(schema, dict) and isinstance(part, str):
                schema = schema[part]
            elif isinstance(schema, list) and isinstance(part, int):
                schema = schema[part]
            else:
                raise KeyError(part)
    except (KeyError, IndexError) as error:
        raise InputValidationError("Unknown packaged schema fragment.") from error
    if not isinstance(schema, dict):
        raise InputValidationError("Schema fragment must be an object.")
    failure = next(Draft202012Validator(schema).iter_errors(data), None)
    if failure is not None:
        location = ".".join(map(str, failure.absolute_path)) or "document"
        if failure.validator == "additionalProperties":
            unknown = sorted(set(failure.instance) - set(failure.schema.get("properties", {})))
            raise InputValidationError(f"Unsupported key at {location}: {', '.join(unknown)}.")
        # Do not include jsonschema's raw instance/value in research-data errors.
        raise InputValidationError(
            f"Invalid {location}: contract constraint {failure.validator}; correct this field."
        )
    return data
