"""Tests for public error helpers."""

from pyjvlink.errors import JVBusyError, JVNoDataError, JVUnavailableError, build_error_for_code


def test_build_error_for_no_data_code_returns_jv_no_data_error() -> None:
    error = build_error_for_code(-1, "No data available")

    assert isinstance(error, JVNoDataError)
    assert error.error_code == -1


def test_build_error_for_busy_code_returns_jv_busy_error_with_retry_after() -> None:
    error = build_error_for_code(-202, "JV-Link session is busy", retry_after=1)

    assert isinstance(error, JVBusyError)
    assert error.error_code == -202
    assert error.retry_after == 1


def test_build_error_for_busy_code_preserves_context() -> None:
    error = build_error_for_code(
        -202,
        "JV-Link session is busy",
        retry_after=1,
        busy_context={
            "operation": "query_stored",
            "path": "/query/stored",
            "request_id": "req-5",
            "started_at": 1711111111,
            "elapsed_ms": 2500,
            "dataspec": "RACE",
        },
    )

    assert isinstance(error, JVBusyError)
    assert error.operation == "query_stored"
    assert error.path == "/query/stored"
    assert error.request_id == "req-5"
    assert error.started_at == 1711111111
    assert error.elapsed_ms == 2500
    assert error.dataspec == "RACE"


def test_build_error_for_unavailable_code_returns_jv_unavailable_error() -> None:
    error = build_error_for_code(-50301, "JV-Link wrapper is not operational")

    assert isinstance(error, JVUnavailableError)
    assert error.error_code == -50301
