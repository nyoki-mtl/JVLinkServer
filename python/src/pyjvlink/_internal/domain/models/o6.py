"""O6 domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import RaceRecordBase
from pyjvlink._internal.protocol.enums import SaleFlag


@dataclass(frozen=True, slots=True)
class O6TrifectaOddsItem:
    """Trifecta odds detail."""

    combination: str | None
    odds: float | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class O6Record(RaceRecordBase):
    """Odds record for trifecta (3-ren-tan)."""

    announcement_at: datetime | None
    num_entries: int | None
    num_starters: int | None
    trifecta_sales_flag: SaleFlag | None
    trifecta_odds: tuple[O6TrifectaOddsItem, ...]
    trifecta_total_votes: int | None
