"""CH domain model."""

from dataclasses import dataclass
from datetime import date

from pyjvlink._internal.domain.models.common import PerformanceStats, RecentGradedWin


@dataclass(frozen=True, slots=True)
class CHRecentGradedWinsItem(RecentGradedWin):
    """CH.recent_graded_wins element."""


@dataclass(frozen=True, slots=True)
class CHPerformanceStatsItem(PerformanceStats):
    """CH.performance_stats element."""


@dataclass(frozen=True, slots=True)
class CHRecord:
    """Trainer master record."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    trainer_code: str | None
    deregistration_flag: str | None
    license_issue_date: date | None
    license_revoked_date: date | None
    birth_date: date | None
    trainer_name: str | None
    trainer_name_kana: str | None
    trainer_name_short: str | None
    trainer_name_english: str | None
    sex_code: str | None
    affiliation_code: str | None
    invitation_area_name: str | None
    recent_graded_wins: tuple[CHRecentGradedWinsItem, ...]
    performance_stats: tuple[CHPerformanceStatsItem, ...]
