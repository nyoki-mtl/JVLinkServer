"""Tests for JVServerConfig validation and env parsing."""

from __future__ import annotations

import pytest

from pyjvlink.errors import JVInvalidDataSpecError, JVInvalidKeyError, JVInvalidParameterError, JVValidationError
from pyjvlink.types import (
    VALID_DATASPECS_BY_OPTION,
    JVDataSpec,
    JVServerConfig,
    QueryOption,
    RaceKeyParts,
    build_race_key,
    build_race_key_short,
)


def test_env_port_must_be_integer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JVLINK_SERVER_PORT", "abc")
    with pytest.raises(JVInvalidParameterError, match="JVLINK_SERVER_PORT must be an integer"):
        JVServerConfig()


def test_port_range_validation() -> None:
    with pytest.raises(JVInvalidParameterError, match="between 1 and 65535"):
        JVServerConfig(port=0)


def test_host_must_be_string() -> None:
    with pytest.raises(JVInvalidParameterError, match="host must be a string"):
        JVServerConfig(host=None)  # type: ignore[arg-type]


def test_port_must_be_integer_direct_arg() -> None:
    with pytest.raises(JVInvalidParameterError, match="port must be an integer"):
        JVServerConfig(port="8765")  # type: ignore[arg-type]


def test_timeout_validation() -> None:
    with pytest.raises(JVInvalidParameterError, match="timeout must be > 0"):
        JVServerConfig(timeout=0)


def test_stream_timeout_validation() -> None:
    with pytest.raises(JVInvalidParameterError, match="stream_read_timeout must be > 0"):
        JVServerConfig(stream_read_timeout=0)


def test_sid_must_not_be_empty() -> None:
    with pytest.raises(JVInvalidParameterError, match="sid must not be empty"):
        JVServerConfig(sid="")


def test_sid_must_be_string() -> None:
    with pytest.raises(JVInvalidParameterError, match="sid must be a string"):
        JVServerConfig(sid=123)  # type: ignore[arg-type]


def test_sid_must_not_start_with_space() -> None:
    with pytest.raises(JVInvalidParameterError, match="must not start with a space"):
        JVServerConfig(sid=" bad")


def test_sid_must_be_64_bytes_or_less() -> None:
    with pytest.raises(JVInvalidParameterError, match="64 bytes or less"):
        JVServerConfig(sid="a" * 65)


def test_log_level_validation() -> None:
    with pytest.raises(JVInvalidParameterError, match="log_level must be one of"):
        JVServerConfig(log_level="trace")


def test_log_level_default_is_warn() -> None:
    assert JVServerConfig().log_level == "warn"


def test_log_level_is_normalized_to_lowercase() -> None:
    assert JVServerConfig(log_level="INFO").log_level == "info"


def test_auto_retry_must_be_boolean() -> None:
    with pytest.raises(JVInvalidParameterError, match="auto_retry must be a boolean"):
        JVServerConfig(auto_retry="true")  # type: ignore[arg-type]


def test_busy_retry_enabled_must_be_boolean() -> None:
    with pytest.raises(JVInvalidParameterError, match="busy_retry_enabled must be a boolean"):
        JVServerConfig(busy_retry_enabled="true")  # type: ignore[arg-type]


def test_busy_max_retries_must_be_non_negative() -> None:
    with pytest.raises(JVInvalidParameterError, match="busy_max_retries must be >= 0"):
        JVServerConfig(busy_max_retries=-1)


def test_busy_backoff_ms_must_be_non_negative() -> None:
    with pytest.raises(JVInvalidParameterError, match="busy_backoff_ms must be >= 0"):
        JVServerConfig(busy_backoff_ms=-1)


def test_option_4_includes_ming() -> None:
    assert JVDataSpec.MING in VALID_DATASPECS_BY_OPTION[4]


def test_query_option_values() -> None:
    assert QueryOption.ACCUMULATED == 1
    assert QueryOption.WEEKLY == 2
    assert QueryOption.SETUP == 3
    assert QueryOption.SETUP_NO_DIALOG == 4


def test_validation_exceptions_are_not_valueerror() -> None:
    assert issubclass(JVInvalidDataSpecError, JVValidationError)
    assert not issubclass(JVInvalidDataSpecError, ValueError)
    assert issubclass(JVInvalidParameterError, JVValidationError)
    assert not issubclass(JVInvalidParameterError, ValueError)


def test_build_race_key_short() -> None:
    key = build_race_key_short(
        RaceKeyParts(
            meet_year=2026,
            meet_month=3,
            meet_day_of_month=1,
            racecourse_code="05",
            race_number=11,
        )
    )

    assert key == "202603010511"


def test_build_race_key() -> None:
    key = build_race_key(
        RaceKeyParts(
            meet_year=2026,
            meet_month=3,
            meet_day_of_month=1,
            racecourse_code="05",
            meet_round=2,
            meet_day=1,
            race_number=11,
        )
    )

    assert key == "2026030105020111"


def test_build_race_key_requires_meet_round_and_day() -> None:
    with pytest.raises(JVInvalidKeyError, match="meet_round and meet_day are required"):
        build_race_key(
            RaceKeyParts(
                meet_year=2026,
                meet_month=3,
                meet_day_of_month=1,
                racecourse_code="05",
                race_number=11,
            )
        )
