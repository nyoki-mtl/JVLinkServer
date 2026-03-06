"""JC domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class JCRecord(RaceRecordBase):
    """Jockey change record."""

    announcement_at: datetime | None
    horse_number: int | None
    horse_name: str | None
    after_weight_carried: int | None
    after_jockey_code: str | None
    after_jockey_name: str | None
    after_apprentice_code: str | None
    before_weight_carried: int | None
    before_jockey_code: str | None
    before_jockey_name: str | None
    before_apprentice_code: str | None
