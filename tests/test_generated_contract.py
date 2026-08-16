from fiscalrail._generated.operations import OPERATIONS
from fiscalrail._resources import WRAPPED_OPERATION_IDS


def test_every_openapi_operation_is_accounted_for() -> None:
    assert WRAPPED_OPERATION_IDS == OPERATIONS.keys()


def test_customer_update_has_one_canonical_operation() -> None:
    assert OPERATIONS["updateCustomer"].method == "PATCH"
    assert "updateCustomerWithPut" not in OPERATIONS
