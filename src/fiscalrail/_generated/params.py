"""Generated from FiscalRail's OpenAPI contract. Do not edit by hand."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal, Required, TypeAlias, TypedDict

from fiscalrail._types import DecimalInput, TaxReferenceList

RequestId: TypeAlias = str


AccountId: TypeAlias = str


ApiKeyId: TypeAlias = str


InvoiceSeriesId: TypeAlias = str


Live: TypeAlias = bool


InvoiceLocale: TypeAlias = Literal["en", "es"]


class AccountDefaultSeries(TypedDict, total=False):
    invoice: Required[InvoiceSeriesId]
    credit_note: Required[InvoiceSeriesId | None]
    amendment: Required[InvoiceSeriesId | None]


AccountInvoiceNumberingScope: TypeAlias = Literal["account", "customer"]


class ApiKey(TypedDict, total=False):
    id: Required[ApiKeyId]
    object: Required[Literal["api_key"]]
    live: Required[Live]
    account: Required[AccountId]
    name: Required[str]
    suffix: Required[str]
    secret: Required[str | None]
    created_at: Required[datetime]


class ApiKeyCreate(TypedDict, total=False):
    name: Required[str]


class ApiKeyList(TypedDict, total=False):
    object: Required[Literal["list"]]
    has_more: Required[bool]
    data: Required[list[ApiKey]]


class RelatedObject(TypedDict, total=False):
    id: Required[str]
    object: Required[str]


class EventData(TypedDict, total=False):
    object: Required[dict[str, Any]]
    previous_attributes: dict[str, Any]


BalanceTransactionKind: TypeAlias = Literal[
    "usage", "top_up", "payment_refund", "payment_dispute", "payment_dispute_reversal"
]


Currency: TypeAlias = Literal["EUR"]


class BalanceTransaction(TypedDict, total=False):
    id: Required[str]
    object: Required[Literal["balance_transaction"]]
    live: Required[Live]
    account: Required[AccountId]
    kind: Required[BalanceTransactionKind]
    amount_cents: Required[int]
    currency: Required[Currency]
    source_event: Required[str | None]
    created_at: Required[datetime]


EventActorType: TypeAlias = Literal["api_key", "user", "system"]


class EventActor(TypedDict, total=False):
    type: Required[EventActorType]
    id: Required[str | None]
    request_id: Required[str | None]


EventDestinationStatus: TypeAlias = Literal["enabled", "disabled"]


class EventDestinationWebhook(TypedDict, total=False):
    url: Required[str]
    signing_secret: Required[str | None]


EventDestinationDisabledReason: TypeAlias = Literal["user", "delivery_failures"] | None


class EventDestination(TypedDict, total=False):
    id: Required[str]
    object: Required[Literal["event_destination"]]
    live: Required[Live]
    account: Required[AccountId]
    name: Required[str]
    type: Required[Literal["webhook"]]
    status: Required[EventDestinationStatus]
    enabled_events: Required[list[str]]
    webhook: Required[EventDestinationWebhook]
    disabled_reason: Required[EventDestinationDisabledReason | None]
    created_at: Required[datetime]
    updated_at: Required[datetime]


class EventDestinationCreate(TypedDict, total=False):
    name: Required[str]
    url: Required[str]
    enabled_events: Required[list[str]]


class EventDestinationUpdate(TypedDict, total=False):
    name: str
    url: str
    enabled_events: list[str]


class EventDestinationList(TypedDict, total=False):
    object: Required[Literal["list"]]
    has_more: Required[bool]
    data: Required[list[EventDestination]]


InvoiceSeriesPurpose: TypeAlias = Literal["invoice", "credit_note", "amendment"]


class InvoiceSeries(TypedDict, total=False):
    id: Required[InvoiceSeriesId]
    object: Required[Literal["invoice_series"]]
    live: Required[Live]
    account: Required[AccountId]
    prefix: Required[str]
    default_for: Required[list[InvoiceSeriesPurpose]]
    created_at: Required[datetime]


class InvoiceSeriesCreate(TypedDict, total=False):
    prefix: Required[str]
    default_for: list[InvoiceSeriesPurpose]


class InvoiceSeriesUpdate(TypedDict, total=False):
    prefix: str
    default_for: list[InvoiceSeriesPurpose]


class InvoiceSeriesList(TypedDict, total=False):
    object: Required[Literal["list"]]
    has_more: Required[bool]
    data: Required[list[InvoiceSeries]]


TaxRegimeId: TypeAlias = Literal["global", "es"]


TaxEffect: TypeAlias = Literal["added", "withheld"]


TaxTreatment: TypeAlias = Literal["taxable", "exempt", "reverse_charge", "not_subject"]


class TaxRegimeTaxRule(TypedDict, total=False):
    rule: Required[str]
    description: Required[str]
    treatment: Required[TaxTreatment]
    rate: Required[str | None]
    authority_code: Required[str | None]
    legal_reference: Required[str | None]
    effective_from: Required[date]
    effective_until: Required[date | None]


CustomerId: TypeAlias = str


TaxIdId: TypeAlias = str


class Address(TypedDict, total=False):
    line_1: Required[str]
    line_2: Required[str | None]
    city: Required[str]
    postal_code: Required[str]
    state: Required[str | None]
    country: Required[str]


TaxIdType: TypeAlias = Literal["es_nif", "eu_vat", "local"]


class TaxIdInput(TypedDict, total=False):
    country: Required[str]
    type: Required[TaxIdType]
    value: Required[str]


class TaxIdSnapshot(TypedDict, total=False):
    country: Required[str]
    type: Required[str]
    value: Required[str]


PartyType: TypeAlias = Literal["account", "customer"]


class TaxIdOwner(TypedDict, total=False):
    type: Required[PartyType]
    id: Required[str]


TaxIdVerificationStatus: TypeAlias = Literal["pending", "completed", "failed"]


class TaxIdVerification(TypedDict, total=False):
    status: Required[TaxIdVerificationStatus]
    valid: Required[bool | None]
    completed_at: Required[datetime | None]


class AddressCreate(TypedDict, total=False):
    line_1: Required[str]
    line_2: str | None
    city: Required[str]
    postal_code: Required[str]
    state: str | None
    country: Required[str]


class AddressUpdate(TypedDict, total=False):
    line_1: str | None
    line_2: str | None
    city: str | None
    postal_code: str | None
    state: str | None
    country: str | None


class InvoiceSupplyPeriodCreate(TypedDict, total=False):
    start_date: Required[date]
    end_date: Required[date]


InvoiceKind: TypeAlias = Literal["invoice", "credit_note"]


InvoiceAmendmentReason: TypeAlias = Literal[
    "refund",
    "discount",
    "incorrect_customer_details",
    "incorrect_lines",
    "incorrect_tax",
    "customer_identification",
    "issued_by_mistake",
]


class InvoiceReference(TypedDict, total=False):
    id: Required[str | None]
    code: Required[str]
    issue_date: Required[date]


class InvoiceSupplyPeriod(TypedDict, total=False):
    start_date: Required[date]
    end_date: Required[date]


class GlobalInvoiceTaxRegime(TypedDict, total=False):
    key: Required[Literal["global"]]


class SpanishInvoiceQr(TypedDict, total=False):
    content: Required[str]
    image_url: Required[str]


VerifactuRegistrationKind: TypeAlias = Literal["alta", "anulacion"]


VerifactuRegistrationStatus: TypeAlias = Literal[
    "pending", "accepted", "accepted_with_errors", "rejected"
]


VerifactuRegistrationErrorCode: TypeAlias = Literal[
    "customer_tax_id_not_registered", "aeat_registration_error"
]


class VerifactuRegistrationRawError(TypedDict, total=False):
    code: Required[str | None]
    message: Required[str | None]


class VerifactuRegistrationError(TypedDict, total=False):
    code: Required[VerifactuRegistrationErrorCode]
    message: Required[str]
    raw: Required[VerifactuRegistrationRawError]


class InvoicePartySource(TypedDict, total=False):
    type: Required[PartyType]
    id: Required[str]


class InvoiceTax(TypedDict, total=False):
    tax: Required[str]
    rule: Required[str]
    effect: Required[TaxEffect]
    treatment: Required[TaxTreatment]
    description: Required[str]
    rate: Required[str | None]
    taxable_base: Required[Decimal]


class InvoiceTaxTotal(InvoiceTax, total=False):
    amount: Required[Decimal]


class InvoiceTotals(TypedDict, total=False):
    subtotal: Required[Decimal]
    tax: Required[Decimal]
    total_with_tax: Required[Decimal]
    withheld_tax: Required[Decimal]
    payable: Required[Decimal]


InvoicePdfStatus: TypeAlias = Literal["rendering", "ready", "failed"]


class InvoicePdf(TypedDict, total=False):
    id: Required[str]
    object: Required[Literal["invoice_pdf"]]
    live: Required[Live]
    invoice: Required[str]
    status: Required[InvoicePdfStatus]
    locale: Required[InvoiceLocale]
    rendered_at: Required[datetime | None]
    url: Required[str | None]
    url_expires_at: Required[datetime | None]


class AuthenticationError(TypedDict, total=False):
    code: Required[Literal["authentication_required"]]
    message: Required[str]


class AuthenticationErrorResponse(TypedDict, total=False):
    error: Required[AuthenticationError]


InvalidRequestErrorCode: TypeAlias = Literal[
    "invalid_request", "invalid_idempotency_key"
]


class InvalidRequestError(TypedDict, total=False):
    code: Required[InvalidRequestErrorCode]
    message: Required[str]


class InvalidRequestErrorResponse(TypedDict, total=False):
    error: Required[InvalidRequestError]


IdempotencyConflictErrorCode: TypeAlias = Literal[
    "idempotency_key_in_use", "idempotency_key_mismatch"
]


class IdempotencyConflictError(TypedDict, total=False):
    code: Required[IdempotencyConflictErrorCode]
    message: Required[str]


class IdempotencyConflictErrorResponse(TypedDict, total=False):
    error: Required[IdempotencyConflictError]


class ResourceNotFoundError(TypedDict, total=False):
    code: Required[Literal["resource_not_found"]]
    message: Required[str]


class ResourceNotFoundErrorResponse(TypedDict, total=False):
    error: Required[ResourceNotFoundError]


InvalidResourceErrorCode: TypeAlias = Literal[
    "invalid_account", "invalid_api_key", "invalid_invoice_series"
]


class BasicValidationDetail(TypedDict, total=False):
    field: Required[str]
    message: Required[str]


class InvalidResourceError(TypedDict, total=False):
    code: Required[InvalidResourceErrorCode]
    message: Required[str]
    details: Required[list[BasicValidationDetail]]


class InvalidResourceErrorResponse(TypedDict, total=False):
    error: Required[InvalidResourceError]


class CustomerNotFoundError(TypedDict, total=False):
    code: Required[Literal["customer_not_found"]]
    message: Required[str]


class CustomerNotFoundErrorResponse(TypedDict, total=False):
    error: Required[CustomerNotFoundError]


class AccountNotConfiguredError(TypedDict, total=False):
    code: Required[Literal["account_not_configured"]]
    message: Required[str]


class AccountNotConfiguredErrorResponse(TypedDict, total=False):
    error: Required[AccountNotConfiguredError]


class BalanceExhaustedError(TypedDict, total=False):
    code: Required[Literal["balance_exhausted"]]
    message: Required[str]


class BalanceExhaustedErrorResponse(TypedDict, total=False):
    error: Required[BalanceExhaustedError]


class PdfRenderInProgressError(TypedDict, total=False):
    code: Required[Literal["pdf_render_in_progress"]]
    message: Required[str]


class PdfRenderInProgressErrorResponse(TypedDict, total=False):
    error: Required[PdfRenderInProgressError]


class PdfRenderingUnavailableError(TypedDict, total=False):
    code: Required[Literal["pdf_rendering_unavailable"]]
    message: Required[str]


class PdfRenderingUnavailableErrorResponse(TypedDict, total=False):
    error: Required[PdfRenderingUnavailableError]


class ValidationDetail(TypedDict, total=False):
    code: Required[str]
    field: Required[str]
    message: Required[str]
    metadata: Required[dict[str, Any]]


class AccountUpdate(TypedDict, total=False):
    invoice_numbering_scope: AccountInvoiceNumberingScope
    default_series: AccountDefaultSeries


class Event(TypedDict, total=False):
    id: Required[str]
    object: Required[Literal["event"]]
    live: Required[Live]
    account: Required[AccountId]
    type: Required[str]
    occurred_at: Required[datetime]
    actor: Required[EventActor]
    related_object: Required[RelatedObject | None]
    data: Required[EventData]


class EventList(TypedDict, total=False):
    object: Required[Literal["list"]]
    has_more: Required[bool]
    data: Required[list[Event]]


class TaxRegimeTax(TypedDict, total=False):
    tax: Required[str]
    name: Required[str]
    effect: Required[TaxEffect]
    rules: Required[list[TaxRegimeTaxRule]]


class TaxId(TypedDict, total=False):
    id: Required[TaxIdId]
    object: Required[Literal["tax_id"]]
    live: Required[Live]
    country: Required[str]
    type: Required[TaxIdType]
    value: Required[str]
    owner: Required[TaxIdOwner]
    verification: Required[TaxIdVerification | None]


class CustomerCreate(TypedDict, total=False):
    name: Required[str]
    invoice_prefix: str
    tax_id: Required[TaxIdInput]
    email: str | None
    phone: str | None
    address: AddressCreate | None


class CustomerUpdate(TypedDict, total=False):
    name: str
    invoice_prefix: str
    tax_id: TaxIdInput
    email: str | None
    phone: str | None
    address: AddressUpdate | None


class TaxReference(TypedDict, total=False):
    tax: Required[str]
    rule: Required[str]
    effect: TaxEffect
    treatment: TaxTreatment
    description: str
    rate: DecimalInput
    taxable_base: DecimalInput


class InvoiceAmendment(TypedDict, total=False):
    id: Required[str]
    object: Required[Literal["invoice_amendment"]]
    live: Required[Live]
    reason: Required[InvoiceAmendmentReason]
    original: Required[InvoiceReference]
    credit_note: Required[InvoiceReference | None]
    replacement: Required[InvoiceReference | None]
    created_at: Required[datetime]


class VerifactuRegistration(TypedDict, total=False):
    id: Required[str]
    object: Required[Literal["verifactu_registration"]]
    live: Required[Live]
    invoice: Required[str]
    kind: Required[VerifactuRegistrationKind]
    status: Required[VerifactuRegistrationStatus]
    submitted_at: Required[datetime | None]
    csv: Required[str | None]
    error: Required[VerifactuRegistrationError | None]


class InvoiceParty(TypedDict, total=False):
    source: Required[InvoicePartySource]
    name: Required[str]
    tax_id: Required[TaxIdSnapshot]
    email: Required[str | None]
    phone: Required[str | None]
    address: Required[Address | None]


class InvoiceLine(TypedDict, total=False):
    index: Required[int]
    description: Required[str]
    quantity: Required[Decimal]
    unit_price: Required[Decimal]
    subtotal: Required[Decimal]
    taxes: Required[list[InvoiceTax]]


class InvalidCustomerError(TypedDict, total=False):
    code: Required[Literal["invalid_customer"]]
    message: Required[str]
    details: Required[list[ValidationDetail]]


class InvalidCustomerErrorResponse(TypedDict, total=False):
    error: Required[InvalidCustomerError]


class InvalidInvoiceError(TypedDict, total=False):
    code: Required[Literal["invalid_invoice"]]
    message: Required[str]
    details: Required[list[ValidationDetail]]


class InvalidInvoiceErrorResponse(TypedDict, total=False):
    error: Required[InvalidInvoiceError]


class Account(TypedDict, total=False):
    id: Required[AccountId]
    object: Required[Literal["account"]]
    live: Required[Live]
    name: Required[str]
    tax_id: Required[TaxId]
    email: Required[str | None]
    phone: Required[str | None]
    address: Required[Address]
    tax_regime: Required[str]
    timezone: Required[str]
    invoice_locale: Required[InvoiceLocale]
    invoice_numbering_scope: Required[AccountInvoiceNumberingScope]
    default_series: Required[AccountDefaultSeries]
    created_at: Required[datetime]
    updated_at: Required[datetime]


class AccountList(TypedDict, total=False):
    object: Required[Literal["list"]]
    has_more: Required[bool]
    data: Required[list[Account]]


class TaxRegime(TypedDict, total=False):
    id: Required[TaxRegimeId]
    object: Required[Literal["tax_regime"]]
    taxes: Required[list[TaxRegimeTax]]


class TaxRegimeList(TypedDict, total=False):
    object: Required[Literal["list"]]
    has_more: Required[bool]
    data: Required[list[TaxRegime]]


class Customer(TypedDict, total=False):
    id: Required[CustomerId]
    object: Required[Literal["customer"]]
    live: Required[Live]
    name: Required[str]
    invoice_prefix: Required[str]
    tax_id: Required[TaxId]
    email: Required[str | None]
    phone: Required[str | None]
    address: Required[Address | None]
    created_at: Required[datetime]
    updated_at: Required[datetime]


class CustomerList(TypedDict, total=False):
    object: Required[Literal["list"]]
    has_more: Required[bool]
    data: Required[list[Customer]]


class InvoiceLineCreate(TypedDict, total=False):
    description: Required[str]
    quantity: DecimalInput
    unit_price: Required[DecimalInput]
    taxes: Required[TaxReferenceList]


class Verifactu(TypedDict, total=False):
    registrations: Required[list[VerifactuRegistration]]


class InvoiceCreate(TypedDict, total=False):
    customer: CustomerId | None
    series: str
    issue_date: date
    supply_period: InvoiceSupplyPeriodCreate
    lines: Required[list[InvoiceLineCreate]]


class InvoiceAmendmentCreate(TypedDict, total=False):
    reason: Required[InvoiceAmendmentReason]
    replacement: InvoiceCreate


class SpanishInvoiceTaxRegimeDetails(TypedDict, total=False):
    qr: Required[SpanishInvoiceQr]
    verifactu: Required[Verifactu]


class SpanishInvoiceTaxRegime(TypedDict, total=False):
    key: Required[Literal["es"]]
    es: Required[SpanishInvoiceTaxRegimeDetails]


InvoiceTaxRegime: TypeAlias = GlobalInvoiceTaxRegime | SpanishInvoiceTaxRegime


class Invoice(TypedDict, total=False):
    id: Required[str]
    object: Required[Literal["invoice"]]
    live: Required[Live]
    account: Required[str]
    kind: Required[InvoiceKind]
    code: Required[str]
    series: Required[str]
    issue_date: Required[date]
    supply_period: Required[InvoiceSupplyPeriod | None]
    preceding_invoice: Required[InvoiceReference | None]
    currency: Required[Literal["EUR"]]
    supplier: Required[InvoiceParty]
    customer: Required[InvoiceParty | None]
    lines: Required[list[InvoiceLine]]
    tax_totals: Required[list[InvoiceTaxTotal]]
    totals: Required[InvoiceTotals]
    created_at: Required[datetime]
    tax_regime: Required[InvoiceTaxRegime]
    amendments: Required[list[InvoiceAmendment]]


class InvoiceList(TypedDict, total=False):
    object: Required[Literal["list"]]
    has_more: Required[bool]
    data: Required[list[Invoice]]
