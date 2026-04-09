"""Tests for CLI behavior."""

from __future__ import annotations

import argparse
import logging
from datetime import date, datetime, time

import pytest

from pyjvlink.cli import _CLI_LOGGER_HANDLER_NAME, _configure_logging, _to_jsonable, async_main, create_parser


@pytest.mark.asyncio
async def test_async_main_without_command_does_not_create_client(monkeypatch: pytest.MonkeyPatch) -> None:
    created = False

    class _UnexpectedClient:
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            _ = (args, kwargs)
            nonlocal created
            created = True

    monkeypatch.setattr("pyjvlink.cli.Client", _UnexpectedClient)

    args = argparse.Namespace(
        command=None,
        host=None,
        port=None,
        timeout=None,
        stream_read_timeout=None,
        sid=None,
    )
    result = await async_main(args)

    assert result == 1
    assert created is False


def test_to_jsonable_serializes_datetime_types() -> None:
    assert _to_jsonable(date(2026, 3, 3)) == "2026-03-03"
    assert _to_jsonable(time(12, 34, 56)) == "12:34:56"
    assert _to_jsonable(datetime(2026, 3, 3, 12, 34, 56)) == "2026-03-03T12:34:56"


def test_create_parser_supports_global_connection_options() -> None:
    parser = create_parser()
    args = parser.parse_args(
        [
            "--host",
            "192.168.10.20",
            "--port",
            "9000",
            "--timeout",
            "45",
            "--stream-read-timeout",
            "600",
            "health",
        ]
    )

    assert args.command == "health"
    assert args.host == "192.168.10.20"
    assert args.port == 9000
    assert args.timeout == 45
    assert args.stream_read_timeout == 600


def test_create_parser_supports_no_auto_retry_flag() -> None:
    parser = create_parser()
    args = parser.parse_args(["query-stored", "RACE", "20260301", "1", "--no-auto-retry"])

    assert args.command == "query-stored"
    assert args.auto_retry is False


def test_configure_logging_targets_package_logger_without_duplicate_handlers() -> None:
    package_logger = logging.getLogger("pyjvlink")
    root_logger = logging.getLogger()

    original_level = package_logger.level
    original_propagate = package_logger.propagate
    original_handlers = list(package_logger.handlers)
    original_root_level = root_logger.level

    try:
        package_logger.handlers = [
            handler for handler in package_logger.handlers if handler.get_name() != _CLI_LOGGER_HANDLER_NAME
        ]

        args = argparse.Namespace(debug=True, verbose=False)
        _configure_logging(args)
        _configure_logging(args)

        cli_handlers = [
            handler for handler in package_logger.handlers if handler.get_name() == _CLI_LOGGER_HANDLER_NAME
        ]
        assert package_logger.level == logging.DEBUG
        assert package_logger.propagate is False
        assert len(cli_handlers) == 1
        assert root_logger.level == original_root_level
    finally:
        package_logger.handlers = original_handlers
        package_logger.setLevel(original_level)
        package_logger.propagate = original_propagate
