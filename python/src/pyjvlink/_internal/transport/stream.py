"""Stream transformation helpers."""

from collections.abc import AsyncIterator, Mapping
from typing import Any

from pyjvlink._internal.protocol.envelope import UNKNOWN_RECORD_TYPE, normalize_wire_record
from pyjvlink._internal.protocol.models import RecordEnvelope, WireRecord


async def wire_record_envelopes(
    records: AsyncIterator[Any],
    *,
    include_raw: bool,
) -> AsyncIterator[RecordEnvelope[WireRecord]]:
    """Convert server NDJSON rows to normalized wire envelopes."""
    try:
        async for row in records:
            if not isinstance(row, Mapping):
                raw = {"type": UNKNOWN_RECORD_TYPE, "data": {}, "raw_row": row} if include_raw else None
                yield RecordEnvelope(type=UNKNOWN_RECORD_TYPE, record={}, raw=raw)
                continue

            record_type, payload = normalize_wire_record(row.get("type"), row.get("data"))
            raw = {"type": record_type, "data": payload} if include_raw else None
            yield RecordEnvelope(type=record_type, record=payload, raw=raw)
    finally:
        close_method = getattr(records, "aclose", None)
        if callable(close_method):
            close_result = close_method()
            if close_result is not None:
                await close_result
