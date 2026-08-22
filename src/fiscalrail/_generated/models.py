"""Generated from FiscalRail's OpenAPI contract. Do not edit by hand."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, StrEnum
from typing import Any, Literal, TypeAlias

from fiscalrail._model import FiscalRailModel, ResponseModel
from fiscalrail._types import DecimalInput

RequestId: TypeAlias = str


AccountId: TypeAlias = str


ApiKeyId: TypeAlias = str


InvoiceSeriesId: TypeAlias = str


PaymentInstructionId: TypeAlias = str


Live: TypeAlias = bool


class InvoiceLocale(StrEnum):
    en = "en"
    es = "es"


@dataclass(frozen=True, kw_only=True, slots=True)
class AccountDefaultSeries(FiscalRailModel):
    invoice: InvoiceSeriesId
    credit_note: InvoiceSeriesId | None
    amendment: InvoiceSeriesId | None


class AccountInvoiceNumberingScope(StrEnum):
    account = "account"
    customer = "customer"


@dataclass(frozen=True, kw_only=True, slots=True)
class ApiKey(ResponseModel):
    id: ApiKeyId
    object: Literal["api_key"]
    live: Live
    account: AccountId
    name: str
    suffix: str
    secret: str | None
    created_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class ApiKeyCreate(FiscalRailModel):
    name: str


@dataclass(frozen=True, kw_only=True, slots=True)
class ApiKeyList(FiscalRailModel):
    object: Literal["list"]
    has_more: bool
    data: list[ApiKey]


@dataclass(frozen=True, kw_only=True, slots=True)
class RelatedObject(FiscalRailModel):
    id: str
    object: str


@dataclass(frozen=True, kw_only=True, slots=True)
class EventData(FiscalRailModel):
    object: dict[str, Any]
    previous_attributes: dict[str, Any] | None = None


class BalanceTransactionKind(StrEnum):
    usage = "usage"
    top_up = "top_up"
    payment_refund = "payment_refund"
    payment_dispute = "payment_dispute"
    payment_dispute_reversal = "payment_dispute_reversal"


class Currency(StrEnum):
    EUR = "EUR"


@dataclass(frozen=True, kw_only=True, slots=True)
class BalanceTransaction(ResponseModel):
    id: str
    object: Literal["balance_transaction"]
    live: Live
    account: AccountId
    kind: BalanceTransactionKind
    amount_cents: int
    currency: Currency
    source_event: str | None
    created_at: datetime


class EventActorType(StrEnum):
    api_key = "api_key"
    user = "user"
    system = "system"


@dataclass(frozen=True, kw_only=True, slots=True)
class EventActor(FiscalRailModel):
    type: EventActorType
    id: str | None
    request_id: str | None


class EventDestinationStatus(StrEnum):
    enabled = "enabled"
    disabled = "disabled"


@dataclass(frozen=True, kw_only=True, slots=True)
class EventDestinationWebhook(FiscalRailModel):
    url: str
    signing_secret: str | None


class EventDestinationDisabledReason(Enum):
    user = "user"
    delivery_failures = "delivery_failures"
    NoneType_None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class EventDestination(ResponseModel):
    id: str
    object: Literal["event_destination"]
    live: Live
    account: AccountId
    name: str
    type: Literal["webhook"]
    status: EventDestinationStatus
    enabled_events: list[str]
    webhook: EventDestinationWebhook
    disabled_reason: EventDestinationDisabledReason | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class EventDestinationCreate(FiscalRailModel):
    name: str
    url: str
    enabled_events: list[str]


@dataclass(frozen=True, kw_only=True, slots=True)
class EventDestinationUpdate(FiscalRailModel):
    name: str | None = None
    url: str | None = None
    enabled_events: list[str] | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class EventDestinationList(FiscalRailModel):
    object: Literal["list"]
    has_more: bool
    data: list[EventDestination]


class InvoiceSeriesPurpose(StrEnum):
    invoice = "invoice"
    credit_note = "credit_note"
    amendment = "amendment"


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceSeries(ResponseModel):
    id: InvoiceSeriesId
    object: Literal["invoice_series"]
    live: Live
    account: AccountId
    prefix: str
    default_for: list[InvoiceSeriesPurpose]
    created_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceSeriesCreate(FiscalRailModel):
    prefix: str
    default_for: list[InvoiceSeriesPurpose] | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceSeriesUpdate(FiscalRailModel):
    prefix: str | None = None
    default_for: list[InvoiceSeriesPurpose] | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceSeriesList(FiscalRailModel):
    object: Literal["list"]
    has_more: bool
    data: list[InvoiceSeries]


@dataclass(frozen=True, kw_only=True, slots=True)
class PaymentInstructionBankTransfer(FiscalRailModel):
    beneficiary: str
    iban: str
    bic: str | None


@dataclass(frozen=True, kw_only=True, slots=True)
class PaymentInstructionBankTransferInput(FiscalRailModel):
    beneficiary: str
    iban: str
    bic: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class PaymentInstructionBankTransferUpdate(FiscalRailModel):
    beneficiary: str | None = None
    iban: str | None = None
    bic: str | None = None


class TaxRegimeId(StrEnum):
    global_ = "global"
    es = "es"


class TaxEffect(StrEnum):
    added = "added"
    withheld = "withheld"


class TaxTreatment(StrEnum):
    taxable = "taxable"
    exempt = "exempt"
    reverse_charge = "reverse_charge"
    not_subject = "not_subject"


@dataclass(frozen=True, kw_only=True, slots=True)
class TaxRegimeTaxRule(FiscalRailModel):
    rule: str
    description: str
    treatment: TaxTreatment
    rate: str | None
    authority_code: str | None
    legal_reference: str | None
    effective_from: date
    effective_until: date | None


CustomerId: TypeAlias = str


TaxIdId: TypeAlias = str


@dataclass(frozen=True, kw_only=True, slots=True)
class Address(FiscalRailModel):
    line_1: str
    line_2: str | None
    city: str
    postal_code: str
    state: str | None
    country: str


class TaxIdType(StrEnum):
    es_nif = "es_nif"
    eu_vat = "eu_vat"
    local = "local"


@dataclass(frozen=True, kw_only=True, slots=True)
class TaxIdInput(FiscalRailModel):
    country: str
    type: TaxIdType
    value: str


@dataclass(frozen=True, kw_only=True, slots=True)
class TaxIdSnapshot(FiscalRailModel):
    country: str
    type: str
    value: str


class PartyType(StrEnum):
    account = "account"
    customer = "customer"


@dataclass(frozen=True, kw_only=True, slots=True)
class TaxIdOwner(FiscalRailModel):
    type: PartyType
    id: str


class TaxIdVerificationStatus(StrEnum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


@dataclass(frozen=True, kw_only=True, slots=True)
class TaxIdVerification(FiscalRailModel):
    status: TaxIdVerificationStatus
    valid: bool | None
    completed_at: datetime | None


@dataclass(frozen=True, kw_only=True, slots=True)
class AddressCreate(FiscalRailModel):
    line_1: str
    city: str
    postal_code: str
    country: str
    line_2: str | None = None
    state: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class AddressUpdate(FiscalRailModel):
    line_1: str | None = None
    line_2: str | None = None
    city: str | None = None
    postal_code: str | None = None
    state: str | None = None
    country: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceSupplyPeriodCreate(FiscalRailModel):
    start_date: date
    end_date: date


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoicePaymentTermsCreate(FiscalRailModel):
    due_date: date | None = None
    options: list[PaymentInstructionId] | None = None


class InvoiceKind(StrEnum):
    invoice = "invoice"
    credit_note = "credit_note"


class InvoiceAmendmentReason(StrEnum):
    refund = "refund"
    discount = "discount"
    incorrect_customer_details = "incorrect_customer_details"
    incorrect_lines = "incorrect_lines"
    incorrect_tax = "incorrect_tax"
    customer_identification = "customer_identification"
    issued_by_mistake = "issued_by_mistake"


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceReference(FiscalRailModel):
    id: str | None
    code: str
    issue_date: date


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceSupplyPeriod(FiscalRailModel):
    start_date: date
    end_date: date


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoicePaymentOption(FiscalRailModel):
    payment_instruction: PaymentInstructionId
    type: Literal["bank_transfer"]
    reference: str
    bank_transfer: PaymentInstructionBankTransfer


@dataclass(frozen=True, kw_only=True, slots=True)
class GlobalInvoiceTaxRegime(FiscalRailModel):
    key: Literal["global"]


@dataclass(frozen=True, kw_only=True, slots=True)
class SpanishInvoiceQr(FiscalRailModel):
    content: str
    image_url: str


class VerifactuRegistrationKind(StrEnum):
    alta = "alta"
    anulacion = "anulacion"


class VerifactuRegistrationStatus(StrEnum):
    pending = "pending"
    accepted = "accepted"
    accepted_with_errors = "accepted_with_errors"
    rejected = "rejected"


class VerifactuRegistrationErrorCode(StrEnum):
    customer_tax_id_not_registered = "customer_tax_id_not_registered"
    aeat_registration_error = "aeat_registration_error"


@dataclass(frozen=True, kw_only=True, slots=True)
class VerifactuRegistrationRawError(FiscalRailModel):
    code: str | None
    message: str | None


@dataclass(frozen=True, kw_only=True, slots=True)
class VerifactuRegistrationError(FiscalRailModel):
    code: VerifactuRegistrationErrorCode
    message: str
    raw: VerifactuRegistrationRawError


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoicePartySource(FiscalRailModel):
    type: PartyType
    id: str


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceTax(FiscalRailModel):
    tax: str
    rule: str
    effect: TaxEffect
    treatment: TaxTreatment
    description: str
    rate: str | None
    taxable_base: Decimal


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceTaxTotal(InvoiceTax):
    amount: Decimal


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceTotals(FiscalRailModel):
    subtotal: Decimal
    tax: Decimal
    total_with_tax: Decimal
    withheld_tax: Decimal
    payable: Decimal


class InvoicePdfStatus(StrEnum):
    rendering = "rendering"
    ready = "ready"
    failed = "failed"


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoicePdf(ResponseModel):
    id: str
    object: Literal["invoice_pdf"]
    live: Live
    invoice: str
    status: InvoicePdfStatus
    locale: InvoiceLocale
    rendered_at: datetime | None
    url: str | None
    url_expires_at: datetime | None


@dataclass(frozen=True, kw_only=True, slots=True)
class AuthenticationError(FiscalRailModel):
    code: Literal["authentication_required"]
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class AuthenticationErrorResponse(FiscalRailModel):
    error: AuthenticationError


class InvalidRequestErrorCode(StrEnum):
    invalid_request = "invalid_request"
    invalid_idempotency_key = "invalid_idempotency_key"


@dataclass(frozen=True, kw_only=True, slots=True)
class InvalidRequestError(FiscalRailModel):
    code: InvalidRequestErrorCode
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class InvalidRequestErrorResponse(FiscalRailModel):
    error: InvalidRequestError


class IdempotencyConflictErrorCode(StrEnum):
    idempotency_key_in_use = "idempotency_key_in_use"
    idempotency_key_mismatch = "idempotency_key_mismatch"


@dataclass(frozen=True, kw_only=True, slots=True)
class IdempotencyConflictError(FiscalRailModel):
    code: IdempotencyConflictErrorCode
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class IdempotencyConflictErrorResponse(FiscalRailModel):
    error: IdempotencyConflictError


@dataclass(frozen=True, kw_only=True, slots=True)
class ResourceNotFoundError(FiscalRailModel):
    code: Literal["resource_not_found"]
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class ResourceNotFoundErrorResponse(FiscalRailModel):
    error: ResourceNotFoundError


class InvalidResourceErrorCode(StrEnum):
    invalid_account = "invalid_account"
    invalid_api_key = "invalid_api_key"
    invalid_invoice_series = "invalid_invoice_series"
    invalid_payment_instruction = "invalid_payment_instruction"


@dataclass(frozen=True, kw_only=True, slots=True)
class BasicValidationDetail(FiscalRailModel):
    field: str
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class InvalidResourceError(FiscalRailModel):
    code: InvalidResourceErrorCode
    message: str
    details: list[BasicValidationDetail]


@dataclass(frozen=True, kw_only=True, slots=True)
class InvalidResourceErrorResponse(FiscalRailModel):
    error: InvalidResourceError


@dataclass(frozen=True, kw_only=True, slots=True)
class CustomerNotFoundError(FiscalRailModel):
    code: Literal["customer_not_found"]
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class CustomerNotFoundErrorResponse(FiscalRailModel):
    error: CustomerNotFoundError


@dataclass(frozen=True, kw_only=True, slots=True)
class AccountNotConfiguredError(FiscalRailModel):
    code: Literal["account_not_configured"]
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class AccountNotConfiguredErrorResponse(FiscalRailModel):
    error: AccountNotConfiguredError


@dataclass(frozen=True, kw_only=True, slots=True)
class BalanceExhaustedError(FiscalRailModel):
    code: Literal["balance_exhausted"]
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class BalanceExhaustedErrorResponse(FiscalRailModel):
    error: BalanceExhaustedError


@dataclass(frozen=True, kw_only=True, slots=True)
class PdfRenderInProgressError(FiscalRailModel):
    code: Literal["pdf_render_in_progress"]
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class PdfRenderInProgressErrorResponse(FiscalRailModel):
    error: PdfRenderInProgressError


@dataclass(frozen=True, kw_only=True, slots=True)
class PdfRenderingUnavailableError(FiscalRailModel):
    code: Literal["pdf_rendering_unavailable"]
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class PdfRenderingUnavailableErrorResponse(FiscalRailModel):
    error: PdfRenderingUnavailableError


@dataclass(frozen=True, kw_only=True, slots=True)
class ValidationDetail(FiscalRailModel):
    code: str
    field: str
    message: str
    metadata: dict[str, Any]


@dataclass(frozen=True, kw_only=True, slots=True)
class AccountUpdate(FiscalRailModel):
    invoice_numbering_scope: AccountInvoiceNumberingScope | None = (
        AccountInvoiceNumberingScope.account
    )
    default_series: AccountDefaultSeries | None = None
    default_payment_instructions: list[PaymentInstructionId] | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Event(ResponseModel):
    id: str
    object: Literal["event"]
    live: Live
    account: AccountId
    type: str
    occurred_at: datetime
    actor: EventActor
    related_object: RelatedObject | None
    data: EventData


@dataclass(frozen=True, kw_only=True, slots=True)
class EventList(FiscalRailModel):
    object: Literal["list"]
    has_more: bool
    data: list[Event]


@dataclass(frozen=True, kw_only=True, slots=True)
class PaymentInstruction(ResponseModel):
    id: PaymentInstructionId
    object: Literal["payment_instruction"]
    live: Live
    account: AccountId
    label: str
    type: Literal["bank_transfer"]
    bank_transfer: PaymentInstructionBankTransfer
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class PaymentInstructionCreate(FiscalRailModel):
    label: str
    type: Literal["bank_transfer"]
    bank_transfer: PaymentInstructionBankTransferInput


@dataclass(frozen=True, kw_only=True, slots=True)
class PaymentInstructionUpdate(FiscalRailModel):
    label: str | None = None
    bank_transfer: PaymentInstructionBankTransferUpdate | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class PaymentInstructionList(FiscalRailModel):
    object: Literal["list"]
    has_more: bool
    data: list[PaymentInstruction]


@dataclass(frozen=True, kw_only=True, slots=True)
class TaxRegimeTax(FiscalRailModel):
    tax: str
    name: str
    effect: TaxEffect
    rules: list[TaxRegimeTaxRule]


@dataclass(frozen=True, kw_only=True, slots=True)
class TaxId(ResponseModel):
    id: TaxIdId
    object: Literal["tax_id"]
    live: Live
    country: str
    type: TaxIdType
    value: str
    owner: TaxIdOwner
    verification: TaxIdVerification | None


@dataclass(frozen=True, kw_only=True, slots=True)
class CustomerCreate(FiscalRailModel):
    name: str
    tax_id: TaxIdInput
    invoice_prefix: str | None = None
    email: str | None = None
    phone: str | None = None
    address: AddressCreate | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class CustomerUpdate(FiscalRailModel):
    name: str | None = None
    invoice_prefix: str | None = None
    tax_id: TaxIdInput | None = None
    email: str | None = None
    phone: str | None = None
    address: AddressUpdate | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class TaxReference(FiscalRailModel):
    tax: str
    rule: str
    effect: TaxEffect | None = None
    treatment: TaxTreatment | None = None
    description: str | None = None
    rate: DecimalInput | None = None
    taxable_base: DecimalInput | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceAmendment(ResponseModel):
    id: str
    object: Literal["invoice_amendment"]
    live: Live
    reason: InvoiceAmendmentReason
    original: InvoiceReference
    credit_note: InvoiceReference | None
    replacement: InvoiceReference | None
    created_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoicePaymentTerms(FiscalRailModel):
    due_date: date | None
    options: list[InvoicePaymentOption]


@dataclass(frozen=True, kw_only=True, slots=True)
class VerifactuRegistration(FiscalRailModel):
    id: str
    object: Literal["verifactu_registration"]
    live: Live
    invoice: str
    kind: VerifactuRegistrationKind
    status: VerifactuRegistrationStatus
    submitted_at: datetime | None
    csv: str | None
    error: VerifactuRegistrationError | None


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceParty(FiscalRailModel):
    source: InvoicePartySource
    name: str
    tax_id: TaxIdSnapshot
    email: str | None
    phone: str | None
    address: Address | None


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceLine(FiscalRailModel):
    index: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal
    taxes: list[InvoiceTax]


@dataclass(frozen=True, kw_only=True, slots=True)
class InvalidCustomerError(FiscalRailModel):
    code: Literal["invalid_customer"]
    message: str
    details: list[ValidationDetail]


@dataclass(frozen=True, kw_only=True, slots=True)
class InvalidCustomerErrorResponse(FiscalRailModel):
    error: InvalidCustomerError


@dataclass(frozen=True, kw_only=True, slots=True)
class InvalidInvoiceError(FiscalRailModel):
    code: Literal["invalid_invoice"]
    message: str
    details: list[ValidationDetail]


@dataclass(frozen=True, kw_only=True, slots=True)
class InvalidInvoiceErrorResponse(FiscalRailModel):
    error: InvalidInvoiceError


@dataclass(frozen=True, kw_only=True, slots=True)
class Account(ResponseModel):
    id: AccountId
    object: Literal["account"]
    live: Live
    name: str
    tax_id: TaxId
    email: str | None
    phone: str | None
    address: Address
    tax_regime: str
    timezone: str
    invoice_locale: InvoiceLocale
    invoice_numbering_scope: AccountInvoiceNumberingScope
    default_series: AccountDefaultSeries
    default_payment_instructions: list[PaymentInstructionId]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class AccountList(FiscalRailModel):
    object: Literal["list"]
    has_more: bool
    data: list[Account]


@dataclass(frozen=True, kw_only=True, slots=True)
class TaxRegime(ResponseModel):
    id: TaxRegimeId
    object: Literal["tax_regime"]
    taxes: list[TaxRegimeTax]


@dataclass(frozen=True, kw_only=True, slots=True)
class TaxRegimeList(FiscalRailModel):
    object: Literal["list"]
    has_more: bool
    data: list[TaxRegime]


@dataclass(frozen=True, kw_only=True, slots=True)
class Customer(ResponseModel):
    id: CustomerId
    object: Literal["customer"]
    live: Live
    name: str
    invoice_prefix: str
    tax_id: TaxId
    email: str | None
    phone: str | None
    address: Address | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class CustomerList(FiscalRailModel):
    object: Literal["list"]
    has_more: bool
    data: list[Customer]


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceLineCreate(FiscalRailModel):
    description: str
    unit_price: DecimalInput
    taxes: list[TaxReference]
    quantity: DecimalInput | None = "1"


@dataclass(frozen=True, kw_only=True, slots=True)
class Verifactu(FiscalRailModel):
    registrations: list[VerifactuRegistration]


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceCreate(FiscalRailModel):
    lines: list[InvoiceLineCreate]
    customer: CustomerId | None = None
    series: str | None = None
    issue_date: date | None = None
    supply_period: InvoiceSupplyPeriodCreate | None = None
    payment_terms: InvoicePaymentTermsCreate | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceAmendmentCreate(FiscalRailModel):
    reason: InvoiceAmendmentReason
    replacement: InvoiceCreate | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class SpanishInvoiceTaxRegimeDetails(FiscalRailModel):
    qr: SpanishInvoiceQr
    verifactu: Verifactu


@dataclass(frozen=True, kw_only=True, slots=True)
class SpanishInvoiceTaxRegime(FiscalRailModel):
    key: Literal["es"]
    es: SpanishInvoiceTaxRegimeDetails


InvoiceTaxRegime: TypeAlias = GlobalInvoiceTaxRegime | SpanishInvoiceTaxRegime


@dataclass(frozen=True, kw_only=True, slots=True)
class Invoice(ResponseModel):
    id: str
    object: Literal["invoice"]
    live: Live
    account: str
    kind: InvoiceKind
    code: str
    series: str
    issue_date: date
    supply_period: InvoiceSupplyPeriod | None
    preceding_invoice: InvoiceReference | None
    currency: Literal["EUR"]
    supplier: InvoiceParty
    customer: InvoiceParty | None
    payment_terms: InvoicePaymentTerms
    lines: list[InvoiceLine]
    tax_totals: list[InvoiceTaxTotal]
    totals: InvoiceTotals
    created_at: datetime
    tax_regime: InvoiceTaxRegime
    amendments: list[InvoiceAmendment]


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceList(FiscalRailModel):
    object: Literal["list"]
    has_more: bool
    data: list[Invoice]
