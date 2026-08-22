from __future__ import annotations

from types import TracebackType

import requests

from fiscalrail._resources import (
    AccountsResource,
    ApiKeysResource,
    CustomersResource,
    EventDestinationsResource,
    EventsResource,
    InvoicePdfsResource,
    InvoiceSeriesResource,
    InvoicesResource,
    PaymentInstructionsResource,
    TaxIdsResource,
    TaxRegimesResource,
)
from fiscalrail._transport import Transport


class FiscalRail:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.fiscalrail.com/v1",
        timeout: float = 30.0,
        max_retries: int = 2,
        session: requests.Session | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key cannot be empty")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        self._transport = Transport(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            session=session,
        )
        self.accounts = AccountsResource(self._transport)
        self.api_keys = ApiKeysResource(self._transport)
        self.customers = CustomersResource(self._transport)
        self.event_destinations = EventDestinationsResource(self._transport)
        self.events = EventsResource(self._transport)
        self.invoice_series = InvoiceSeriesResource(self._transport)
        self.invoices = InvoicesResource(self._transport)
        self.invoice_pdfs = InvoicePdfsResource(self._transport)
        self.payment_instructions = PaymentInstructionsResource(self._transport)
        self.tax_ids = TaxIdsResource(self._transport)
        self.tax_regimes = TaxRegimesResource(self._transport)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> FiscalRail:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
