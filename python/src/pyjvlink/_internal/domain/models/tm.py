"""TM domain model."""

from dataclasses import dataclass
from datetime import time

from pyjvlink._internal.domain.models.common import RaceRecordBase


@dataclass(frozen=True, slots=True)
class TMMiningPredictionsItem:
    """Matchup-based data mining prediction for a single horse."""

    horse_number: int | None
    prediction_score: float | None


@dataclass(frozen=True, slots=True)
class TMRecord(RaceRecordBase):
    """Matchup-based data mining prediction record."""

    data_creation_time: time | None
    mining_predictions: tuple[TMMiningPredictionsItem, ...]
