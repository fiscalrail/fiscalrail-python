from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import requests
from conftest import json_response, make_client, request_json, tax_id_payload


def api_key_payload(*, secret: str | None = None) -> dict[str, Any]:
    return {
        "id": "key_123",
        "object": "api_key",
        "live": False,
        "account": "acct_123",
        "name": "Production server",
        "suffix": "abcd",
        "secret": secret,
        "created_at": "2026-08-16T10:00:00Z",
    }


def event_payload() -> dict[str, Any]:
    return {
        "id": "evt_123",
        "object": "event",
        "live": False,
        "account": "acct_123",
        "type": "customer.created",
        "occurred_at": "2026-08-16T10:00:00Z",
        "actor": {"type": "api_key", "id": "key_123", "request_id": "req_123"},
        "related_object": {"id": "cus_123", "object": "customer"},
        "data": {"object": {"id": "cus_123", "object": "customer"}},
    }


def tax_regime_payload() -> dict[str, Any]:
    return {
        "id": "es",
        "object": "tax_regime",
        "taxes": [
            {
                "tax": "vat",
                "name": "IVA",
                "effect": "added",
                "rules": [
                    {
                        "rule": "general",
                        "description": "IVA 21%",
                        "treatment": "taxable",
                        "rate": "21%",
                        "authority_code": None,
                        "legal_reference": "Ley 37/1992, articulo 90",
                        "effective_from": "2012-09-01",
                        "effective_until": None,
                    }
                ],
            }
        ],
    }


def responses(*payloads: dict[str, Any]) -> Iterator[requests.Response]:
    for payload in payloads:
        yield json_response(payload)


def test_api_keys_cover_create_list_retrieve_and_delete() -> None:
    calls: list[requests.PreparedRequest] = []
    queued = responses(
        api_key_payload(secret="ak_test_once"),
        {"object": "list", "has_more": False, "data": [api_key_payload()]},
        api_key_payload(),
    )

    def handler(request: requests.PreparedRequest) -> requests.Response:
        calls.append(request)
        if request.method == "DELETE":
            response = requests.Response()
            response.status_code = 204
            return response
        return next(queued)

    resource = make_client(handler).api_keys
    created = resource.create(name="Production server")
    page = resource.list(limit=10)
    retrieved = resource.retrieve("key_123")
    resource.delete("key_123")

    assert created.secret == "ak_test_once"
    assert request_json(calls[0]) == {"name": "Production server"}
    assert calls[1].url.endswith("/api-keys?limit=10")
    assert page.data[0].suffix == "abcd"
    assert retrieved.secret is None
    assert calls[3].method == "DELETE"


def test_events_cover_filtered_list_and_retrieve() -> None:
    queued = responses(
        {"object": "list", "has_more": False, "data": [event_payload()]},
        event_payload(),
    )
    calls: list[requests.PreparedRequest] = []

    def handler(request: requests.PreparedRequest) -> requests.Response:
        calls.append(request)
        return next(queued)

    resource = make_client(handler).events
    page = resource.list(types=["customer.created", "invoice.created"], limit=20)
    event = resource.retrieve("evt_123")

    assert "types=customer.created%2Cinvoice.created" in calls[0].url
    assert page.data[0].actor.request_id == "req_123"
    assert event.related_object is not None
    assert event.related_object.id == "cus_123"


def test_tax_regimes_cover_list_and_retrieve() -> None:
    queued = responses(
        {"object": "list", "has_more": False, "data": [tax_regime_payload()]},
        tax_regime_payload(),
    )
    resource = make_client(lambda request: next(queued)).tax_regimes

    page = resource.list()
    regime = resource.retrieve("es")

    assert page.data[0].id == "es"
    assert regime.taxes[0].rules[0].rate == "21%"


def test_tax_ids_retrieve() -> None:
    resource = make_client(
        lambda request: json_response(tax_id_payload())
    ).tax_ids

    tax_id = resource.retrieve("tax_id_123")

    assert tax_id.value == "B87654323"
