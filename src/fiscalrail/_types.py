from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, NotRequired, Required, TypeAlias, TypedDict

DecimalInput: TypeAlias = Decimal | int | str


@dataclass(frozen=True, slots=True)
class TaxReference:
    """A typed tax and rule pair accepted by invoice lines."""

    tax: str
    rule: str


class TaxReferenceParams(TypedDict):
    tax: Required[str]
    rule: Required[str]
    effect: NotRequired[Literal["added", "withheld"]]
    treatment: NotRequired[
        Literal["taxable", "exempt", "reverse_charge", "not_subject"]
    ]
    description: NotRequired[str]
    rate: NotRequired[DecimalInput]
    taxable_base: NotRequired[DecimalInput]


TaxReferenceInput: TypeAlias = TaxReference | TaxReferenceParams
TaxReferenceList: TypeAlias = list[TaxReferenceInput]
