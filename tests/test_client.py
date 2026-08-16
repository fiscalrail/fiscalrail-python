from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Any

import pytest
import requests
from conftest import (
    HandlerAdapter,
    address_payload,
    json_response,
    make_client,
    make_session,
    tax_id_payload,
)

from fiscalrail import FiscalRail
from fiscalrail._transport import Transport


def account_payload() -> dict[str, Any]:
    return {
        "id": "acct_123",
        "object": "account",
        "live": False,
        "name": "Example supplier",
        "tax_id": tax_id_payload(owner_type="account", owner_id="acct_123"),
        "email": None,
        "phone": None,
        "address": address_payload(),
        "environment": "test",
        "tax_regime": "es",
        "timezone": "Europe/Madrid",
        "invoice_locale": "en",
        "default_invoice_series": "inv_ser_123",
        "default_credit_note_series": "inv_ser_456",
        "default_amendment_series": "inv_ser_789",
        "created_at": "2026-08-16T10:00:00Z",
        "updated_at": "2026-08-16T10:00:00Z",
    }


def test_accepts_an_explicit_api_key() -> None:
    with FiscalRail(
        "ak_test_explicit",
        session=make_session(
            lambda request: json_response(
                {"object": "list", "has_more": False, "data": []}
            )
        )
    ) as client:
        page = client.accounts.list()
    assert page.data == []


def test_rejects_an_empty_api_key() -> None:
    with pytest.raises(ValueError, match="api_key cannot be empty"):
        FiscalRail("")


def test_sends_authentication_and_parses_account() -> None:
    def handler(request: requests.PreparedRequest) -> requests.Response:
        assert request.headers["Authorization"] == "Bearer ak_test_example"
        assert request.headers["User-Agent"].startswith("fiscalrail-python/")
        return json_response(
            {"object": "list", "has_more": False, "data": [account_payload()]},
            headers={"Request-Id": "req_123"},
        )

    page = make_client(handler).accounts.list()
    assert page.request_id == "req_123"
    assert page.data[0].environment == "test"
    assert page.data[0].default_invoice_series == "inv_ser_123"


def test_response_models_are_frozen_and_preserve_unknown_fields() -> None:
    payload = account_payload()
    payload["future_field"] = {"enabled": True}

    page = make_client(
        lambda request: json_response(
            {"object": "list", "has_more": False, "data": [payload]}
        )
    ).accounts.list()
    account = page.data[0]

    assert account.extra_fields == {"future_field": {"enabled": True}}
    assert account.future_field == {"enabled": True}
    assert account.to_dict(mode="json")["future_field"] == {"enabled": True}
    with pytest.raises(FrozenInstanceError):
        account.name = "Changed"  # type: ignore[misc]


def test_injected_session_remains_caller_owned() -> None:
    class TrackingSession(requests.Session):
        closed = False

        def close(self) -> None:
            self.closed = True
            super().close()

    session = TrackingSession()
    session.mount(
        "https://",
        HandlerAdapter(
            lambda request: json_response(
                {"object": "list", "has_more": False, "data": []}
            )
        ),
    )

    client = FiscalRail(api_key="ak_test_example", session=session)
    client.accounts.list()
    client.close()

    assert session.closed is False
    session.close()


def test_retry_backoff_is_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    waits: list[float] = []
    monkeypatch.setattr("fiscalrail._transport.time.sleep", waits.append)

    Transport._wait(attempt=20)

    assert waits == [30.0]
