"""RC domain model."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class RCRecordHoldersItem:
    """Record-holding horse information."""

    pedigree_reg_num: str | None
    horse_name: str | None
    horse_symbol_code: str | None
    sex_code: str | None
    trainer_code: str | None
    trainer_name: str | None
    impost_weight: float | None
    jockey_code: str | None
    jockey_name: str | None


@dataclass(frozen=True, slots=True)
class RCRecord:
    """Record (course/GI record) master record."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    record_identification_code: str | None
    meet_year: int | None
    meet_month: int | None
    meet_day_of_month: int | None
    racecourse_code: str | None
    meet_round: int | None
    meet_day: int | None
    race_number: int | None
    special_race_number: int | None
    race_name_main: str | None
    grade_code: str | None
    race_type_code: str | None
    distance: int | None
    track_code: str | None
    record_type_code: str | None
    record_time: str | None
    weather_code: str | None
    turf_track_condition_code: str | None
    dirt_track_condition_code: str | None
    record_holders: tuple[RCRecordHoldersItem, ...]
