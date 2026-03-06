"""BN domain model."""

from dataclasses import dataclass
from datetime import date

from pyjvlink._internal.domain.models.common import SimplePerformanceStats


@dataclass(frozen=True, slots=True)
class BNPerformanceStatsItem(SimplePerformanceStats):
    """BN.performance_stats element."""


@dataclass(frozen=True, slots=True)
class BNRecord:
    """Owner master record."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    owner_code: str | None
    owner_name_with_corp: str | None
    owner_name: str | None
    owner_name_kana: str | None
    owner_name_english: str | None
    silk_colors_code: str | None
    performance_stats: tuple[BNPerformanceStatsItem, ...]
