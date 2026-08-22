from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from urllib.parse import parse_qs, urlsplit

import requests
from conftest import json_response, make_client, request_json


def payment_instruction_payload(*, label: str = "Main EUR account") -> dict[str, Any]:
    return {
        "id": "pay_ins_123",
        "object": "payment_instruction",
        "live": False,
        "account": "acct_123",
        "label": label,
        "type": "bank_transfer",
        "bank_transfer": {
            "beneficiary": "Example supplier",
            "iban": "ES9121000418450200051332",
            "bic": "CAIXESBBXXX",
        },
        "created_at": "2026-08-22T10:00:00Z",
        "updated_at": "2026-08-22T10:00:00Z",
    }


def responses(*payloads: dict[str, Any]) -> Iterator[requests.Response]:
    for payload in payloads:
        yield json_response(payload)


def test_payment_instructions_cover_crud_and_list() -> None:
    calls: list[requests.PreparedRequest] = []
    queued = responses(
        payment_instruction_payload(),
        payment_instruction_payload(),
        payment_instruction_payload(label="Updated account"),
        {
            "object": "list",
            "has_more": False,
            "data": [payment_instruction_payload(label="Updated account")],
        },
    )

    def handler(request: requests.PreparedRequest) -> requests.Response:
        calls.append(request)
        if request.method == "DELETE":
            response = requests.Response()
            response.status_code = 204
            return response
        return next(queued)

    resource = make_client(handler).payment_instructions
    created = resource.create(
        label="Main EUR account",
        type="bank_transfer",
        bank_transfer={
            "beneficiary": "Example supplier",
            "iban": "ES91 2100 0418 4502 0005 1332",
            "bic": "CAIXESBBXXX",
        },
    )
    retrieved = resource.retrieve(created.id)
    updated = resource.update(created.id, label="Updated account")
    page = resource.list(limit=10)
    resource.delete(created.id)

    assert request_json(calls[0]) == {
        "label": "Main EUR account",
        "type": "bank_transfer",
        "bank_transfer": {
            "beneficiary": "Example supplier",
            "iban": "ES91 2100 0418 4502 0005 1332",
            "bic": "CAIXESBBXXX",
        },
    }
    assert retrieved.bank_transfer.iban == "ES9121000418450200051332"
    assert request_json(calls[2]) == {"label": "Updated account"}
    assert updated.label == "Updated account"
    assert parse_qs(urlsplit(calls[3].url).query) == {"limit": ["10"]}
    assert page.data[0].id == created.id
    assert calls[4].method == "DELETE"
