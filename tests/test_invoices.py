from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

import requests
from conftest import invoice_payload, json_response, make_client, request_json

from fiscalrail.tax_regimes.es import irpf, vat


def test_issue_serializes_python_values_and_country_helpers() -> None:
    captured_key: str | None = None

    def handler(request: requests.PreparedRequest) -> requests.Response:
        nonlocal captured_key
        captured_key = request.headers["Idempotency-Key"]
        body = request_json(request)
        assert body == {
            "customer": "cus_123",
            "issue_date": "2026-08-16",
            "lines": [
                {
                    "description": "Consulting services",
                    "unit_price": "2500.00",
                    "taxes": [
                        {"tax": "vat", "rule": "general"},
                        {"tax": "irpf", "rule": "professionals"},
                    ],
                }
            ],
        }
        return json_response(
            invoice_payload(),
            status_code=201,
            headers={"Request-Id": "req_123"},
        )

    invoice = make_client(handler).invoices.issue(
        customer="cus_123",
        issue_date=date(2026, 8, 16),
        lines=[
            {
                "description": "Consulting services",
                "unit_price": Decimal("2500.00"),
                "taxes": [vat.general, irpf.professionals],
            }
        ],
    )

    assert captured_key is not None
    UUID(captured_key)
    assert invoice.idempotency_key == captured_key
    assert invoice.request_id == "req_123"
    assert invoice.issue_date == date(2026, 8, 16)
    assert invoice.totals.payable == Decimal("2650.00")
    assert invoice.payment_terms.due_date == date(2026, 9, 15)
    assert invoice.payment_terms.options[0].bank_transfer.iban == (
        "ES9121000418450200051332"
    )
    assert invoice.to_dict(mode="json")["totals"]["payable"] == "2650.00"


def test_issue_preserves_explicit_idempotency_key_and_replay_metadata() -> None:
    def handler(request: requests.PreparedRequest) -> requests.Response:
        assert request.headers["Idempotency-Key"] == "operation-123"
        return json_response(
            invoice_payload(),
            status_code=201,
            headers={
                "Request-Id": "req_replay",
                "Idempotent-Replayed": "req_original",
            },
        )

    invoice = make_client(handler).invoices.issue(
        idempotency_key="operation-123",
        lines=[
            {
                "description": "Consulting",
                "unit_price": "100.00",
                "taxes": [vat.general],
            }
        ],
    )
    assert invoice.idempotency_key == "operation-123"
    assert invoice.idempotent_replayed == "req_original"
