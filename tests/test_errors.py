from __future__ import annotations

import pytest
import requests
from conftest import json_response, make_client

from fiscalrail import InvalidInvoiceError, ResponseParseError
from fiscalrail.tax_regimes.es import vat


def test_maps_structured_error_and_preserves_request_metadata() -> None:
    def handler(request: requests.PreparedRequest) -> requests.Response:
        return json_response(
            {
                "error": {
                    "code": "invalid_invoice",
                    "message": "The invoice is invalid",
                    "details": [
                        {
                            "code": "required_value",
                            "field": "customer.address",
                            "message": "is required",
                            "metadata": {},
                        }
                    ],
                }
            },
            status_code=422,
            headers={"Request-Id": "req_error"},
        )

    with pytest.raises(InvalidInvoiceError) as raised:
        make_client(handler).invoices.issue(
            idempotency_key="operation-123",
            lines=[
                {
                    "description": "Consulting",
                    "unit_price": "100.00",
                    "taxes": [vat.general],
                }
            ],
        )

    error = raised.value
    assert error.code == "invalid_invoice"
    assert error.request_id == "req_error"
    assert error.idempotency_key == "operation-123"
    assert error.details[0].field == "customer.address"


def test_reports_response_contract_failures() -> None:
    def handler(request: requests.PreparedRequest) -> requests.Response:
        return json_response(
            {"object": "list", "has_more": False, "data": [{"id": 123}]},
            headers={"Request-Id": "req_bad_response"},
        )

    with pytest.raises(ResponseParseError) as raised:
        make_client(handler).customers.list()

    error = raised.value
    assert error.model == "Page[Customer]"
    assert error.field == "$.data[0].id"
    assert error.request_id == "req_bad_response"
