"""AV domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class AVRecord(RaceRecordBase):
    """Scratch / exclusion record."""

    announcement_at: datetime | None
    horse_number: int | None
    horse_name: str | None
    exclusion_reason_code: str | None
