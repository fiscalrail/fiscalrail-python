from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

import requests
from conftest import customer_payload, json_response, make_client, request_json


def test_create_customer_uses_typed_keyword_payload() -> None:
    def handler(request: requests.PreparedRequest) -> requests.Response:
        assert request.method == "POST"
        assert urlsplit(request.url).path == "/v1/customers"
        assert request_json(request) == {
            "name": "Acme SL",
            "tax_id": {"country": "ES", "type": "es_nif", "value": "B87654323"},
            "email": "billing@example.com",
        }
        return json_response(customer_payload(), status_code=201)

    customer = make_client(handler).customers.create(
        name="Acme SL",
        tax_id={"country": "ES", "type": "es_nif", "value": "B87654323"},
        email="billing@example.com",
    )
    assert customer.id == "cus_123"
    assert customer.live is False


def test_iter_follows_starting_after_cursor() -> None:
    request_count = 0

    def handler(request: requests.PreparedRequest) -> requests.Response:
        nonlocal request_count
        request_count += 1
        payload = customer_payload()
        payload["id"] = f"cus_{request_count}"
        query = parse_qs(urlsplit(request.url).query)
        if request_count == 1:
            assert "starting_after" not in query
            return json_response(
                {"object": "list", "has_more": True, "data": [payload]}
            )
        assert query["starting_after"] == ["cus_1"]
        return json_response({"object": "list", "has_more": False, "data": [payload]})

    customers = list(make_client(handler).customers.iter(page_size=1))
    assert [customer.id for customer in customers] == ["cus_1", "cus_2"]
