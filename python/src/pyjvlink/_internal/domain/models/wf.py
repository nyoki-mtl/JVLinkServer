"""WF domain model."""

from dataclasses import dataclass

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class WFTargetRacesItem:
    """WIN5 target race info."""

    racecourse_code: str | None
    meet_round: int | None
    meet_day: int | None
    race_number: int | None


@dataclass(frozen=True, slots=True)
class WFPayoutInfoItem:
    """WIN5 payout detail."""

    combination: str | None
    payout: int | None
    winning_tickets: int | None


@dataclass(frozen=True, slots=True)
class WFRecord(RaceRecordBase):
    """WIN5 (multi-race pool) record."""

    target_races: tuple[WFTargetRacesItem, ...]
    total_tickets_sold: int | None
    valid_ticket_counts: tuple[int, ...]
    refund_flag: str | None
    void_flag: str | None
    no_winner_flag: str | None
    carryover_initial: int | None
    carryover_remaining: int | None
    payout_info: tuple[WFPayoutInfoItem, ...]
