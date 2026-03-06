"""H6 domain model."""

from dataclasses import dataclass

from pyjvlink._internal.domain.models.common import RaceRecordBase
from pyjvlink._internal.protocol.enums import SaleFlag


@dataclass(frozen=True, slots=True)
class H6TrifectaVotesItem:
    """H6.trifecta_votes element."""

    combination: str | None
    votes: int | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class H6Record(RaceRecordBase):
    """Vote counts record for trifecta (3-ren-tan)."""

    num_entries: int | None
    num_starters: int | None
    trifecta_sales_flag: SaleFlag | None
    refund_horse_numbers: tuple[str, ...]
    trifecta_votes: tuple[H6TrifectaVotesItem, ...]
    trifecta_total_votes: int | None
    trifecta_refund_votes: int | None
