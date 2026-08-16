from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Any

from fiscalrail.errors import WebhookSignatureError

DEFAULT_TOLERANCE = 300


def verify_signature(
    payload: bytes | str,
    signature: str,
    secret: str,
    *,
    tolerance: int | None = DEFAULT_TOLERANCE,
    now: int | float | datetime | None = None,
) -> int:
    """Verify a FiscalRail-Signature header and return its Unix timestamp."""
    payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload
    timestamp, signatures = _parse_header(signature)
    signed_payload = str(timestamp).encode("ascii") + b"." + payload_bytes
    expected = hmac.new(
        secret.encode("utf-8"), signed_payload, hashlib.sha256
    ).hexdigest()
    if not any(hmac.compare_digest(expected, candidate) for candidate in signatures):
        raise WebhookSignatureError("No matching FiscalRail webhook signature")

    if tolerance is not None:
        if tolerance < 0:
            raise ValueError("tolerance cannot be negative")
        current = _timestamp(now)
        if abs(current - timestamp) > tolerance:
            raise WebhookSignatureError(
                "FiscalRail webhook timestamp is outside the allowed tolerance"
            )

    return timestamp


def construct_event(
    payload: bytes | str,
    signature: str,
    secret: str,
    *,
    tolerance: int | None = DEFAULT_TOLERANCE,
    now: int | float | datetime | None = None,
) -> dict[str, Any]:
    """Verify and decode a FiscalRail webhook using the unmodified request body."""
    verify_signature(
        payload,
        signature,
        secret,
        tolerance=tolerance,
        now=now,
    )
    try:
        event = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise WebhookSignatureError(
            "FiscalRail webhook payload is not valid JSON"
        ) from error
    if not isinstance(event, dict):
        raise WebhookSignatureError("FiscalRail webhook payload must be a JSON object")
    return event


def _parse_header(value: str) -> tuple[int, list[str]]:
    fields: dict[str, list[str]] = {}
    for item in value.split(","):
        key, separator, field_value = item.strip().partition("=")
        if separator and key and field_value:
            fields.setdefault(key, []).append(field_value)

    timestamps = fields.get("t", [])
    signatures = fields.get("v1", [])
    if len(timestamps) != 1 or not signatures:
        raise WebhookSignatureError("Malformed FiscalRail-Signature header")
    try:
        timestamp = int(timestamps[0])
    except ValueError as error:
        raise WebhookSignatureError(
            "Malformed FiscalRail-Signature timestamp"
        ) from error
    return timestamp, signatures


def _timestamp(value: int | float | datetime | None) -> int:
    if value is None:
        return int(time.time())
    if isinstance(value, datetime):
        return int(value.timestamp())
    return int(value)
