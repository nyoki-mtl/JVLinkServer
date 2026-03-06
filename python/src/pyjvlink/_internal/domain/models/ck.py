"""CK domain model."""

from dataclasses import dataclass

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class CKPerformanceStats:
    """Annual performance stats for jockey/trainer in CK."""

    year: int | None
    flat_prize_money: int | None
    obstacle_prize_money: int | None
    flat_added_money: int | None
    obstacle_added_money: int | None
    turf_placing_counts: tuple[int, ...]
    dirt_placing_counts: tuple[int, ...]
    obstacle_placing_counts: tuple[int, ...]
    turf_dist_1200_placing_counts: tuple[int, ...]
    turf_dist_1201_1400_placing_counts: tuple[int, ...]
    turf_dist_1401_1600_placing_counts: tuple[int, ...]
    turf_dist_1601_1800_placing_counts: tuple[int, ...]
    turf_dist_1801_2000_placing_counts: tuple[int, ...]
    turf_dist_2001_2200_placing_counts: tuple[int, ...]
    turf_dist_2201_2400_placing_counts: tuple[int, ...]
    turf_dist_2401_2800_placing_counts: tuple[int, ...]
    turf_dist_2801_placing_counts: tuple[int, ...]
    dirt_dist_1200_placing_counts: tuple[int, ...]
    dirt_dist_1201_1400_placing_counts: tuple[int, ...]
    dirt_dist_1401_1600_placing_counts: tuple[int, ...]
    dirt_dist_1601_1800_placing_counts: tuple[int, ...]
    dirt_dist_1801_2000_placing_counts: tuple[int, ...]
    dirt_dist_2001_2200_placing_counts: tuple[int, ...]
    dirt_dist_2201_2400_placing_counts: tuple[int, ...]
    dirt_dist_2401_2800_placing_counts: tuple[int, ...]
    dirt_dist_2801_placing_counts: tuple[int, ...]
    sapporo_turf_placing_counts: tuple[int, ...]
    hakodate_turf_placing_counts: tuple[int, ...]
    fukushima_turf_placing_counts: tuple[int, ...]
    niigata_turf_placing_counts: tuple[int, ...]
    tokyo_turf_placing_counts: tuple[int, ...]
    nakayama_turf_placing_counts: tuple[int, ...]
    chukyo_turf_placing_counts: tuple[int, ...]
    kyoto_turf_placing_counts: tuple[int, ...]
    hanshin_turf_placing_counts: tuple[int, ...]
    kokura_turf_placing_counts: tuple[int, ...]
    sapporo_dirt_placing_counts: tuple[int, ...]
    hakodate_dirt_placing_counts: tuple[int, ...]
    fukushima_dirt_placing_counts: tuple[int, ...]
    niigata_dirt_placing_counts: tuple[int, ...]
    tokyo_dirt_placing_counts: tuple[int, ...]
    nakayama_dirt_placing_counts: tuple[int, ...]
    chukyo_dirt_placing_counts: tuple[int, ...]
    kyoto_dirt_placing_counts: tuple[int, ...]
    hanshin_dirt_placing_counts: tuple[int, ...]
    kokura_dirt_placing_counts: tuple[int, ...]
    sapporo_obstacle_placing_counts: tuple[int, ...]
    hakodate_obstacle_placing_counts: tuple[int, ...]
    fukushima_obstacle_placing_counts: tuple[int, ...]
    niigata_obstacle_placing_counts: tuple[int, ...]
    tokyo_obstacle_placing_counts: tuple[int, ...]
    nakayama_obstacle_placing_counts: tuple[int, ...]
    chukyo_obstacle_placing_counts: tuple[int, ...]
    kyoto_obstacle_placing_counts: tuple[int, ...]
    hanshin_obstacle_placing_counts: tuple[int, ...]
    kokura_obstacle_placing_counts: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class CKSimplePerformanceStats:
    """Annual owner/breeder performance stats in CK."""

    year: int | None
    prize_money: int | None
    added_money: int | None
    placing_counts: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class CKJockeyPerformanceStatsItem(CKPerformanceStats):
    """CK.jockey_performance_stats element."""


@dataclass(frozen=True, slots=True)
class CKTrainerPerformanceStatsItem(CKPerformanceStats):
    """CK.trainer_performance_stats element."""


@dataclass(frozen=True, slots=True)
class CKOwnerPerformanceStatsItem(CKSimplePerformanceStats):
    """CK.owner_performance_stats element."""


@dataclass(frozen=True, slots=True)
class CKBreederPerformanceStatsItem(CKSimplePerformanceStats):
    """CK.breeder_performance_stats element."""


@dataclass(frozen=True, slots=True)
class CKRecord(RaceRecordBase):
    """Race appearance stats (placing counts) record."""

    pedigree_reg_num: str | None
    horse_name: str | None
    flat_purse_total: int | None
    obstacle_purse_total: int | None
    flat_added_money_total: int | None
    obstacle_added_money_total: int | None
    flat_earned_money_total: int | None
    obstacle_earned_money_total: int | None
    total_placing_counts: tuple[int, ...]
    jra_total_placing_counts: tuple[int, ...]
    turf_straight_placing_counts: tuple[int, ...]
    turf_right_placing_counts: tuple[int, ...]
    turf_left_placing_counts: tuple[int, ...]
    dirt_straight_placing_counts: tuple[int, ...]
    dirt_right_placing_counts: tuple[int, ...]
    dirt_left_placing_counts: tuple[int, ...]
    obstacle_placing_counts: tuple[int, ...]
    turf_good_placing_counts: tuple[int, ...]
    turf_yielding_placing_counts: tuple[int, ...]
    turf_heavy_placing_counts: tuple[int, ...]
    turf_soft_placing_counts: tuple[int, ...]
    dirt_good_placing_counts: tuple[int, ...]
    dirt_yielding_placing_counts: tuple[int, ...]
    dirt_heavy_placing_counts: tuple[int, ...]
    dirt_soft_placing_counts: tuple[int, ...]
    obstacle_good_placing_counts: tuple[int, ...]
    obstacle_yielding_placing_counts: tuple[int, ...]
    obstacle_heavy_placing_counts: tuple[int, ...]
    obstacle_soft_placing_counts: tuple[int, ...]
    running_style_counts: tuple[int, ...]
    registered_race_count: int | None
    jockey_code: str | None
    jockey_name: str | None
    jockey_performance_stats: tuple[CKJockeyPerformanceStatsItem, ...]
    trainer_code: str | None
    trainer_name: str | None
    trainer_performance_stats: tuple[CKTrainerPerformanceStatsItem, ...]
    owner_code: str | None
    owner_name_with_corp: str | None
    owner_name_individual: str | None
    owner_performance_stats: tuple[CKOwnerPerformanceStatsItem, ...]
    breeder_code: str | None
    breeder_name_with_corp: str | None
    breeder_name_individual: str | None
    breeder_performance_stats: tuple[CKBreederPerformanceStatsItem, ...]
