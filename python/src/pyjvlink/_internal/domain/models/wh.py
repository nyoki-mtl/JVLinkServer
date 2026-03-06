"""WH domain model."""

from dataclasses import dataclass
from datetime import datetime

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class WHHorseWeightInfosItem:
    """Horse body weight details."""

    horse_number: int | None
    horse_name: str | None
    horse_weight: int | None
    weight_change_sign: str | None
    weight_change_diff: int | None


@dataclass(frozen=True, slots=True)
class WHRecord(RaceRecordBase):
    """Horse body weight record."""

    announcement_at: datetime | None
    horse_weight_infos: tuple[WHHorseWeightInfosItem, ...]
