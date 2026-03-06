"""HR domain model."""

from dataclasses import dataclass

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class Payback:
    """Payout detail."""

    number: str | None
    payout: int | None
    popularity_rank: int | None


@dataclass(frozen=True, slots=True)
class HRWinPaybackItem(Payback):
    """HR.win_payback element."""


@dataclass(frozen=True, slots=True)
class HRPlacePaybackItem(Payback):
    """HR.place_payback element."""


@dataclass(frozen=True, slots=True)
class HRBracketQuinellaPaybackItem(Payback):
    """HR.bracket_quinella_payback element."""


@dataclass(frozen=True, slots=True)
class HRQuinellaPaybackItem(Payback):
    """HR.quinella_payback element."""


@dataclass(frozen=True, slots=True)
class HRWidePaybackItem(Payback):
    """HR.wide_payback element."""


@dataclass(frozen=True, slots=True)
class HRExactaPaybackItem(Payback):
    """HR.exacta_payback element."""


@dataclass(frozen=True, slots=True)
class HRTrioPaybackItem(Payback):
    """HR.trio_payback element."""


@dataclass(frozen=True, slots=True)
class HRTrifectaPaybackItem(Payback):
    """HR.trifecta_payback element."""


@dataclass(frozen=True, slots=True)
class HRRecord(RaceRecordBase):
    """Payback record."""

    num_entries: int | None
    num_starters: int | None
    win_cancelled_flag: str | None
    place_cancelled_flag: str | None
    bracket_quinella_cancelled_flag: str | None
    quinella_cancelled_flag: str | None
    wide_cancelled_flag: str | None
    exacta_cancelled_flag: str | None
    trio_cancelled_flag: str | None
    trifecta_cancelled_flag: str | None
    win_special_payout_flag: str | None
    place_special_payout_flag: str | None
    bracket_quinella_special_payout_flag: str | None
    quinella_special_payout_flag: str | None
    wide_special_payout_flag: str | None
    exacta_special_payout_flag: str | None
    trio_special_payout_flag: str | None
    trifecta_special_payout_flag: str | None
    win_refund_flag: str | None
    place_refund_flag: str | None
    bracket_quinella_refund_flag: str | None
    quinella_refund_flag: str | None
    wide_refund_flag: str | None
    exacta_refund_flag: str | None
    trio_refund_flag: str | None
    trifecta_refund_flag: str | None
    refund_horse_number_info_28: str | None
    refund_bracket_info: str | None
    refund_same_bracket_info: str | None
    win_payback: tuple[HRWinPaybackItem, ...]
    place_payback: tuple[HRPlacePaybackItem, ...]
    bracket_quinella_payback: tuple[HRBracketQuinellaPaybackItem, ...]
    quinella_payback: tuple[HRQuinellaPaybackItem, ...]
    wide_payback: tuple[HRWidePaybackItem, ...]
    exacta_payback: tuple[HRExactaPaybackItem, ...]
    trio_payback: tuple[HRTrioPaybackItem, ...]
    trifecta_payback: tuple[HRTrifectaPaybackItem, ...]
