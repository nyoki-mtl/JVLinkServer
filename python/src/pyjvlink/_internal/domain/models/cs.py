"""CS domain model."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class CSRecord:
    """Course info record (コース情報)."""

    type: str
    data_code: str | None
    data_creation_date: date | None
    racecourse_code: str | None
    distance: int | None
    track_code: str | None
    course_revision_date: date | None
    course_description: str | None
