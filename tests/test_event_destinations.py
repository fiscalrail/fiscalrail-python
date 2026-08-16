from __future__ import annotations

from urllib.parse import urlsplit

import requests
from conftest import json_response, make_client, request_json


def event_destination_payload() -> dict[str, object]:
    return {
        "id": "evt_dst_123",
        "object": "event_destination",
        "live": False,
        "account": "acct_123",
        "name": "Invoice updates",
        "type": "webhook",
        "status": "enabled",
        "enabled_events": ["invoice.issued"],
        "webhook": {
            "url": "https://example.com/webhooks/fiscalrail",
            "signing_secret": "whsec_example",
        },
        "disabled_reason": None,
        "created_at": "2026-08-16T10:00:00Z",
        "updated_at": "2026-08-16T10:00:00Z",
    }


def test_create_event_destination_uses_generated_contract() -> None:
    def handler(request: requests.PreparedRequest) -> requests.Response:
        assert request.method == "POST"
        assert urlsplit(request.url).path == "/v1/event-destinations"
        assert request_json(request) == {
            "name": "Invoice updates",
            "url": "https://example.com/webhooks/fiscalrail",
            "enabled_events": ["invoice.issued"],
        }
        return json_response(event_destination_payload(), status_code=201)

    destination = make_client(handler).event_destinations.create(
        name="Invoice updates",
        url="https://example.com/webhooks/fiscalrail",
        enabled_events=["invoice.issued"],
    )

    assert destination.id == "evt_dst_123"
    assert destination.webhook.signing_secret == "whsec_example"
