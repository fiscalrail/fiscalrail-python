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
- `client.api_keys`
- `client.customers`
- `client.event_destinations`
- `client.events`
- `client.invoice_series`
- `client.invoices`
- `client.invoice_pdfs`
- `client.tax_ids`
- `client.tax_regimes`

Invoices use the domain verbs `issue` and `amend`; they are never updated.
Customer and series resources expose ordinary create, retrieve, update, list
and delete operations.

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
