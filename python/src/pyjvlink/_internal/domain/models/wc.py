"""WC domain model."""

from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True, slots=True)
class WCRecord:
    """Woodchip training record (ウッドチップ調教)."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    training_center_code: str | None
    training_date: date | None
    training_time: time | None
    pedigree_reg_num: str | None
    course: str | None
    track_direction: str | None
    total_time_10f: str | None
    lap_time_2000_1800: str | None
    total_time_9f: str | None
    lap_time_1800_1600: str | None
    total_time_8f: str | None
    lap_time_1600_1400: str | None
    total_time_7f: str | None
    lap_time_1400_1200: str | None
    total_time_6f: str | None
    lap_time_1200_1000: str | None
    total_time_5f: str | None
    lap_time_1000_800: str | None
    total_time_4f: str | None
    lap_time_800_600: str | None
    total_time_3f: str | None
    lap_time_600_400: str | None
    total_time_2f: str | None
    lap_time_400_200: str | None
    lap_time_200_0: str | None
