from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import requests

from fiscalrail._binary import BinaryContent
from fiscalrail._serialization import to_jsonable
from fiscalrail._version import __version__
from fiscalrail.errors import APIConnectionError, APITimeoutError, api_error


@dataclass(frozen=True, slots=True)
class JsonResponse:
    data: Any
    status_code: int
    request_id: str | None
    idempotent_replayed: str | None


class Transport:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float,
        max_retries: int,
        session: requests.Session | None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._owns_session = session is None
        self._session = session or requests.Session()

    def request_json(
        self,
        method: str,
        path: str,
        *,
        body: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        retry_safe: bool,
        idempotency_key: str | None = None,
    ) -> JsonResponse:
        response = self._request(
            method,
            path,
            body=body,
            params=params,
            headers=headers,
            retry_safe=retry_safe,
            idempotency_key=idempotency_key,
        )
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise APIConnectionError(
                "FiscalRail returned a non-JSON response",
                idempotency_key=idempotency_key,
            ) from exc
        return JsonResponse(
            data=data,
            status_code=response.status_code,
            request_id=response.headers.get("Request-Id"),
            idempotent_replayed=response.headers.get("Idempotent-Replayed"),
        )

    def request_bytes(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        retry_safe: bool,
    ) -> BinaryContent:
        response = self._request(
            method,
            path,
            headers={"Accept": "application/pdf", **(headers or {})},
            retry_safe=retry_safe,
        )
        return BinaryContent(
            content=response.content,
            content_type=response.headers.get("Content-Type"),
            request_id=response.headers.get("Request-Id"),
        )

    def request_empty(
        self,
        method: str,
        path: str,
        *,
        retry_safe: bool,
    ) -> None:
        self._request(method, path, retry_safe=retry_safe)

    def close(self) -> None:
        if self._owns_session:
            self._session.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        retry_safe: bool,
        idempotency_key: str | None = None,
    ) -> requests.Response:
        request_headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
            "User-Agent": f"fiscalrail-python/{__version__}",
            **(headers or {}),
        }
        if idempotency_key:
            request_headers["Idempotency-Key"] = idempotency_key

        request_kwargs: dict[str, Any] = {
            "headers": request_headers,
            "timeout": self._timeout,
        }
        if body is not None:
            request_kwargs["json"] = to_jsonable(body)
        if params:
            request_kwargs["params"] = to_jsonable(params)

        for attempt in range(self._max_retries + 1):
            try:
                response = self._session.request(
                    method,
                    f"{self._base_url}{path}",
                    **request_kwargs,
                )
            except requests.Timeout as exc:
                if retry_safe and attempt < self._max_retries:
                    self._wait(attempt)
                    continue
                raise APITimeoutError(
                    "Request to FiscalRail timed out",
                    idempotency_key=idempotency_key,
                ) from exc
            except requests.RequestException as exc:
                if retry_safe and attempt < self._max_retries:
                    self._wait(attempt)
                    continue
                raise APIConnectionError(
                    "Could not connect to FiscalRail",
                    idempotency_key=idempotency_key,
                ) from exc

            if response.status_code < 400:
                return response

            retryable_status = (
                response.status_code in {408, 429} or response.status_code >= 500
            )
            if retry_safe and retryable_status and attempt < self._max_retries:
                self._wait(attempt, response.headers.get("Retry-After"))
                continue

            try:
                payload: Any = response.json()
            except requests.exceptions.JSONDecodeError:
                payload = response.text
            raise api_error(
                status_code=response.status_code,
                request_id=response.headers.get("Request-Id"),
                payload=payload,
                idempotency_key=idempotency_key,
            )

        raise AssertionError("unreachable")

    @staticmethod
    def _wait(attempt: int, retry_after: str | None = None) -> None:
        if retry_after:
            try:
                time.sleep(min(float(retry_after), 30.0))
                return
            except ValueError:
                pass
        time.sleep(min(0.25 * (2**attempt), 30.0))
