"""SK domain model."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class SKRecord:
    """Offspring master record."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    pedigree_reg_num: str | None
    birth_date: date | None
    sex_code: str | None
    breed_code: str | None
    coat_color_code: str | None
    import_code: str | None
    import_year: int | None
    breeder_code: str | None
    birthplace_name: str | None
    three_gen_pedigree_breeding_reg_nums: tuple[str, ...]
