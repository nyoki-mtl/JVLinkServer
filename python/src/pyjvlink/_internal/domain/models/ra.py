"""RA domain model."""

from dataclasses import dataclass
from datetime import time

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class RACornerPassingOrderItem:
    """Corner passing order information."""

    corner: int | None
    lap_count: int | None
    passing_order: str | None


@dataclass(frozen=True, slots=True)
class RARecord(RaceRecordBase):
    """Race header record."""

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
    before_grade_code: str | None
    race_type_code: str | None
    race_symbol_code: str | None
    weight_type_code: str | None
    race_cond_code_2yo: str | None
    race_cond_code_3yo: str | None
    race_cond_code_4yo: str | None
    race_cond_code_5yo_up: str | None
    race_cond_code_youngest: str | None
    race_condition_name: str | None
    distance: int | None
    before_distance: int | None
    track_code: str | None
    before_track_code: str | None
    course_code: str | None
    before_course_code: str | None
    purse_money: tuple[int, ...]
    before_purse_money: tuple[int, ...]
    added_money: tuple[int, ...]
    before_added_money: tuple[int, ...]
    post_time: time | None
    before_post_time: time | None
    num_entries: int | None
    num_starters: int | None
    num_finishers: int | None
    weather_code: str | None
    turf_track_condition_code: str | None
    dirt_track_condition_code: str | None
    lap_times: tuple[str, ...]
    mile_time: str | None
    first_3f_time: str | None
    first_4f_time: str | None
    last_3f_time: str | None
    last_4f_time: str | None
    corner_passing_order: tuple[RACornerPassingOrderItem, ...]
    record_update_code: str | None
