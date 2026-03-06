"""Protocol layer models."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

TRecord = TypeVar("TRecord")
WireRecord = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class UnknownRecord:
    """Fallback model for unknown record types."""

    type: str
    data: dict[str, Any]


@dataclass(frozen=True, slots=True)
class RecordEnvelope(Generic[TRecord]):
    """Normalized record envelope for NDJSON stream rows."""

    type: str
    record: TRecord
    raw: dict[str, Any] | None = None
