from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, fields, replace
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Any, Literal, Self, cast


def _empty_extra_fields() -> Mapping[str, Any]:
    return MappingProxyType({})


@dataclass(frozen=True, slots=True, kw_only=True)
class FiscalRailModel:
    """Base for dependency-free, immutable API response values."""

    extra_fields: Mapping[str, Any] = field(
        default_factory=_empty_extra_fields,
        repr=False,
        compare=False,
        metadata={"serialize": False, "decode": False},
    )

    def __getattr__(self, name: str) -> Any:
        try:
            return self.extra_fields[name]
        except KeyError as error:
            raise AttributeError(name) from error

    def to_dict(self, *, mode: Literal["python", "json"] = "python") -> dict[str, Any]:
        value = _model_to_dict(self)
        return value if mode == "python" else cast(dict[str, Any], _to_jsonable(value))


@dataclass(frozen=True, slots=True, kw_only=True)
class ResponseModel(FiscalRailModel):
    request_id: str | None = field(
        default=None,
        repr=False,
        compare=False,
        metadata={"serialize": False, "decode": False},
    )
    idempotent_replayed: str | None = field(
        default=None,
        repr=False,
        compare=False,
        metadata={"serialize": False, "decode": False},
    )
    idempotency_key: str | None = field(
        default=None,
        repr=False,
        compare=False,
        metadata={"serialize": False, "decode": False},
    )

    def with_response_metadata(
        self,
        *,
        request_id: str | None,
        idempotent_replayed: str | None = None,
        idempotency_key: str | None = None,
    ) -> Self:
        return replace(
            self,
            request_id=request_id,
            idempotent_replayed=idempotent_replayed,
            idempotency_key=idempotency_key,
        )


def _model_to_dict(model: FiscalRailModel) -> dict[str, Any]:
    result = dict(model.extra_fields)
    for model_field in fields(model):
        if model_field.metadata.get("serialize", True):
            result[model_field.name] = _to_python(getattr(model, model_field.name))
    return result


def _to_python(value: Any) -> Any:
    if isinstance(value, FiscalRailModel):
        return _model_to_dict(value)
    if isinstance(value, Mapping):
        return {str(key): _to_python(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_to_python(item) for item in value]
    return value


def _to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Enum):
        return _to_jsonable(value.value)
    if isinstance(value, Mapping):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_to_jsonable(item) for item in value]
    raise TypeError(f"Cannot serialize {type(value).__name__} to JSON")
