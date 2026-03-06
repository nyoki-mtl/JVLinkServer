"""Protocol value parsing helpers."""

from collections.abc import Iterable, Mapping
from datetime import date, datetime, time
from enum import Enum
from typing import Any, TypeVar

TEnum = TypeVar("TEnum", bound=Enum)


def to_str(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def to_int(value: Any) -> int | None:
    normalized = to_str(value)
    if normalized is None:
        return None
    try:
        return int(normalized)
    except ValueError:
        return None


def to_float(value: Any, *, scale: float = 1.0) -> float | None:
    parsed = to_int(value)
    if parsed is None:
        return None
    return parsed / scale


def to_date_yyyymmdd(value: Any) -> date | None:
    normalized = to_str(value)
    if normalized is None or len(normalized) != 8 or not normalized.isdigit():
        return None
    try:
        return datetime.strptime(normalized, "%Y%m%d").date()
    except ValueError:
        return None


def to_month_day(value: Any) -> tuple[int | None, int | None]:
    normalized = to_str(value)
    if normalized is None or len(normalized) != 4 or not normalized.isdigit():
        return None, None

    month = int(normalized[:2])
    day = int(normalized[2:4])
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None, None
    return month, day


def to_time_hhmm(value: Any) -> time | None:
    normalized = to_str(value)
    if normalized is None or len(normalized) != 4 or not normalized.isdigit():
        return None
    # JV initial value "0000" means "unset" for HHMM fields.
    if normalized == "0000":
        return None
    hour = int(normalized[:2])
    minute = int(normalized[2:4])
    try:
        return time(hour=hour, minute=minute)
    except ValueError:
        return None


def to_mmddhhmm_parts(value: Any) -> tuple[int | None, int | None, int | None, int | None]:
    normalized = to_str(value)
    if normalized is None or len(normalized) != 8 or not normalized.isdigit():
        return None, None, None, None
    month = int(normalized[:2])
    day = int(normalized[2:4])
    hour = int(normalized[4:6])
    minute = int(normalized[6:8])
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None, None, None, None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None, None, None, None
    return month, day, hour, minute


def to_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def to_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, Iterable) and not isinstance(value, str | bytes | bytearray | Mapping):
        return list(value)
    return []


def to_enum(value: Any, enum_type: type[TEnum]) -> TEnum | None:
    normalized = to_str(value)
    if normalized is None:
        return None
    try:
        return enum_type(normalized)
    except ValueError:
        return None
