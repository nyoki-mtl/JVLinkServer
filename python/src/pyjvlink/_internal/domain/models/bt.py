"""BT domain model."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class BTRecord:
    """Lineage/pedigree information record."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    breeding_reg_num: str | None
    lineage_id: str | None
    lineage_name: str | None
    lineage_description: str | None
