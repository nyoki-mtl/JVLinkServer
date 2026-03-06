"""O3 domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import RaceRecordBase
from pyjvlink._internal.protocol.enums import SaleFlag


@dataclass(frozen=True, slots=True)
class O3WideOddsItem:
    """Wide odds detail (min/max range)."""

    combination: str | None
    min_odds: float | None
    max_odds: float | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class O3Record(RaceRecordBase):
    """Odds record for wide."""

    announcement_at: datetime | None
    num_entries: int | None
    num_starters: int | None
    wide_sales_flag: SaleFlag | None
    wide_odds: tuple[O3WideOddsItem, ...]
    wide_total_votes: int | None
