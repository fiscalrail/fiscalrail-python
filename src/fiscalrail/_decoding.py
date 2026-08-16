from __future__ import annotations

from collections.abc import Mapping
from dataclasses import MISSING, fields
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from functools import lru_cache
from types import MappingProxyType, NoneType, UnionType
from typing import (
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from fiscalrail.models import FiscalRailModel, ItemT, Page, ResponseModel

ModelT = TypeVar("ModelT", bound=FiscalRailModel)
PageItemT = TypeVar("PageItemT", bound=ResponseModel)


class DecodeError(ValueError):
    def __init__(self, path: tuple[str | int, ...], message: str) -> None:
        super().__init__(message)
        self.path = path
        self.message = message

    @property
    def field(self) -> str:
        if not self.path:
            return "$"
        result = "$"
        for part in self.path:
            result += f"[{part}]" if isinstance(part, int) else f".{part}"
        return result


def decode_model(
    model: type[ModelT],
    value: Any,
    *,
    typevars: Mapping[object, object] | None = None,
) -> ModelT:
    if not isinstance(value, Mapping):
        raise DecodeError((), f"expected an object, got {type(value).__name__}")

    substitutions = typevars or {}
    hints = _type_hints(model)
    decoded: dict[str, Any] = {}
    known_fields: set[str] = set()

    for model_field in fields(model):
        if not model_field.metadata.get("decode", True):
            continue
        known_fields.add(model_field.name)
        if model_field.name not in value:
            if (
                model_field.default is not MISSING
                or model_field.default_factory is not MISSING
            ):
                continue
            raise DecodeError((model_field.name,), "field is missing")
        decoded[model_field.name] = _decode_value(
            hints[model_field.name],
            value[model_field.name],
            (model_field.name,),
            substitutions,
        )

    decoded["extra_fields"] = MappingProxyType(
        {str(key): item for key, item in value.items() if key not in known_fields}
    )
    try:
        return model(**decoded)
    except (TypeError, ValueError) as error:
        raise DecodeError((), str(error)) from error


def decode_page(item_model: type[PageItemT], value: Any) -> Page[PageItemT]:
    return cast(
        Page[PageItemT],
        decode_model(Page, value, typevars={ItemT: item_model}),
    )


@lru_cache
def _type_hints(model: type[FiscalRailModel]) -> dict[str, Any]:
    return get_type_hints(model)


def _decode_value(
    annotation: Any,
    value: Any,
    path: tuple[str | int, ...],
    typevars: Mapping[object, object],
) -> Any:
    annotation = typevars.get(annotation, annotation)
    if annotation is Any or annotation is object:
        return value

    origin = get_origin(annotation)
    arguments = get_args(annotation)

    if origin in (Union, UnionType):
        if value is None and NoneType in arguments:
            return None
        errors: list[DecodeError] = []
        for option in arguments:
            if option is NoneType:
                continue
            try:
                return _decode_value(option, value, path, typevars)
            except DecodeError as error:
                errors.append(error)
        expected = " or ".join(_type_name(option) for option in arguments)
        raise DecodeError(path, f"expected {expected}, got {type(value).__name__}")

    if origin is list:
        if not isinstance(value, list):
            raise DecodeError(path, f"expected a list, got {type(value).__name__}")
        item_type = arguments[0] if arguments else Any
        return [
            _decode_value(item_type, item, (*path, index), typevars)
            for index, item in enumerate(value)
        ]

    if origin is dict:
        if not isinstance(value, Mapping):
            raise DecodeError(path, f"expected an object, got {type(value).__name__}")
        key_type, item_type = arguments or (Any, Any)
        return {
            _decode_value(key_type, key, (*path, str(key)), typevars): _decode_value(
                item_type, item, (*path, str(key)), typevars
            )
            for key, item in value.items()
        }

    if origin is Literal:
        if any(value == option and type(value) is type(option) for option in arguments):
            return value
        expected = ", ".join(repr(option) for option in arguments)
        raise DecodeError(path, f"expected one of {expected}, got {value!r}")

    if isinstance(annotation, type) and issubclass(annotation, FiscalRailModel):
        try:
            return decode_model(annotation, value, typevars=typevars)
        except DecodeError as error:
            raise DecodeError((*path, *error.path), error.message) from error

    if isinstance(annotation, type) and issubclass(annotation, Enum):
        try:
            return annotation(value)
        except (TypeError, ValueError) as error:
            message = f"invalid {_type_name(annotation)} value {value!r}"
            raise DecodeError(path, message) from error

    if annotation is Decimal:
        if isinstance(value, Decimal):
            return value
        if isinstance(value, bool) or not isinstance(value, str | int):
            raise DecodeError(
                path, f"expected a decimal string, got {type(value).__name__}"
            )
        try:
            return Decimal(value)
        except InvalidOperation as error:
            raise DecodeError(path, f"invalid decimal value {value!r}") from error

    if annotation is datetime:
        if isinstance(value, datetime):
            return value
        if not isinstance(value, str):
            raise DecodeError(
                path, f"expected an ISO timestamp, got {type(value).__name__}"
            )
        try:
            return datetime.fromisoformat(value)
        except ValueError as error:
            raise DecodeError(path, f"invalid ISO timestamp {value!r}") from error

    if annotation is date:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if not isinstance(value, str):
            raise DecodeError(path, f"expected an ISO date, got {type(value).__name__}")
        try:
            return date.fromisoformat(value)
        except ValueError as error:
            raise DecodeError(path, f"invalid ISO date {value!r}") from error

    if annotation is bool:
        if type(value) is bool:
            return value
        raise DecodeError(path, f"expected bool, got {type(value).__name__}")
    if annotation is int:
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        raise DecodeError(path, f"expected int, got {type(value).__name__}")
    if annotation is float:
        if isinstance(value, int | float) and not isinstance(value, bool):
            return float(value)
        raise DecodeError(path, f"expected float, got {type(value).__name__}")
    if annotation is str:
        if isinstance(value, str):
            return value
        raise DecodeError(path, f"expected str, got {type(value).__name__}")
    if annotation is NoneType:
        if value is None:
            return None
        raise DecodeError(path, f"expected None, got {type(value).__name__}")
    if isinstance(annotation, type) and isinstance(value, annotation):
        return value

    raise DecodeError(path, f"unsupported response type {_type_name(annotation)}")


def _type_name(annotation: Any) -> str:
    return getattr(annotation, "__name__", str(annotation))
