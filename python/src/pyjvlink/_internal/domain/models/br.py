"""BR domain model."""

from dataclasses import dataclass
from datetime import date

from pyjvlink._internal.domain.models.common import SimplePerformanceStats


@dataclass(frozen=True, slots=True)
class BRPerformanceStatsItem(SimplePerformanceStats):
    """BR.performance_stats element."""


@dataclass(frozen=True, slots=True)
class BRRecord:
    """Breeder master record."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    breeder_code: str | None
    breeder_name_with_corp: str | None
    breeder_name: str | None
    breeder_name_kana: str | None
    breeder_name_english: str | None
    address: str | None
    performance_stats: tuple[BRPerformanceStatsItem, ...]
