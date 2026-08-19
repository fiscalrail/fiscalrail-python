from __future__ import annotations

from collections.abc import Iterator, Sequence
from datetime import date
from typing import Any, TypeVar, Unpack
from uuid import uuid4

from fiscalrail._binary import BinaryContent
from fiscalrail._decoding import DecodeError, decode_model, decode_page
from fiscalrail._generated.operations import OPERATIONS
from fiscalrail._transport import JsonResponse, Transport
from fiscalrail.errors import ResponseParseError
from fiscalrail.models import (
    Account,
    ApiKey,
    Customer,
    Event,
    EventDestination,
    Invoice,
    InvoiceAmendment,
    InvoicePdf,
    InvoiceSeries,
    Page,
    ResponseModel,
    TaxId,
    TaxRegime,
)
from fiscalrail.params import (
    AccountUpdateParams,
    ApiKeyCreateParams,
    CustomerCreateParams,
    CustomerUpdateParams,
    EventDestinationCreateParams,
    EventDestinationUpdateParams,
    InvoiceAmendmentReason,
    InvoiceIssueParams,
    InvoiceLocale,
    InvoiceSeriesCreateParams,
    InvoiceSeriesUpdateParams,
)

ModelT = TypeVar("ModelT", bound=ResponseModel)

WRAPPED_OPERATION_IDS = frozenset(
    {
        "createCustomer",
        "createApiKey",
        "createInvoiceSeries",
        "deleteCustomer",
        "deleteApiKey",
        "deleteEventDestination",
        "deleteInvoiceSeries",
        "issueInvoice",
        "createEventDestination",
        "disableEventDestination",
        "enableEventDestination",
        "listAccounts",
        "listApiKeys",
        "listCustomers",
        "listEventDestinations",
        "listEvents",
        "listInvoiceSeries",
        "listInvoices",
        "listTaxRegimes",
        "amendInvoice",
        "renderInvoicePdf",
        "retrieveAccount",
        "retrieveApiKey",
        "retrieveCustomer",
        "retrieveEventDestination",
        "retrieveEvent",
        "retrieveInvoice",
        "retrieveInvoicePdf",
        "retrieveInvoiceSeries",
        "retrieveTaxId",
        "retrieveTaxRegime",
        "updateAccount",
        "updateCustomer",
        "updateEventDestination",
        "updateInvoiceSeries",
    }
)


def _operation(operation_id: str, **path_parameters: str) -> tuple[str, str]:
    operation = OPERATIONS[operation_id]
    return operation.method, operation.path.format(**path_parameters)


def _parse(
    model: type[ModelT],
    response: JsonResponse,
    *,
    idempotency_key: str | None = None,
) -> ModelT:
    try:
        parsed = decode_model(model, response.data)
    except DecodeError as error:
        raise ResponseParseError(
            model=model.__name__,
            field=error.field,
            message=error.message,
            request_id=response.request_id,
        ) from error
    return parsed.with_response_metadata(
        request_id=response.request_id,
        idempotent_replayed=response.idempotent_replayed,
        idempotency_key=idempotency_key,
    )


def _parse_page(
    model: type[ModelT],
    response: JsonResponse,
) -> Page[ModelT]:
    try:
        parsed = decode_page(model, response.data)
    except DecodeError as error:
        raise ResponseParseError(
            model=f"Page[{model.__name__}]",
            field=error.field,
            message=error.message,
            request_id=response.request_id,
        ) from error
    return parsed.with_response_metadata(request_id=response.request_id)


def _params(**values: Any) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


class AccountsResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def list(self) -> Page[Account]:
        response = self._transport.request_json(
            *_operation("listAccounts"), retry_safe=True
        )
        return _parse_page(Account, response)

    def retrieve(self, account_id: str) -> Account:
        response = self._transport.request_json(
            *_operation("retrieveAccount", id=account_id), retry_safe=True
        )
        return _parse(Account, response)

    def update(self, account_id: str, **params: Unpack[AccountUpdateParams]) -> Account:
        response = self._transport.request_json(
            *_operation("updateAccount", id=account_id),
            body=params,
            retry_safe=False,
        )
        return _parse(Account, response)


class ApiKeysResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def create(self, **params: Unpack[ApiKeyCreateParams]) -> ApiKey:
        response = self._transport.request_json(
            *_operation("createApiKey"), body=params, retry_safe=False
        )
        return _parse(ApiKey, response)

    def retrieve(self, api_key_id: str) -> ApiKey:
        response = self._transport.request_json(
            *_operation("retrieveApiKey", id=api_key_id), retry_safe=True
        )
        return _parse(ApiKey, response)

    def delete(self, api_key_id: str) -> None:
        self._transport.request_empty(
            *_operation("deleteApiKey", id=api_key_id), retry_safe=False
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        ending_before: str | None = None,
    ) -> Page[ApiKey]:
        response = self._transport.request_json(
            *_operation("listApiKeys"),
            params=_params(
                limit=limit,
                starting_after=starting_after,
                ending_before=ending_before,
            ),
            retry_safe=True,
        )
        return _parse_page(ApiKey, response)


class EventsResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def retrieve(self, event_id: str) -> Event:
        response = self._transport.request_json(
            *_operation("retrieveEvent", id=event_id), retry_safe=True
        )
        return _parse(Event, response)

    def list(
        self,
        *,
        types: Sequence[str] | None = None,
        limit: int | None = None,
        starting_after: str | None = None,
        ending_before: str | None = None,
    ) -> Page[Event]:
        response = self._transport.request_json(
            *_operation("listEvents"),
            params=_params(
                types=",".join(types) if types is not None else None,
                limit=limit,
                starting_after=starting_after,
                ending_before=ending_before,
            ),
            retry_safe=True,
        )
        return _parse_page(Event, response)

    def iter(
        self,
        *,
        types: Sequence[str] | None = None,
        page_size: int = 100,
    ) -> Iterator[Event]:
        starting_after: str | None = None
        while True:
            page = self.list(
                types=types,
                limit=page_size,
                starting_after=starting_after,
            )
            yield from page.data
            if not page.has_more or not page.data:
                return
            starting_after = page.data[-1].id


class TaxRegimesResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def list(self) -> Page[TaxRegime]:
        response = self._transport.request_json(
            *_operation("listTaxRegimes"), retry_safe=True
        )
        return _parse_page(TaxRegime, response)

    def retrieve(self, regime_id: str) -> TaxRegime:
        response = self._transport.request_json(
            *_operation("retrieveTaxRegime", id=regime_id), retry_safe=True
        )
        return _parse(TaxRegime, response)


class TaxIdsResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def retrieve(self, tax_id: str) -> TaxId:
        response = self._transport.request_json(
            *_operation("retrieveTaxId", id=tax_id), retry_safe=True
        )
        return _parse(TaxId, response)


class CustomersResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def create(self, **params: Unpack[CustomerCreateParams]) -> Customer:
        response = self._transport.request_json(
            *_operation("createCustomer"), body=params, retry_safe=False
        )
        return _parse(Customer, response)

    def retrieve(self, customer_id: str) -> Customer:
        response = self._transport.request_json(
            *_operation("retrieveCustomer", id=customer_id), retry_safe=True
        )
        return _parse(Customer, response)

    def update(
        self, customer_id: str, **params: Unpack[CustomerUpdateParams]
    ) -> Customer:
        response = self._transport.request_json(
            *_operation("updateCustomer", id=customer_id),
            body=params,
            retry_safe=False,
        )
        return _parse(Customer, response)

    def delete(self, customer_id: str) -> None:
        self._transport.request_empty(
            *_operation("deleteCustomer", id=customer_id), retry_safe=False
        )

    def list(
        self,
        *,
        q: str | None = None,
        country: str | None = None,
        limit: int | None = None,
        starting_after: str | None = None,
        ending_before: str | None = None,
    ) -> Page[Customer]:
        response = self._transport.request_json(
            *_operation("listCustomers"),
            params=_params(
                q=q,
                country=country,
                limit=limit,
                starting_after=starting_after,
                ending_before=ending_before,
            ),
            retry_safe=True,
        )
        return _parse_page(Customer, response)

    def iter(
        self,
        *,
        q: str | None = None,
        country: str | None = None,
        page_size: int = 100,
    ) -> Iterator[Customer]:
        starting_after: str | None = None
        while True:
            page = self.list(
                q=q,
                country=country,
                limit=page_size,
                starting_after=starting_after,
            )
            yield from page.data
            if not page.has_more or not page.data:
                return
            starting_after = page.data[-1].id


class EventDestinationsResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def create(
        self, **params: Unpack[EventDestinationCreateParams]
    ) -> EventDestination:
        response = self._transport.request_json(
            *_operation("createEventDestination"), body=params, retry_safe=False
        )
        return _parse(EventDestination, response)

    def retrieve(self, destination_id: str) -> EventDestination:
        response = self._transport.request_json(
            *_operation("retrieveEventDestination", id=destination_id),
            retry_safe=True,
        )
        return _parse(EventDestination, response)

    def update(
        self,
        destination_id: str,
        **params: Unpack[EventDestinationUpdateParams],
    ) -> EventDestination:
        response = self._transport.request_json(
            *_operation("updateEventDestination", id=destination_id),
            body=params,
            retry_safe=False,
        )
        return _parse(EventDestination, response)

    def delete(self, destination_id: str) -> None:
        self._transport.request_empty(
            *_operation("deleteEventDestination", id=destination_id),
            retry_safe=False,
        )

    def enable(self, destination_id: str) -> EventDestination:
        response = self._transport.request_json(
            *_operation("enableEventDestination", id=destination_id),
            retry_safe=True,
        )
        return _parse(EventDestination, response)

    def disable(self, destination_id: str) -> EventDestination:
        response = self._transport.request_json(
            *_operation("disableEventDestination", id=destination_id),
            retry_safe=True,
        )
        return _parse(EventDestination, response)

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        ending_before: str | None = None,
    ) -> Page[EventDestination]:
        response = self._transport.request_json(
            *_operation("listEventDestinations"),
            params=_params(
                limit=limit,
                starting_after=starting_after,
                ending_before=ending_before,
            ),
            retry_safe=True,
        )
        return _parse_page(EventDestination, response)


class InvoiceSeriesResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def create(self, **params: Unpack[InvoiceSeriesCreateParams]) -> InvoiceSeries:
        response = self._transport.request_json(
            *_operation("createInvoiceSeries"), body=params, retry_safe=False
        )
        return _parse(InvoiceSeries, response)

    def retrieve(self, series_id: str) -> InvoiceSeries:
        response = self._transport.request_json(
            *_operation("retrieveInvoiceSeries", id=series_id), retry_safe=True
        )
        return _parse(InvoiceSeries, response)

    def update(
        self, series_id: str, **params: Unpack[InvoiceSeriesUpdateParams]
    ) -> InvoiceSeries:
        response = self._transport.request_json(
            *_operation("updateInvoiceSeries", id=series_id),
            body=params,
            retry_safe=False,
        )
        return _parse(InvoiceSeries, response)

    def delete(self, series_id: str) -> None:
        self._transport.request_empty(
            *_operation("deleteInvoiceSeries", id=series_id), retry_safe=False
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        ending_before: str | None = None,
    ) -> Page[InvoiceSeries]:
        response = self._transport.request_json(
            *_operation("listInvoiceSeries"),
            params=_params(
                limit=limit,
                starting_after=starting_after,
                ending_before=ending_before,
            ),
            retry_safe=True,
        )
        return _parse_page(InvoiceSeries, response)


class InvoicesResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def issue(
        self,
        *,
        idempotency_key: str | None = None,
        **params: Unpack[InvoiceIssueParams],
    ) -> Invoice:
        request_key = idempotency_key or str(uuid4())
        response = self._transport.request_json(
            *_operation("issueInvoice"),
            body=params,
            retry_safe=True,
            idempotency_key=request_key,
        )
        return _parse(Invoice, response, idempotency_key=request_key)

    def retrieve(self, invoice_id: str) -> Invoice:
        response = self._transport.request_json(
            *_operation("retrieveInvoice", id=invoice_id), retry_safe=True
        )
        return _parse(Invoice, response)

    def amend(
        self,
        invoice_id: str,
        *,
        reason: InvoiceAmendmentReason,
        replacement: InvoiceIssueParams | None = None,
        idempotency_key: str | None = None,
    ) -> InvoiceAmendment:
        request_key = idempotency_key or str(uuid4())
        body: dict[str, Any] = {"reason": reason}
        if replacement is not None:
            body["replacement"] = replacement
        response = self._transport.request_json(
            *_operation("amendInvoice", invoice_id=invoice_id),
            body=body,
            retry_safe=True,
            idempotency_key=request_key,
        )
        return _parse(InvoiceAmendment, response, idempotency_key=request_key)

    def list(
        self,
        *,
        q: str | None = None,
        customer: str | None = None,
        issue_date_from: date | str | None = None,
        issue_date_to: date | str | None = None,
        limit: int | None = None,
        starting_after: str | None = None,
        ending_before: str | None = None,
    ) -> Page[Invoice]:
        response = self._transport.request_json(
            *_operation("listInvoices"),
            params=_params(
                q=q,
                customer=customer,
                issue_date_from=issue_date_from,
                issue_date_to=issue_date_to,
                limit=limit,
                starting_after=starting_after,
                ending_before=ending_before,
            ),
            retry_safe=True,
        )
        return _parse_page(Invoice, response)

    def iter(
        self,
        *,
        q: str | None = None,
        customer: str | None = None,
        issue_date_from: date | str | None = None,
        issue_date_to: date | str | None = None,
        page_size: int = 100,
    ) -> Iterator[Invoice]:
        starting_after: str | None = None
        while True:
            page = self.list(
                q=q,
                customer=customer,
                issue_date_from=issue_date_from,
                issue_date_to=issue_date_to,
                limit=page_size,
                starting_after=starting_after,
            )
            yield from page.data
            if not page.has_more or not page.data:
                return
            starting_after = page.data[-1].id


class InvoicePdfsResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def retrieve(self, invoice_id: str) -> InvoicePdf:
        response = self._transport.request_json(
            *_operation("retrieveInvoicePdf", invoice_id=invoice_id), retry_safe=True
        )
        return _parse(InvoicePdf, response)

    def retrieve_content(self, invoice_id: str) -> BinaryContent:
        return self._transport.request_bytes(
            *_operation("retrieveInvoicePdf", invoice_id=invoice_id), retry_safe=True
        )

    def render(
        self, invoice_id: str, *, locale: InvoiceLocale | None = None
    ) -> InvoicePdf:
        headers = {"Accept-Language": locale} if locale else None
        response = self._transport.request_json(
            *_operation("renderInvoicePdf", invoice_id=invoice_id),
            headers=headers,
            retry_safe=True,
        )
        return _parse(InvoicePdf, response)

    def render_content(
        self, invoice_id: str, *, locale: InvoiceLocale | None = None
    ) -> BinaryContent:
        headers = {"Accept-Language": locale} if locale else None
        return self._transport.request_bytes(
            *_operation("renderInvoicePdf", invoice_id=invoice_id),
            headers=headers,
            retry_safe=True,
        )
