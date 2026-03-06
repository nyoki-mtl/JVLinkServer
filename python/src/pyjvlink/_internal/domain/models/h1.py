"""H1 domain model."""

from dataclasses import dataclass

from pyjvlink._internal.domain.models.common import RaceRecordBase
from pyjvlink._internal.protocol.enums import SaleFlag


@dataclass(frozen=True, slots=True)
class H1WinVotesItem:
    """H1.win_votes element."""

    horse_number: int | None
    votes: int | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class H1PlaceVotesItem:
    """H1.place_votes element."""

    horse_number: int | None
    votes: int | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class H1BracketQuinellaVotesItem:
    """H1.bracket_quinella_votes element."""

    combination: str | None
    votes: int | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class H1QuinellaVotesItem:
    """H1.quinella_votes element."""

    combination: str | None
    votes: int | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class H1WideVotesItem:
    """H1.wide_votes element."""

    combination: str | None
    votes: int | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class H1ExactaVotesItem:
    """H1.exacta_votes element."""

    combination: str | None
    votes: int | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class H1TrioVotesItem:
    """H1.trio_votes element."""

    combination: str | None
    votes: int | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class H1Record(RaceRecordBase):
    """Vote counts record (win/place/bracket-quinella/quinella/wide/exacta/trio)."""

    num_entries: int | None
    num_starters: int | None
    win_sales_flag: SaleFlag | None
    place_sales_flag: SaleFlag | None
    bracket_quinella_sales_flag: SaleFlag | None
    quinella_sales_flag: SaleFlag | None
    wide_sales_flag: SaleFlag | None
    exacta_sales_flag: SaleFlag | None
    trio_sales_flag: SaleFlag | None
    place_payout_key: int | None
    refund_horse_numbers: tuple[str, ...]
    refund_bracket_numbers: tuple[str, ...]
    refund_same_bracket: tuple[str, ...]
    win_votes: tuple[H1WinVotesItem, ...]
    place_votes: tuple[H1PlaceVotesItem, ...]
    bracket_quinella_votes: tuple[H1BracketQuinellaVotesItem, ...]
    quinella_votes: tuple[H1QuinellaVotesItem, ...]
    wide_votes: tuple[H1WideVotesItem, ...]
    exacta_votes: tuple[H1ExactaVotesItem, ...]
    trio_votes: tuple[H1TrioVotesItem, ...]
    win_total_votes: int | None
    place_total_votes: int | None
    bracket_quinella_total_votes: int | None
    quinella_total_votes: int | None
    wide_total_votes: int | None
    exacta_total_votes: int | None
    trio_total_votes: int | None
    win_refund_votes: int | None
    place_refund_votes: int | None
    bracket_quinella_refund_votes: int | None
    quinella_refund_votes: int | None
    wide_refund_votes: int | None
    exacta_refund_votes: int | None
    trio_refund_votes: int | None
