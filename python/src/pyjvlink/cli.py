#!/usr/bin/env python3
"""PyJVLink command line interface."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, time
from enum import Enum
from typing import Any

from pyjvlink import Client, JVServerConfig
from pyjvlink.errors import JVConnectionError, JVLinkError, JVValidationError

_CLI_LOGGER_HANDLER_NAME = "pyjvlink_cli_stderr"
_CLI_LOGGER_FORMAT = "%(levelname)s %(name)s: %(message)s"


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="pyjvlink",
        description="PyJVLink Command Line Interface",
        epilog="""Examples:
  # Check server health
  pyjvlink health

  # Get stored race data from 2024/04/01
  pyjvlink query-stored RACE 20240401 1

  # Get stored data with filters
  pyjvlink query-stored RACE 20240401 1 --record-types RA SE --max-records 100

  # Get realtime odds data
  pyjvlink query-realtime 0B12 --key 202401070511
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--host", help="JVLinkServer host (default: JVLINK_SERVER_HOST or 127.0.0.1)")
    parser.add_argument("--port", type=int, help="JVLinkServer port (default: JVLINK_SERVER_PORT or 8765)")
    parser.add_argument("--timeout", type=int, help="HTTP timeout seconds (default: JVLINK_HTTP_TIMEOUT or 60)")
    parser.add_argument(
        "--stream-read-timeout",
        type=int,
        help="Streaming read timeout seconds (default: JVLINK_STREAM_READ_TIMEOUT or 300)",
    )
    parser.add_argument("--sid", help="Software ID for JVInit (default: JVLINK_SID or UNKNOWN)")
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output (INFO level)")
    verbosity.add_argument("--debug", action="store_true", help="Enable debug output (DEBUG level)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("health", help="Check server health")
    subparsers.add_parser("version", help="Get server version")
    subparsers.add_parser("session", help="Show current single-session state")
    subparsers.add_parser("session-reset", help="Reset the current single-session state")

    stored_parser = subparsers.add_parser("query-stored", help="Query JV-Link stored data")
    stored_parser.add_argument("dataspec", help="Data specification (e.g., RACE, TOKU)")
    stored_parser.add_argument("from_datetime", help="Start datetime (YYYYMMDDHHMMSS or YYYYMMDD)")
    stored_parser.add_argument(
        "option",
        type=int,
        help="Query option (1: accumulated, 2: weekly, 3: setup, 4: setup-no-dialog)",
    )
    stored_parser.add_argument("--max-records", type=int, default=-1, help="Maximum records to retrieve (-1 for all)")
    stored_parser.add_argument("--to-date", help="End datetime (YYYYMMDDHHMMSS or YYYYMMDD)")
    stored_parser.add_argument("--record-types", nargs="+", help="Filter by record types (e.g., RA SE HR)")
    retry_mode = stored_parser.add_mutually_exclusive_group()
    retry_mode.add_argument("--auto-retry", dest="auto_retry", action="store_true", help="Enable auto-retry")
    retry_mode.add_argument("--no-auto-retry", dest="auto_retry", action="store_false", help="Disable auto-retry")
    stored_parser.set_defaults(auto_retry=None)
    stored_parser.add_argument("--max-retries", type=int, help="Maximum retry count")
    stored_parser.add_argument("--retry-delay-ms", type=int, help="Retry delay in milliseconds")
    busy_retry_mode = stored_parser.add_mutually_exclusive_group()
    busy_retry_mode.add_argument(
        "--busy-retry",
        dest="busy_retry_enabled",
        action="store_true",
        help="Enable automatic retry when the session is busy",
    )
    busy_retry_mode.add_argument(
        "--no-busy-retry",
        dest="busy_retry_enabled",
        action="store_false",
        help="Disable automatic retry when the session is busy",
    )
    stored_parser.set_defaults(busy_retry_enabled=None)
    stored_parser.add_argument("--busy-max-retries", type=int, help="Maximum busy retry count")
    stored_parser.add_argument("--busy-backoff-ms", type=int, help="Busy retry backoff in milliseconds")
    retry_after_mode = stored_parser.add_mutually_exclusive_group()
    retry_after_mode.add_argument(
        "--respect-retry-after",
        dest="respect_retry_after",
        action="store_true",
        help="Use Retry-After header when retrying busy responses",
    )
    retry_after_mode.add_argument(
        "--ignore-retry-after",
        dest="respect_retry_after",
        action="store_false",
        help="Ignore Retry-After header and use --busy-backoff-ms",
    )
    stored_parser.set_defaults(respect_retry_after=None)
    stored_parser.add_argument("--format", choices=["json", "raw"], default="json", help="Output format")

    realtime_parser = subparsers.add_parser("query-realtime", help="Query JV-Link realtime data")
    realtime_parser.add_argument("dataspec", help="Data specification (e.g., 0B12, 0B15)")
    realtime_parser.add_argument("--key", required=True, help="Required realtime request key (dataspec-specific)")
    realtime_busy_retry_mode = realtime_parser.add_mutually_exclusive_group()
    realtime_busy_retry_mode.add_argument(
        "--busy-retry",
        dest="busy_retry_enabled",
        action="store_true",
        help="Enable automatic retry when the session is busy",
    )
    realtime_busy_retry_mode.add_argument(
        "--no-busy-retry",
        dest="busy_retry_enabled",
        action="store_false",
        help="Disable automatic retry when the session is busy",
    )
    realtime_parser.set_defaults(busy_retry_enabled=None, respect_retry_after=None)
    realtime_parser.add_argument("--busy-max-retries", type=int, help="Maximum busy retry count")
    realtime_parser.add_argument("--busy-backoff-ms", type=int, help="Busy retry backoff in milliseconds")
    realtime_retry_after_mode = realtime_parser.add_mutually_exclusive_group()
    realtime_retry_after_mode.add_argument(
        "--respect-retry-after",
        dest="respect_retry_after",
        action="store_true",
        help="Use Retry-After header when retrying busy responses",
    )
    realtime_retry_after_mode.add_argument(
        "--ignore-retry-after",
        dest="respect_retry_after",
        action="store_false",
        help="Ignore Retry-After header and use --busy-backoff-ms",
    )
    realtime_parser.add_argument("--format", choices=["json", "raw"], default="json", help="Output format")

    return parser


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, date | datetime | time):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    return value


def _envelope_to_dict(envelope: Any) -> dict[str, Any]:
    return {
        "type": envelope.type,
        "record": _to_jsonable(envelope.record),
        "raw": _to_jsonable(envelope.raw),
    }


async def health_command(client: Client) -> int:
    """Run health command."""
    try:
        result = await client.get_health()
        status = result.get("status", "unknown")
        if status == "healthy":
            print("[OK] Server is healthy")
            return 0
        print(f"[FAIL] Server is unhealthy: {status}", file=sys.stderr)
        jvlink_info = result.get("components", {}).get("jvlink", {})
        if isinstance(jvlink_info, dict):
            fault_message = jvlink_info.get("last_fault_message")
            if isinstance(fault_message, str) and fault_message:
                print(f"[FAIL] JV-Link detail: {fault_message}", file=sys.stderr)
        return 1
    except JVConnectionError:
        print("[FAIL] Cannot connect to JVLinkServer", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"[FAIL] Error: {error}", file=sys.stderr)
        return 1


async def version_command(client: Client) -> int:
    """Run version command."""
    try:
        result = await client.get_version()
        print(f"API version: {result.get('api_version', 'unknown')}")

        if "server" in result:
            server_info = result["server"]
            print(f"Server version: {server_info.get('version', 'unknown')}")
            print(f"Build date: {server_info.get('build_date', 'unknown')}")

        if "environment" in result and "jvlink_version" in result["environment"]:
            print(f"JV-Link version: {result['environment']['jvlink_version']}")

        return 0
    except JVConnectionError:
        print("[FAIL] Cannot connect to JVLinkServer", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"[FAIL] Error: {error}", file=sys.stderr)
        return 1


async def session_command(client: Client) -> int:
    """Run session command."""
    try:
        result = await client.get_session()
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except JVConnectionError:
        print("[FAIL] Cannot connect to JVLinkServer", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"[FAIL] Error: {error}", file=sys.stderr)
        return 1


async def session_reset_command(client: Client) -> int:
    """Run session-reset command."""
    try:
        result = await client.reset_session()
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except JVConnectionError:
        print("[FAIL] Cannot connect to JVLinkServer", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"[FAIL] Error: {error}", file=sys.stderr)
        return 1


async def stored_command(client: Client, args: argparse.Namespace) -> int:
    """Run query-stored command."""
    try:
        count = 0
        print(f"Querying stored data: {args.dataspec} (option={args.option})...", file=sys.stderr)

        kwargs: dict[str, Any] = {
            "dataspec": args.dataspec,
            "from_datetime": args.from_datetime,
            "option": args.option,
            "max_records": args.max_records,
        }

        if args.to_date:
            kwargs["to_date"] = args.to_date
        if args.record_types:
            kwargs["record_types"] = args.record_types
        if args.auto_retry is not None:
            kwargs["auto_retry"] = args.auto_retry
        if args.max_retries is not None:
            kwargs["max_retries"] = args.max_retries
        if args.retry_delay_ms is not None:
            kwargs["retry_delay_ms"] = args.retry_delay_ms
        if args.busy_retry_enabled is not None:
            kwargs["busy_retry_enabled"] = args.busy_retry_enabled
        if args.busy_max_retries is not None:
            kwargs["busy_max_retries"] = args.busy_max_retries
        if args.busy_backoff_ms is not None:
            kwargs["busy_backoff_ms"] = args.busy_backoff_ms
        if args.respect_retry_after is not None:
            kwargs["respect_retry_after"] = args.respect_retry_after

        result = (
            await client.query_stored_raw(**kwargs) if args.format == "raw" else await client.query_stored(**kwargs)
        )

        print(
            f"Meta: read_count={result.meta.get('read_count')}, "
            f"download_count={result.meta.get('download_count')}, "
            f"last_file_timestamp={result.meta.get('last_file_timestamp')}",
            file=sys.stderr,
        )

        async for envelope in result.records:
            if args.format == "json":
                print(json.dumps(_envelope_to_dict(envelope), ensure_ascii=False))
            else:
                print(envelope)
            count += 1

        print(f"\nRetrieved {count} records", file=sys.stderr)
        return 0
    except JVConnectionError:
        print("[FAIL] Cannot connect to JVLinkServer", file=sys.stderr)
        return 1
    except JVValidationError as error:
        print(f"[FAIL] Invalid parameter: {error}", file=sys.stderr)
        return 1
    except JVLinkError as error:
        print(f"[FAIL] JV-Link error: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"[FAIL] Error: {error}", file=sys.stderr)
        return 1


async def realtime_command(client: Client, args: argparse.Namespace) -> int:
    """Run query-realtime command."""
    try:
        count = 0
        print(f"Querying realtime data: {args.dataspec}...", file=sys.stderr)

        result = (
            await client.query_realtime_raw(
                dataspec=args.dataspec,
                key=args.key,
                busy_retry_enabled=args.busy_retry_enabled,
                busy_max_retries=args.busy_max_retries,
                busy_backoff_ms=args.busy_backoff_ms,
                respect_retry_after=args.respect_retry_after,
            )
            if args.format == "raw"
            else await client.query_realtime(
                dataspec=args.dataspec,
                key=args.key,
                busy_retry_enabled=args.busy_retry_enabled,
                busy_max_retries=args.busy_max_retries,
                busy_backoff_ms=args.busy_backoff_ms,
                respect_retry_after=args.respect_retry_after,
            )
        )

        print(f"Total records available: {result.meta.get('count', 'unknown')}", file=sys.stderr)
        if "event_type" in result.meta:
            print(f"Event type: {result.meta['event_type']}", file=sys.stderr)

        async for envelope in result.records:
            if args.format == "json":
                print(json.dumps(_envelope_to_dict(envelope), ensure_ascii=False))
            else:
                print(envelope)
            count += 1

        print(f"\nRetrieved {count} records", file=sys.stderr)
        return 0
    except JVConnectionError:
        print("[FAIL] Cannot connect to JVLinkServer", file=sys.stderr)
        return 1
    except JVValidationError as error:
        print(f"[FAIL] Invalid parameter: {error}", file=sys.stderr)
        return 1
    except JVLinkError as error:
        print(f"[FAIL] JV-Link error: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"[FAIL] Error: {error}", file=sys.stderr)
        return 1


async def async_main(args: argparse.Namespace) -> int:
    """Async main entrypoint."""
    if args.command is None:
        print("No command specified. Use --help for usage information.", file=sys.stderr)
        return 1

    config_kwargs: dict[str, Any] = {}
    if args.host is not None:
        config_kwargs["host"] = args.host
    if args.port is not None:
        config_kwargs["port"] = args.port
    if args.timeout is not None:
        config_kwargs["timeout"] = args.timeout
    if args.stream_read_timeout is not None:
        config_kwargs["stream_read_timeout"] = args.stream_read_timeout
    if args.sid is not None:
        config_kwargs["sid"] = args.sid
    config = JVServerConfig(**config_kwargs)

    async with Client(config=config) as client:
        if args.command == "health":
            return await health_command(client)
        if args.command == "version":
            return await version_command(client)
        if args.command == "session":
            return await session_command(client)
        if args.command == "session-reset":
            return await session_reset_command(client)
        if args.command == "query-stored":
            return await stored_command(client, args)
        if args.command == "query-realtime":
            return await realtime_command(client, args)
        return 1


def _configure_logging(args: argparse.Namespace) -> None:
    """Configure logging based on CLI verbosity flags."""
    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    else:
        return

    package_logger = logging.getLogger("pyjvlink")
    package_logger.setLevel(level)
    package_logger.propagate = False

    handler: logging.Handler | None = None
    for existing_handler in package_logger.handlers:
        if existing_handler.get_name() == _CLI_LOGGER_HANDLER_NAME:
            handler = existing_handler
            break

    if handler is None:
        stream_handler = logging.StreamHandler(stream=sys.stderr)
        stream_handler.set_name(_CLI_LOGGER_HANDLER_NAME)
        stream_handler.setFormatter(logging.Formatter(_CLI_LOGGER_FORMAT))
        package_logger.addHandler(stream_handler)
        handler = stream_handler

    handler.setLevel(level)


def main() -> None:
    """CLI entrypoint."""
    parser = create_parser()
    args = parser.parse_args()
    _configure_logging(args)

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    exit_code = asyncio.run(async_main(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
