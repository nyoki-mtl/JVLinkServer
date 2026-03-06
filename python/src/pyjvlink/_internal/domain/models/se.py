"""SE domain model."""

from dataclasses import dataclass

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class SEOpponentHorsesItem:
    """Opponent horse (1st place finisher) information."""

    pedigree_reg_num: str | None
    horse_name: str | None


@dataclass(frozen=True, slots=True)
class SERecord(RaceRecordBase):
    """Horse-by-race record."""

    bracket_number: int | None
    horse_number: int | None
    pedigree_reg_num: str | None
    horse_name: str | None
    horse_symbol_code: str | None
    horse_sex_code: str | None
    breed_code: str | None
    coat_color_code: str | None
    horse_age: int | None
    east_west_affiliation_code: str | None
    trainer_code: str | None
    trainer_short_name: str | None
    owner_code: str | None
    owner_name_individual: str | None
    silk_colors: str | None
    carrying_weight: float | None
    before_carrying_weight: float | None
    blinker_usage_code: str | None
    jockey_code: str | None
    before_jockey_code: str | None
    jockey_short_name: str | None
    before_jockey_short_name: str | None
    jockey_apprentice_code: str | None
    before_jockey_apprentice_code: str | None
    horse_weight: int | None
    weight_change_sign: str | None
    weight_change_diff: int | None
    abnormality_code: str | None
    finish_order: int | None
    confirmed_placing: int | None
    dead_heat_code: str | None
    dead_heat_count: int | None
    finish_time: str | None
    margin_code: str | None
    margin_code_plus: str | None
    margin_code_plus_plus: str | None
    corner1_position: int | None
    corner2_position: int | None
    corner3_position: int | None
    corner4_position: int | None
    win_odds: float | None
    win_popularity_rank: int | None
    earned_purse_money: int | None
    earned_added_money: int | None
    last_4f_time: str | None
    last_3f_time: str | None
    opponent_horses: tuple[SEOpponentHorsesItem, ...]
    time_diff: int | None
    record_update_code: str | None
    mining_code: str | None
    mining_pred_finish_time: str | None
    mining_pred_err_margin_plus: str | None
    mining_pred_err_margin_minus: str | None
    mining_pred_rank: int | None
    current_race_running_style_judgement: str | None
