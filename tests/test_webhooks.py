from __future__ import annotations

import hashlib
import hmac

import pytest

from fiscalrail import WebhookSignatureError
from fiscalrail.webhooks import construct_event, verify_signature

SECRET = "whsec_test_secret"
TIMESTAMP = 1_775_000_000
PAYLOAD = b'{"id":"evt_123","object":"event","type":"invoice.created"}'


def signature(payload: bytes = PAYLOAD, *, timestamp: int = TIMESTAMP) -> str:
    digest = hmac.new(
        SECRET.encode(),
        str(timestamp).encode() + b"." + payload,
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={digest}"


def test_construct_event_verifies_and_decodes_the_raw_body() -> None:
    event = construct_event(PAYLOAD, signature(), SECRET, now=TIMESTAMP)

    assert event["id"] == "evt_123"
    assert event["type"] == "invoice.created"


def test_accepts_any_matching_v1_signature_during_secret_rotation() -> None:
    header = f"{signature()},v1={'0' * 64}"

    assert verify_signature(PAYLOAD, header, SECRET, now=TIMESTAMP) == TIMESTAMP


def test_rejects_a_tampered_payload() -> None:
    with pytest.raises(WebhookSignatureError, match="No matching"):
        construct_event(PAYLOAD + b" ", signature(), SECRET, now=TIMESTAMP)


def test_rejects_a_stale_timestamp() -> None:
    with pytest.raises(WebhookSignatureError, match="tolerance"):
        verify_signature(PAYLOAD, signature(), SECRET, now=TIMESTAMP + 301)


@pytest.mark.parametrize("header", ["", "v1=abc", "t=nope,v1=abc"])
def test_rejects_malformed_headers(header: str) -> None:
    with pytest.raises(WebhookSignatureError, match="Malformed"):
        verify_signature(PAYLOAD, header, SECRET, now=TIMESTAMP)


def test_rejects_invalid_json_after_a_valid_signature() -> None:
    payload = b"not-json"
    with pytest.raises(WebhookSignatureError, match="valid JSON"):
        construct_event(payload, signature(payload), SECRET, now=TIMESTAMP)
