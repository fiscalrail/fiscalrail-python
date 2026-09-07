from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
import requests
from conftest import json_response, make_client, make_session

from fiscalrail import FiscalRail
from fiscalrail.errors import ResourceNotFoundError, ResponseParseError
from fiscalrail.models import (
    Balance,
    GlobalAccountTaxRegime,
    SpanishAccountRepresentationStatus,
    SpanishAccountTaxRegime,
)


def balance_payload(amount: str = "12.34") -> dict[str, Any]:
    return {
        "id": "bal_123",
        "object": "balance",
        "live": True,
        "account": "acct_123",
        "amount": amount,
        "currency": "EUR",
        "updated_at": "2026-09-07T10:00:00Z",
    }


def spanish_regime_payload() -> dict[str, Any]:
    return {
        "object": "account_tax_regime",
        "account": "acct_123",
        "key": "es",
        "es": {
            "representation": {
                "kind": "aeat_registered_power",
                "power_code": "IZ860",
                "status": "verified",
                "verified_at": "2026-09-07T10:00:00Z",
                "last_checked_at": "2026-09-07T10:00:00Z",
            }
        },
    }


@pytest.mark.parametrize("amount", ["12.34", "0.00", "-0.01", "999999999999.99"])
def test_balance_retrieval_decodes_money_and_response_metadata(amount: str) -> None:
    def handler(request: requests.PreparedRequest) -> requests.Response:
        assert request.method == "GET"
        assert request.url == "https://api.fiscalrail.test/v1/accounts/acct_123/balance"
        assert request.body is None
        return json_response(
            {**balance_payload(amount), "future_field": "retained"},
            headers={"Request-Id": "req_balance"},
        )

    balance = make_client(handler).balances.retrieve("acct_123")

    assert isinstance(balance, Balance)
    assert balance.amount == Decimal(amount)
    assert balance.currency == "EUR"
    assert balance.updated_at == datetime(2026, 9, 7, 10, tzinfo=UTC)
    assert balance.request_id == "req_balance"
    assert balance.extra_fields == {"future_field": "retained"}
    assert balance.to_dict(mode="json")["amount"] == amount
    with pytest.raises(FrozenInstanceError):
        balance.amount = Decimal("999")  # type: ignore[misc]


def test_spanish_account_regime_decodes_representation_and_metadata() -> None:
    def handler(request: requests.PreparedRequest) -> requests.Response:
        assert request.method == "GET"
        assert request.url == (
            "https://api.fiscalrail.test/v1/accounts/acct_123/tax-regime"
        )
        assert request.body is None
        return json_response(
            spanish_regime_payload(), headers={"Request-Id": "req_regime"}
        )

    regime = make_client(handler).account_tax_regimes.retrieve("acct_123")

    assert isinstance(regime, SpanishAccountTaxRegime)
    assert regime.request_id == "req_regime"
    representation = regime.es.representation
    assert representation is not None
    assert representation.status is SpanishAccountRepresentationStatus.verified
    assert representation.verified_at == datetime(2026, 9, 7, 10, tzinfo=UTC)
    assert representation.last_checked_at == representation.verified_at
    serialized = regime.to_dict(mode="json")
    assert serialized["es"]["representation"]["status"] == "verified"
    assert serialized["es"]["representation"]["verified_at"] == (
        "2026-09-07T10:00:00+00:00"
    )


def test_spanish_test_account_has_no_representation() -> None:
    payload = spanish_regime_payload()
    payload["es"]["representation"] = None
    regime = make_client(
        lambda request: json_response(payload)
    ).account_tax_regimes.retrieve("acct_test")

    assert isinstance(regime, SpanishAccountTaxRegime)
    assert regime.es.representation is None


def test_unverified_representation_has_nullable_timestamps() -> None:
    payload = spanish_regime_payload()
    payload["es"]["representation"].update(
        status="not_started", verified_at=None, last_checked_at=None
    )
    regime = make_client(
        lambda request: json_response(payload)
    ).account_tax_regimes.retrieve("acct_123")

    assert isinstance(regime, SpanishAccountTaxRegime)
    assert regime.es.representation is not None
    assert regime.es.representation.verified_at is None
    assert regime.es.representation.last_checked_at is None


def test_global_account_regime_preserves_unknown_fields_and_metadata() -> None:
    payload = {
        "object": "account_tax_regime",
        "account": "acct_123",
        "key": "global",
        "future_field": True,
    }
    regime = make_client(
        lambda request: json_response(payload, headers={"Request-Id": "req_global"})
    ).account_tax_regimes.retrieve("acct_123")

    assert isinstance(regime, GlobalAccountTaxRegime)
    assert regime.request_id == "req_global"
    assert regime.extra_fields == {"future_field": True}
    assert regime.to_dict(mode="json") == payload
    with pytest.raises(FrozenInstanceError):
        regime.account = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ([], "$"),
        ({"object": "account_tax_regime", "account": "acct_123"}, "$.key"),
        (
            {"object": "account_tax_regime", "account": "acct_123", "key": "unknown"},
            "$.key",
        ),
        (
            {"object": "account_tax_regime", "account": "acct_123", "key": "es"},
            "$.es",
        ),
        (
            {
                "object": "account_tax_regime",
                "account": "acct_123",
                "key": "es",
                "es": {},
            },
            "$.es.representation",
        ),
    ],
)
def test_invalid_account_regimes_raise_parse_errors_with_request_id(
    payload: Any, field: str
) -> None:
    client = make_client(
        lambda request: json_response(payload, headers={"Request-Id": "req_invalid"})
    )
    with pytest.raises(ResponseParseError) as caught:
        client.account_tax_regimes.retrieve("acct_123")

    assert caught.value.field == field
    assert caught.value.request_id == "req_invalid"


def test_invalid_balance_reports_the_amount_field() -> None:
    payload = balance_payload()
    payload["amount"] = True
    client = make_client(lambda request: json_response(payload))
    with pytest.raises(ResponseParseError) as caught:
        client.balances.retrieve("acct_123")
    assert caught.value.field == "$.amount"


@pytest.mark.parametrize("resource", ["balances", "account_tax_regimes"])
def test_account_resources_propagate_not_found(resource: str) -> None:
    client = make_client(
        lambda request: json_response(
            {"error": {"code": "resource_not_found", "message": "Not found"}},
            status_code=404,
            headers={"Request-Id": "req_missing"},
        )
    )
    with pytest.raises(ResourceNotFoundError) as caught:
        getattr(client, resource).retrieve("acct_test")
    assert caught.value.request_id == "req_missing"


@pytest.mark.parametrize(
    ("resource", "payload"),
    [
        ("balances", balance_payload()),
        ("account_tax_regimes", spanish_regime_payload()),
    ],
)
def test_account_reads_use_safe_retries(resource: str, payload: dict[str, Any]) -> None:
    calls: list[requests.PreparedRequest] = []

    def handler(request: requests.PreparedRequest) -> requests.Response:
        calls.append(request)
        if len(calls) == 1:
            return json_response({}, status_code=503, headers={"Retry-After": "0"})
        return json_response(payload)

    with FiscalRail(
        "ak_test_example", max_retries=1, session=make_session(handler)
    ) as sdk:
        getattr(sdk, resource).retrieve("acct_123")

    assert len(calls) == 2
    assert calls[0].url == calls[1].url
    assert all(request.method == "GET" for request in calls)
