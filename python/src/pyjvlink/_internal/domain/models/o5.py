"""O5 domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import RaceRecordBase
from pyjvlink._internal.protocol.enums import SaleFlag


@dataclass(frozen=True, slots=True)
class O5TrioOddsItem:
    """Trio odds detail."""

    combination: str | None
    odds: float | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class O5Record(RaceRecordBase):
    """Odds record for trio (3-ren-puku)."""

    announcement_at: datetime | None
    num_entries: int | None
    num_starters: int | None
    trio_sales_flag: SaleFlag | None
    trio_odds: tuple[O5TrioOddsItem, ...]
    trio_total_votes: int | None
