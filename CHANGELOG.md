# Changelog

All notable changes to the FiscalRail Python SDK are documented here.

## 0.1.0 — 2026-08-16

- Add a typed, pooled `requests` client for the complete FiscalRail API.
- Generate immutable response dataclasses, request `TypedDict`s, enums, and the
  operation registry from FiscalRail's published OpenAPI contract.
- Add automatic safe retries and idempotency support for invoice issuance and
  amendments.
- Add webhook signature verification with timestamp tolerance.
- Add country-specific Spanish IVA and IRPF helpers.
