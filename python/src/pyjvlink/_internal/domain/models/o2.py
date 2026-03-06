"""O2 domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import RaceRecordBase
from pyjvlink._internal.protocol.enums import SaleFlag


@dataclass(frozen=True, slots=True)
class O2QuinellaOddsItem:
    """Quinella odds detail."""

    combination: str | None
    odds: float | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class O2Record(RaceRecordBase):
    """Odds record for quinella (umaren)."""

    announcement_at: datetime | None
    num_entries: int | None
    num_starters: int | None
    quinella_sales_flag: SaleFlag | None
    quinella_odds: tuple[O2QuinellaOddsItem, ...]
    quinella_total_votes: int | None
