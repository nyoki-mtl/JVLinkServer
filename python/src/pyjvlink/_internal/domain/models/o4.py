"""O4 domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import RaceRecordBase
from pyjvlink._internal.protocol.enums import SaleFlag


@dataclass(frozen=True, slots=True)
class O4ExactaOddsItem:
    """Exacta odds detail."""

    combination: str | None
    odds: float | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class O4Record(RaceRecordBase):
    """Odds record for exacta (umatan)."""

    announcement_at: datetime | None
    num_entries: int | None
    num_starters: int | None
    exacta_sales_flag: SaleFlag | None
    exacta_odds: tuple[O4ExactaOddsItem, ...]
    exacta_total_votes: int | None
