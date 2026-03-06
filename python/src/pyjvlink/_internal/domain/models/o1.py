"""O1 domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import RaceRecordBase
from pyjvlink._internal.protocol.enums import SaleFlag


@dataclass(frozen=True, slots=True)
class O1WinOddsItem:
    """Win odds detail."""

    horse_number: int | None
    odds: float | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class O1PlaceOddsItem:
    """Place odds detail."""

    horse_number: int | None
    min_odds: float | None
    max_odds: float | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class O1BracketQuinellaOddsItem:
    """Bracket quinella odds detail."""

    combination: str | None
    odds: float | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class O1Record(RaceRecordBase):
    """Odds record for win/place/bracket quinella."""

    announcement_at: datetime | None
    num_entries: int | None
    num_starters: int | None
    win_sales_flag: SaleFlag | None
    place_sales_flag: SaleFlag | None
    bracket_quinella_sales_flag: SaleFlag | None
    place_payout_key: int | None
    win_odds: tuple[O1WinOddsItem, ...]
    place_odds: tuple[O1PlaceOddsItem, ...]
    bracket_quinella_odds: tuple[O1BracketQuinellaOddsItem, ...]
    win_total_votes: int | None
    place_total_votes: int | None
    bracket_quinella_total_votes: int | None
