"""CC domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class CCRecord(RaceRecordBase):
    """Course change record."""

    announcement_at: datetime | None
    after_distance: int | None
    after_track_code: str | None
    before_distance: int | None
    before_track_code: str | None
    reason_code: str | None
