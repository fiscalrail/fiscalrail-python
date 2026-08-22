from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

from fiscalrail._generated.models import (
    Account,
    AccountDefaultSeries,
    AccountInvoiceNumberingScope,
    Address,
    ApiKey,
    Customer,
    Event,
    EventDestination,
    GlobalInvoiceTaxRegime,
    Invoice,
    InvoiceAmendment,
    InvoiceLine,
    InvoiceParty,
    InvoicePartySource,
    InvoicePaymentOption,
    InvoicePaymentTerms,
    InvoicePdf,
    InvoiceReference,
    InvoiceSeries,
    InvoiceSupplyPeriod,
    InvoiceTax,
    InvoiceTaxRegime,
    InvoiceTaxTotal,
    InvoiceTotals,
    PaymentInstruction,
    PaymentInstructionBankTransfer,
    SpanishInvoiceQr,
    SpanishInvoiceTaxRegime,
    SpanishInvoiceTaxRegimeDetails,
    TaxId,
    TaxIdOwner,
    TaxIdSnapshot,
    TaxIdVerification,
    TaxRegime,
    TaxRegimeTax,
    TaxRegimeTaxRule,
    Verifactu,
    VerifactuRegistration,
    VerifactuRegistrationError,
)
from fiscalrail._model import FiscalRailModel, ResponseModel

# Compatibility names for the first SDK prototype. The owning types are generated
# directly from the OpenAPI component names above.
PartySource = InvoicePartySource
PartyTaxId = TaxIdSnapshot
PartySnapshot = InvoiceParty
ResolvedTax = InvoiceTax
TaxTotal = InvoiceTaxTotal
InvoiceRegistrationError = VerifactuRegistrationError
InvoiceQr = SpanishInvoiceQr
VerifactuDetails = Verifactu
SpanishInvoiceDetails = SpanishInvoiceTaxRegimeDetails

ItemT = TypeVar("ItemT", bound=ResponseModel)


@dataclass(frozen=True, slots=True, kw_only=True)
class Page(ResponseModel, Generic[ItemT]):
    object: Literal["list"]
    has_more: bool
    data: list[ItemT]


__all__ = [
    "Account",
    "AccountDefaultSeries",
    "AccountInvoiceNumberingScope",
    "Address",
    "ApiKey",
    "Customer",
    "Event",
    "EventDestination",
    "FiscalRailModel",
    "GlobalInvoiceTaxRegime",
    "Invoice",
    "InvoiceAmendment",
    "InvoiceLine",
    "InvoiceParty",
    "InvoicePartySource",
    "InvoicePdf",
    "InvoicePaymentOption",
    "InvoicePaymentTerms",
    "InvoiceQr",
    "InvoiceReference",
    "InvoiceRegistrationError",
    "InvoiceSeries",
    "InvoiceSupplyPeriod",
    "InvoiceTax",
    "InvoiceTaxRegime",
    "InvoiceTaxTotal",
    "InvoiceTotals",
    "Page",
    "PartySnapshot",
    "PartySource",
    "PartyTaxId",
    "PaymentInstruction",
    "PaymentInstructionBankTransfer",
    "ResolvedTax",
    "ResponseModel",
    "SpanishInvoiceDetails",
    "SpanishInvoiceQr",
    "SpanishInvoiceTaxRegime",
    "SpanishInvoiceTaxRegimeDetails",
    "TaxId",
    "TaxIdOwner",
    "TaxIdSnapshot",
    "TaxIdVerification",
    "TaxRegime",
    "TaxRegimeTax",
    "TaxRegimeTaxRule",
    "TaxTotal",
    "Verifactu",
    "VerifactuDetails",
    "VerifactuRegistration",
]
