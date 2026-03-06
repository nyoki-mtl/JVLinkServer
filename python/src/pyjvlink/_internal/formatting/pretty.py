"""Pretty formatter driven by generated schema metadata."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import asdict, is_dataclass
from typing import Any

from pyjvlink._internal.protocol.generated.formatter_meta import FORMATTER_META


def _to_mapping(record: Any) -> dict[str, Any]:
    if isinstance(record, Mapping):
        return dict(record)
    if is_dataclass(record):
        return asdict(record)
    data = getattr(record, "__dict__", None)
    if isinstance(data, dict):
        return dict(data)
    return {}


def _detect_record_type(record_type: str | None, payload: Mapping[str, Any]) -> str:
    if record_type:
        return record_type.upper()
    value = payload.get("type")
    if isinstance(value, str) and value.strip():
        return value.strip().upper()
    return "UNKNOWN"


def _render_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, str | int | float | bool):
        return str(value)
    return json.dumps(value, ensure_ascii=False, default=str)


def format_record(record: Any, *, record_type: str | None = None) -> str:
    """Format one record with schema metadata order and labels."""

    payload = _to_mapping(record)
    detected_type = _detect_record_type(record_type, payload)
    meta = FORMATTER_META.get(detected_type)
    if meta is None:
        return json.dumps(payload, ensure_ascii=False, default=str, indent=2)

    lines: list[str] = [f"[{detected_type}]"]
    for field_meta in meta:
        if field_meta.name not in payload:
            continue
        value = payload[field_meta.name]
        if value is None:
            continue
        suffix = f" ({field_meta.unit})" if field_meta.unit else ""
        lines.append(f"{field_meta.label}{suffix}: {_render_value(value)}")
    return "\n".join(lines)


def format_records(records: Iterable[Any], *, record_type: str | None = None) -> str:
    """Format multiple records and join with blank line."""

    return "\n\n".join(format_record(record, record_type=record_type) for record in records)
