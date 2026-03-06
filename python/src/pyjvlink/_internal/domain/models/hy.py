"""HY domain model."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class HYRecord:
    """Horse name meaning record (馬名の意味由来)."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    pedigree_reg_num: str | None
    horse_name: str | None
    horse_name_meaning: str | None
