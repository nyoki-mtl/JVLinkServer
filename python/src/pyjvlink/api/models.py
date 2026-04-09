"""Public API result models."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Generic, TypeVar

from pyjvlink._internal.protocol.models import RecordEnvelope
from pyjvlink.api.types import RealtimeQueryMeta, StoredQueryMeta

TRecord = TypeVar("TRecord")


async def _collect_batches(
    records: AsyncIterator[RecordEnvelope[TRecord]],
    size: int,
) -> AsyncIterator[list[RecordEnvelope[TRecord]]]:
    if size <= 0:
        raise ValueError(f"batch size must be > 0, got {size}.")

    batch: list[RecordEnvelope[TRecord]] = []
    async for envelope in records:
        batch.append(envelope)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


@dataclass(frozen=True, slots=True)
class StoredResult(Generic[TRecord]):
    """Stored query result."""

    meta: StoredQueryMeta
    records: AsyncIterator[RecordEnvelope[TRecord]]

    async def collect(self) -> list[RecordEnvelope[TRecord]]:
        """Collect all streamed envelopes into a list."""
        return [envelope async for envelope in self.records]

    def batches(self, size: int) -> AsyncIterator[list[RecordEnvelope[TRecord]]]:
        """Iterate over streamed envelopes in fixed-size batches."""
        return _collect_batches(self.records, size)


@dataclass(frozen=True, slots=True)
class RealtimeResult(Generic[TRecord]):
    """Realtime query result."""

    meta: RealtimeQueryMeta
    records: AsyncIterator[RecordEnvelope[TRecord]]

    async def collect(self) -> list[RecordEnvelope[TRecord]]:
        """Collect all streamed envelopes into a list."""
        return [envelope async for envelope in self.records]

    def batches(self, size: int) -> AsyncIterator[list[RecordEnvelope[TRecord]]]:
        """Iterate over streamed envelopes in fixed-size batches."""
        return _collect_batches(self.records, size)
