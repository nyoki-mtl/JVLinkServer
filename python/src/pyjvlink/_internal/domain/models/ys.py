"""YS domain model."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class YSGradedRaceGuideItem:
    """Graded race guide entry in schedule."""

    special_race_number: int | None
    race_name_main: str | None
    race_short_name_10: str | None
    race_short_name_6: str | None
    race_short_name_3: str | None
    graded_race_round_number: int | None
    grade_code: str | None
    race_type_code: str | None
    race_symbol_code: str | None
    weight_type_code: str | None
    distance: int | None
    track_code: str | None


@dataclass(frozen=True, slots=True)
class YSRecord:
    """Race schedule record (開催スケジュール)."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    meet_year: int | None
    meet_month: int | None
    meet_day_of_month: int | None
    racecourse_code: str | None
    meet_round: int | None
    meet_day: int | None
    weekday_code: str | None
    graded_race_guide: tuple[YSGradedRaceGuideItem, ...]
