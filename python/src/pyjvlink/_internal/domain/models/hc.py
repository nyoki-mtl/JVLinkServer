"""HC domain model."""

from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True, slots=True)
class HCRecord:
    """Slope training record (坂路調教)."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    training_center_code: str | None
    training_date: date | None
    training_time: time | None
    pedigree_reg_num: str | None
    total_time_4f: str | None
    lap_time_800_600: str | None
    total_time_3f: str | None
    lap_time_600_400: str | None
    total_time_2f: str | None
    lap_time_400_200: str | None
    lap_time_200_0: str | None
