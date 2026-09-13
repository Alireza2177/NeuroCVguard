"""Shared conversion for fixed, typed internal dataclasses, not a plugin mechanism."""

from collections.abc import Mapping
from dataclasses import dataclass, fields
from enum import Enum
from types import MappingProxyType, UnionType
from typing import Any, ClassVar, Self, Union, cast, get_args, get_origin, get_type_hints

from neurocvguard.errors import InputValidationError, NeuroCVguardError
from neurocvguard.schema import validate_document
from neurocvguard.serialization import JSONObject, _json_value, strict_json_loads


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def _decode(annotation: Any, value: Any) -> Any:
    if value is None:
        return None
    origin = get_origin(annotation)
    arguments = get_args(annotation)
    if origin in (UnionType, Union):
        candidates = [item for item in arguments if item is not type(None)]
        if len(candidates) == 1:
            return _decode(candidates[0], value)
        return _freeze(value)
    if origin is tuple:
        return tuple(_decode(arguments[0], item) for item in value)
    if origin is Mapping:
        return _freeze(value)
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return annotation(value)
    if isinstance(annotation, type) and issubclass(annotation, Record):
        return annotation.from_dict(value)
    return value


@dataclass(frozen=True)
class Record:
    """Fixed schema-backed dataclass support shared by config and result records."""

    _schema_name: ClassVar[str]
    _schema_path: ClassVar[tuple[str | int, ...]] = ()
    _omit_none: ClassVar[tuple[str, ...]] = ()
    _error_type: ClassVar[type[NeuroCVguardError]] = InputValidationError

    def __post_init__(self) -> None:
        try:
            data = self._validated(_json_value(self, allow_records=True))
        except InputValidationError as error:
            raise self._error_type(str(error)) from None
        annotations = get_type_hints(type(self))
        for field in fields(self):
            if field.name in data:
                object.__setattr__(
                    self, field.name, _decode(annotations[field.name], data[field.name])
                )
        self._validate_semantics()

    @classmethod
    def _validated(cls, value: object) -> JSONObject:
        try:
            return validate_document(cls._schema_name, value, path=cls._schema_path)
        except InputValidationError as error:
            raise cls._error_type(str(error)) from None

    def _validate_semantics(self) -> None:
        pass

    def _as_dict(self) -> JSONObject:
        return cast(JSONObject, _json_value(self, allow_records=True))

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Construct a detached typed record from its structural contract.

        Parameters
        ----------
        value : object
            JSON mapping; no keys are inferred or dropped.

        Returns
        -------
        Self
            Validated frozen record. This does not audit supplied research data.

        Raises
        ------
        InputValidationError
            Structure, version, or record semantics are invalid.

        Examples
        --------
        Round trip with ``SplitPlan.from_dict(plan.to_operational_dict())``.
        """
        data = cls._validated(value)
        return cls(**data)

    @classmethod
    def from_json(cls, text: str) -> Self:
        """Parse strict JSON and construct a typed record.

        Parameters
        ----------
        text : str
            A document of this record's contract.

        Returns
        -------
        Self
            An independently owned record.

        Raises
        ------
        InputValidationError
            JSON syntax or contract validation failed.

        Examples
        --------
        Use ``AuditConfig.from_json(text)`` for an explicit JSON configuration.
        """
        try:
            return cls.from_dict(strict_json_loads(text))
        except InputValidationError as error:
            raise cls._error_type(str(error)) from None
