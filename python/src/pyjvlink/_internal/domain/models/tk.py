"""TK domain model."""

from dataclasses import dataclass
from datetime import date

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class TKEntryHorsesItem:
    """Registered horse entry."""

    serial_number: int | None
    pedigree_reg_num: str | None
    horse_name: str | None
    horse_symbol_code: str | None
    sex_code: str | None
    trainer_affiliation_code: str | None
    trainer_code: str | None
    trainer_short_name: str | None
    impost_weight: int | None
    exchange_code: str | None


@dataclass(frozen=True, slots=True)
class TKRecord(RaceRecordBase):
    """Special registration record."""

    weekday_code: str | None
    special_race_number: int | None
    race_name_main: str | None
    race_name_subtitle: str | None
    race_name_parentheses: str | None
    race_name_main_english: str | None
    race_name_subtitle_english: str | None
    race_name_parentheses_english: str | None
    race_short_name_10: str | None
    race_short_name_6: str | None
    race_short_name_3: str | None
    race_name_code: str | None
    graded_race_round_number: int | None
    grade_code: str | None
    race_type_code: str | None
    race_symbol_code: str | None
    weight_type_code: str | None
    race_cond_code_2yo: str | None
    race_cond_code_3yo: str | None
    race_cond_code_4yo: str | None
    race_cond_code_5yo_up: str | None
    race_cond_code_youngest: str | None
    distance: int | None
    track_code: str | None
    course_code: str | None
    handicap_announcement_date: date | None
    num_entries: int | None
    entry_horses: tuple[TKEntryHorsesItem, ...]
