"""Shared domain model types."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class PerformanceStats:
    """Annual performance stats for jockeys (KS) and trainers (CH)."""

    year: int | None
    flat_prize_money: int | None
    steeplechase_prize_money: int | None
    flat_added_money: int | None
    steeplechase_added_money: int | None
    flat_placing_counts: tuple[int, ...]
    steeplechase_placing_counts: tuple[int, ...]
    sapporo_flat_placing_counts: tuple[int, ...]
    sapporo_steeplechase_placing_counts: tuple[int, ...]
    hakodate_flat_placing_counts: tuple[int, ...]
    hakodate_steeplechase_placing_counts: tuple[int, ...]
    fukushima_flat_placing_counts: tuple[int, ...]
    fukushima_steeplechase_placing_counts: tuple[int, ...]
    niigata_flat_placing_counts: tuple[int, ...]
    niigata_steeplechase_placing_counts: tuple[int, ...]
    tokyo_flat_placing_counts: tuple[int, ...]
    tokyo_steeplechase_placing_counts: tuple[int, ...]
    nakayama_flat_placing_counts: tuple[int, ...]
    nakayama_steeplechase_placing_counts: tuple[int, ...]
    chukyo_flat_placing_counts: tuple[int, ...]
    chukyo_steeplechase_placing_counts: tuple[int, ...]
    kyoto_flat_placing_counts: tuple[int, ...]
    kyoto_steeplechase_placing_counts: tuple[int, ...]
    hanshin_flat_placing_counts: tuple[int, ...]
    hanshin_steeplechase_placing_counts: tuple[int, ...]
    kokura_flat_placing_counts: tuple[int, ...]
    kokura_steeplechase_placing_counts: tuple[int, ...]
    turf_class_d_placing_counts: tuple[int, ...]
    turf_class_e_placing_counts: tuple[int, ...]
    turf_gt2200_placing_counts: tuple[int, ...]
    dirt_class_d_placing_counts: tuple[int, ...]
    dirt_class_e_placing_counts: tuple[int, ...]
    dirt_gt2200_placing_counts: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class RecentGradedWin:
    """Recent graded race win info for jockeys (KS) and trainers (CH)."""

    race_key: str | None
    race_name_main: str | None
    race_short_name_10: str | None
    race_short_name_6: str | None
    race_short_name_3: str | None
    grade_code: str | None
    num_starters: int | None
    pedigree_reg_num: str | None
    horse_name: str | None


@dataclass(frozen=True, slots=True)
class SimplePerformanceStats:
    """Annual performance stats for owners (BN) and breeders (BR)."""

    year: int | None
    prize_money: int | None
    added_money: int | None
    placing_counts: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class MeetRecordBase:
    """Common fields for meet-scoped records (no race_number/race_id)."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    meet_year: int | None
    meet_month: int | None
    meet_day_of_month: int | None
    racecourse_code: str | None
    meet_round: int | None
    meet_day: int | None


@dataclass(frozen=True, slots=True)
class RaceRecordBase(MeetRecordBase):
    """Common fields for race-scoped records."""

    race_number: int | None
    race_id: str | None
    race_id_short: str | None
