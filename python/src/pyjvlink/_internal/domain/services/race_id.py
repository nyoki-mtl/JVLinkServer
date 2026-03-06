"""Pure functions for race-derived identifiers."""

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class RaceIdParts:
    """Input values required to build race identifiers."""

    meet_year: int | None
    meet_month: int | None
    meet_day_of_month: int | None
    racecourse_code: str | None
    meet_round: int | None
    meet_day: int | None
    race_number: int | None


@dataclass(frozen=True, slots=True)
class AnnouncementParts:
    """Input values required to infer announcement datetime."""

    announcement_month: int | None
    announcement_day: int | None
    announcement_hour: int | None
    announcement_minute: int | None
    data_creation_date: date | None
    meet_year: int | None


def build_race_id(parts: RaceIdParts) -> str | None:
    if (
        parts.meet_year is None
        or parts.meet_month is None
        or parts.meet_day_of_month is None
        or parts.racecourse_code is None
        or parts.meet_round is None
        or parts.meet_day is None
        or parts.race_number is None
    ):
        return None

    racecourse_code = parts.racecourse_code.strip()
    if len(racecourse_code) != 2:
        return None

    try:
        return (
            f"{parts.meet_year:04d}{parts.meet_month:02d}{parts.meet_day_of_month:02d}"
            f"{racecourse_code}{parts.meet_round:02d}{parts.meet_day:02d}{parts.race_number:02d}"
        )
    except ValueError:
        return None


def build_race_id_short(parts: RaceIdParts) -> str | None:
    if (
        parts.meet_year is None
        or parts.meet_month is None
        or parts.meet_day_of_month is None
        or parts.racecourse_code is None
        or parts.race_number is None
    ):
        return None

    racecourse_code = parts.racecourse_code.strip()
    if len(racecourse_code) != 2:
        return None

    try:
        return (
            f"{parts.meet_year:04d}{parts.meet_month:02d}{parts.meet_day_of_month:02d}"
            f"{racecourse_code}{parts.race_number:02d}"
        )
    except ValueError:
        return None


def infer_announcement_at(parts: AnnouncementParts) -> datetime | None:
    if (
        parts.announcement_month is None
        or parts.announcement_day is None
        or parts.announcement_hour is None
        or parts.announcement_minute is None
    ):
        return None

    year: int | None = None
    if (
        parts.data_creation_date is not None
        and parts.data_creation_date.month == parts.announcement_month
        and parts.data_creation_date.day == parts.announcement_day
    ):
        year = parts.data_creation_date.year
    elif parts.meet_year is not None:
        year = parts.meet_year

    if year is None:
        return None

    try:
        return datetime(
            year=year,
            month=parts.announcement_month,
            day=parts.announcement_day,
            hour=parts.announcement_hour,
            minute=parts.announcement_minute,
        )
    except ValueError:
        return None
