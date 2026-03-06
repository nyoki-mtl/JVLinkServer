"""Record decoders from wire payload to domain model."""

from collections.abc import AsyncIterator, Callable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any

from pyjvlink._internal.domain.models import (
    AVRecord,
    BNPerformanceStatsItem,
    BNRecord,
    BRPerformanceStatsItem,
    BRRecord,
    BTRecord,
    CCRecord,
    CHPerformanceStatsItem,
    CHRecentGradedWinsItem,
    CHRecord,
    CKBreederPerformanceStatsItem,
    CKJockeyPerformanceStatsItem,
    CKOwnerPerformanceStatsItem,
    CKRecord,
    CKTrainerPerformanceStatsItem,
    CSRecord,
    DMMiningPredictionsItem,
    DMRecord,
    DomainRecord,
    H1BracketQuinellaVotesItem,
    H1ExactaVotesItem,
    H1PlaceVotesItem,
    H1QuinellaVotesItem,
    H1Record,
    H1TrioVotesItem,
    H1WideVotesItem,
    H1WinVotesItem,
    H6Record,
    H6TrifectaVotesItem,
    HCRecord,
    HNRecord,
    HRBracketQuinellaPaybackItem,
    HRExactaPaybackItem,
    HRPlacePaybackItem,
    HRQuinellaPaybackItem,
    HRRecord,
    HRTrifectaPaybackItem,
    HRTrioPaybackItem,
    HRWidePaybackItem,
    HRWinPaybackItem,
    HSRecord,
    HYRecord,
    JCRecord,
    JGRecord,
    KSFirstRideInfoItem,
    KSFirstWinInfoItem,
    KSPerformanceStatsItem,
    KSRecentGradedWinsItem,
    KSRecord,
    O1BracketQuinellaOddsItem,
    O1PlaceOddsItem,
    O1Record,
    O1WinOddsItem,
    O2QuinellaOddsItem,
    O2Record,
    O3Record,
    O3WideOddsItem,
    O4ExactaOddsItem,
    O4Record,
    O5Record,
    O5TrioOddsItem,
    O6Record,
    O6TrifectaOddsItem,
    RACornerPassingOrderItem,
    RARecord,
    RCRecord,
    RCRecordHoldersItem,
    SEOpponentHorsesItem,
    SERecord,
    SKRecord,
    TCRecord,
    TKEntryHorsesItem,
    TKRecord,
    TMMiningPredictionsItem,
    TMRecord,
    UMPedigree3GenItem,
    UMRecord,
    WCRecord,
    WERecord,
    WFPayoutInfoItem,
    WFRecord,
    WFTargetRacesItem,
    WHHorseWeightInfosItem,
    WHRecord,
    YSGradedRaceGuideItem,
    YSRecord,
)
from pyjvlink._internal.domain.services import (
    AnnouncementParts,
    RaceIdParts,
    build_race_id,
    build_race_id_short,
    infer_announcement_at,
)
from pyjvlink._internal.protocol.enums import SaleFlag
from pyjvlink._internal.protocol.envelope import UNKNOWN_RECORD_TYPE, normalize_record_type, normalize_wire_record
from pyjvlink._internal.protocol.generated.registry import RECORD_TYPES
from pyjvlink._internal.protocol.models import RecordEnvelope, UnknownRecord, WireRecord
from pyjvlink._internal.protocol.validators import (
    to_date_yyyymmdd,
    to_dict,
    to_enum,
    to_float,
    to_int,
    to_list,
    to_mmddhhmm_parts,
    to_month_day,
    to_str,
    to_time_hhmm,
)

DecodeFn = Callable[[Mapping[str, Any]], DomainRecord]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _RaceContext:
    data_code: str | None
    data_creation_date: date | None
    meet_year: int | None
    meet_month: int | None
    meet_day_of_month: int | None
    racecourse_code: str | None
    meet_round: int | None
    meet_day: int | None
    race_number: int | None
    race_id: str | None
    race_id_short: str | None


def _build_context(payload: Mapping[str, Any]) -> _RaceContext:
    data_creation_date = to_date_yyyymmdd(payload.get("data_creation_date"))
    meet_year = to_int(payload.get("meet_year"))
    meet_month, meet_day_of_month = to_month_day(payload.get("meet_date"))
    racecourse_code = to_str(payload.get("racecourse_code"))
    meet_round = to_int(payload.get("meet_round"))
    meet_day = to_int(payload.get("meet_day"))
    race_number = to_int(payload.get("race_number"))

    parts = RaceIdParts(
        meet_year=meet_year,
        meet_month=meet_month,
        meet_day_of_month=meet_day_of_month,
        racecourse_code=racecourse_code,
        meet_round=meet_round,
        meet_day=meet_day,
        race_number=race_number,
    )
    return _RaceContext(
        data_code=to_str(payload.get("data_code")),
        data_creation_date=data_creation_date,
        meet_year=meet_year,
        meet_month=meet_month,
        meet_day_of_month=meet_day_of_month,
        racecourse_code=racecourse_code,
        meet_round=meet_round,
        meet_day=meet_day,
        race_number=race_number,
        race_id=build_race_id(parts),
        race_id_short=build_race_id_short(parts),
    )


def _meet_kwargs(context: _RaceContext) -> dict[str, Any]:
    return {
        "data_code": context.data_code,
        "data_creation_date": context.data_creation_date,
        "meet_year": context.meet_year,
        "meet_month": context.meet_month,
        "meet_day_of_month": context.meet_day_of_month,
        "racecourse_code": context.racecourse_code,
        "meet_round": context.meet_round,
        "meet_day": context.meet_day,
    }


def _context_kwargs(context: _RaceContext) -> dict[str, Any]:
    return {
        **_meet_kwargs(context),
        "race_number": context.race_number,
        "race_id": context.race_id,
        "race_id_short": context.race_id_short,
    }


def _decode_announcement(payload: Mapping[str, Any], context: _RaceContext) -> Any:
    month, day, hour, minute = to_mmddhhmm_parts(payload.get("announcement_datetime"))
    return infer_announcement_at(
        AnnouncementParts(
            announcement_month=month,
            announcement_day=day,
            announcement_hour=hour,
            announcement_minute=minute,
            data_creation_date=context.data_creation_date,
            meet_year=context.meet_year,
        )
    )


def _build_header_context(payload: Mapping[str, Any]) -> tuple[str | None, date | None]:
    return to_str(payload.get("data_code")), to_date_yyyymmdd(payload.get("data_creation_date"))


# ---------------------------------------------------------------------------
# Race record decoders
# ---------------------------------------------------------------------------


# --- RA ---


def _decode_corner_passing_order(values: Any) -> tuple[RACornerPassingOrderItem, ...]:
    records: list[RACornerPassingOrderItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            RACornerPassingOrderItem(
                corner=to_int(row.get("corner")),
                lap_count=to_int(row.get("lap_count")),
                passing_order=to_str(row.get("passing_order")),
            )
        )
    return tuple(records)


def _decode_ra(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return RARecord(
        type="RA",
        **_context_kwargs(context),
        weekday_code=to_str(payload.get("weekday_code")),
        special_race_number=to_int(payload.get("special_race_number")),
        race_name_main=to_str(payload.get("race_name_main")),
        race_name_subtitle=to_str(payload.get("race_name_subtitle")),
        race_name_parentheses=to_str(payload.get("race_name_parentheses")),
        race_name_main_english=to_str(payload.get("race_name_main_english")),
        race_name_subtitle_english=to_str(payload.get("race_name_subtitle_english")),
        race_name_parentheses_english=to_str(payload.get("race_name_parentheses_english")),
        race_short_name_10=to_str(payload.get("race_short_name_10")),
        race_short_name_6=to_str(payload.get("race_short_name_6")),
        race_short_name_3=to_str(payload.get("race_short_name_3")),
        race_name_code=to_str(payload.get("race_name_code")),
        graded_race_round_number=to_int(payload.get("graded_race_round_number")),
        grade_code=to_str(payload.get("grade_code")),
        before_grade_code=to_str(payload.get("before_grade_code")),
        race_type_code=to_str(payload.get("race_type_code")),
        race_symbol_code=to_str(payload.get("race_symbol_code")),
        weight_type_code=to_str(payload.get("weight_type_code")),
        race_cond_code_2yo=to_str(payload.get("race_cond_code_2yo")),
        race_cond_code_3yo=to_str(payload.get("race_cond_code_3yo")),
        race_cond_code_4yo=to_str(payload.get("race_cond_code_4yo")),
        race_cond_code_5yo_up=to_str(payload.get("race_cond_code_5yo_up")),
        race_cond_code_youngest=to_str(payload.get("race_cond_code_youngest")),
        race_condition_name=to_str(payload.get("race_condition_name")),
        distance=to_int(payload.get("distance")),
        before_distance=to_int(payload.get("before_distance")),
        track_code=to_str(payload.get("track_code")),
        before_track_code=to_str(payload.get("before_track_code")),
        course_code=to_str(payload.get("course_code")),
        before_course_code=to_str(payload.get("before_course_code")),
        purse_money=_decode_int_array(payload.get("purse_money")),
        before_purse_money=_decode_int_array(payload.get("before_purse_money")),
        added_money=_decode_int_array(payload.get("added_money")),
        before_added_money=_decode_int_array(payload.get("before_added_money")),
        post_time=to_time_hhmm(payload.get("post_time")),
        before_post_time=to_time_hhmm(payload.get("before_post_time")),
        num_entries=to_int(payload.get("num_entries")),
        num_starters=to_int(payload.get("num_starters")),
        num_finishers=to_int(payload.get("num_finishers")),
        weather_code=to_str(payload.get("weather_code")),
        turf_track_condition_code=to_str(payload.get("turf_track_condition_code")),
        dirt_track_condition_code=to_str(payload.get("dirt_track_condition_code")),
        lap_times=_decode_str_array(payload.get("lap_times")),
        mile_time=to_str(payload.get("mile_time")),
        first_3f_time=to_str(payload.get("first_3f_time")),
        first_4f_time=to_str(payload.get("first_4f_time")),
        last_3f_time=to_str(payload.get("last_3f_time")),
        last_4f_time=to_str(payload.get("last_4f_time")),
        corner_passing_order=_decode_corner_passing_order(payload.get("corner_passing_order")),
        record_update_code=to_str(payload.get("record_update_code")),
    )


# --- SE ---


def _decode_opponent_horses(values: Any) -> tuple[SEOpponentHorsesItem, ...]:
    records: list[SEOpponentHorsesItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            SEOpponentHorsesItem(
                pedigree_reg_num=to_str(row.get("pedigree_reg_num")),
                horse_name=to_str(row.get("horse_name")),
            )
        )
    return tuple(records)


def _decode_se(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return SERecord(
        type="SE",
        **_context_kwargs(context),
        bracket_number=to_int(payload.get("bracket_number")),
        horse_number=to_int(payload.get("horse_number")),
        pedigree_reg_num=to_str(payload.get("pedigree_reg_num")),
        horse_name=to_str(payload.get("horse_name")),
        horse_symbol_code=to_str(payload.get("horse_symbol_code")),
        horse_sex_code=to_str(payload.get("horse_sex_code")),
        breed_code=to_str(payload.get("breed_code")),
        coat_color_code=to_str(payload.get("coat_color_code")),
        horse_age=to_int(payload.get("horse_age")),
        east_west_affiliation_code=to_str(payload.get("east_west_affiliation_code")),
        trainer_code=to_str(payload.get("trainer_code")),
        trainer_short_name=to_str(payload.get("trainer_short_name")),
        owner_code=to_str(payload.get("owner_code")),
        owner_name_individual=to_str(payload.get("owner_name_individual")),
        silk_colors=to_str(payload.get("silk_colors")),
        carrying_weight=to_float(payload.get("carrying_weight"), scale=10),
        before_carrying_weight=to_float(payload.get("before_carrying_weight"), scale=10),
        blinker_usage_code=to_str(payload.get("blinker_usage_code")),
        jockey_code=to_str(payload.get("jockey_code")),
        before_jockey_code=to_str(payload.get("before_jockey_code")),
        jockey_short_name=to_str(payload.get("jockey_short_name")),
        before_jockey_short_name=to_str(payload.get("before_jockey_short_name")),
        jockey_apprentice_code=to_str(payload.get("jockey_apprentice_code")),
        before_jockey_apprentice_code=to_str(payload.get("before_jockey_apprentice_code")),
        horse_weight=to_int(payload.get("horse_weight")),
        weight_change_sign=to_str(payload.get("weight_change_sign")),
        weight_change_diff=to_int(payload.get("weight_change_diff")),
        abnormality_code=to_str(payload.get("abnormality_code")),
        finish_order=to_int(payload.get("finish_order")),
        confirmed_placing=to_int(payload.get("confirmed_placing")),
        dead_heat_code=to_str(payload.get("dead_heat_code")),
        dead_heat_count=to_int(payload.get("dead_heat_count")),
        finish_time=to_str(payload.get("finish_time")),
        margin_code=to_str(payload.get("margin_code")),
        margin_code_plus=to_str(payload.get("margin_code_plus")),
        margin_code_plus_plus=to_str(payload.get("margin_code_plus_plus")),
        corner1_position=to_int(payload.get("corner1_position")),
        corner2_position=to_int(payload.get("corner2_position")),
        corner3_position=to_int(payload.get("corner3_position")),
        corner4_position=to_int(payload.get("corner4_position")),
        win_odds=to_float(payload.get("win_odds"), scale=10),
        win_popularity_rank=to_int(payload.get("win_popularity_rank")),
        earned_purse_money=to_int(payload.get("earned_purse_money")),
        earned_added_money=to_int(payload.get("earned_added_money")),
        last_4f_time=to_str(payload.get("last_4f_time")),
        last_3f_time=to_str(payload.get("last_3f_time")),
        opponent_horses=_decode_opponent_horses(payload.get("opponent_horses")),
        time_diff=to_int(payload.get("time_diff")),
        record_update_code=to_str(payload.get("record_update_code")),
        mining_code=to_str(payload.get("mining_code")),
        mining_pred_finish_time=to_str(payload.get("mining_pred_finish_time")),
        mining_pred_err_margin_plus=to_str(payload.get("mining_pred_err_margin_plus")),
        mining_pred_err_margin_minus=to_str(payload.get("mining_pred_err_margin_minus")),
        mining_pred_rank=to_int(payload.get("mining_pred_rank")),
        current_race_running_style_judgement=to_str(payload.get("current_race_running_style_judgement")),
    )


# --- HR ---


def _decode_payback_list(values: Any, item_cls: type[Any]) -> tuple[Any, ...]:
    paybacks: list[Any] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        paybacks.append(
            item_cls(
                number=to_str(row.get("number")),
                payout=to_int(row.get("payout")),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(paybacks)


def _decode_hr(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return HRRecord(
        type="HR",
        **_context_kwargs(context),
        num_entries=to_int(payload.get("num_entries")),
        num_starters=to_int(payload.get("num_starters")),
        win_cancelled_flag=to_str(payload.get("win_cancelled_flag")),
        place_cancelled_flag=to_str(payload.get("place_cancelled_flag")),
        bracket_quinella_cancelled_flag=to_str(payload.get("bracket_quinella_cancelled_flag")),
        quinella_cancelled_flag=to_str(payload.get("quinella_cancelled_flag")),
        wide_cancelled_flag=to_str(payload.get("wide_cancelled_flag")),
        exacta_cancelled_flag=to_str(payload.get("exacta_cancelled_flag")),
        trio_cancelled_flag=to_str(payload.get("trio_cancelled_flag")),
        trifecta_cancelled_flag=to_str(payload.get("trifecta_cancelled_flag")),
        win_special_payout_flag=to_str(payload.get("win_special_payout_flag")),
        place_special_payout_flag=to_str(payload.get("place_special_payout_flag")),
        bracket_quinella_special_payout_flag=to_str(payload.get("bracket_quinella_special_payout_flag")),
        quinella_special_payout_flag=to_str(payload.get("quinella_special_payout_flag")),
        wide_special_payout_flag=to_str(payload.get("wide_special_payout_flag")),
        exacta_special_payout_flag=to_str(payload.get("exacta_special_payout_flag")),
        trio_special_payout_flag=to_str(payload.get("trio_special_payout_flag")),
        trifecta_special_payout_flag=to_str(payload.get("trifecta_special_payout_flag")),
        win_refund_flag=to_str(payload.get("win_refund_flag")),
        place_refund_flag=to_str(payload.get("place_refund_flag")),
        bracket_quinella_refund_flag=to_str(payload.get("bracket_quinella_refund_flag")),
        quinella_refund_flag=to_str(payload.get("quinella_refund_flag")),
        wide_refund_flag=to_str(payload.get("wide_refund_flag")),
        exacta_refund_flag=to_str(payload.get("exacta_refund_flag")),
        trio_refund_flag=to_str(payload.get("trio_refund_flag")),
        trifecta_refund_flag=to_str(payload.get("trifecta_refund_flag")),
        refund_horse_number_info_28=to_str(payload.get("refund_horse_number_info_28")),
        refund_bracket_info=to_str(payload.get("refund_bracket_info")),
        refund_same_bracket_info=to_str(payload.get("refund_same_bracket_info")),
        win_payback=_decode_payback_list(payload.get("win_payback"), HRWinPaybackItem),
        place_payback=_decode_payback_list(payload.get("place_payback"), HRPlacePaybackItem),
        bracket_quinella_payback=_decode_payback_list(
            payload.get("bracket_quinella_payback"), HRBracketQuinellaPaybackItem
        ),
        quinella_payback=_decode_payback_list(payload.get("quinella_payback"), HRQuinellaPaybackItem),
        wide_payback=_decode_payback_list(payload.get("wide_payback"), HRWidePaybackItem),
        exacta_payback=_decode_payback_list(payload.get("exacta_payback"), HRExactaPaybackItem),
        trio_payback=_decode_payback_list(payload.get("trio_payback"), HRTrioPaybackItem),
        trifecta_payback=_decode_payback_list(payload.get("trifecta_payback"), HRTrifectaPaybackItem),
    )


# --- WH ---


def _decode_horse_weight_infos(values: Any) -> tuple[WHHorseWeightInfosItem, ...]:
    records: list[WHHorseWeightInfosItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            WHHorseWeightInfosItem(
                horse_number=to_int(row.get("horse_number")),
                horse_name=to_str(row.get("horse_name")),
                horse_weight=to_int(row.get("horse_weight")),
                weight_change_sign=to_str(row.get("weight_change_sign")),
                weight_change_diff=to_int(row.get("weight_change_diff")),
            )
        )
    return tuple(records)


def _decode_wh(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return WHRecord(
        type="WH",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        horse_weight_infos=_decode_horse_weight_infos(payload.get("horse_weight_infos")),
    )


# --- O1 ---


def _decode_win_odds(values: Any) -> tuple[O1WinOddsItem, ...]:
    records: list[O1WinOddsItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            O1WinOddsItem(
                horse_number=to_int(row.get("horse_number")),
                odds=to_float(row.get("odds"), scale=10),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_place_odds(values: Any) -> tuple[O1PlaceOddsItem, ...]:
    records: list[O1PlaceOddsItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            O1PlaceOddsItem(
                horse_number=to_int(row.get("horse_number")),
                min_odds=to_float(row.get("min_odds"), scale=10),
                max_odds=to_float(row.get("max_odds"), scale=10),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_bracket_odds(values: Any) -> tuple[O1BracketQuinellaOddsItem, ...]:
    records: list[O1BracketQuinellaOddsItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            O1BracketQuinellaOddsItem(
                combination=to_str(row.get("combination")),
                odds=to_float(row.get("odds"), scale=10),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_o1(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return O1Record(
        type="O1",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        num_entries=to_int(payload.get("num_entries")),
        num_starters=to_int(payload.get("num_starters")),
        win_sales_flag=to_enum(payload.get("win_sales_flag"), SaleFlag),
        place_sales_flag=to_enum(payload.get("place_sales_flag"), SaleFlag),
        bracket_quinella_sales_flag=to_enum(payload.get("bracket_quinella_sales_flag"), SaleFlag),
        place_payout_key=to_int(payload.get("place_payout_key")),
        win_odds=_decode_win_odds(payload.get("win_odds")),
        place_odds=_decode_place_odds(payload.get("place_odds")),
        bracket_quinella_odds=_decode_bracket_odds(payload.get("bracket_quinella_odds")),
        win_total_votes=to_int(payload.get("win_total_votes")),
        place_total_votes=to_int(payload.get("place_total_votes")),
        bracket_quinella_total_votes=to_int(payload.get("bracket_quinella_total_votes")),
    )


# --- TK ---


def _decode_entry_horses(values: Any) -> tuple[TKEntryHorsesItem, ...]:
    records: list[TKEntryHorsesItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            TKEntryHorsesItem(
                serial_number=to_int(row.get("serial_number")),
                pedigree_reg_num=to_str(row.get("pedigree_reg_num")),
                horse_name=to_str(row.get("horse_name")),
                horse_symbol_code=to_str(row.get("horse_symbol_code")),
                sex_code=to_str(row.get("sex_code")),
                trainer_affiliation_code=to_str(row.get("trainer_affiliation_code")),
                trainer_code=to_str(row.get("trainer_code")),
                trainer_short_name=to_str(row.get("trainer_short_name")),
                impost_weight=to_int(row.get("impost_weight")),
                exchange_code=to_str(row.get("exchange_code")),
            )
        )
    return tuple(records)


def _decode_tk(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return TKRecord(
        type="TK",
        **_context_kwargs(context),
        weekday_code=to_str(payload.get("weekday_code")),
        special_race_number=to_int(payload.get("special_race_number")),
        race_name_main=to_str(payload.get("race_name_main")),
        race_name_subtitle=to_str(payload.get("race_name_subtitle")),
        race_name_parentheses=to_str(payload.get("race_name_parentheses")),
        race_name_main_english=to_str(payload.get("race_name_main_english")),
        race_name_subtitle_english=to_str(payload.get("race_name_subtitle_english")),
        race_name_parentheses_english=to_str(payload.get("race_name_parentheses_english")),
        race_short_name_10=to_str(payload.get("race_short_name_10")),
        race_short_name_6=to_str(payload.get("race_short_name_6")),
        race_short_name_3=to_str(payload.get("race_short_name_3")),
        race_name_code=to_str(payload.get("race_name_code")),
        graded_race_round_number=to_int(payload.get("graded_race_round_number")),
        grade_code=to_str(payload.get("grade_code")),
        race_type_code=to_str(payload.get("race_type_code")),
        race_symbol_code=to_str(payload.get("race_symbol_code")),
        weight_type_code=to_str(payload.get("weight_type_code")),
        race_cond_code_2yo=to_str(payload.get("race_cond_code_2yo")),
        race_cond_code_3yo=to_str(payload.get("race_cond_code_3yo")),
        race_cond_code_4yo=to_str(payload.get("race_cond_code_4yo")),
        race_cond_code_5yo_up=to_str(payload.get("race_cond_code_5yo_up")),
        race_cond_code_youngest=to_str(payload.get("race_cond_code_youngest")),
        distance=to_int(payload.get("distance")),
        track_code=to_str(payload.get("track_code")),
        course_code=to_str(payload.get("course_code")),
        handicap_announcement_date=to_date_yyyymmdd(payload.get("handicap_announcement_date")),
        num_entries=to_int(payload.get("num_entries")),
        entry_horses=_decode_entry_horses(payload.get("entry_horses")),
    )


# --- H1 ---


def _decode_h1_horse_number_votes(values: Any, item_cls: type[Any]) -> tuple[Any, ...]:
    records: list[Any] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            item_cls(
                horse_number=to_int(row.get("horse_number")),
                votes=to_int(row.get("votes")),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_h1_combination_votes(values: Any, item_cls: type[Any]) -> tuple[Any, ...]:
    records: list[Any] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            item_cls(
                combination=to_str(row.get("combination")),
                votes=to_int(row.get("votes")),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_h6_trifecta_votes(values: Any) -> tuple[H6TrifectaVotesItem, ...]:
    records: list[H6TrifectaVotesItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            H6TrifectaVotesItem(
                combination=to_str(row.get("combination")),
                votes=to_int(row.get("votes")),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_h1(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return H1Record(
        type="H1",
        **_context_kwargs(context),
        num_entries=to_int(payload.get("num_entries")),
        num_starters=to_int(payload.get("num_starters")),
        win_sales_flag=to_enum(payload.get("win_sales_flag"), SaleFlag),
        place_sales_flag=to_enum(payload.get("place_sales_flag"), SaleFlag),
        bracket_quinella_sales_flag=to_enum(payload.get("bracket_quinella_sales_flag"), SaleFlag),
        quinella_sales_flag=to_enum(payload.get("quinella_sales_flag"), SaleFlag),
        wide_sales_flag=to_enum(payload.get("wide_sales_flag"), SaleFlag),
        exacta_sales_flag=to_enum(payload.get("exacta_sales_flag"), SaleFlag),
        trio_sales_flag=to_enum(payload.get("trio_sales_flag"), SaleFlag),
        place_payout_key=to_int(payload.get("place_payout_key")),
        refund_horse_numbers=_decode_str_array(payload.get("refund_horse_numbers")),
        refund_bracket_numbers=_decode_str_array(payload.get("refund_bracket_numbers")),
        refund_same_bracket=_decode_str_array(payload.get("refund_same_bracket")),
        win_votes=_decode_h1_horse_number_votes(payload.get("win_votes"), H1WinVotesItem),
        place_votes=_decode_h1_horse_number_votes(payload.get("place_votes"), H1PlaceVotesItem),
        bracket_quinella_votes=_decode_h1_combination_votes(
            payload.get("bracket_quinella_votes"), H1BracketQuinellaVotesItem
        ),
        quinella_votes=_decode_h1_combination_votes(payload.get("quinella_votes"), H1QuinellaVotesItem),
        wide_votes=_decode_h1_combination_votes(payload.get("wide_votes"), H1WideVotesItem),
        exacta_votes=_decode_h1_combination_votes(payload.get("exacta_votes"), H1ExactaVotesItem),
        trio_votes=_decode_h1_combination_votes(payload.get("trio_votes"), H1TrioVotesItem),
        win_total_votes=to_int(payload.get("win_total_votes")),
        place_total_votes=to_int(payload.get("place_total_votes")),
        bracket_quinella_total_votes=to_int(payload.get("bracket_quinella_total_votes")),
        quinella_total_votes=to_int(payload.get("quinella_total_votes")),
        wide_total_votes=to_int(payload.get("wide_total_votes")),
        exacta_total_votes=to_int(payload.get("exacta_total_votes")),
        trio_total_votes=to_int(payload.get("trio_total_votes")),
        win_refund_votes=to_int(payload.get("win_refund_votes")),
        place_refund_votes=to_int(payload.get("place_refund_votes")),
        bracket_quinella_refund_votes=to_int(payload.get("bracket_quinella_refund_votes")),
        quinella_refund_votes=to_int(payload.get("quinella_refund_votes")),
        wide_refund_votes=to_int(payload.get("wide_refund_votes")),
        exacta_refund_votes=to_int(payload.get("exacta_refund_votes")),
        trio_refund_votes=to_int(payload.get("trio_refund_votes")),
    )


# --- H6 ---


def _decode_h6(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return H6Record(
        type="H6",
        **_context_kwargs(context),
        num_entries=to_int(payload.get("num_entries")),
        num_starters=to_int(payload.get("num_starters")),
        trifecta_sales_flag=to_enum(payload.get("trifecta_sales_flag"), SaleFlag),
        refund_horse_numbers=_decode_str_array(payload.get("refund_horse_numbers")),
        trifecta_votes=_decode_h6_trifecta_votes(payload.get("trifecta_votes")),
        trifecta_total_votes=to_int(payload.get("trifecta_total_votes")),
        trifecta_refund_votes=to_int(payload.get("trifecta_refund_votes")),
    )


# --- O2 ---


def _decode_quinella_odds(values: Any) -> tuple[O2QuinellaOddsItem, ...]:
    records: list[O2QuinellaOddsItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            O2QuinellaOddsItem(
                combination=to_str(row.get("combination")),
                odds=to_float(row.get("odds"), scale=10),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_o2(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return O2Record(
        type="O2",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        num_entries=to_int(payload.get("num_entries")),
        num_starters=to_int(payload.get("num_starters")),
        quinella_sales_flag=to_enum(payload.get("quinella_sales_flag"), SaleFlag),
        quinella_odds=_decode_quinella_odds(payload.get("quinella_odds")),
        quinella_total_votes=to_int(payload.get("quinella_total_votes")),
    )


# --- O3 ---


def _decode_wide_odds(values: Any) -> tuple[O3WideOddsItem, ...]:
    records: list[O3WideOddsItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            O3WideOddsItem(
                combination=to_str(row.get("combination")),
                min_odds=to_float(row.get("min_odds"), scale=10),
                max_odds=to_float(row.get("max_odds"), scale=10),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_o3(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return O3Record(
        type="O3",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        num_entries=to_int(payload.get("num_entries")),
        num_starters=to_int(payload.get("num_starters")),
        wide_sales_flag=to_enum(payload.get("wide_sales_flag"), SaleFlag),
        wide_odds=_decode_wide_odds(payload.get("wide_odds")),
        wide_total_votes=to_int(payload.get("wide_total_votes")),
    )


# --- O4 ---


def _decode_exacta_odds(values: Any) -> tuple[O4ExactaOddsItem, ...]:
    records: list[O4ExactaOddsItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            O4ExactaOddsItem(
                combination=to_str(row.get("combination")),
                odds=to_float(row.get("odds"), scale=10),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_o4(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return O4Record(
        type="O4",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        num_entries=to_int(payload.get("num_entries")),
        num_starters=to_int(payload.get("num_starters")),
        exacta_sales_flag=to_enum(payload.get("exacta_sales_flag"), SaleFlag),
        exacta_odds=_decode_exacta_odds(payload.get("exacta_odds")),
        exacta_total_votes=to_int(payload.get("exacta_total_votes")),
    )


# --- O5 ---


def _decode_trio_odds(values: Any) -> tuple[O5TrioOddsItem, ...]:
    records: list[O5TrioOddsItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            O5TrioOddsItem(
                combination=to_str(row.get("combination")),
                odds=to_float(row.get("odds"), scale=10),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_o5(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return O5Record(
        type="O5",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        num_entries=to_int(payload.get("num_entries")),
        num_starters=to_int(payload.get("num_starters")),
        trio_sales_flag=to_enum(payload.get("trio_sales_flag"), SaleFlag),
        trio_odds=_decode_trio_odds(payload.get("trio_odds")),
        trio_total_votes=to_int(payload.get("trio_total_votes")),
    )


# --- O6 ---


def _decode_trifecta_odds(values: Any) -> tuple[O6TrifectaOddsItem, ...]:
    records: list[O6TrifectaOddsItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            O6TrifectaOddsItem(
                combination=to_str(row.get("combination")),
                odds=to_float(row.get("odds"), scale=10),
                popularity_rank=to_int(row.get("popularity_rank")),
            )
        )
    return tuple(records)


def _decode_o6(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return O6Record(
        type="O6",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        num_entries=to_int(payload.get("num_entries")),
        num_starters=to_int(payload.get("num_starters")),
        trifecta_sales_flag=to_enum(payload.get("trifecta_sales_flag"), SaleFlag),
        trifecta_odds=_decode_trifecta_odds(payload.get("trifecta_odds")),
        trifecta_total_votes=to_int(payload.get("trifecta_total_votes")),
    )


# --- WF ---


def _decode_target_races(values: Any) -> tuple[WFTargetRacesItem, ...]:
    records: list[WFTargetRacesItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            WFTargetRacesItem(
                racecourse_code=to_str(row.get("racecourse_code")),
                meet_round=to_int(row.get("meet_round")),
                meet_day=to_int(row.get("meet_day")),
                race_number=to_int(row.get("race_number")),
            )
        )
    return tuple(records)


def _decode_payout_info(values: Any) -> tuple[WFPayoutInfoItem, ...]:
    records: list[WFPayoutInfoItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            WFPayoutInfoItem(
                combination=to_str(row.get("combination")),
                payout=to_int(row.get("payout")),
                winning_tickets=to_int(row.get("winning_tickets")),
            )
        )
    return tuple(records)


def _decode_wf(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return WFRecord(
        type="WF",
        **_context_kwargs(context),
        target_races=_decode_target_races(payload.get("target_races")),
        total_tickets_sold=to_int(payload.get("total_tickets_sold")),
        valid_ticket_counts=_decode_int_array(payload.get("valid_ticket_counts")),
        refund_flag=to_str(payload.get("refund_flag")),
        void_flag=to_str(payload.get("void_flag")),
        no_winner_flag=to_str(payload.get("no_winner_flag")),
        carryover_initial=to_int(payload.get("carryover_initial")),
        carryover_remaining=to_int(payload.get("carryover_remaining")),
        payout_info=_decode_payout_info(payload.get("payout_info")),
    )


# --- JG ---


def _decode_jg(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return JGRecord(
        type="JG",
        **_context_kwargs(context),
        pedigree_reg_num=to_str(payload.get("pedigree_reg_num")),
        horse_name=to_str(payload.get("horse_name")),
        entry_order=to_int(payload.get("entry_order")),
        entry_code=to_str(payload.get("entry_code")),
        exclusion_code=to_str(payload.get("exclusion_code")),
    )


# --- DM ---


def _decode_time_mining_predictions(values: Any) -> tuple[DMMiningPredictionsItem, ...]:
    records: list[DMMiningPredictionsItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            DMMiningPredictionsItem(
                horse_number=to_int(row.get("horse_number")),
                predicted_finish_time=to_str(row.get("predicted_finish_time")),
                error_margin_plus=to_str(row.get("error_margin_plus")),
                error_margin_minus=to_str(row.get("error_margin_minus")),
            )
        )
    return tuple(records)


def _decode_dm(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return DMRecord(
        type="DM",
        **_context_kwargs(context),
        data_creation_time=to_time_hhmm(payload.get("data_creation_time")),
        mining_predictions=_decode_time_mining_predictions(payload.get("mining_predictions")),
    )


# --- TM ---


def _decode_matchup_mining_predictions(values: Any) -> tuple[TMMiningPredictionsItem, ...]:
    records: list[TMMiningPredictionsItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            TMMiningPredictionsItem(
                horse_number=to_int(row.get("horse_number")),
                prediction_score=to_float(row.get("prediction_score"), scale=10),
            )
        )
    return tuple(records)


def _decode_tm(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return TMRecord(
        type="TM",
        **_context_kwargs(context),
        data_creation_time=to_time_hhmm(payload.get("data_creation_time")),
        mining_predictions=_decode_matchup_mining_predictions(payload.get("mining_predictions")),
    )


# --- CK ---


def _decode_int_array(values: Any) -> tuple[int, ...]:
    return tuple(to_int(v) or 0 for v in to_list(values))


def _decode_str_array(values: Any) -> tuple[str, ...]:
    return tuple(to_str(v) or "" for v in to_list(values))


def _decode_ck_performance_stats(values: Any, item_cls: type[Any]) -> tuple[Any, ...]:
    records: list[Any] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            item_cls(
                year=to_int(row.get("year")),
                flat_prize_money=to_int(row.get("flat_prize_money")),
                obstacle_prize_money=to_int(row.get("obstacle_prize_money")),
                flat_added_money=to_int(row.get("flat_added_money")),
                obstacle_added_money=to_int(row.get("obstacle_added_money")),
                turf_placing_counts=_decode_int_array(row.get("turf_placing_counts")),
                dirt_placing_counts=_decode_int_array(row.get("dirt_placing_counts")),
                obstacle_placing_counts=_decode_int_array(row.get("obstacle_placing_counts")),
                turf_dist_1200_placing_counts=_decode_int_array(row.get("turf_dist_1200_placing_counts")),
                turf_dist_1201_1400_placing_counts=_decode_int_array(row.get("turf_dist_1201_1400_placing_counts")),
                turf_dist_1401_1600_placing_counts=_decode_int_array(row.get("turf_dist_1401_1600_placing_counts")),
                turf_dist_1601_1800_placing_counts=_decode_int_array(row.get("turf_dist_1601_1800_placing_counts")),
                turf_dist_1801_2000_placing_counts=_decode_int_array(row.get("turf_dist_1801_2000_placing_counts")),
                turf_dist_2001_2200_placing_counts=_decode_int_array(row.get("turf_dist_2001_2200_placing_counts")),
                turf_dist_2201_2400_placing_counts=_decode_int_array(row.get("turf_dist_2201_2400_placing_counts")),
                turf_dist_2401_2800_placing_counts=_decode_int_array(row.get("turf_dist_2401_2800_placing_counts")),
                turf_dist_2801_placing_counts=_decode_int_array(row.get("turf_dist_2801_placing_counts")),
                dirt_dist_1200_placing_counts=_decode_int_array(row.get("dirt_dist_1200_placing_counts")),
                dirt_dist_1201_1400_placing_counts=_decode_int_array(row.get("dirt_dist_1201_1400_placing_counts")),
                dirt_dist_1401_1600_placing_counts=_decode_int_array(row.get("dirt_dist_1401_1600_placing_counts")),
                dirt_dist_1601_1800_placing_counts=_decode_int_array(row.get("dirt_dist_1601_1800_placing_counts")),
                dirt_dist_1801_2000_placing_counts=_decode_int_array(row.get("dirt_dist_1801_2000_placing_counts")),
                dirt_dist_2001_2200_placing_counts=_decode_int_array(row.get("dirt_dist_2001_2200_placing_counts")),
                dirt_dist_2201_2400_placing_counts=_decode_int_array(row.get("dirt_dist_2201_2400_placing_counts")),
                dirt_dist_2401_2800_placing_counts=_decode_int_array(row.get("dirt_dist_2401_2800_placing_counts")),
                dirt_dist_2801_placing_counts=_decode_int_array(row.get("dirt_dist_2801_placing_counts")),
                sapporo_turf_placing_counts=_decode_int_array(row.get("sapporo_turf_placing_counts")),
                hakodate_turf_placing_counts=_decode_int_array(row.get("hakodate_turf_placing_counts")),
                fukushima_turf_placing_counts=_decode_int_array(row.get("fukushima_turf_placing_counts")),
                niigata_turf_placing_counts=_decode_int_array(row.get("niigata_turf_placing_counts")),
                tokyo_turf_placing_counts=_decode_int_array(row.get("tokyo_turf_placing_counts")),
                nakayama_turf_placing_counts=_decode_int_array(row.get("nakayama_turf_placing_counts")),
                chukyo_turf_placing_counts=_decode_int_array(row.get("chukyo_turf_placing_counts")),
                kyoto_turf_placing_counts=_decode_int_array(row.get("kyoto_turf_placing_counts")),
                hanshin_turf_placing_counts=_decode_int_array(row.get("hanshin_turf_placing_counts")),
                kokura_turf_placing_counts=_decode_int_array(row.get("kokura_turf_placing_counts")),
                sapporo_dirt_placing_counts=_decode_int_array(row.get("sapporo_dirt_placing_counts")),
                hakodate_dirt_placing_counts=_decode_int_array(row.get("hakodate_dirt_placing_counts")),
                fukushima_dirt_placing_counts=_decode_int_array(row.get("fukushima_dirt_placing_counts")),
                niigata_dirt_placing_counts=_decode_int_array(row.get("niigata_dirt_placing_counts")),
                tokyo_dirt_placing_counts=_decode_int_array(row.get("tokyo_dirt_placing_counts")),
                nakayama_dirt_placing_counts=_decode_int_array(row.get("nakayama_dirt_placing_counts")),
                chukyo_dirt_placing_counts=_decode_int_array(row.get("chukyo_dirt_placing_counts")),
                kyoto_dirt_placing_counts=_decode_int_array(row.get("kyoto_dirt_placing_counts")),
                hanshin_dirt_placing_counts=_decode_int_array(row.get("hanshin_dirt_placing_counts")),
                kokura_dirt_placing_counts=_decode_int_array(row.get("kokura_dirt_placing_counts")),
                sapporo_obstacle_placing_counts=_decode_int_array(row.get("sapporo_obstacle_placing_counts")),
                hakodate_obstacle_placing_counts=_decode_int_array(row.get("hakodate_obstacle_placing_counts")),
                fukushima_obstacle_placing_counts=_decode_int_array(row.get("fukushima_obstacle_placing_counts")),
                niigata_obstacle_placing_counts=_decode_int_array(row.get("niigata_obstacle_placing_counts")),
                tokyo_obstacle_placing_counts=_decode_int_array(row.get("tokyo_obstacle_placing_counts")),
                nakayama_obstacle_placing_counts=_decode_int_array(row.get("nakayama_obstacle_placing_counts")),
                chukyo_obstacle_placing_counts=_decode_int_array(row.get("chukyo_obstacle_placing_counts")),
                kyoto_obstacle_placing_counts=_decode_int_array(row.get("kyoto_obstacle_placing_counts")),
                hanshin_obstacle_placing_counts=_decode_int_array(row.get("hanshin_obstacle_placing_counts")),
                kokura_obstacle_placing_counts=_decode_int_array(row.get("kokura_obstacle_placing_counts")),
            )
        )
    return tuple(records)


def _decode_ck_simple_performance_stats(values: Any, item_cls: type[Any]) -> tuple[Any, ...]:
    records: list[Any] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            item_cls(
                year=to_int(row.get("year")),
                prize_money=to_int(row.get("prize_money")),
                added_money=to_int(row.get("added_money")),
                placing_counts=_decode_int_array(row.get("placing_counts")),
            )
        )
    return tuple(records)


def _decode_ck(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    return CKRecord(
        type="CK",
        **_context_kwargs(context),
        pedigree_reg_num=to_str(payload.get("pedigree_reg_num")),
        horse_name=to_str(payload.get("horse_name")),
        flat_purse_total=to_int(payload.get("flat_purse_total")),
        obstacle_purse_total=to_int(payload.get("obstacle_purse_total")),
        flat_added_money_total=to_int(payload.get("flat_added_money_total")),
        obstacle_added_money_total=to_int(payload.get("obstacle_added_money_total")),
        flat_earned_money_total=to_int(payload.get("flat_earned_money_total")),
        obstacle_earned_money_total=to_int(payload.get("obstacle_earned_money_total")),
        total_placing_counts=_decode_int_array(payload.get("total_placing_counts")),
        jra_total_placing_counts=_decode_int_array(payload.get("jra_total_placing_counts")),
        turf_straight_placing_counts=_decode_int_array(payload.get("turf_straight_placing_counts")),
        turf_right_placing_counts=_decode_int_array(payload.get("turf_right_placing_counts")),
        turf_left_placing_counts=_decode_int_array(payload.get("turf_left_placing_counts")),
        dirt_straight_placing_counts=_decode_int_array(payload.get("dirt_straight_placing_counts")),
        dirt_right_placing_counts=_decode_int_array(payload.get("dirt_right_placing_counts")),
        dirt_left_placing_counts=_decode_int_array(payload.get("dirt_left_placing_counts")),
        obstacle_placing_counts=_decode_int_array(payload.get("obstacle_placing_counts")),
        turf_good_placing_counts=_decode_int_array(payload.get("turf_good_placing_counts")),
        turf_yielding_placing_counts=_decode_int_array(payload.get("turf_yielding_placing_counts")),
        turf_heavy_placing_counts=_decode_int_array(payload.get("turf_heavy_placing_counts")),
        turf_soft_placing_counts=_decode_int_array(payload.get("turf_soft_placing_counts")),
        dirt_good_placing_counts=_decode_int_array(payload.get("dirt_good_placing_counts")),
        dirt_yielding_placing_counts=_decode_int_array(payload.get("dirt_yielding_placing_counts")),
        dirt_heavy_placing_counts=_decode_int_array(payload.get("dirt_heavy_placing_counts")),
        dirt_soft_placing_counts=_decode_int_array(payload.get("dirt_soft_placing_counts")),
        obstacle_good_placing_counts=_decode_int_array(payload.get("obstacle_good_placing_counts")),
        obstacle_yielding_placing_counts=_decode_int_array(payload.get("obstacle_yielding_placing_counts")),
        obstacle_heavy_placing_counts=_decode_int_array(payload.get("obstacle_heavy_placing_counts")),
        obstacle_soft_placing_counts=_decode_int_array(payload.get("obstacle_soft_placing_counts")),
        running_style_counts=_decode_int_array(payload.get("running_style_counts")),
        registered_race_count=to_int(payload.get("registered_race_count")),
        jockey_code=to_str(payload.get("jockey_code")),
        jockey_name=to_str(payload.get("jockey_name")),
        jockey_performance_stats=_decode_ck_performance_stats(
            payload.get("jockey_performance_stats"), CKJockeyPerformanceStatsItem
        ),
        trainer_code=to_str(payload.get("trainer_code")),
        trainer_name=to_str(payload.get("trainer_name")),
        trainer_performance_stats=_decode_ck_performance_stats(
            payload.get("trainer_performance_stats"), CKTrainerPerformanceStatsItem
        ),
        owner_code=to_str(payload.get("owner_code")),
        owner_name_with_corp=to_str(payload.get("owner_name_with_corp")),
        owner_name_individual=to_str(payload.get("owner_name_individual")),
        owner_performance_stats=_decode_ck_simple_performance_stats(
            payload.get("owner_performance_stats"), CKOwnerPerformanceStatsItem
        ),
        breeder_code=to_str(payload.get("breeder_code")),
        breeder_name_with_corp=to_str(payload.get("breeder_name_with_corp")),
        breeder_name_individual=to_str(payload.get("breeder_name_individual")),
        breeder_performance_stats=_decode_ck_simple_performance_stats(
            payload.get("breeder_performance_stats"), CKBreederPerformanceStatsItem
        ),
    )


# --- WE ---


def _decode_we(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return WERecord(
        type="WE",
        **_meet_kwargs(context),
        announcement_at=announcement_at,
        change_identifier=to_str(payload.get("change_identifier")),
        weather_code=to_str(payload.get("weather_code")),
        turf_track_condition_code=to_str(payload.get("turf_track_condition_code")),
        dirt_track_condition_code=to_str(payload.get("dirt_track_condition_code")),
        before_weather_code=to_str(payload.get("before_weather_code")),
        before_turf_track_condition_code=to_str(payload.get("before_turf_track_condition_code")),
        before_dirt_track_condition_code=to_str(payload.get("before_dirt_track_condition_code")),
    )


# --- AV ---


def _decode_av(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return AVRecord(
        type="AV",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        horse_number=to_int(payload.get("horse_number")),
        horse_name=to_str(payload.get("horse_name")),
        exclusion_reason_code=to_str(payload.get("exclusion_reason_code")),
    )


# --- JC ---


def _decode_jc(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return JCRecord(
        type="JC",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        horse_number=to_int(payload.get("horse_number")),
        horse_name=to_str(payload.get("horse_name")),
        after_weight_carried=to_int(payload.get("after_weight_carried")),
        after_jockey_code=to_str(payload.get("after_jockey_code")),
        after_jockey_name=to_str(payload.get("after_jockey_name")),
        after_apprentice_code=to_str(payload.get("after_apprentice_code")),
        before_weight_carried=to_int(payload.get("before_weight_carried")),
        before_jockey_code=to_str(payload.get("before_jockey_code")),
        before_jockey_name=to_str(payload.get("before_jockey_name")),
        before_apprentice_code=to_str(payload.get("before_apprentice_code")),
    )


# --- TC ---


def _decode_tc(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return TCRecord(
        type="TC",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        after_post_time=to_time_hhmm(payload.get("after_post_time")),
        before_post_time=to_time_hhmm(payload.get("before_post_time")),
    )


# --- CC ---


def _decode_cc(payload: Mapping[str, Any]) -> DomainRecord:
    context = _build_context(payload)
    announcement_at = _decode_announcement(payload, context)
    return CCRecord(
        type="CC",
        **_context_kwargs(context),
        announcement_at=announcement_at,
        after_distance=to_int(payload.get("after_distance")),
        after_track_code=to_str(payload.get("after_track_code")),
        before_distance=to_int(payload.get("before_distance")),
        before_track_code=to_str(payload.get("before_track_code")),
        reason_code=to_str(payload.get("reason_code")),
    )


# ---------------------------------------------------------------------------
# Master/non-race record decoders
# ---------------------------------------------------------------------------


# --- UM ---


def _decode_um_pedigree_3gen(values: Any) -> tuple[UMPedigree3GenItem, ...]:
    records: list[UMPedigree3GenItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            UMPedigree3GenItem(
                breeding_reg_num=to_str(row.get("breeding_reg_num")),
                horse_name=to_str(row.get("horse_name")),
            )
        )
    return tuple(records)


def _decode_um(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return UMRecord(
        type="UM",
        data_code=data_code,
        data_creation_date=data_creation_date,
        pedigree_reg_num=to_str(payload.get("pedigree_reg_num")),
        deregistration_flag=to_str(payload.get("deregistration_flag")),
        registration_date=to_date_yyyymmdd(payload.get("registration_date")),
        deregistration_date=to_date_yyyymmdd(payload.get("deregistration_date")),
        birth_date=to_date_yyyymmdd(payload.get("birth_date")),
        horse_name=to_str(payload.get("horse_name")),
        horse_name_kana=to_str(payload.get("horse_name_kana")),
        horse_name_english=to_str(payload.get("horse_name_english")),
        jra_facility_flag=to_str(payload.get("jra_facility_flag")),
        horse_symbol_code=to_str(payload.get("horse_symbol_code")),
        sex_code=to_str(payload.get("sex_code")),
        breed_code=to_str(payload.get("breed_code")),
        coat_color_code=to_str(payload.get("coat_color_code")),
        pedigree_3gen=_decode_um_pedigree_3gen(payload.get("pedigree_3gen")),
        affiliation_code=to_str(payload.get("affiliation_code")),
        trainer_code=to_str(payload.get("trainer_code")),
        trainer_name_short=to_str(payload.get("trainer_name_short")),
        invitation_area_name=to_str(payload.get("invitation_area_name")),
        breeder_code=to_str(payload.get("breeder_code")),
        breeder_name=to_str(payload.get("breeder_name")),
        birthplace_name=to_str(payload.get("birthplace_name")),
        owner_code=to_str(payload.get("owner_code")),
        owner_name=to_str(payload.get("owner_name")),
        flat_prize_money_total=to_int(payload.get("flat_prize_money_total")),
        steeplechase_prize_money_total=to_int(payload.get("steeplechase_prize_money_total")),
        flat_added_money_total=to_int(payload.get("flat_added_money_total")),
        steeplechase_added_money_total=to_int(payload.get("steeplechase_added_money_total")),
        flat_earnings_total=to_int(payload.get("flat_earnings_total")),
        steeplechase_earnings_total=to_int(payload.get("steeplechase_earnings_total")),
        overall_placing_counts=_decode_int_array(payload.get("overall_placing_counts")),
        central_placing_counts=_decode_int_array(payload.get("central_placing_counts")),
        turf_straight_placing_counts=_decode_int_array(payload.get("turf_straight_placing_counts")),
        turf_right_placing_counts=_decode_int_array(payload.get("turf_right_placing_counts")),
        turf_left_placing_counts=_decode_int_array(payload.get("turf_left_placing_counts")),
        dirt_straight_placing_counts=_decode_int_array(payload.get("dirt_straight_placing_counts")),
        dirt_right_placing_counts=_decode_int_array(payload.get("dirt_right_placing_counts")),
        dirt_left_placing_counts=_decode_int_array(payload.get("dirt_left_placing_counts")),
        steeplechase_placing_counts=_decode_int_array(payload.get("steeplechase_placing_counts")),
        turf_good_placing_counts=_decode_int_array(payload.get("turf_good_placing_counts")),
        turf_slightly_heavy_placing_counts=_decode_int_array(payload.get("turf_slightly_heavy_placing_counts")),
        turf_heavy_placing_counts=_decode_int_array(payload.get("turf_heavy_placing_counts")),
        turf_bad_placing_counts=_decode_int_array(payload.get("turf_bad_placing_counts")),
        dirt_good_placing_counts=_decode_int_array(payload.get("dirt_good_placing_counts")),
        dirt_slightly_heavy_placing_counts=_decode_int_array(payload.get("dirt_slightly_heavy_placing_counts")),
        dirt_heavy_placing_counts=_decode_int_array(payload.get("dirt_heavy_placing_counts")),
        dirt_bad_placing_counts=_decode_int_array(payload.get("dirt_bad_placing_counts")),
        steeplechase_good_placing_counts=_decode_int_array(payload.get("steeplechase_good_placing_counts")),
        steeplechase_slightly_heavy_placing_counts=_decode_int_array(
            payload.get("steeplechase_slightly_heavy_placing_counts")
        ),
        steeplechase_heavy_placing_counts=_decode_int_array(payload.get("steeplechase_heavy_placing_counts")),
        steeplechase_bad_placing_counts=_decode_int_array(payload.get("steeplechase_bad_placing_counts")),
        turf_short_placing_counts=_decode_int_array(payload.get("turf_short_placing_counts")),
        turf_mid_placing_counts=_decode_int_array(payload.get("turf_mid_placing_counts")),
        turf_long_placing_counts=_decode_int_array(payload.get("turf_long_placing_counts")),
        dirt_short_placing_counts=_decode_int_array(payload.get("dirt_short_placing_counts")),
        dirt_mid_placing_counts=_decode_int_array(payload.get("dirt_mid_placing_counts")),
        dirt_long_placing_counts=_decode_int_array(payload.get("dirt_long_placing_counts")),
        running_style_counts=_decode_int_array(payload.get("running_style_counts")),
        registered_race_count=to_int(payload.get("registered_race_count")),
    )


# --- KS ---


def _decode_first_ride_info(values: Any) -> tuple[KSFirstRideInfoItem, ...]:
    records: list[KSFirstRideInfoItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row or to_str(row.get("race_key")) is None:
            continue
        records.append(
            KSFirstRideInfoItem(
                race_key=to_str(row.get("race_key")),
                num_starters=to_int(row.get("num_starters")),
                pedigree_reg_num=to_str(row.get("pedigree_reg_num")),
                horse_name=to_str(row.get("horse_name")),
                confirmed_placing=to_int(row.get("confirmed_placing")),
                abnormality_code=to_str(row.get("abnormality_code")),
            )
        )
    return tuple(records)


def _decode_first_win_info(values: Any) -> tuple[KSFirstWinInfoItem, ...]:
    records: list[KSFirstWinInfoItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row or to_str(row.get("race_key")) is None:
            continue
        records.append(
            KSFirstWinInfoItem(
                race_key=to_str(row.get("race_key")),
                num_starters=to_int(row.get("num_starters")),
                pedigree_reg_num=to_str(row.get("pedigree_reg_num")),
                horse_name=to_str(row.get("horse_name")),
            )
        )
    return tuple(records)


def _decode_recent_graded_wins(values: Any, item_cls: type[Any]) -> tuple[Any, ...]:
    records: list[Any] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            item_cls(
                race_key=to_str(row.get("race_key")),
                race_name_main=to_str(row.get("race_name_main")),
                race_short_name_10=to_str(row.get("race_short_name_10")),
                race_short_name_6=to_str(row.get("race_short_name_6")),
                race_short_name_3=to_str(row.get("race_short_name_3")),
                grade_code=to_str(row.get("grade_code")),
                num_starters=to_int(row.get("num_starters")),
                pedigree_reg_num=to_str(row.get("pedigree_reg_num")),
                horse_name=to_str(row.get("horse_name")),
            )
        )
    return tuple(records)


def _decode_performance_stats(values: Any, item_cls: type[Any]) -> tuple[Any, ...]:
    records: list[Any] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            item_cls(
                year=to_int(row.get("year")),
                flat_prize_money=to_int(row.get("flat_prize_money")),
                steeplechase_prize_money=to_int(row.get("steeplechase_prize_money")),
                flat_added_money=to_int(row.get("flat_added_money")),
                steeplechase_added_money=to_int(row.get("steeplechase_added_money")),
                flat_placing_counts=_decode_int_array(row.get("flat_placing_counts")),
                steeplechase_placing_counts=_decode_int_array(row.get("steeplechase_placing_counts")),
                sapporo_flat_placing_counts=_decode_int_array(row.get("sapporo_flat_placing_counts")),
                sapporo_steeplechase_placing_counts=_decode_int_array(row.get("sapporo_steeplechase_placing_counts")),
                hakodate_flat_placing_counts=_decode_int_array(row.get("hakodate_flat_placing_counts")),
                hakodate_steeplechase_placing_counts=_decode_int_array(row.get("hakodate_steeplechase_placing_counts")),
                fukushima_flat_placing_counts=_decode_int_array(row.get("fukushima_flat_placing_counts")),
                fukushima_steeplechase_placing_counts=_decode_int_array(
                    row.get("fukushima_steeplechase_placing_counts")
                ),
                niigata_flat_placing_counts=_decode_int_array(row.get("niigata_flat_placing_counts")),
                niigata_steeplechase_placing_counts=_decode_int_array(row.get("niigata_steeplechase_placing_counts")),
                tokyo_flat_placing_counts=_decode_int_array(row.get("tokyo_flat_placing_counts")),
                tokyo_steeplechase_placing_counts=_decode_int_array(row.get("tokyo_steeplechase_placing_counts")),
                nakayama_flat_placing_counts=_decode_int_array(row.get("nakayama_flat_placing_counts")),
                nakayama_steeplechase_placing_counts=_decode_int_array(row.get("nakayama_steeplechase_placing_counts")),
                chukyo_flat_placing_counts=_decode_int_array(row.get("chukyo_flat_placing_counts")),
                chukyo_steeplechase_placing_counts=_decode_int_array(row.get("chukyo_steeplechase_placing_counts")),
                kyoto_flat_placing_counts=_decode_int_array(row.get("kyoto_flat_placing_counts")),
                kyoto_steeplechase_placing_counts=_decode_int_array(row.get("kyoto_steeplechase_placing_counts")),
                hanshin_flat_placing_counts=_decode_int_array(row.get("hanshin_flat_placing_counts")),
                hanshin_steeplechase_placing_counts=_decode_int_array(row.get("hanshin_steeplechase_placing_counts")),
                kokura_flat_placing_counts=_decode_int_array(row.get("kokura_flat_placing_counts")),
                kokura_steeplechase_placing_counts=_decode_int_array(row.get("kokura_steeplechase_placing_counts")),
                turf_class_d_placing_counts=_decode_int_array(row.get("turf_class_d_placing_counts")),
                turf_class_e_placing_counts=_decode_int_array(row.get("turf_class_e_placing_counts")),
                turf_gt2200_placing_counts=_decode_int_array(row.get("turf_gt2200_placing_counts")),
                dirt_class_d_placing_counts=_decode_int_array(row.get("dirt_class_d_placing_counts")),
                dirt_class_e_placing_counts=_decode_int_array(row.get("dirt_class_e_placing_counts")),
                dirt_gt2200_placing_counts=_decode_int_array(row.get("dirt_gt2200_placing_counts")),
            )
        )
    return tuple(records)


def _decode_ks(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return KSRecord(
        type="KS",
        data_code=data_code,
        data_creation_date=data_creation_date,
        jockey_code=to_str(payload.get("jockey_code")),
        deregistration_flag=to_str(payload.get("deregistration_flag")),
        license_issue_date=to_date_yyyymmdd(payload.get("license_issue_date")),
        license_revoked_date=to_date_yyyymmdd(payload.get("license_revoked_date")),
        birth_date=to_date_yyyymmdd(payload.get("birth_date")),
        jockey_name=to_str(payload.get("jockey_name")),
        jockey_name_kana=to_str(payload.get("jockey_name_kana")),
        jockey_name_short=to_str(payload.get("jockey_name_short")),
        jockey_name_english=to_str(payload.get("jockey_name_english")),
        sex_code=to_str(payload.get("sex_code")),
        riding_qualification_code=to_str(payload.get("riding_qualification_code")),
        jockey_apprentice_code=to_str(payload.get("jockey_apprentice_code")),
        affiliation_code=to_str(payload.get("affiliation_code")),
        invitation_area_name=to_str(payload.get("invitation_area_name")),
        affiliated_trainer_code=to_str(payload.get("affiliated_trainer_code")),
        affiliated_trainer_name_short=to_str(payload.get("affiliated_trainer_name_short")),
        first_ride_info=_decode_first_ride_info(payload.get("first_ride_info")),
        first_win_info=_decode_first_win_info(payload.get("first_win_info")),
        recent_graded_wins=_decode_recent_graded_wins(payload.get("recent_graded_wins"), KSRecentGradedWinsItem),
        performance_stats=_decode_performance_stats(payload.get("performance_stats"), KSPerformanceStatsItem),
    )


# --- CH ---


def _decode_ch(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return CHRecord(
        type="CH",
        data_code=data_code,
        data_creation_date=data_creation_date,
        trainer_code=to_str(payload.get("trainer_code")),
        deregistration_flag=to_str(payload.get("deregistration_flag")),
        license_issue_date=to_date_yyyymmdd(payload.get("license_issue_date")),
        license_revoked_date=to_date_yyyymmdd(payload.get("license_revoked_date")),
        birth_date=to_date_yyyymmdd(payload.get("birth_date")),
        trainer_name=to_str(payload.get("trainer_name")),
        trainer_name_kana=to_str(payload.get("trainer_name_kana")),
        trainer_name_short=to_str(payload.get("trainer_name_short")),
        trainer_name_english=to_str(payload.get("trainer_name_english")),
        sex_code=to_str(payload.get("sex_code")),
        affiliation_code=to_str(payload.get("affiliation_code")),
        invitation_area_name=to_str(payload.get("invitation_area_name")),
        recent_graded_wins=_decode_recent_graded_wins(payload.get("recent_graded_wins"), CHRecentGradedWinsItem),
        performance_stats=_decode_performance_stats(payload.get("performance_stats"), CHPerformanceStatsItem),
    )


# --- BR ---


def _decode_simple_performance_stats(values: Any, item_cls: type[Any]) -> tuple[Any, ...]:
    records: list[Any] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            item_cls(
                year=to_int(row.get("year")),
                prize_money=to_int(row.get("prize_money")),
                added_money=to_int(row.get("added_money")),
                placing_counts=_decode_int_array(row.get("placing_counts")),
            )
        )
    return tuple(records)


def _decode_br(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return BRRecord(
        type="BR",
        data_code=data_code,
        data_creation_date=data_creation_date,
        breeder_code=to_str(payload.get("breeder_code")),
        breeder_name_with_corp=to_str(payload.get("breeder_name_with_corp")),
        breeder_name=to_str(payload.get("breeder_name")),
        breeder_name_kana=to_str(payload.get("breeder_name_kana")),
        breeder_name_english=to_str(payload.get("breeder_name_english")),
        address=to_str(payload.get("address")),
        performance_stats=_decode_simple_performance_stats(payload.get("performance_stats"), BRPerformanceStatsItem),
    )


# --- BN ---


def _decode_bn(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return BNRecord(
        type="BN",
        data_code=data_code,
        data_creation_date=data_creation_date,
        owner_code=to_str(payload.get("owner_code")),
        owner_name_with_corp=to_str(payload.get("owner_name_with_corp")),
        owner_name=to_str(payload.get("owner_name")),
        owner_name_kana=to_str(payload.get("owner_name_kana")),
        owner_name_english=to_str(payload.get("owner_name_english")),
        silk_colors_code=to_str(payload.get("silk_colors_code")),
        performance_stats=_decode_simple_performance_stats(payload.get("performance_stats"), BNPerformanceStatsItem),
    )


# --- RC ---


def _decode_record_holders(values: Any) -> tuple[RCRecordHoldersItem, ...]:
    records: list[RCRecordHoldersItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            RCRecordHoldersItem(
                pedigree_reg_num=to_str(row.get("pedigree_reg_num")),
                horse_name=to_str(row.get("horse_name")),
                horse_symbol_code=to_str(row.get("horse_symbol_code")),
                sex_code=to_str(row.get("sex_code")),
                trainer_code=to_str(row.get("trainer_code")),
                trainer_name=to_str(row.get("trainer_name")),
                impost_weight=to_float(row.get("impost_weight"), scale=10),
                jockey_code=to_str(row.get("jockey_code")),
                jockey_name=to_str(row.get("jockey_name")),
            )
        )
    return tuple(records)


def _decode_rc(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    meet_month, meet_day_of_month = to_month_day(payload.get("meet_date"))
    return RCRecord(
        type="RC",
        data_code=data_code,
        data_creation_date=data_creation_date,
        record_identification_code=to_str(payload.get("record_identification_code")),
        meet_year=to_int(payload.get("meet_year")),
        meet_month=meet_month,
        meet_day_of_month=meet_day_of_month,
        racecourse_code=to_str(payload.get("racecourse_code")),
        meet_round=to_int(payload.get("meet_round")),
        meet_day=to_int(payload.get("meet_day")),
        race_number=to_int(payload.get("race_number")),
        special_race_number=to_int(payload.get("special_race_number")),
        race_name_main=to_str(payload.get("race_name_main")),
        grade_code=to_str(payload.get("grade_code")),
        race_type_code=to_str(payload.get("race_type_code")),
        distance=to_int(payload.get("distance")),
        track_code=to_str(payload.get("track_code")),
        record_type_code=to_str(payload.get("record_type_code")),
        record_time=to_str(payload.get("record_time")),
        weather_code=to_str(payload.get("weather_code")),
        turf_track_condition_code=to_str(payload.get("turf_track_condition_code")),
        dirt_track_condition_code=to_str(payload.get("dirt_track_condition_code")),
        record_holders=_decode_record_holders(payload.get("record_holders")),
    )


# --- HN ---


def _decode_hn(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return HNRecord(
        type="HN",
        data_code=data_code,
        data_creation_date=data_creation_date,
        breeding_reg_num=to_str(payload.get("breeding_reg_num")),
        pedigree_reg_num=to_str(payload.get("pedigree_reg_num")),
        horse_name=to_str(payload.get("horse_name")),
        horse_name_kana=to_str(payload.get("horse_name_kana")),
        horse_name_english=to_str(payload.get("horse_name_english")),
        birth_year=to_int(payload.get("birth_year")),
        sex_code=to_str(payload.get("sex_code")),
        breed_code=to_str(payload.get("breed_code")),
        coat_color_code=to_str(payload.get("coat_color_code")),
        import_code=to_str(payload.get("import_code")),
        import_year=to_int(payload.get("import_year")),
        birthplace_name=to_str(payload.get("birthplace_name")),
        sire_breeding_reg_num=to_str(payload.get("sire_breeding_reg_num")),
        dam_breeding_reg_num=to_str(payload.get("dam_breeding_reg_num")),
    )


# --- SK ---


def _decode_sk(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    raw_pedigree = to_list(payload.get("three_gen_pedigree_breeding_reg_nums"))
    pedigree = tuple(to_str(v) or "" for v in raw_pedigree)
    return SKRecord(
        type="SK",
        data_code=data_code,
        data_creation_date=data_creation_date,
        pedigree_reg_num=to_str(payload.get("pedigree_reg_num")),
        birth_date=to_date_yyyymmdd(payload.get("birth_date")),
        sex_code=to_str(payload.get("sex_code")),
        breed_code=to_str(payload.get("breed_code")),
        coat_color_code=to_str(payload.get("coat_color_code")),
        import_code=to_str(payload.get("import_code")),
        import_year=to_int(payload.get("import_year")),
        breeder_code=to_str(payload.get("breeder_code")),
        birthplace_name=to_str(payload.get("birthplace_name")),
        three_gen_pedigree_breeding_reg_nums=pedigree,
    )


# --- BT ---


def _decode_bt(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return BTRecord(
        type="BT",
        data_code=data_code,
        data_creation_date=data_creation_date,
        breeding_reg_num=to_str(payload.get("breeding_reg_num")),
        lineage_id=to_str(payload.get("lineage_id")),
        lineage_name=to_str(payload.get("lineage_name")),
        lineage_description=to_str(payload.get("lineage_description")),
    )


# --- HC ---


def _decode_hc(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return HCRecord(
        type="HC",
        data_code=data_code,
        data_creation_date=data_creation_date,
        training_center_code=to_str(payload.get("training_center_code")),
        training_date=to_date_yyyymmdd(payload.get("training_date")),
        training_time=to_time_hhmm(payload.get("training_time")),
        pedigree_reg_num=to_str(payload.get("pedigree_reg_num")),
        total_time_4f=to_str(payload.get("total_time_4f")),
        lap_time_800_600=to_str(payload.get("lap_time_800_600")),
        total_time_3f=to_str(payload.get("total_time_3f")),
        lap_time_600_400=to_str(payload.get("lap_time_600_400")),
        total_time_2f=to_str(payload.get("total_time_2f")),
        lap_time_400_200=to_str(payload.get("lap_time_400_200")),
        lap_time_200_0=to_str(payload.get("lap_time_200_0")),
    )


# --- YS ---


def _decode_graded_race_guide(values: Any) -> tuple[YSGradedRaceGuideItem, ...]:
    records: list[YSGradedRaceGuideItem] = []
    for item in to_list(values):
        row = to_dict(item)
        if not row:
            continue
        records.append(
            YSGradedRaceGuideItem(
                special_race_number=to_int(row.get("special_race_number")),
                race_name_main=to_str(row.get("race_name_main")),
                race_short_name_10=to_str(row.get("race_short_name_10")),
                race_short_name_6=to_str(row.get("race_short_name_6")),
                race_short_name_3=to_str(row.get("race_short_name_3")),
                graded_race_round_number=to_int(row.get("graded_race_round_number")),
                grade_code=to_str(row.get("grade_code")),
                race_type_code=to_str(row.get("race_type_code")),
                race_symbol_code=to_str(row.get("race_symbol_code")),
                weight_type_code=to_str(row.get("weight_type_code")),
                distance=to_int(row.get("distance")),
                track_code=to_str(row.get("track_code")),
            )
        )
    return tuple(records)


def _decode_ys(payload: Mapping[str, Any]) -> DomainRecord:
    meet_month, meet_day_of_month = to_month_day(payload.get("meet_date"))
    return YSRecord(
        type="YS",
        data_code=to_str(payload.get("data_code")),
        data_creation_date=to_date_yyyymmdd(payload.get("data_creation_date")),
        meet_year=to_int(payload.get("meet_year")),
        meet_month=meet_month,
        meet_day_of_month=meet_day_of_month,
        racecourse_code=to_str(payload.get("racecourse_code")),
        meet_round=to_int(payload.get("meet_round")),
        meet_day=to_int(payload.get("meet_day")),
        weekday_code=to_str(payload.get("weekday_code")),
        graded_race_guide=_decode_graded_race_guide(payload.get("graded_race_guide")),
    )


# --- HS ---


def _decode_hs(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return HSRecord(
        type="HS",
        data_code=data_code,
        data_creation_date=data_creation_date,
        pedigree_reg_num=to_str(payload.get("pedigree_reg_num")),
        sire_breeding_reg_num=to_str(payload.get("sire_breeding_reg_num")),
        dam_breeding_reg_num=to_str(payload.get("dam_breeding_reg_num")),
        birth_year=to_int(payload.get("birth_year")),
        market_code=to_str(payload.get("market_code")),
        organizer_name=to_str(payload.get("organizer_name")),
        market_name=to_str(payload.get("market_name")),
        market_start_date=to_date_yyyymmdd(payload.get("market_start_date")),
        market_end_date=to_date_yyyymmdd(payload.get("market_end_date")),
        horse_age_at_trade=to_int(payload.get("horse_age_at_trade")),
        trade_price=to_int(payload.get("trade_price")),
    )


# --- HY ---


def _decode_hy(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return HYRecord(
        type="HY",
        data_code=data_code,
        data_creation_date=data_creation_date,
        pedigree_reg_num=to_str(payload.get("pedigree_reg_num")),
        horse_name=to_str(payload.get("horse_name")),
        horse_name_meaning=to_str(payload.get("horse_name_meaning")),
    )


# --- CS ---


def _decode_cs(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return CSRecord(
        type="CS",
        data_code=data_code,
        data_creation_date=data_creation_date,
        racecourse_code=to_str(payload.get("racecourse_code")),
        distance=to_int(payload.get("distance")),
        track_code=to_str(payload.get("track_code")),
        course_revision_date=to_date_yyyymmdd(payload.get("course_revision_date")),
        course_description=to_str(payload.get("course_description")),
    )


# --- WC ---


def _decode_wc(payload: Mapping[str, Any]) -> DomainRecord:
    data_code, data_creation_date = _build_header_context(payload)
    return WCRecord(
        type="WC",
        data_code=data_code,
        data_creation_date=data_creation_date,
        training_center_code=to_str(payload.get("training_center_code")),
        training_date=to_date_yyyymmdd(payload.get("training_date")),
        training_time=to_time_hhmm(payload.get("training_time")),
        pedigree_reg_num=to_str(payload.get("pedigree_reg_num")),
        course=to_str(payload.get("course")),
        track_direction=to_str(payload.get("track_direction")),
        total_time_10f=to_str(payload.get("total_time_10f")),
        lap_time_2000_1800=to_str(payload.get("lap_time_2000_1800")),
        total_time_9f=to_str(payload.get("total_time_9f")),
        lap_time_1800_1600=to_str(payload.get("lap_time_1800_1600")),
        total_time_8f=to_str(payload.get("total_time_8f")),
        lap_time_1600_1400=to_str(payload.get("lap_time_1600_1400")),
        total_time_7f=to_str(payload.get("total_time_7f")),
        lap_time_1400_1200=to_str(payload.get("lap_time_1400_1200")),
        total_time_6f=to_str(payload.get("total_time_6f")),
        lap_time_1200_1000=to_str(payload.get("lap_time_1200_1000")),
        total_time_5f=to_str(payload.get("total_time_5f")),
        lap_time_1000_800=to_str(payload.get("lap_time_1000_800")),
        total_time_4f=to_str(payload.get("total_time_4f")),
        total_time_3f=to_str(payload.get("total_time_3f")),
        total_time_2f=to_str(payload.get("total_time_2f")),
        lap_time_800_600=to_str(payload.get("lap_time_800_600")),
        lap_time_600_400=to_str(payload.get("lap_time_600_400")),
        lap_time_400_200=to_str(payload.get("lap_time_400_200")),
        lap_time_200_0=to_str(payload.get("lap_time_200_0")),
    )


# ---------------------------------------------------------------------------
# Decoder registry & public API
# ---------------------------------------------------------------------------


DEFAULT_DECODER_MAP: dict[str, DecodeFn] = {
    "AV": _decode_av,
    "BN": _decode_bn,
    "BR": _decode_br,
    "BT": _decode_bt,
    "CC": _decode_cc,
    "CH": _decode_ch,
    "CK": _decode_ck,
    "CS": _decode_cs,
    "DM": _decode_dm,
    "H1": _decode_h1,
    "H6": _decode_h6,
    "HC": _decode_hc,
    "HN": _decode_hn,
    "HR": _decode_hr,
    "HS": _decode_hs,
    "HY": _decode_hy,
    "JC": _decode_jc,
    "JG": _decode_jg,
    "KS": _decode_ks,
    "O1": _decode_o1,
    "O2": _decode_o2,
    "O3": _decode_o3,
    "O4": _decode_o4,
    "O5": _decode_o5,
    "O6": _decode_o6,
    "RA": _decode_ra,
    "RC": _decode_rc,
    "SE": _decode_se,
    "SK": _decode_sk,
    "TC": _decode_tc,
    "TK": _decode_tk,
    "TM": _decode_tm,
    "UM": _decode_um,
    "WC": _decode_wc,
    "WE": _decode_we,
    "WF": _decode_wf,
    "WH": _decode_wh,
    "YS": _decode_ys,
}


class RecordDecoder:
    """Central registry-based record decoder."""

    def __init__(
        self,
        registry: Mapping[str, DecodeFn] | None = None,
        *,
        known_record_types: set[str] | None = None,
    ) -> None:
        self._known_record_types: set[str] = (
            {normalize_record_type(record_type) for record_type in known_record_types}
            if known_record_types is not None
            else set(RECORD_TYPES)
        )
        self._registry: dict[str, DecodeFn] = {
            record_type: decoder
            for record_type, decoder in DEFAULT_DECODER_MAP.items()
            if record_type in self._known_record_types
        }
        if registry is not None:
            for record_type, decoder in registry.items():
                normalized = normalize_record_type(record_type)
                self._known_record_types.add(normalized)
                self._registry[normalized] = decoder

    @property
    def known_record_types(self) -> frozenset[str]:
        return frozenset(self._known_record_types)

    def decode(self, record_type: str, payload: Mapping[str, Any]) -> DomainRecord:
        normalized, normalized_payload = normalize_wire_record(record_type, payload)
        if normalized not in self._known_record_types:
            return UnknownRecord(type=normalized, data=normalized_payload)
        decoder = self._registry.get(normalized)
        if decoder is None:
            return UnknownRecord(type=normalized, data=normalized_payload)
        return decoder(normalized_payload)

    def decode_envelope(self, envelope: RecordEnvelope[WireRecord]) -> RecordEnvelope[DomainRecord]:
        record_type, payload = normalize_wire_record(envelope.type, envelope.record)
        domain_record = self.decode(record_type, payload)
        return RecordEnvelope(type=record_type, record=domain_record, raw=envelope.raw)


def create_record_from_data(record_data: Any, decoder: RecordDecoder | None = None) -> DomainRecord:
    """Decode a single wire row payload to domain record."""
    active_decoder = decoder or RecordDecoder()
    if not isinstance(record_data, Mapping):
        return UnknownRecord(type=UNKNOWN_RECORD_TYPE, data={})
    record_type, payload = normalize_wire_record(record_data.get("type"), record_data.get("data"))
    return active_decoder.decode(record_type, payload)


async def decode_record_envelopes(
    records: AsyncIterator[RecordEnvelope[WireRecord]],
    decoder: RecordDecoder,
) -> AsyncIterator[RecordEnvelope[DomainRecord]]:
    try:
        async for record in records:
            yield decoder.decode_envelope(record)
    finally:
        close_method = getattr(records, "aclose", None)
        if callable(close_method):
            close_result = close_method()
            if close_result is not None:
                await close_result
