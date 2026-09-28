# FiscalRail Python SDK

Typed Python client for issuing immutable invoices through FiscalRail.

[Documentation](https://docs.fiscalrail.com/en/docs/python-sdk) ·
[Changelog](https://github.com/fiscalrail/fiscalrail-python/blob/main/CHANGELOG.md)

```bash
python -m pip install fiscalrail
```

Pass a Test or Live secret explicitly when creating the client.

## Issue an invoice

```python
import os
from decimal import Decimal

from fiscalrail import FiscalRail
from fiscalrail.tax_regimes.es import irpf, vat

client = FiscalRail(os.environ["FISCALRAIL_API_KEY"])

invoice = client.invoices.issue(
    customer="cus_...",
    lines=[
        {
            "description": "Consulting services",
            "unit_price": Decimal("2500.00"),
            "taxes": [vat.general, irpf.professionals],
        }
    ],
)

pdf = client.invoice_pdfs.render_content(invoice.id, locale="en")
pdf.write_to_file(f"{invoice.code}.pdf")
```

The API key is required. Your application may read it from an environment
variable or secret manager, but the SDK never reads process configuration on
its own. The key selects the Test or Live account; the SDK has no separate
environment switch.

The client owns a pooled `requests.Session` by default. Applications that need
custom proxy, TLS, adapter or observability configuration can inject one:

```python
import os

import requests

from fiscalrail import FiscalRail

session = requests.Session()
client = FiscalRail(os.environ["FISCALRAIL_API_KEY"], session=session)
```

Injected sessions remain owned by the caller and are not closed by the SDK.

Invoice issuance automatically uses an idempotency key. Durable workflows can
provide and persist their own:

```python
invoice = client.invoices.issue(
    idempotency_key="a49b50f6-1571-4e06-a243-e258bda98e40",
    customer="cus_...",
    lines=[
        {
            "description": "Consulting services",
            "unit_price": "2500.00",
            "taxes": [vat.general],
        }
    ],
)
```

## Payment instructions

Create reusable payment instructions, optionally make them account defaults,
and set an invoice due date without sending bank details on every issuance:

```python
from datetime import date

instruction = client.payment_instructions.create(
    label="Main EUR account",
    type="bank_transfer",
    bank_transfer={
        "beneficiary": "Example supplier",
        "iban": "ES91 2100 0418 4502 0005 1332",
        "bic": "CAIXESBBXXX",
    },
)

client.account_invoicing.update(
    default_payment_instructions=[instruction.id],
)

invoice = client.invoices.issue(
    payment_terms={"due_date": date(2026, 9, 30)},
    lines=[
        {
            "description": "Consulting services",
            "unit_price": "2500.00",
            "taxes": [vat.general],
        }
    ],
)
```

Pass `payment_terms={"options": [instruction.id]}` to override the account
defaults for a specific invoice. Pass an empty `options` list to render no
payment instructions.

## Typed request values

Calls are type checked directly. Exported `TypedDict` definitions also make
larger payloads reusable without introducing runtime parameter wrappers:

```python
from fiscalrail.params import InvoiceIssueParams

params = InvoiceIssueParams(
    customer="cus_...",
    lines=[
        {
            "description": "Consulting services",
            "unit_price": Decimal("2500.00"),
            "taxes": [vat.general, irpf.professionals],
        }
    ],
)

invoice = client.invoices.issue(**params)
```

Responses are dependency-free frozen dataclasses. Dates, timestamps and monetary
amounts are parsed into `date`, `datetime` and `Decimal` values. Unknown response
fields are retained in `response.extra_fields` for forward compatibility and
remain available through attribute access.

The response dataclasses, request `TypedDict`s, enums and operation registry are
generated from FiscalRail's OpenAPI contract. The public client and resource
methods remain hand-written so they can expose domain verbs, pooling,
idempotency and retry behavior instead of generator-shaped HTTP calls.

## Resources

- `client.accounts`
- `client.account_invoicing`
- `client.account_tax_regimes`
- `client.api_keys`
- `client.balances`
- `client.customers`
- `client.event_destinations`
- `client.events`
- `client.invoice_series`
- `client.invoices`
- `client.invoice_pdfs`
- `client.payment_instructions`
- `client.tax_ids`
- `client.tax_regimes`

Invoices use the domain verbs `issue` and `amend`; they are never updated.
The current account and its invoicing settings each expose retrieve and update. Customer and
series and payment-instruction resources expose ordinary create, retrieve,
update, list and delete operations.

## Account balance and tax-regime state

```python
balance = client.balances.retrieve()
print(balance.amount)  # Decimal, including zero or negative balances

regime = client.account_tax_regimes.retrieve()
if regime.key == "es" and regime.es.representation is not None:
    print(regime.es.representation.status)
```

Balances exist only for Live accounts; retrieving a Test account's balance
raises `ResourceNotFoundError`. The amount is informational: paid operations
can still fail with `BalanceExhaustedError` if the balance changes.

Account tax regimes return a `GlobalAccountTaxRegime` or
`SpanishAccountTaxRegime`. Spanish Test accounts have `es.representation=None`;
unverified Live representation timestamps can also be `None`. Both resources
retain `request_id`, preserve unknown fields, and use the client's safe-read
retry behavior. `client.tax_regimes` continues to expose the general tax
catalog; `client.account_tax_regimes` exposes account-specific state.

## Verify webhooks

Verify the exact request body before parsing or processing it:

```python
from fiscalrail.webhooks import construct_event

event = construct_event(raw_body, signature_header, signing_secret)
```

`construct_event` checks the HMAC in constant time, applies a five-minute
timestamp tolerance, and raises `WebhookSignatureError` when verification
fails.

## Development

```bash
uv sync --all-groups
uv run python scripts/generate_contract.py
uv run python scripts/generate_contract.py --check
uv run pytest
uv run ty check
uv run ruff check .
uv build
```

Release maintainers should follow the
[release guide](https://github.com/fiscalrail/fiscalrail-python/blob/main/RELEASING.md).
