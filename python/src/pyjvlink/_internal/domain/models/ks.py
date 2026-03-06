"""KS domain model."""

from dataclasses import dataclass
from datetime import date

from pyjvlink._internal.domain.models.common import PerformanceStats, RecentGradedWin


@dataclass(frozen=True, slots=True)
class KSFirstRideInfoItem:
    """First ride information for a jockey."""

    race_key: str | None
    num_starters: int | None
    pedigree_reg_num: str | None
    horse_name: str | None
    confirmed_placing: int | None
    abnormality_code: str | None


@dataclass(frozen=True, slots=True)
class KSFirstWinInfoItem:
    """First win information for a jockey."""

    race_key: str | None
    num_starters: int | None
    pedigree_reg_num: str | None
    horse_name: str | None


@dataclass(frozen=True, slots=True)
class KSRecentGradedWinsItem(RecentGradedWin):
    """KS.recent_graded_wins element."""


@dataclass(frozen=True, slots=True)
class KSPerformanceStatsItem(PerformanceStats):
    """KS.performance_stats element."""


@dataclass(frozen=True, slots=True)
class KSRecord:
    """Jockey master record."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    jockey_code: str | None
    deregistration_flag: str | None
    license_issue_date: date | None
    license_revoked_date: date | None
    birth_date: date | None
    jockey_name: str | None
    jockey_name_kana: str | None
    jockey_name_short: str | None
    jockey_name_english: str | None
    sex_code: str | None
    riding_qualification_code: str | None
    jockey_apprentice_code: str | None
    affiliation_code: str | None
    invitation_area_name: str | None
    affiliated_trainer_code: str | None
    affiliated_trainer_name_short: str | None
    first_ride_info: tuple[KSFirstRideInfoItem, ...]
    first_win_info: tuple[KSFirstWinInfoItem, ...]
    recent_graded_wins: tuple[KSRecentGradedWinsItem, ...]
    performance_stats: tuple[KSPerformanceStatsItem, ...]
