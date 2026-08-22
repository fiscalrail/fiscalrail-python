from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationDetail:
    field: str
    message: str
    code: str | None = None
    metadata: Mapping[str, Any] | None = None


class FiscalRailError(Exception):
    """Base class for all SDK errors."""


class WebhookSignatureError(FiscalRailError):
    """A webhook signature is missing, invalid, or outside its tolerance."""


class ResponseParseError(FiscalRailError):
    """The API returned a response that does not match the SDK contract."""

    def __init__(
        self,
        *,
        model: str,
        field: str,
        message: str,
        request_id: str | None,
    ) -> None:
        super().__init__(
            f"Could not parse FiscalRail {model} response at {field}: {message}"
        )
        self.model = model
        self.field = field
        self.message = message
        self.request_id = request_id


class APIConnectionError(FiscalRailError):
    def __init__(self, message: str, *, idempotency_key: str | None = None) -> None:
        super().__init__(message)
        self.idempotency_key = idempotency_key


class APITimeoutError(APIConnectionError):
    pass


class APIError(FiscalRailError):
    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int,
        request_id: str | None,
        details: list[ValidationDetail] | None = None,
        idempotency_key: str | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.request_id = request_id
        self.details = details or []
        self.idempotency_key = idempotency_key
        self.body = body

    def __str__(self) -> str:
        suffix = f" (request_id: {self.request_id})" if self.request_id else ""
        return f"{self.message}{suffix}"


class AuthenticationError(APIError):
    pass


class InvalidRequestError(APIError):
    pass


class ResourceNotFoundError(APIError):
    pass


class InvalidCustomerError(APIError):
    pass


class CustomerNotFoundError(APIError):
    pass


class InvalidInvoiceError(APIError):
    pass


class InvalidInvoiceSeriesError(APIError):
    pass


class InvalidPaymentInstructionError(APIError):
    pass


class InvalidInvoiceAmendmentError(APIError):
    pass


class AccountNotConfiguredError(APIError):
    pass


class BalanceExhaustedError(APIError):
    pass


class IdempotencyConflictError(APIError):
    pass


class PdfRenderInProgressError(APIError):
    pass


class PdfRenderingUnavailableError(APIError):
    pass


_ERROR_CLASSES: dict[str, type[APIError]] = {
    "authentication_required": AuthenticationError,
    "invalid_request": InvalidRequestError,
    "invalid_idempotency_key": InvalidRequestError,
    "resource_not_found": ResourceNotFoundError,
    "invalid_customer": InvalidCustomerError,
    "customer_not_found": CustomerNotFoundError,
    "invalid_invoice": InvalidInvoiceError,
    "invalid_invoice_series": InvalidInvoiceSeriesError,
    "invalid_payment_instruction": InvalidPaymentInstructionError,
    "invalid_invoice_amendment": InvalidInvoiceAmendmentError,
    "account_not_configured": AccountNotConfiguredError,
    "balance_exhausted": BalanceExhaustedError,
    "idempotency_key_in_use": IdempotencyConflictError,
    "idempotency_key_mismatch": IdempotencyConflictError,
    "pdf_render_in_progress": PdfRenderInProgressError,
    "pdf_rendering_unavailable": PdfRenderingUnavailableError,
}


def api_error(
    *,
    status_code: int,
    request_id: str | None,
    payload: Any,
    idempotency_key: str | None,
) -> APIError:
    error_data = payload.get("error", {}) if isinstance(payload, dict) else {}
    code = str(error_data.get("code") or f"http_{status_code}")
    message = str(
        error_data.get("message") or f"FiscalRail returned HTTP {status_code}"
    )
    raw_details = error_data.get("details")
    details: list[ValidationDetail] = []
    if isinstance(raw_details, list):
        for detail in raw_details:
            if not isinstance(detail, dict):
                continue
            metadata = detail.get("metadata")
            details.append(
                ValidationDetail(
                    field=str(detail.get("field") or "base"),
                    message=str(detail.get("message") or "Invalid value"),
                    code=str(detail["code"]) if detail.get("code") else None,
                    metadata=metadata if isinstance(metadata, dict) else None,
                )
            )

    error_class = _ERROR_CLASSES.get(code, APIError)
    return error_class(
        message,
        code=code,
        status_code=status_code,
        request_id=request_id,
        details=details,
        idempotency_key=idempotency_key,
        body=payload,
    )
