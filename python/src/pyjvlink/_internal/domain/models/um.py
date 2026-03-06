"""UM domain model."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class UMPedigree3GenItem:
    """Three-generation pedigree element."""

    breeding_reg_num: str | None
    horse_name: str | None


@dataclass(frozen=True, slots=True)
class UMRecord:
    """Racehorse master record."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    pedigree_reg_num: str | None
    deregistration_flag: str | None
    registration_date: date | None
    deregistration_date: date | None
    birth_date: date | None
    horse_name: str | None
    horse_name_kana: str | None
    horse_name_english: str | None
    jra_facility_flag: str | None
    horse_symbol_code: str | None
    sex_code: str | None
    breed_code: str | None
    coat_color_code: str | None
    pedigree_3gen: tuple[UMPedigree3GenItem, ...]
    affiliation_code: str | None
    trainer_code: str | None
    trainer_name_short: str | None
    invitation_area_name: str | None
    breeder_code: str | None
    breeder_name: str | None
    birthplace_name: str | None
    owner_code: str | None
    owner_name: str | None
    flat_prize_money_total: int | None
    steeplechase_prize_money_total: int | None
    flat_added_money_total: int | None
    steeplechase_added_money_total: int | None
    flat_earnings_total: int | None
    steeplechase_earnings_total: int | None
    overall_placing_counts: tuple[int, ...]
    central_placing_counts: tuple[int, ...]
    turf_straight_placing_counts: tuple[int, ...]
    turf_right_placing_counts: tuple[int, ...]
    turf_left_placing_counts: tuple[int, ...]
    dirt_straight_placing_counts: tuple[int, ...]
    dirt_right_placing_counts: tuple[int, ...]
    dirt_left_placing_counts: tuple[int, ...]
    steeplechase_placing_counts: tuple[int, ...]
    turf_good_placing_counts: tuple[int, ...]
    turf_slightly_heavy_placing_counts: tuple[int, ...]
    turf_heavy_placing_counts: tuple[int, ...]
    turf_bad_placing_counts: tuple[int, ...]
    dirt_good_placing_counts: tuple[int, ...]
    dirt_slightly_heavy_placing_counts: tuple[int, ...]
    dirt_heavy_placing_counts: tuple[int, ...]
    dirt_bad_placing_counts: tuple[int, ...]
    steeplechase_good_placing_counts: tuple[int, ...]
    steeplechase_slightly_heavy_placing_counts: tuple[int, ...]
    steeplechase_heavy_placing_counts: tuple[int, ...]
    steeplechase_bad_placing_counts: tuple[int, ...]
    turf_short_placing_counts: tuple[int, ...]
    turf_mid_placing_counts: tuple[int, ...]
    turf_long_placing_counts: tuple[int, ...]
    dirt_short_placing_counts: tuple[int, ...]
    dirt_mid_placing_counts: tuple[int, ...]
    dirt_long_placing_counts: tuple[int, ...]
    running_style_counts: tuple[int, ...]
    registered_race_count: int | None
