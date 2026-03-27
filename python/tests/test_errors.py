"""Tests for public error helpers."""

from pyjvlink.errors import JVBusyError, JVNoDataError, build_error_for_code


def test_build_error_for_no_data_code_returns_jv_no_data_error() -> None:
    error = build_error_for_code(-1, "No data available")

    assert isinstance(error, JVNoDataError)
    assert error.error_code == -1


def test_build_error_for_busy_code_returns_jv_busy_error_with_retry_after() -> None:
    error = build_error_for_code(-202, "JV-Link session is busy", retry_after=1)

    assert isinstance(error, JVBusyError)
    assert error.error_code == -202
    assert error.retry_after == 1
