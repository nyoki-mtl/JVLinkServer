"""Public API result models."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Generic, TypeVar

from pyjvlink._internal.protocol.models import RecordEnvelope
from pyjvlink.api.types import RealtimeQueryMeta, StoredQueryMeta

TRecord = TypeVar("TRecord")


@dataclass(frozen=True, slots=True)
class StoredResult(Generic[TRecord]):
    """Stored query result."""

    meta: StoredQueryMeta
    records: AsyncIterator[RecordEnvelope[TRecord]]

    async def collect(self) -> list[RecordEnvelope[TRecord]]:
        """Collect all streamed envelopes into a list."""
        return [envelope async for envelope in self.records]


@dataclass(frozen=True, slots=True)
class RealtimeResult(Generic[TRecord]):
    """Realtime query result."""

    meta: RealtimeQueryMeta
    records: AsyncIterator[RecordEnvelope[TRecord]]

    async def collect(self) -> list[RecordEnvelope[TRecord]]:
        """Collect all streamed envelopes into a list."""
        return [envelope async for envelope in self.records]
