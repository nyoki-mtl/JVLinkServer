"""Tests for public error helpers."""

from pyjvlink.errors import JVNoDataError, build_error_for_code


def test_build_error_for_no_data_code_returns_jv_no_data_error() -> None:
    error = build_error_for_code(-1, "No data available")

    assert isinstance(error, JVNoDataError)
    assert error.error_code == -1
