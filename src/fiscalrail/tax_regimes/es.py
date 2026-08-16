from typing import Final

from fiscalrail.params import TaxReference


class _Vat:
    exempt_intra_eu_goods: Final = TaxReference("vat", "exempt_intra_eu_goods")
    general: Final = TaxReference("vat", "general")
    not_subject_place_of_supply: Final = TaxReference(
        "vat", "not_subject_place_of_supply"
    )
    reduced: Final = TaxReference("vat", "reduced")
    super_reduced: Final = TaxReference("vat", "super_reduced")


class _Irpf:
    new_professionals: Final = TaxReference("irpf", "new_professionals")
    professionals: Final = TaxReference("irpf", "professionals")


vat: Final = _Vat()
irpf: Final = _Irpf()
