# Changelog

All notable changes to the FiscalRail Python SDK are documented here.

## 0.3.0 — 2026-08-22

- Add `client.payment_instructions` with create, retrieve, update, list, and
  delete operations for bank-transfer instructions.
- Add account default payment instructions and invoice payment terms to the
  generated request and response types.
- Decode rendered payment options, including their snapshotted bank details and
  invoice payment reference.
- Add `InvalidPaymentInstructionError` for payment-instruction validation
  failures.

## 0.2.0 — 2026-08-19

- Update the Account model for nested default series and account-wide invoice
  numbering scope.
- Add `client.accounts.update()` for changing Account invoicing settings.
- Add customer invoice prefixes to response and create/update parameter types.

## 0.1.0 — 2026-08-16

- Add a typed, pooled `requests` client for the complete FiscalRail API.
- Generate immutable response dataclasses, request `TypedDict`s, enums, and the
  operation registry from FiscalRail's published OpenAPI contract.
- Add automatic safe retries and idempotency support for invoice issuance and
  amendments.
- Add webhook signature verification with timestamp tolerance.
- Add country-specific Spanish IVA and IRPF helpers.
