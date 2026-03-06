"""Helpers for normalizing record envelope payloads."""

from typing import Any

from pyjvlink._internal.protocol.validators import to_dict, to_str

UNKNOWN_RECORD_TYPE = "UNKNOWN"


def normalize_record_type(value: Any) -> str:
    normalized = to_str(value)
    if normalized is None:
        return UNKNOWN_RECORD_TYPE
    return normalized.upper()


def normalize_wire_record(record_type: Any, payload: Any) -> tuple[str, dict[str, Any]]:
    return normalize_record_type(record_type), to_dict(payload)
