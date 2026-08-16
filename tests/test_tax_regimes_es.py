from fiscalrail.params import TaxReference
from fiscalrail.tax_regimes.es import irpf, vat


def test_spanish_helpers_are_typed_tax_references() -> None:
    assert vat.general == TaxReference(tax="vat", rule="general")
    assert vat.reduced == TaxReference(tax="vat", rule="reduced")
    assert irpf.professionals == TaxReference(tax="irpf", rule="professionals")
