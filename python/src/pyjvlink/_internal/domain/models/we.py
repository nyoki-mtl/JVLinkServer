"""WE domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import MeetRecordBase


@dataclass(frozen=True, slots=True)
class WERecord(MeetRecordBase):
    """Weather and track condition record."""

    announcement_at: datetime | None
    change_identifier: str | None
    weather_code: str | None
    turf_track_condition_code: str | None
    dirt_track_condition_code: str | None
    before_weather_code: str | None
    before_turf_track_condition_code: str | None
    before_dirt_track_condition_code: str | None
