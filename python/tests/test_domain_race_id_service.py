"""Tests for domain race_id services."""

from datetime import date, datetime

from pyjvlink._internal.domain.services import (
    AnnouncementParts,
    RaceIdParts,
    build_race_id,
    build_race_id_short,
    infer_announcement_at,
)


def test_build_race_id() -> None:
    parts = RaceIdParts(
        meet_year=2026,
        meet_month=3,
        meet_day_of_month=1,
        racecourse_code="05",
        meet_round=2,
        meet_day=1,
        race_number=11,
    )
    assert build_race_id(parts) == "2026030105020111"


def test_build_race_id_short() -> None:
    parts = RaceIdParts(
        meet_year=2026,
        meet_month=3,
        meet_day_of_month=1,
        racecourse_code="05",
        meet_round=2,
        meet_day=1,
        race_number=11,
    )
    assert build_race_id_short(parts) == "202603010511"


def test_infer_announcement_at_prefers_data_creation_date() -> None:
    parts = AnnouncementParts(
        announcement_month=3,
        announcement_day=2,
        announcement_hour=10,
        announcement_minute=30,
        data_creation_date=date(2024, 3, 2),
        meet_year=2026,
    )
    assert infer_announcement_at(parts) == datetime(2024, 3, 2, 10, 30)


def test_infer_announcement_at_falls_back_to_meet_year() -> None:
    parts = AnnouncementParts(
        announcement_month=3,
        announcement_day=1,
        announcement_hour=9,
        announcement_minute=45,
        data_creation_date=date(2024, 2, 28),
        meet_year=2026,
    )
    assert infer_announcement_at(parts) == datetime(2026, 3, 1, 9, 45)
