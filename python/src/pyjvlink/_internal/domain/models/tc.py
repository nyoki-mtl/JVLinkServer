"""TC domain model."""

from dataclasses import dataclass
from datetime import datetime, time

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class TCRecord(RaceRecordBase):
    """Post time change record."""

    announcement_at: datetime | None
    after_post_time: time | None
    before_post_time: time | None
