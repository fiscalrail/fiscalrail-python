from __future__ import annotations

from urllib.parse import urlsplit

import requests
from conftest import binary_response, make_client


def test_render_content_is_explicit_and_returns_binary_content() -> None:
    def handler(request: requests.PreparedRequest) -> requests.Response:
        assert request.method == "POST"
        assert urlsplit(request.url).path == "/v1/invoices/inv_123/pdf"
        assert request.headers["Accept"] == "application/pdf"
        assert request.headers["Accept-Language"] == "en"
        return binary_response(
            b"%PDF-example",
            status_code=201,
            headers={"Content-Type": "application/pdf", "Request-Id": "req_pdf"},
        )

    content = make_client(handler).invoice_pdfs.render_content("inv_123", locale="en")
    assert bytes(content) == b"%PDF-example"
    assert content.content_type == "application/pdf"
    assert content.request_id == "req_pdf"
