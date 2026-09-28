from datetime import date
from decimal import Decimal

from fiscalrail import FiscalRail
from fiscalrail.models import (
    AccountTaxRegime,
    ApiKey,
    Balance,
    Customer,
    Event,
    Invoice,
    PaymentInstruction,
    TaxId,
    TaxRegime,
)
from fiscalrail.params import (
    AccountUpdateParams,
    CustomerCreateParams,
    InvoiceIssueParams,
    PaymentInstructionCreateParams,
)
from fiscalrail.tax_regimes.es import irpf, vat
from fiscalrail.webhooks import construct_event

client = FiscalRail(api_key="ak_test_example")

balance: Balance = client.balances.retrieve()
balance_amount: Decimal = balance.amount
account_regime: AccountTaxRegime = client.account_tax_regimes.retrieve()
if account_regime.key == "es" and account_regime.es.representation is not None:
    representation_status: str = account_regime.es.representation.status

payment_instruction_params = PaymentInstructionCreateParams(
    label="Main EUR account",
    type="bank_transfer",
    bank_transfer={
        "beneficiary": "Example supplier",
        "iban": "ES9121000418450200051332",
    },
)
payment_instruction: PaymentInstruction = client.payment_instructions.create(
    **payment_instruction_params
)

account_update = AccountUpdateParams(
    address={"line_1": "Updated street 1", "line_2": None},
    name="Example supplier",
)
client.accounts.update(**account_update)
client.account_invoicing.update(
    numbering_scope="customer",
    default_payment_instructions=[payment_instruction.id],
)

customer_params = CustomerCreateParams(
    name="Acme SL",
    tax_id={"country": "ES", "type": "es_nif", "value": "B87654323"},
)
customer: Customer = client.customers.create(**customer_params)

invoice_params = InvoiceIssueParams(
    customer=customer.id,
    issue_date=date.today(),
    payment_terms={
        "due_date": date.today(),
        "options": [payment_instruction.id],
    },
    lines=[
        {
            "description": "Consulting services",
            "unit_price": Decimal("2500.00"),
            "taxes": [vat.general, irpf.professionals],
        }
    ],
)
invoice: Invoice = client.invoices.issue(**invoice_params)
payable: Decimal = invoice.totals.payable

api_key: ApiKey = client.api_keys.create(name="Worker")
event: Event = client.events.retrieve("evt_example")
tax_id: TaxId = client.tax_ids.retrieve("tax_id_example")
tax_regime: TaxRegime = client.tax_regimes.retrieve("es")
webhook_event: dict[str, object] = construct_event(
    b'{"id":"evt_example"}',
    "t=1775000000,v1=signature",
    "whsec_example",
)
