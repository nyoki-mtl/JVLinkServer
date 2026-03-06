"""Tests for record decoder."""

from datetime import date, time

import pytest

from pyjvlink._internal.codecs.record_decoder import (
    RecordDecoder,
    create_record_from_data,
    decode_record_envelopes,
)
from pyjvlink._internal.protocol.generated.registry import RECORD_TYPES
from pyjvlink._internal.protocol.models import RecordEnvelope
from pyjvlink.records import (
    AVRecord,
    BNRecord,
    BRRecord,
    BTRecord,
    CCRecord,
    CHRecord,
    CKRecord,
    CSRecord,
    DMRecord,
    H1Record,
    H6Record,
    HCRecord,
    HNRecord,
    HRRecord,
    HSRecord,
    HYRecord,
    JCRecord,
    JGRecord,
    KSRecord,
    O1Record,
    O2Record,
    O3Record,
    O4Record,
    O5Record,
    O6Record,
    RARecord,
    RCRecord,
    SERecord,
    SKRecord,
    TCRecord,
    TKRecord,
    TMRecord,
    UMRecord,
    UnknownRecord,
    WCRecord,
    WERecord,
    WFRecord,
    WHRecord,
    YSRecord,
)


class _ClosableEnvelopeStream:
    def __init__(self, envelopes: list[RecordEnvelope[dict]]) -> None:
        self._envelopes = envelopes
        self._index = 0
        self.closed = False

    def __aiter__(self) -> "_ClosableEnvelopeStream":
        return self

    async def __anext__(self) -> RecordEnvelope[dict]:
        if self._index >= len(self._envelopes):
            raise StopAsyncIteration
        envelope = self._envelopes[self._index]
        self._index += 1
        return envelope

    async def aclose(self) -> None:
        self.closed = True


_RACE_PAYLOAD = {
    "data_code": "1",
    "data_creation_date": "20260301",
    "meet_year": "2026",
    "meet_date": "0301",
    "racecourse_code": "05",
    "meet_round": "02",
    "meet_day": "01",
    "race_number": "11",
}


# ---------------------------------------------------------------------------
# Race records (5 original + 10 from 0003 pack)
# ---------------------------------------------------------------------------


def test_decode_ra() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "RA",
        {
            **_RACE_PAYLOAD,
            "race_name_main": "弥生賞",
            "distance": "2000",
            "track_code": "11",
            "post_time": "1545",
            "corner_passing_order": [
                {
                    "corner": "1",
                    "lap_count": "2",
                    "passing_order": "08-07-06",
                }
            ],
        },
    )
    assert isinstance(record, RARecord)
    assert record.race_id == "2026030105020111"
    assert record.race_name_main == "弥生賞"
    assert len(record.corner_passing_order) == 1
    assert record.corner_passing_order[0].corner == 1
    assert record.corner_passing_order[0].lap_count == 2
    assert record.corner_passing_order[0].passing_order == "08-07-06"


def test_decode_se() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "SE",
        {
            **_RACE_PAYLOAD,
            "horse_number": "08",
            "pedigree_reg_num": "2019100001",
            "horse_name": "テストホース",
            "carrying_weight": "550",
            "before_carrying_weight": "548",
            "win_odds": "0123",
            "finish_order": "01",
            "confirmed_placing": "01",
            "opponent_horses": [
                {
                    "pedigree_reg_num": "2018100001",
                    "horse_name": "ライバルホース",
                }
            ],
        },
    )
    assert isinstance(record, SERecord)
    assert record.horse_number == 8
    assert record.confirmed_placing == 1
    assert record.carrying_weight == 55.0
    assert record.before_carrying_weight == 54.8
    assert record.win_odds == 12.3
    assert len(record.opponent_horses) == 1
    assert record.opponent_horses[0].pedigree_reg_num == "2018100001"
    assert record.opponent_horses[0].horse_name == "ライバルホース"


def test_decode_hr() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "HR",
        {
            **_RACE_PAYLOAD,
            "num_entries": "18",
            "num_starters": "16",
            "win_cancelled_flag": "0",
            "place_special_payout_flag": "1",
            "trifecta_refund_flag": "0",
            "refund_horse_number_info_28": "01020304050607080910111213141516",
            "refund_bracket_info": "0102030405060708",
            "refund_same_bracket_info": "0",
            "win_payback": [{"number": "08", "payout": "000000520", "popularity_rank": "02"}],
            "place_payback": [{"number": "08", "payout": "000000190", "popularity_rank": "02"}],
            "bracket_quinella_payback": [{"number": "12", "payout": "000000870", "popularity_rank": "03"}],
            "quinella_payback": [{"number": "0812", "payout": "000001420", "popularity_rank": "05"}],
            "wide_payback": [{"number": "0812", "payout": "000000540", "popularity_rank": "04"}],
            "exacta_payback": [{"number": "0812", "payout": "000002340", "popularity_rank": "09"}],
            "trio_payback": [{"number": "081204", "payout": "000004560", "popularity_rank": "12"}],
            "trifecta_payback": [{"number": "081204", "payout": "000102300", "popularity_rank": "34"}],
        },
    )
    assert isinstance(record, HRRecord)
    assert record.win_payback[0].number == "08"
    assert record.bracket_quinella_payback[0].payout == 870
    assert record.wide_payback[0].number == "0812"
    assert record.exacta_payback[0].popularity_rank == 9
    assert record.trio_payback[0].payout == 4560
    assert record.trifecta_payback[0].payout == 102300
    assert record.win_cancelled_flag == "0"
    assert record.place_special_payout_flag == "1"
    assert record.refund_bracket_info == "0102030405060708"


def test_decode_wh() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "WH",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03010930",
            "horse_weight_infos": [
                {
                    "horse_number": "08",
                    "horse_name": "テストホース",
                    "horse_weight": "486",
                    "weight_change_sign": "+",
                    "weight_change_diff": "004",
                }
            ],
        },
    )
    assert isinstance(record, WHRecord)
    assert record.announcement_at is not None
    assert record.horse_weight_infos[0].horse_weight == 486


def test_decode_o1() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "O1",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03010930",
            "num_entries": "18",
            "num_starters": "16",
            "win_sales_flag": "7",
            "place_sales_flag": "7",
            "bracket_quinella_sales_flag": "7",
            "place_payout_key": "3",
            "win_odds": [{"horse_number": "08", "odds": "0123", "popularity_rank": "02"}],
            "place_odds": [{"horse_number": "08", "min_odds": "0102", "max_odds": "0144", "popularity_rank": "02"}],
            "bracket_quinella_odds": [{"combination": "12", "odds": "0234", "popularity_rank": "12"}],
            "win_total_votes": "00000012345",
            "place_total_votes": "00000054321",
            "bracket_quinella_total_votes": "00000033333",
        },
    )
    assert isinstance(record, O1Record)
    assert record.win_odds[0].odds == 12.3
    assert record.win_total_votes == 12345


def test_decode_tk() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "TK",
        {
            **_RACE_PAYLOAD,
            "race_name_main": "日本ダービー",
            "grade_code": "1",
            "race_type_code": "11",
            "distance": "2400",
            "track_code": "11",
            "handicap_announcement_date": "20260303",
            "num_entries": "020",
            "entry_horses": [
                {
                    "serial_number": "001",
                    "pedigree_reg_num": "2023100001",
                    "horse_name": "テスト馬",
                    "sex_code": "1",
                    "trainer_code": "01001",
                    "trainer_short_name": "テスト",
                    "impost_weight": "570",
                }
            ],
        },
    )
    assert isinstance(record, TKRecord)
    assert record.race_name_main == "日本ダービー"
    assert record.handicap_announcement_date == date(2026, 3, 3)
    assert record.num_entries == 20
    assert record.entry_horses[0].pedigree_reg_num == "2023100001"
    assert record.entry_horses[0].impost_weight == 570


def test_decode_h1() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "H1",
        {
            **_RACE_PAYLOAD,
            "num_entries": "18",
            "num_starters": "16",
            "win_sales_flag": "7",
            "place_sales_flag": "7",
            "bracket_quinella_sales_flag": "7",
            "quinella_sales_flag": "7",
            "wide_sales_flag": "7",
            "exacta_sales_flag": "7",
            "trio_sales_flag": "7",
            "win_votes": [{"horse_number": "01", "votes": "00000001234", "popularity_rank": "03"}],
            "place_votes": [{"horse_number": "01", "votes": "00000002345", "popularity_rank": "02"}],
            "bracket_quinella_votes": [{"combination": "12", "votes": "00000003456", "popularity_rank": "01"}],
            "quinella_votes": [{"combination": "0102", "votes": "00000004567", "popularity_rank": "010"}],
            "wide_votes": [{"combination": "0102", "votes": "00000005678", "popularity_rank": "015"}],
            "exacta_votes": [{"combination": "0102", "votes": "00000006789", "popularity_rank": "020"}],
            "trio_votes": [{"combination": "010203", "votes": "00000007890", "popularity_rank": "030"}],
            "win_total_votes": "00000100000",
            "place_total_votes": "00000200000",
            "bracket_quinella_total_votes": "00000300000",
            "quinella_total_votes": "00000400000",
            "wide_total_votes": "00000500000",
            "exacta_total_votes": "00000600000",
            "trio_total_votes": "00000700000",
        },
    )
    assert isinstance(record, H1Record)
    assert record.win_votes[0].horse_number == 1
    assert record.win_votes[0].votes == 1234
    assert record.quinella_votes[0].combination == "0102"
    assert record.win_total_votes == 100000
    assert record.trio_total_votes == 700000


def test_decode_h6() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "H6",
        {
            **_RACE_PAYLOAD,
            "num_entries": "18",
            "num_starters": "16",
            "trifecta_sales_flag": "7",
            "trifecta_votes": [{"combination": "010203", "votes": "00000012345", "popularity_rank": "0001"}],
            "trifecta_total_votes": "00000999999",
        },
    )
    assert isinstance(record, H6Record)
    assert record.trifecta_votes[0].combination == "010203"
    assert record.trifecta_votes[0].votes == 12345
    assert record.trifecta_total_votes == 999999


def test_decode_o2() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "O2",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03010930",
            "num_entries": "18",
            "num_starters": "16",
            "quinella_sales_flag": "7",
            "quinella_odds": [{"combination": "0108", "odds": "001234", "popularity_rank": "005"}],
            "quinella_total_votes": "00000012345",
        },
    )
    assert isinstance(record, O2Record)
    assert record.quinella_odds[0].combination == "0108"
    assert record.quinella_odds[0].odds == 123.4
    assert record.quinella_total_votes == 12345


def test_decode_o3() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "O3",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03010930",
            "num_entries": "18",
            "num_starters": "16",
            "wide_sales_flag": "7",
            "wide_odds": [{"combination": "0108", "min_odds": "00123", "max_odds": "00456", "popularity_rank": "005"}],
            "wide_total_votes": "00000012345",
        },
    )
    assert isinstance(record, O3Record)
    assert record.wide_odds[0].min_odds == 12.3
    assert record.wide_odds[0].max_odds == 45.6
    assert record.wide_total_votes == 12345


def test_decode_o4() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "O4",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03010930",
            "num_entries": "18",
            "num_starters": "16",
            "exacta_sales_flag": "7",
            "exacta_odds": [{"combination": "0801", "odds": "005678", "popularity_rank": "010"}],
            "exacta_total_votes": "00000054321",
        },
    )
    assert isinstance(record, O4Record)
    assert record.exacta_odds[0].combination == "0801"
    assert record.exacta_odds[0].odds == 567.8
    assert record.exacta_total_votes == 54321


def test_decode_o5() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "O5",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03010930",
            "num_entries": "18",
            "num_starters": "16",
            "trio_sales_flag": "7",
            "trio_odds": [{"combination": "010208", "odds": "012345", "popularity_rank": "100"}],
            "trio_total_votes": "00000099999",
        },
    )
    assert isinstance(record, O5Record)
    assert record.trio_odds[0].combination == "010208"
    assert record.trio_odds[0].odds == 1234.5
    assert record.trio_total_votes == 99999


def test_decode_o6() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "O6",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03010930",
            "num_entries": "18",
            "num_starters": "16",
            "trifecta_sales_flag": "7",
            "trifecta_odds": [{"combination": "080102", "odds": "0123456", "popularity_rank": "0001"}],
            "trifecta_total_votes": "00000088888",
        },
    )
    assert isinstance(record, O6Record)
    assert record.trifecta_odds[0].combination == "080102"
    assert record.trifecta_odds[0].odds == 12345.6
    assert record.trifecta_total_votes == 88888


def test_decode_wf() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "WF",
        {
            **_RACE_PAYLOAD,
            "target_races": [
                {"racecourse_code": "05", "meet_round": "02", "meet_day": "01", "race_number": "09"},
                {"racecourse_code": "06", "meet_round": "03", "meet_day": "02", "race_number": "10"},
            ],
            "total_tickets_sold": "00000050000",
            "refund_flag": "0",
            "void_flag": "0",
            "no_winner_flag": "0",
            "carryover_initial": "000000000000000",
            "carryover_remaining": "000000000000000",
            "payout_info": [{"combination": "0102030405", "payout": "012345678", "winning_tickets": "0000000001"}],
        },
    )
    assert isinstance(record, WFRecord)
    assert len(record.target_races) == 2
    assert record.target_races[0].racecourse_code == "05"
    assert record.target_races[0].race_number == 9
    assert record.total_tickets_sold == 50000
    assert record.payout_info[0].payout == 12345678


def test_decode_jg() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "JG",
        {
            **_RACE_PAYLOAD,
            "pedigree_reg_num": "2023100005",
            "horse_name": "除外馬",
            "entry_order": "001",
            "entry_code": "2",
            "exclusion_code": "1",
        },
    )
    assert isinstance(record, JGRecord)
    assert record.pedigree_reg_num == "2023100005"
    assert record.horse_name == "除外馬"
    assert record.entry_order == 1
    assert record.entry_code == "2"
    assert record.exclusion_code == "1"


# ---------------------------------------------------------------------------
# Race records with mining predictions (0005 pack)
# ---------------------------------------------------------------------------


def test_decode_dm() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "DM",
        {
            **_RACE_PAYLOAD,
            "data_creation_time": "0930",
            "mining_predictions": [
                {
                    "horse_number": "01",
                    "predicted_finish_time": "15850",
                    "error_margin_plus": "0120",
                    "error_margin_minus": "0150",
                },
                {
                    "horse_number": "02",
                    "predicted_finish_time": "15920",
                    "error_margin_plus": "0100",
                    "error_margin_minus": "0130",
                },
            ],
        },
    )
    assert isinstance(record, DMRecord)
    assert record.race_id == "2026030105020111"
    assert record.data_creation_time == time(9, 30)
    assert len(record.mining_predictions) == 2
    assert record.mining_predictions[0].horse_number == 1
    assert record.mining_predictions[0].predicted_finish_time == "15850"


def test_decode_tm() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "TM",
        {
            **_RACE_PAYLOAD,
            "data_creation_time": "1015",
            "mining_predictions": [
                {"horse_number": "01", "prediction_score": "0856"},
                {"horse_number": "02", "prediction_score": "0723"},
            ],
        },
    )
    assert isinstance(record, TMRecord)
    assert record.race_id == "2026030105020111"
    assert record.data_creation_time == time(10, 15)
    assert len(record.mining_predictions) == 2
    assert record.mining_predictions[0].horse_number == 1
    assert record.mining_predictions[0].prediction_score == 85.6


def test_decode_dm_time_zero_maps_to_none() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "DM",
        {
            **_RACE_PAYLOAD,
            "data_creation_time": "0000",
            "mining_predictions": [],
        },
    )
    assert isinstance(record, DMRecord)
    assert record.data_creation_time is None


def test_decode_ck() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "CK",
        {
            **_RACE_PAYLOAD,
            "pedigree_reg_num": "2019100001",
            "horse_name": "テストホース",
            "flat_purse_total": "000123456",
            "obstacle_purse_total": "000000000",
            "flat_added_money_total": "000000321",
            "obstacle_added_money_total": "000000654",
            "flat_earned_money_total": "000000987",
            "obstacle_earned_money_total": "000000111",
            "total_placing_counts": ["003", "002", "001", "001", "000", "005"],
            "jra_total_placing_counts": ["003", "002", "001", "001", "000", "005"],
            "turf_right_placing_counts": ["001", "000", "000", "000", "000", "001"],
            "dirt_left_placing_counts": ["000", "001", "000", "000", "000", "001"],
            "running_style_counts": ["001", "002", "003", "004", "005"],
            "registered_race_count": "012",
            "jockey_code": "01234",
            "jockey_name": "テスト騎手",
            "jockey_performance_stats": [
                {
                    "year": "2026",
                    "flat_prize_money": "0000001234",
                    "obstacle_prize_money": "0000000020",
                    "flat_added_money": "0000000100",
                    "obstacle_added_money": "0000000005",
                    "turf_placing_counts": ["001", "002", "003", "004", "005", "006", "007", "008", "009", "010"],
                    "dirt_dist_1200_placing_counts": ["011", "012", "013", "014", "015", "016", "017", "018"],
                    "tokyo_turf_placing_counts": ["001", "000", "001", "000", "000", "002"],
                    "kokura_obstacle_placing_counts": ["000", "001", "000", "000", "000", "000"],
                }
            ],
            "trainer_code": "05678",
            "trainer_name": "テスト調教師",
            "trainer_performance_stats": [
                {
                    "year": "2025",
                    "flat_prize_money": "0000002222",
                    "turf_placing_counts": ["002", "001", "000", "000", "000", "003"],
                }
            ],
            "owner_code": "100001",
            "owner_name_with_corp": "テストオーナー株式会社",
            "owner_name_individual": "テストオーナー",
            "owner_performance_stats": [
                {
                    "year": "2026",
                    "prize_money": "0000012345",
                    "added_money": "0000000456",
                    "placing_counts": [
                        "010",
                        "009",
                        "008",
                        "007",
                        "006",
                        "005",
                        "004",
                        "003",
                        "002",
                        "001",
                        "000",
                        "011",
                    ],
                }
            ],
            "breeder_code": "200001",
            "breeder_name_with_corp": "テストブリーダー株式会社",
            "breeder_name_individual": "テストブリーダー",
            "breeder_performance_stats": [
                {
                    "year": "2024",
                    "prize_money": "0000003333",
                    "added_money": "0000000012",
                    "placing_counts": [
                        "001",
                        "001",
                        "001",
                        "001",
                        "001",
                        "001",
                        "001",
                        "001",
                        "001",
                        "001",
                        "001",
                        "001",
                    ],
                }
            ],
        },
    )
    assert isinstance(record, CKRecord)
    assert record.race_id == "2026030105020111"
    assert record.pedigree_reg_num == "2019100001"
    assert record.flat_purse_total == 123456
    assert record.flat_added_money_total == 321
    assert record.flat_earned_money_total == 987
    assert record.total_placing_counts == (3, 2, 1, 1, 0, 5)
    assert record.turf_right_placing_counts == (1, 0, 0, 0, 0, 1)
    assert record.running_style_counts == (1, 2, 3, 4, 5)
    assert record.registered_race_count == 12
    assert record.jockey_code == "01234"
    assert len(record.jockey_performance_stats) == 1
    assert record.jockey_performance_stats[0].flat_prize_money == 1234
    assert record.jockey_performance_stats[0].dirt_dist_1200_placing_counts == (11, 12, 13, 14, 15, 16, 17, 18)
    assert record.jockey_performance_stats[0].tokyo_turf_placing_counts == (1, 0, 1, 0, 0, 2)
    assert len(record.trainer_performance_stats) == 1
    assert record.trainer_performance_stats[0].year == 2025
    assert record.trainer_performance_stats[0].turf_placing_counts == (2, 1, 0, 0, 0, 3)
    assert len(record.owner_performance_stats) == 1
    assert record.owner_performance_stats[0].added_money == 456
    assert record.owner_performance_stats[0].placing_counts[-1] == 11
    assert record.owner_code == "100001"
    assert record.owner_name_with_corp == "テストオーナー株式会社"
    assert len(record.breeder_performance_stats) == 1
    assert record.breeder_performance_stats[0].year == 2024
    assert record.breeder_performance_stats[0].placing_counts == (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    assert record.breeder_code == "200001"
    assert record.breeder_name_individual == "テストブリーダー"


# ---------------------------------------------------------------------------
# Realtime change records (0006 pack)
# ---------------------------------------------------------------------------


def test_decode_we() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "WE",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03011000",
            "change_identifier": "2",
            "weather_code": "2",
            "turf_track_condition_code": "1",
            "dirt_track_condition_code": "1",
            "before_weather_code": "1",
            "before_turf_track_condition_code": "0",
            "before_dirt_track_condition_code": "0",
        },
    )
    assert isinstance(record, WERecord)
    assert record.announcement_at is not None
    assert record.announcement_at.month == 3
    assert record.announcement_at.day == 1
    assert record.announcement_at.hour == 10
    assert record.announcement_at.minute == 0
    assert record.change_identifier == "2"
    assert record.weather_code == "2"
    assert record.turf_track_condition_code == "1"
    assert record.before_weather_code == "1"


def test_decode_av() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "AV",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03010845",
            "horse_number": "03",
            "horse_name": "テストホース",
            "exclusion_reason_code": "001",
        },
    )
    assert isinstance(record, AVRecord)
    assert record.announcement_at is not None
    assert record.announcement_at.hour == 8
    assert record.announcement_at.minute == 45
    assert record.horse_number == 3
    assert record.horse_name == "テストホース"
    assert record.exclusion_reason_code == "001"


def test_decode_jc() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "JC",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03010900",
            "horse_number": "05",
            "horse_name": "テストホース",
            "after_weight_carried": "550",
            "after_jockey_code": "01234",
            "after_jockey_name": "変更後騎手",
            "after_apprentice_code": "0",
            "before_weight_carried": "540",
            "before_jockey_code": "05678",
            "before_jockey_name": "変更前騎手",
            "before_apprentice_code": "1",
        },
    )
    assert isinstance(record, JCRecord)
    assert record.announcement_at is not None
    assert record.horse_number == 5
    assert record.after_weight_carried == 550
    assert record.after_jockey_code == "01234"
    assert record.after_jockey_name == "変更後騎手"
    assert record.before_weight_carried == 540
    assert record.before_jockey_code == "05678"
    assert record.before_jockey_name == "変更前騎手"
    assert record.before_apprentice_code == "1"


def test_decode_tc() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "TC",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03011030",
            "after_post_time": "1600",
            "before_post_time": "1545",
        },
    )
    assert isinstance(record, TCRecord)
    assert record.announcement_at is not None
    assert record.announcement_at.hour == 10
    assert record.announcement_at.minute == 30
    assert record.after_post_time == time(16, 0)
    assert record.before_post_time == time(15, 45)


def test_decode_cc() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "CC",
        {
            **_RACE_PAYLOAD,
            "announcement_datetime": "03011100",
            "after_distance": "1800",
            "after_track_code": "23",
            "before_distance": "2000",
            "before_track_code": "11",
            "reason_code": "1",
        },
    )
    assert isinstance(record, CCRecord)
    assert record.announcement_at is not None
    assert record.announcement_at.hour == 11
    assert record.after_distance == 1800
    assert record.after_track_code == "23"
    assert record.before_distance == 2000
    assert record.before_track_code == "11"
    assert record.reason_code == "1"


# ---------------------------------------------------------------------------
# Master-core records (0004 pack)
# ---------------------------------------------------------------------------


def test_decode_um() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "UM",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "pedigree_reg_num": "2019100001",
            "deregistration_flag": "0",
            "registration_date": "20190401",
            "deregistration_date": "00000000",
            "horse_name": "テストホース",
            "horse_name_kana": "ﾃｽﾄﾎｰｽ",
            "horse_name_english": "TEST HORSE",
            "jra_facility_flag": "0",
            "horse_symbol_code": "01",
            "sex_code": "1",
            "breed_code": "0101",
            "coat_color_code": "03",
            "birth_date": "20190415",
            "affiliation_code": "2",
            "trainer_code": "01234",
            "trainer_name_short": "テスト調",
            "invitation_area_name": "北海道",
            "owner_code": "012345",
            "owner_name": "テスト馬主",
            "breeder_code": "01234567",
            "breeder_name": "テスト生産者",
            "birthplace_name": "日高",
            "flat_prize_money_total": "000001234",
            "steeplechase_prize_money_total": "000000000",
            "flat_added_money_total": "000000100",
            "steeplechase_added_money_total": "000000000",
            "flat_earnings_total": "000001500",
            "steeplechase_earnings_total": "000000000",
            "overall_placing_counts": ["010", "002", "001", "001", "000", "014"],
            "central_placing_counts": ["008", "002", "001", "001", "000", "012"],
            "turf_short_placing_counts": ["001", "001", "000", "000", "000", "002"],
            "dirt_long_placing_counts": ["000", "001", "000", "000", "000", "001"],
            "running_style_counts": ["002", "003", "004", "005", "006"],
            "registered_race_count": "014",
            "pedigree_3gen": [
                {
                    "breeding_reg_num": "0000001111",
                    "horse_name": "父馬",
                },
                {
                    "breeding_reg_num": "0000002222",
                    "horse_name": "母馬",
                },
            ],
        },
    )
    assert isinstance(record, UMRecord)
    assert record.pedigree_reg_num == "2019100001"
    assert record.horse_name == "テストホース"
    assert record.horse_name_english == "TEST HORSE"
    assert record.sex_code == "1"
    assert record.breed_code == "0101"
    assert record.registration_date == date(2019, 4, 1)
    assert record.owner_name == "テスト馬主"
    assert record.flat_prize_money_total == 1234
    assert record.overall_placing_counts == (10, 2, 1, 1, 0, 14)
    assert record.running_style_counts == (2, 3, 4, 5, 6)
    assert record.registered_race_count == 14
    assert len(record.pedigree_3gen) == 2
    assert record.pedigree_3gen[0].breeding_reg_num == "0000001111"
    assert record.pedigree_3gen[1].horse_name == "母馬"


def test_decode_ks() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "KS",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "jockey_code": "01234",
            "jockey_name": "テスト騎手",
            "jockey_name_short": "テスト",
            "birth_date": "19900101",
            "license_issue_date": "20100301",
            "license_revoked_date": "00000000",
            "deregistration_flag": "0",
            "affiliation_code": "1",
            "first_ride_info": [
                {
                    "race_key": "2026030105010101",
                    "num_starters": "16",
                    "pedigree_reg_num": "2019100001",
                    "horse_name": "初騎乗馬",
                    "confirmed_placing": "05",
                    "abnormality_code": "0",
                }
            ],
            "first_win_info": [
                {
                    "race_key": "2026030205010202",
                    "num_starters": "16",
                    "pedigree_reg_num": "2019100002",
                    "horse_name": "初勝利馬",
                }
            ],
            "recent_graded_wins": [
                {
                    "race_key": "2026030305010303",
                    "race_name_main": "重賞A",
                    "race_short_name_10": "重賞A10",
                    "race_short_name_6": "重賞A6",
                    "race_short_name_3": "重A3",
                    "grade_code": "1",
                    "num_starters": "18",
                    "pedigree_reg_num": "2019100003",
                    "horse_name": "重賞勝利馬",
                }
            ],
            "performance_stats": [
                {
                    "year": "2026",
                    "flat_prize_money": "0000123456",
                    "steeplechase_prize_money": "0000001200",
                    "flat_added_money": "0000000300",
                    "steeplechase_added_money": "0000000100",
                    "flat_placing_counts": ["000001", "000001", "000000", "000000", "000000", "000000"],
                    "steeplechase_placing_counts": ["000000", "000000", "000000", "000000", "000000", "000000"],
                    "tokyo_flat_placing_counts": ["000003", "000001", "000000", "000000", "000000", "000000"],
                    "dirt_gt2200_placing_counts": ["000000", "000000", "000000", "000000", "000000", "000010"],
                }
            ],
        },
    )
    assert isinstance(record, KSRecord)
    assert record.jockey_code == "01234"
    assert record.jockey_name == "テスト騎手"
    assert record.deregistration_flag == "0"
    assert len(record.first_ride_info) == 1
    assert record.first_ride_info[0].horse_name == "初騎乗馬"
    assert len(record.first_win_info) == 1
    assert record.first_win_info[0].race_key == "2026030205010202"
    assert len(record.recent_graded_wins) == 1
    assert record.recent_graded_wins[0].race_name_main == "重賞A"
    assert len(record.performance_stats) == 1
    assert record.performance_stats[0].year == 2026
    assert record.performance_stats[0].flat_prize_money == 123456
    assert record.performance_stats[0].flat_placing_counts == (1, 1, 0, 0, 0, 0)
    assert record.performance_stats[0].tokyo_flat_placing_counts == (3, 1, 0, 0, 0, 0)


def test_decode_ks_skips_blank_first_ride_and_first_win_items() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "KS",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "jockey_code": "01234",
            "first_ride_info": [
                {
                    "race_key": "2026030105010101",
                    "num_starters": "16",
                    "pedigree_reg_num": "2019100001",
                    "horse_name": "初騎乗馬",
                    "confirmed_placing": "05",
                    "abnormality_code": "0",
                },
                {
                    "race_key": "                ",
                    "num_starters": "  ",
                    "pedigree_reg_num": "          ",
                    "horse_name": "                                    ",
                    "confirmed_placing": "  ",
                    "abnormality_code": " ",
                },
            ],
            "first_win_info": [
                {
                    "race_key": "2026030205010202",
                    "num_starters": "16",
                    "pedigree_reg_num": "2019100002",
                    "horse_name": "初勝利馬",
                },
                {
                    "race_key": "                ",
                    "num_starters": "  ",
                    "pedigree_reg_num": "          ",
                    "horse_name": "                                    ",
                },
            ],
        },
    )
    assert isinstance(record, KSRecord)
    assert len(record.first_ride_info) == 1
    assert record.first_ride_info[0].race_key == "2026030105010101"
    assert len(record.first_win_info) == 1
    assert record.first_win_info[0].race_key == "2026030205010202"


def test_decode_ch() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "CH",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "trainer_code": "01234",
            "trainer_name": "テスト調教師",
            "trainer_name_short": "テスト",
            "license_issue_date": "20050401",
            "license_revoked_date": "00000000",
            "deregistration_flag": "0",
            "affiliation_code": "1",
            "recent_graded_wins": [
                {
                    "race_key": "2026022805011101",
                    "race_name_main": "重賞B",
                    "race_short_name_10": "重賞B10",
                    "race_short_name_6": "重賞B6",
                    "race_short_name_3": "重B3",
                    "grade_code": "2",
                    "num_starters": "16",
                    "pedigree_reg_num": "2019100101",
                    "horse_name": "勝利馬B",
                }
            ],
            "performance_stats": [
                {
                    "year": "2026",
                    "flat_prize_money": "0000222222",
                    "steeplechase_prize_money": "0000003300",
                    "flat_added_money": "0000000400",
                    "steeplechase_added_money": "0000000200",
                    "flat_placing_counts": ["000002", "000001", "000000", "000000", "000000", "000000"],
                    "steeplechase_placing_counts": ["000000", "000000", "000000", "000000", "000000", "000001"],
                    "hanshin_flat_placing_counts": ["000002", "000001", "000000", "000000", "000000", "000000"],
                }
            ],
        },
    )
    assert isinstance(record, CHRecord)
    assert record.trainer_code == "01234"
    assert record.trainer_name == "テスト調教師"
    assert record.affiliation_code == "1"
    assert len(record.recent_graded_wins) == 1
    assert record.recent_graded_wins[0].horse_name == "勝利馬B"
    assert len(record.performance_stats) == 1
    assert record.performance_stats[0].flat_prize_money == 222222
    assert record.performance_stats[0].hanshin_flat_placing_counts == (2, 1, 0, 0, 0, 0)


def test_decode_br() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "BR",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "breeder_code": "01234567",
            "breeder_name": "テスト牧場",
            "address": "北海道",
            "performance_stats": [
                {
                    "year": "2026",
                    "prize_money": "0001234500",
                    "added_money": "0000004500",
                    "placing_counts": ["000001", "000002", "000003", "000004", "000005", "000006"],
                }
            ],
        },
    )
    assert isinstance(record, BRRecord)
    assert record.breeder_code == "01234567"
    assert record.breeder_name == "テスト牧場"
    assert record.address == "北海道"
    assert len(record.performance_stats) == 1
    assert record.performance_stats[0].year == 2026
    assert record.performance_stats[0].prize_money == 1234500
    assert record.performance_stats[0].placing_counts == (1, 2, 3, 4, 5, 6)


def test_decode_bn() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "BN",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "owner_code": "012345",
            "owner_name": "テスト馬主",
            "owner_name_kana": "ﾃｽﾄﾊﾞﾇｼ",
            "silk_colors_code": "水色，赤山形一本輪",
            "performance_stats": [
                {
                    "year": "2026",
                    "prize_money": "0000234500",
                    "added_money": "0000005500",
                    "placing_counts": ["000011", "000012", "000013", "000014", "000015", "000016"],
                }
            ],
        },
    )
    assert isinstance(record, BNRecord)
    assert record.owner_code == "012345"
    assert record.owner_name == "テスト馬主"
    assert record.owner_name_kana == "ﾃｽﾄﾊﾞﾇｼ"
    assert record.silk_colors_code == "水色，赤山形一本輪"
    assert len(record.performance_stats) == 1
    assert record.performance_stats[0].added_money == 5500
    assert record.performance_stats[0].placing_counts == (11, 12, 13, 14, 15, 16)


def test_decode_rc() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "RC",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "record_identification_code": "1",
            "race_name_main": "テスト競走",
            "distance": "2000",
            "track_code": "11",
            "record_time": "1585",
            "weather_code": "1",
            "turf_track_condition_code": "1",
            "dirt_track_condition_code": "0",
            "record_holders": [
                {
                    "pedigree_reg_num": "2019101001",
                    "horse_name": "レコードホース",
                    "horse_symbol_code": "00",
                    "sex_code": "1",
                    "trainer_code": "12345",
                    "trainer_name": "調教師A",
                    "impost_weight": "570",
                    "jockey_code": "54321",
                    "jockey_name": "騎手A",
                }
            ],
        },
    )
    assert isinstance(record, RCRecord)
    assert record.record_identification_code == "1"
    assert record.distance == 2000
    assert record.record_time == "1585"
    assert len(record.record_holders) == 1
    assert record.record_holders[0].horse_name == "レコードホース"
    assert record.record_holders[0].impost_weight == 57.0


# ---------------------------------------------------------------------------
# Master-extended records (0005 pack)
# ---------------------------------------------------------------------------


def test_decode_hn() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "HN",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "breeding_reg_num": "0000012345",
            "pedigree_reg_num": "2015100001",
            "horse_name": "テスト繁殖馬",
            "birth_year": "2010",
            "sex_code": "2",
            "sire_breeding_reg_num": "0000054321",
            "dam_breeding_reg_num": "0000067890",
        },
    )
    assert isinstance(record, HNRecord)
    assert record.breeding_reg_num == "0000012345"
    assert record.horse_name == "テスト繁殖馬"
    assert record.birth_year == 2010
    assert record.sex_code == "2"


def test_decode_sk() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "SK",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "pedigree_reg_num": "2019100001",
            "birth_date": "20190415",
            "sex_code": "1",
            "breeder_code": "01234567",
            "birthplace_name": "北海道",
            "three_gen_pedigree_breeding_reg_nums": [
                "0000000001",
                "0000000002",
                "0000000003",
                "0000000004",
            ],
        },
    )
    assert isinstance(record, SKRecord)
    assert record.pedigree_reg_num == "2019100001"
    assert record.sex_code == "1"
    assert len(record.three_gen_pedigree_breeding_reg_nums) == 4
    assert record.three_gen_pedigree_breeding_reg_nums[0] == "0000000001"


def test_decode_bt() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "BT",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "breeding_reg_num": "0000012345",
            "lineage_id": "010203040506070809101112",
            "lineage_name": "サンデーサイレンス",
        },
    )
    assert isinstance(record, BTRecord)
    assert record.breeding_reg_num == "0000012345"
    assert record.lineage_name == "サンデーサイレンス"


# ---------------------------------------------------------------------------
# Supplemental records (0007 pack)
# ---------------------------------------------------------------------------


def test_decode_hc() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "HC",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "training_center_code": "0",
            "training_date": "20260228",
            "training_time": "0630",
            "pedigree_reg_num": "2022100123",
            "total_time_4f": "0543",
            "lap_time_800_600": "143",
            "total_time_3f": "0400",
            "lap_time_600_400": "137",
            "total_time_2f": "0263",
            "lap_time_400_200": "132",
            "lap_time_200_0": "131",
        },
    )
    assert isinstance(record, HCRecord)
    assert record.type == "HC"
    assert record.training_center_code == "0"
    assert record.training_date == date(2026, 2, 28)
    assert record.training_time == time(6, 30)
    assert record.pedigree_reg_num == "2022100123"
    assert record.total_time_4f == "0543"
    assert record.lap_time_200_0 == "131"


def test_decode_ys() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "YS",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "meet_year": "2026",
            "meet_date": "0301",
            "racecourse_code": "05",
            "meet_round": "02",
            "meet_day": "01",
            "weekday_code": "0",
            "graded_race_guide": [
                {
                    "special_race_number": "0123",
                    "race_name_main": "弥生賞",
                    "grade_code": "2",
                    "distance": "2000",
                    "track_code": "11",
                }
            ],
        },
    )
    assert isinstance(record, YSRecord)
    assert record.type == "YS"
    assert record.meet_year == 2026
    assert record.meet_month == 3
    assert record.meet_day_of_month == 1
    assert record.racecourse_code == "05"
    assert record.meet_round == 2
    assert record.meet_day == 1
    assert record.weekday_code == "0"
    assert len(record.graded_race_guide) == 1
    assert record.graded_race_guide[0].race_name_main == "弥生賞"
    assert record.graded_race_guide[0].distance == 2000


def test_decode_hs() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "HS",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "pedigree_reg_num": "2022100123",
            "birth_year": "2022",
            "market_code": "001234",
            "market_name": "セレクトセール",
            "market_start_date": "20230710",
            "market_end_date": "20230711",
            "horse_age_at_trade": "1",
            "trade_price": "0050000000",
        },
    )
    assert isinstance(record, HSRecord)
    assert record.type == "HS"
    assert record.pedigree_reg_num == "2022100123"
    assert record.birth_year == 2022
    assert record.market_name == "セレクトセール"
    assert record.market_start_date == date(2023, 7, 10)
    assert record.horse_age_at_trade == 1
    assert record.trade_price == 50000000


def test_decode_hy() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "HY",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "pedigree_reg_num": "2022100123",
            "horse_name": "テストホース",
            "horse_name_meaning": "テスト用の馬名",
        },
    )
    assert isinstance(record, HYRecord)
    assert record.type == "HY"
    assert record.pedigree_reg_num == "2022100123"
    assert record.horse_name == "テストホース"
    assert record.horse_name_meaning == "テスト用の馬名"


def test_decode_cs() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "CS",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "racecourse_code": "05",
            "distance": "2000",
            "track_code": "11",
            "course_revision_date": "20200101",
            "course_description": "コースの説明文",
        },
    )
    assert isinstance(record, CSRecord)
    assert record.type == "CS"
    assert record.racecourse_code == "05"
    assert record.distance == 2000
    assert record.track_code == "11"
    assert record.course_revision_date == date(2020, 1, 1)
    assert record.course_description == "コースの説明文"


def test_decode_wc() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "WC",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "training_center_code": "1",
            "training_date": "20260228",
            "training_time": "0700",
            "pedigree_reg_num": "2022100123",
            "course": "0",
            "track_direction": "0",
            "total_time_4f": "0543",
            "total_time_3f": "0400",
            "total_time_2f": "0263",
            "lap_time_200_0": "131",
        },
    )
    assert isinstance(record, WCRecord)
    assert record.type == "WC"
    assert record.training_center_code == "1"
    assert record.training_date == date(2026, 2, 28)
    assert record.training_time == time(7, 0)
    assert record.pedigree_reg_num == "2022100123"
    assert record.course == "0"
    assert record.track_direction == "0"
    assert record.total_time_4f == "0543"
    assert record.lap_time_200_0 == "131"


# ---------------------------------------------------------------------------
# General decoder tests
# ---------------------------------------------------------------------------


def test_decode_unknown_record() -> None:
    decoder = RecordDecoder()
    record = decoder.decode("ZZ", {"foo": "bar"})
    assert isinstance(record, UnknownRecord)
    assert record.type == "ZZ"


def test_decoder_uses_generated_known_record_types() -> None:
    decoder = RecordDecoder()
    assert decoder.known_record_types == RECORD_TYPES


def test_create_record_from_data_decodes_domain_record() -> None:
    record = create_record_from_data(
        {
            "type": "ra",
            "data": {
                "data_code": "1",
                "data_creation_date": "20260301",
                "meet_year": "2026",
                "meet_date": "0301",
                "racecourse_code": "05",
                "meet_round": "02",
                "meet_day": "01",
                "race_number": "11",
                "race_name_main": "弥生賞",
                "distance": "2000",
                "track_code": "11",
                "post_time": "1545",
            },
        }
    )
    assert isinstance(record, RARecord)


def test_create_record_from_data_handles_non_mapping() -> None:
    record = create_record_from_data(["not", "mapping"])
    assert isinstance(record, UnknownRecord)
    assert record.type == "UNKNOWN"
    assert record.data == {}


@pytest.mark.asyncio
async def test_decode_record_envelopes_closes_source_when_closed_early() -> None:
    source = _ClosableEnvelopeStream(
        [
            RecordEnvelope(
                type="RA",
                record={
                    **_RACE_PAYLOAD,
                    "race_name_main": "弥生賞",
                    "distance": "2000",
                    "track_code": "11",
                    "post_time": "1545",
                },
                raw=None,
            )
        ]
    )
    decoder = RecordDecoder()

    records = decode_record_envelopes(source, decoder)
    first = await records.__anext__()

    assert isinstance(first.record, RARecord)

    await records.aclose()
    assert source.closed is True
