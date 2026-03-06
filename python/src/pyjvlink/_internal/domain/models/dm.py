"""DM domain model."""

from dataclasses import dataclass
from datetime import time

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class DMMiningPredictionsItem:
    """Time-based data mining prediction for a single horse."""

    horse_number: int | None
    predicted_finish_time: str | None
    error_margin_plus: str | None
    error_margin_minus: str | None


@dataclass(frozen=True, slots=True)
class DMRecord(RaceRecordBase):
    """Time-based data mining prediction record."""

    data_creation_time: time | None
    mining_predictions: tuple[DMMiningPredictionsItem, ...]
