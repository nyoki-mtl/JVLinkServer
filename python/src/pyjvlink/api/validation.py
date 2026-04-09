"""Input normalization and validation for public API facade."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime

from pyjvlink.errors import (
    JVInvalidDataSpecError,
    JVInvalidFromTimeError,
    JVInvalidKeyError,
    JVInvalidOptionError,
    JVInvalidParameterError,
)
from pyjvlink.types import (
    DATASPEC_TO_RECORDS,
    REALTIME_DATASPECS,
    VALID_DATASPECS_BY_OPTION,
    JVDataSpec,
    QueryOption,
    RaceKeyParts,
    RealtimeKeyInput,
    StoredDataspecInput,
    build_race_key,
    build_race_key_short,
)

_OPTION_NAMES = {1: "accumulated data", 2: "weekly data", 3: "setup data", 4: "setup data (no dialog)"}
_NO_END_DATE_SPECS = frozenset({"TOKU", "DIFF", "DIFN", "HOSE", "HOSN", "HOYU", "COMM"})
_REALTIME_DATE_ONLY_DATASPECS = frozenset({JVDataSpec.SOKHO_KAISAI_BATCH, JVDataSpec.SOKHO_WIN5})
_REALTIME_RACE_ONLY_DATASPECS = frozenset(
    {
        JVDataSpec.SOKHO_RACE_RESULT,
        JVDataSpec.SOKHO_HYOSU_ALL,
        JVDataSpec.SOKHO_ODDS_ALL,
        JVDataSpec.SOKHO_ODDS_TANFUKU,
        JVDataSpec.SOKHO_ODDS_UMAREN,
        JVDataSpec.SOKHO_ODDS_WIDE,
        JVDataSpec.SOKHO_ODDS_UMATAN,
        JVDataSpec.SOKHO_ODDS_SANRENPUKU,
        JVDataSpec.SOKHO_ODDS_SANRENTAN,
        JVDataSpec.JIKEI_ODDS_TANFUKU,
        JVDataSpec.JIKEI_ODDS_UMAREN,
    }
)
_REALTIME_DATE_OR_RACE_DATASPECS = frozenset(
    {
        JVDataSpec.BATAI,
        JVDataSpec.SOKHO_DATA_MINING,
        JVDataSpec.SOKHO_RACE_UMA,
        JVDataSpec.SOKHO_DM_TAISEN,
    }
)
_REALTIME_EVENT_ONLY_DATASPECS = frozenset({JVDataSpec.SOKHO_KAISAI_SHITEI})
_EVENT_RECORD_TYPES = frozenset({"AV", "CC", "JC", "TC", "WE"})
_DATE_KEY_RE = re.compile(r"\d{8}")
_RACE_KEY_SHORT_RE = re.compile(r"\d{8}[A-Z0-9]{2}\d{2}")
_RACE_KEY_FULL_RE = re.compile(r"\d{8}[A-Z0-9]{2}\d{6}")
_EVENT_KEY_RE = re.compile(r"[A-Z0-9]{2}\d{8}[A-Z0-9]{2}\d{2}\d{14}")


@dataclass(frozen=True, slots=True)
class StoredQueryInput:
    """Normalized input for query_stored."""

    dataspec: str
    dataspecs: tuple[str, ...]
    from_datetime: str
    to_date: str | None
    record_types: list[str] | None


def normalize_datetime_arg(arg_name: str, value: str, *, end_of_day: bool = False) -> str:
    """Validate YYYYMMDD / YYYYMMDDHHMMSS and normalize to YYYYMMDDHHMMSS."""
    if not isinstance(value, str):
        raise JVInvalidFromTimeError(f"{arg_name} must be a string. Got {type(value).__name__}.")

    if len(value) == 8 and value.isdigit():
        try:
            datetime.strptime(value, "%Y%m%d")
        except ValueError as e:
            raise JVInvalidFromTimeError(
                f"Invalid {arg_name}: '{value}'. Expected a real date in YYYYMMDD format."
            ) from e
        return value + ("235959" if end_of_day else "000000")

    if len(value) == 14 and value.isdigit():
        try:
            datetime.strptime(value, "%Y%m%d%H%M%S")
        except ValueError as e:
            raise JVInvalidFromTimeError(
                f"Invalid {arg_name}: '{value}'. Expected a real datetime in YYYYMMDDHHMMSS format."
            ) from e
        return value

    raise JVInvalidFromTimeError(f"Invalid {arg_name}: '{value}'. Use YYYYMMDD or YYYYMMDDHHMMSS.")


def parse_stored_dataspecs_arg(dataspec: StoredDataspecInput) -> list[JVDataSpec]:
    """Validate query_stored dataspec."""
    chunks: list[str]
    if isinstance(dataspec, JVDataSpec):
        chunks = [dataspec.value]
    elif isinstance(dataspec, str):
        normalized = dataspec.strip().upper()
        if not normalized:
            raise JVInvalidDataSpecError("dataspec must not be empty.")
        if len(normalized) % 4 != 0:
            raise JVInvalidDataSpecError(
                f"Invalid dataspec format: '{dataspec}'. dataspec must be one or more concatenated 4-character codes."
            )
        chunks = [normalized[i : i + 4] for i in range(0, len(normalized), 4)]
    elif isinstance(dataspec, Sequence):
        if not dataspec:
            raise JVInvalidDataSpecError("dataspec must not be empty.")
        chunks = []
        for item in dataspec:
            if isinstance(item, JVDataSpec):
                chunks.append(item.value)
                continue
            if not isinstance(item, str):
                raise JVInvalidDataSpecError("dataspec sequence must contain only strings or JVDataSpec values.")

            cleaned = item.strip().upper()
            if not cleaned:
                raise JVInvalidDataSpecError("dataspec sequence must not include empty values.")
            if len(cleaned) != 4:
                raise JVInvalidDataSpecError(
                    f"Invalid dataspec item: '{item}'. Sequence items must be single 4-character dataspec codes."
                )
            chunks.append(cleaned)
    else:
        raise JVInvalidDataSpecError("dataspec must be a string, JVDataSpec, or a sequence of dataspec values.")

    parsed_specs: list[JVDataSpec] = []
    seen_specs: set[JVDataSpec] = set()
    duplicate_specs: list[str] = []
    unknown_specs: list[str] = []

    for chunk in chunks:
        try:
            parsed = JVDataSpec(chunk)
        except ValueError:
            unknown_specs.append(chunk)
            continue

        if parsed in seen_specs:
            duplicate_specs.append(parsed.value)
            continue

        seen_specs.add(parsed)
        parsed_specs.append(parsed)

    if unknown_specs:
        valid_values = ", ".join([e.value for e in JVDataSpec])
        joined_unknown = ", ".join(unknown_specs)
        raise JVInvalidDataSpecError(f"Unknown dataspec: {joined_unknown}. Valid values: {valid_values}") from None
    if duplicate_specs:
        joined_duplicates = ", ".join(dict.fromkeys(duplicate_specs))
        raise JVInvalidDataSpecError(
            f"Duplicate dataspec is not allowed: {joined_duplicates}. Remove duplicates from dataspec."
        )

    return parsed_specs


def normalize_record_types_arg(dataspecs: list[JVDataSpec], record_types: list[str] | None) -> list[str] | None:
    """Validate and normalize record_types for query_stored."""
    if record_types is None:
        return None
    if not record_types:
        raise JVInvalidParameterError("record_types must not be empty when specified.")

    allowed_record_types: set[str] = set()
    for dataspec in dataspecs:
        allowed_record_types.update(DATASPEC_TO_RECORDS.get(dataspec, ()))
    if not allowed_record_types:
        joined_dataspecs = ",".join(spec.value for spec in dataspecs)
        raise JVInvalidParameterError(f"No record type mapping is defined for dataspec '{joined_dataspecs}'.")

    normalized: list[str] = []
    for record_type in record_types:
        if not isinstance(record_type, str):
            raise JVInvalidParameterError("record_types must be a list of strings.")
        cleaned = record_type.strip().upper()
        if not cleaned:
            raise JVInvalidParameterError("record_types must not include empty values.")
        normalized.append(cleaned)

    invalid = sorted({record_type for record_type in normalized if record_type not in allowed_record_types})
    if invalid:
        valid_sorted = ", ".join(sorted(allowed_record_types))
        joined_dataspecs = ",".join(spec.value for spec in dataspecs)
        raise JVInvalidParameterError(
            f"Unsupported record_types for dataspec '{joined_dataspecs}': {', '.join(invalid)}. "
            f"Valid record_types: {valid_sorted}"
        )

    return list(dict.fromkeys(normalized))


def _normalize_realtime_key_text(dataspec: JVDataSpec, key: str | None) -> str:
    """Validate common realtime key constraints before dataspec-specific checks."""
    if key is None:
        raise JVInvalidKeyError(f"key is required for realtime dataspec '{dataspec.value}'.")
    if not isinstance(key, str):
        raise JVInvalidKeyError("key must be a string.")

    normalized = key.strip().upper()
    if not normalized:
        raise JVInvalidKeyError("key cannot be empty.")
    return normalized


def _normalize_realtime_date_key(key: str, *, original: str) -> str:
    if not _DATE_KEY_RE.fullmatch(key):
        raise JVInvalidKeyError(f"Invalid key format: '{original}'. Use YYYYMMDD.")

    try:
        datetime.strptime(key, "%Y%m%d")
    except ValueError as e:
        raise JVInvalidKeyError(f"Invalid key date: '{original}'. Expected a real date in YYYYMMDD format.") from e
    return key


def _normalize_realtime_race_key(key: str, *, original: str) -> str:
    if not (_RACE_KEY_SHORT_RE.fullmatch(key) or _RACE_KEY_FULL_RE.fullmatch(key)):
        raise JVInvalidKeyError(f"Invalid key format: '{original}'. Use YYYYMMDDJJRR or YYYYMMDDJJKKHHRR.")

    try:
        datetime.strptime(key[:8], "%Y%m%d")
    except ValueError as e:
        raise JVInvalidKeyError(f"Invalid key date: '{original}'. Expected a real date in YYYYMMDD format.") from e
    return key


def _normalize_realtime_event_key(key: str, *, original: str) -> str:
    if not _EVENT_KEY_RE.fullmatch(key):
        raise JVInvalidKeyError(f"Invalid key format: '{original}'. Use TTYYYYMMDDJJRRNNNNNNNNNNNNNN.")

    if key[:2] not in _EVENT_RECORD_TYPES:
        valid_types = ", ".join(sorted(_EVENT_RECORD_TYPES))
        raise JVInvalidKeyError(
            f"Invalid event key record type: '{original}'. Use one of the 0B16 event prefixes: {valid_types}."
        )

    try:
        datetime.strptime(key[2:10], "%Y%m%d")
        datetime.strptime(key[-14:], "%Y%m%d%H%M%S")
    except ValueError as e:
        raise JVInvalidKeyError(
            f"Invalid event key date component: '{original}'. Expected real YYYYMMDD and YYYYMMDDHHMMSS values."
        ) from e
    return key


def _coerce_realtime_key_input(key: RealtimeKeyInput | None) -> str | None:
    if key is None or isinstance(key, str):
        return key
    if isinstance(key, datetime):
        return key.strftime("%Y%m%d")
    if isinstance(key, date):
        return key.strftime("%Y%m%d")
    if isinstance(key, RaceKeyParts):
        if key.meet_round is not None and key.meet_day is not None:
            return build_race_key(key)
        return build_race_key_short(key)
    raise JVInvalidKeyError("key must be a string, date, datetime, or RaceKeyParts.")


def normalize_realtime_key_arg(dataspec: JVDataSpec, key: RealtimeKeyInput | None) -> str:
    """Validate and normalize JVRTOpen key by realtime dataspec."""
    coerced_key = _coerce_realtime_key_input(key)
    original = coerced_key if isinstance(coerced_key, str) else str(key)
    normalized = _normalize_realtime_key_text(dataspec, coerced_key)

    if dataspec in _REALTIME_DATE_ONLY_DATASPECS:
        return _normalize_realtime_date_key(normalized, original=original)

    if dataspec in _REALTIME_RACE_ONLY_DATASPECS:
        return _normalize_realtime_race_key(normalized, original=original)

    if dataspec in _REALTIME_DATE_OR_RACE_DATASPECS:
        if _DATE_KEY_RE.fullmatch(normalized):
            return _normalize_realtime_date_key(normalized, original=original)
        return _normalize_realtime_race_key(normalized, original=original)

    if dataspec in _REALTIME_EVENT_ONLY_DATASPECS:
        return _normalize_realtime_event_key(normalized, original=original)

    raise JVInvalidKeyError(f"Unsupported realtime dataspec for key validation: '{dataspec.value}'.")


def validate_stored_query_input(
    dataspec: StoredDataspecInput,
    from_datetime: str,
    option: int | QueryOption,
    *,
    to_date: str | None = None,
    record_types: list[str] | None = None,
) -> StoredQueryInput:
    """Validate and normalize inputs for query_stored/query_stored_raw."""
    if not isinstance(option, int) or isinstance(option, bool):
        raise JVInvalidOptionError(f"option must be an integer 1, 2, 3, or 4. Got {type(option).__name__}.")

    data_specs = parse_stored_dataspecs_arg(dataspec)
    concatenated_dataspec = "".join(spec.value for spec in data_specs)

    realtime_specs = [spec.value for spec in data_specs if spec in REALTIME_DATASPECS]
    if realtime_specs:
        valid_realtime_values = sorted([spec.value for spec in REALTIME_DATASPECS])
        raise JVInvalidDataSpecError(
            f"Dataspec '{','.join(realtime_specs)}' is a realtime dataspec and cannot be used with query_stored(). "
            f"Realtime dataspecs: {', '.join(valid_realtime_values)}. "
            "Use query_realtime() instead."
        )

    if option not in VALID_DATASPECS_BY_OPTION:
        raise JVInvalidOptionError(f"Invalid option: {option}. Must be 1, 2, 3, or 4.")

    valid_dataspecs = VALID_DATASPECS_BY_OPTION[option]
    unsupported_specs = [spec.value for spec in data_specs if spec not in valid_dataspecs]
    if unsupported_specs:
        valid_dataspec_values = sorted([spec.value for spec in valid_dataspecs])
        option_name = _OPTION_NAMES[option]
        raise JVInvalidOptionError(
            f"Dataspec '{','.join(unsupported_specs)}' is not supported for {option_name} (option={option}). "
            f"Valid dataspecs: {', '.join(valid_dataspec_values)}"
        )

    from_datetime_normalized = normalize_datetime_arg("from_datetime", from_datetime, end_of_day=False)

    normalized_to_date: str | None = None
    if to_date:
        range_unsupported_specs = [spec.value for spec in data_specs if spec.value in _NO_END_DATE_SPECS]
        if range_unsupported_specs:
            raise JVInvalidFromTimeError(
                f"Dataspec '{','.join(range_unsupported_specs)}' does not support end date specification. "
                f"These dataspecs only support from_datetime: {', '.join(sorted(_NO_END_DATE_SPECS))}"
            )

        normalized_to_date = normalize_datetime_arg("to_date", to_date, end_of_day=True)
        if from_datetime_normalized > normalized_to_date:
            raise JVInvalidFromTimeError(
                "Invalid date range: from_datetime "
                f"({from_datetime_normalized}) must be <= to_date ({normalized_to_date})."
            )

    normalized_record_types = normalize_record_types_arg(data_specs, record_types)
    return StoredQueryInput(
        dataspec=concatenated_dataspec,
        dataspecs=tuple(spec.value for spec in data_specs),
        from_datetime=from_datetime_normalized,
        to_date=normalized_to_date,
        record_types=normalized_record_types,
    )


def validate_realtime_query_input(dataspec: str | JVDataSpec, key: RealtimeKeyInput | None = None) -> tuple[str, str]:
    """Validate and normalize inputs for query_realtime/query_realtime_raw."""
    if not isinstance(dataspec, str):
        raise JVInvalidDataSpecError("dataspec must be a string.")

    normalized_dataspec = dataspec.strip().upper()
    if not normalized_dataspec:
        raise JVInvalidDataSpecError("dataspec must not be empty.")
    try:
        data_spec_enum = JVDataSpec(normalized_dataspec)
    except ValueError:
        raise JVInvalidDataSpecError(
            f"Unknown dataspec: '{dataspec}'. Valid values: {', '.join([e.value for e in JVDataSpec])}"
        ) from None

    if data_spec_enum not in REALTIME_DATASPECS:
        valid_realtime_values = sorted([spec.value for spec in REALTIME_DATASPECS])
        raise JVInvalidDataSpecError(
            f"Dataspec '{dataspec}' is not a valid realtime dataspec. "
            f"Valid realtime dataspecs: {', '.join(valid_realtime_values)}. "
            "Use query_stored() for stored data."
        )

    return data_spec_enum.value, normalize_realtime_key_arg(data_spec_enum, key)


def validate_retry_overrides(max_retries: int | None, retry_delay_ms: int | None) -> tuple[int | None, int | None]:
    """Validate optional per-call retry overrides."""
    if max_retries is not None and (not isinstance(max_retries, int) or isinstance(max_retries, bool)):
        raise JVInvalidParameterError(f"max_retries must be an integer >= 0, got {type(max_retries).__name__}.")
    if retry_delay_ms is not None and (not isinstance(retry_delay_ms, int) or isinstance(retry_delay_ms, bool)):
        raise JVInvalidParameterError(f"retry_delay_ms must be an integer >= 0, got {type(retry_delay_ms).__name__}.")

    if max_retries is not None and max_retries < 0:
        raise JVInvalidParameterError(f"max_retries must be >= 0, got {max_retries}.")
    if retry_delay_ms is not None and retry_delay_ms < 0:
        raise JVInvalidParameterError(f"retry_delay_ms must be >= 0, got {retry_delay_ms}.")
    return max_retries, retry_delay_ms


def validate_busy_retry_overrides(
    busy_retry_enabled: bool | None,
    busy_max_retries: int | None,
    busy_backoff_ms: int | None,
    respect_retry_after: bool | None,
) -> tuple[bool | None, int | None, int | None, bool | None]:
    """Validate optional per-call busy retry overrides."""
    if busy_retry_enabled is not None and not isinstance(busy_retry_enabled, bool):
        raise JVInvalidParameterError(f"busy_retry_enabled must be a boolean, got {type(busy_retry_enabled).__name__}.")
    if busy_max_retries is not None and (not isinstance(busy_max_retries, int) or isinstance(busy_max_retries, bool)):
        raise JVInvalidParameterError(
            f"busy_max_retries must be an integer >= 0, got {type(busy_max_retries).__name__}."
        )
    if busy_backoff_ms is not None and (not isinstance(busy_backoff_ms, int) or isinstance(busy_backoff_ms, bool)):
        raise JVInvalidParameterError(f"busy_backoff_ms must be an integer >= 0, got {type(busy_backoff_ms).__name__}.")
    if respect_retry_after is not None and not isinstance(respect_retry_after, bool):
        raise JVInvalidParameterError(
            f"respect_retry_after must be a boolean, got {type(respect_retry_after).__name__}."
        )

    if busy_max_retries is not None and busy_max_retries < 0:
        raise JVInvalidParameterError(f"busy_max_retries must be >= 0, got {busy_max_retries}.")
    if busy_backoff_ms is not None and busy_backoff_ms < 0:
        raise JVInvalidParameterError(f"busy_backoff_ms must be >= 0, got {busy_backoff_ms}.")
    return busy_retry_enabled, busy_max_retries, busy_backoff_ms, respect_retry_after


def validate_max_records(max_records: int) -> int:
    """Validate query max_records argument."""
    if not isinstance(max_records, int) or isinstance(max_records, bool):
        raise JVInvalidParameterError(f"max_records must be an integer >= -1, got {type(max_records).__name__}.")
    if max_records < -1:
        raise JVInvalidParameterError(f"max_records must be >= -1, got {max_records}.")
    return max_records


def validate_non_empty_text(name: str, value: str) -> str:
    """Validate non-empty text input."""
    if not isinstance(value, str):
        raise JVInvalidParameterError(f"{name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise JVInvalidParameterError(f"{name} cannot be empty")
    return normalized
