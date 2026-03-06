"""HN domain model."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class HNRecord:
    """Breeding horse master record."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    breeding_reg_num: str | None
    pedigree_reg_num: str | None
    horse_name: str | None
    horse_name_kana: str | None
    horse_name_english: str | None
    birth_year: int | None
    sex_code: str | None
    breed_code: str | None
    coat_color_code: str | None
    import_code: str | None
    import_year: int | None
    birthplace_name: str | None
    sire_breeding_reg_num: str | None
    dam_breeding_reg_num: str | None
