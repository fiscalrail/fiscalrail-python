from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Any

import requests
from requests.adapters import BaseAdapter

from fiscalrail import FiscalRail

Handler = Callable[[requests.PreparedRequest], requests.Response]


class HandlerAdapter(BaseAdapter):
    def __init__(self, handler: Handler) -> None:
        self._handler = handler

    def send(
        self, request: requests.PreparedRequest, **kwargs: Any
    ) -> requests.Response:
        response = self._handler(request)
        response.request = request
        response.url = request.url
        response.connection = self
        return response

    def close(self) -> None:
        pass


def make_session(handler: Handler) -> requests.Session:
    session = requests.Session()
    session.mount("https://", HandlerAdapter(handler))
    return session


def make_client(handler: Handler) -> FiscalRail:
    return FiscalRail(
        api_key="ak_test_example",
        base_url="https://api.fiscalrail.test/v1",
        max_retries=0,
        session=make_session(handler),
    )


def json_response(
    payload: Any,
    *,
    status_code: int = 200,
    headers: Mapping[str, str] | None = None,
) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.headers.update({"Content-Type": "application/json", **(headers or {})})
    response.encoding = "utf-8"
    response._content = json.dumps(payload).encode("utf-8")
    return response


def binary_response(
    content: bytes,
    *,
    status_code: int = 200,
    headers: Mapping[str, str] | None = None,
) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.headers.update(headers or {})
    response._content = content
    return response


def request_json(request: requests.PreparedRequest) -> Any:
    body = request.body
    if not isinstance(body, str | bytes | bytearray):
        raise AssertionError(f"Expected a JSON request body, got {type(body).__name__}")
    return json.loads(body)


def address_payload() -> dict[str, Any]:
    return {
        "line_1": "Gran Via 1",
        "line_2": None,
        "city": "Madrid",
        "postal_code": "28013",
        "state": "Madrid",
        "country": "ES",
    }


def tax_id_payload(
    *, owner_type: str = "customer", owner_id: str = "cus_123"
) -> dict[str, Any]:
    return {
        "id": "tax_id_123",
        "object": "tax_id",
        "live": False,
        "country": "ES",
        "type": "es_nif",
        "value": "B87654323",
        "owner": {"type": owner_type, "id": owner_id},
        "verification": None,
    }


def customer_payload() -> dict[str, Any]:
    return {
        "id": "cus_123",
        "object": "customer",
        "live": False,
        "name": "Acme SL",
        "invoice_prefix": "ACMEXY",
        "tax_id": tax_id_payload(),
        "email": "billing@example.com",
        "phone": None,
        "address": address_payload(),
        "created_at": "2026-08-16T10:00:00Z",
        "updated_at": "2026-08-16T10:00:00Z",
    }


def invoice_payload() -> dict[str, Any]:
    snapshot_tax_id = {
        "country": "ES",
        "type": "es_nif",
        "value": "B87654323",
    }
    return {
        "id": "inv_123",
        "object": "invoice",
        "live": False,
        "account": "acct_123",
        "kind": "invoice",
        "code": "TEST-INV-00001",
        "series": "inv_ser_123",
        "issue_date": "2026-08-16",
        "supply_period": None,
        "preceding_invoice": None,
        "currency": "EUR",
        "supplier": {
            "source": {"type": "account", "id": "acct_123"},
            "name": "Example supplier",
            "tax_id": snapshot_tax_id,
            "email": None,
            "phone": None,
            "address": address_payload(),
        },
        "customer": {
            "source": {"type": "customer", "id": "cus_123"},
            "name": "Acme SL",
            "tax_id": snapshot_tax_id,
            "email": "billing@example.com",
            "phone": None,
            "address": address_payload(),
        },
        "lines": [
            {
                "index": 1,
                "description": "Consulting services",
                "quantity": "1.0",
                "unit_price": "2500.00",
                "subtotal": "2500.00",
                "taxes": [
                    {
                        "tax": "vat",
                        "rule": "general",
                        "effect": "added",
                        "treatment": "taxable",
                        "description": "IVA 21%",
                        "rate": "21%",
                        "taxable_base": "2500.00",
                    },
                    {
                        "tax": "irpf",
                        "rule": "professionals",
                        "effect": "withheld",
                        "treatment": "taxable",
                        "description": "Retencion IRPF 15%",
                        "rate": "15%",
                        "taxable_base": "2500.00",
                    },
                ],
            }
        ],
        "tax_totals": [
            {
                "tax": "vat",
                "rule": "general",
                "effect": "added",
                "treatment": "taxable",
                "description": "IVA 21%",
                "rate": "21%",
                "taxable_base": "2500.00",
                "amount": "525.00",
            },
            {
                "tax": "irpf",
                "rule": "professionals",
                "effect": "withheld",
                "treatment": "taxable",
                "description": "Retencion IRPF 15%",
                "rate": "15%",
                "taxable_base": "2500.00",
                "amount": "375.00",
            },
        ],
        "totals": {
            "subtotal": "2500.00",
            "tax": "525.00",
            "total_with_tax": "3025.00",
            "withheld_tax": "375.00",
            "payable": "2650.00",
        },
        "created_at": "2026-08-16T10:00:00Z",
        "tax_regime": {
            "key": "es",
            "es": {
                "qr": {
                    "content": "https://example.test/qr",
                    "image_url": "https://example.test/qr.svg",
                },
                "verifactu": {"registrations": []},
            },
        },
        "amendments": [],
    }
