"""HTTP/SSE transport implementation."""

from __future__ import annotations

import asyncio
import base64
import binascii
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any, NoReturn, cast

import httpx

from pyjvlink.api.types import (
    CourseFileResponse,
    DeleteFileResponse,
    HealthResponse,
    SaveCourseResponse,
    SaveUniformResponse,
    VersionResponse,
)
from pyjvlink.errors import (
    JVConnectionError,
    JVDataError,
    JVServerError,
    JVTimeoutError,
    build_error_for_code,
    raise_for_error_code,
)
from pyjvlink.types import JVServerConfig

logger = logging.getLogger(__name__)


class HttpTransport:
    """HTTP/SSE transport layer."""

    def __init__(self, config: JVServerConfig) -> None:
        self.config = config
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        if self._client is not None:
            return
        self._client = httpx.AsyncClient(
            base_url=f"http://{self.config.host}:{self.config.port}",
            timeout=self.config.timeout,
            headers={
                "Accept": "application/json, application/x-ndjson",
                "Content-Type": "application/json; charset=utf-8",
            },
        )

    async def stop(self) -> None:
        if self._client is None:
            return
        await self._client.aclose()
        self._client = None

    def _build_url(self, endpoint: str) -> str:
        version_agnostic_endpoints = {"/health", "/version", "/openapi.json"}
        if endpoint in version_agnostic_endpoints:
            return endpoint
        if self.config.api_version and self.config.api_version != "v1":
            return f"/{self.config.api_version}/{endpoint.lstrip('/')}"
        return endpoint

    def _require_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise JVConnectionError("Client not started. Call start() first.")
        return self._client

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> int | None:
        raw_retry_after = response.headers.get("Retry-After")
        if raw_retry_after is None:
            return None
        try:
            retry_after = int(raw_retry_after)
        except ValueError:
            logger.debug("Failed to parse Retry-After header: %s", raw_retry_after)
            return None
        return retry_after if retry_after >= 0 else None

    def _parse_server_error(self, error: httpx.HTTPStatusError) -> tuple[str, int, int | None]:
        error_code = error.response.status_code
        error_message = error.response.text
        retry_after = self._parse_retry_after(error.response)
        try:
            payload = cast(dict[str, Any], error.response.json())
            error_info = payload.get("error")
            if isinstance(error_info, dict):
                parsed_message = error_info.get("message")
                parsed_code = error_info.get("code")
                if isinstance(parsed_message, str) and parsed_message.strip():
                    error_message = parsed_message
                if isinstance(parsed_code, int):
                    error_code = parsed_code
        except (ValueError, KeyError, AttributeError):
            logger.debug("Failed to parse structured error from response body")
        return error_message, error_code, retry_after

    def _raise_server_error(
        self,
        error_message: str,
        error_code: int,
        retry_after: int | None,
        cause: Exception,
    ) -> NoReturn:
        raise build_error_for_code(
            error_code,
            error_message,
            default_exc=JVServerError,
            retry_after=retry_after,
        ) from cause

    async def _request_json(
        self, method: str, endpoint: str, *, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        client = self._require_client()
        try:
            response = await client.request(method, self._build_url(endpoint), json=payload)
            response.raise_for_status()
            parsed = response.json()
            if not isinstance(parsed, dict):
                raise JVDataError(f"Invalid JSON response format: expected object, got {type(parsed).__name__}.")
            return cast(dict[str, Any], parsed)
        except httpx.HTTPStatusError as e:
            error_message, error_code, retry_after = self._parse_server_error(e)
            self._raise_server_error(error_message, error_code, retry_after, e)
        except httpx.TimeoutException as e:
            raise JVTimeoutError(f"HTTP request timeout: {endpoint}") from e
        except httpx.ConnectError as e:
            raise JVConnectionError(f"HTTP connection failed: {e}") from e
        except httpx.NetworkError as e:
            raise JVConnectionError(f"HTTP network error: {e}") from e
        except ValueError as e:
            raise JVDataError(f"Invalid JSON response from {endpoint}: {e}") from e

    async def _request_binary(
        self, endpoint: str, *, payload: dict[str, Any], timeout: float | None = None
    ) -> httpx.Response:
        client = self._require_client()
        try:
            response = await client.post(self._build_url(endpoint), json=payload, timeout=timeout)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            error_message, error_code, retry_after = self._parse_server_error(e)
            self._raise_server_error(error_message, error_code, retry_after, e)
        except httpx.TimeoutException as e:
            raise JVTimeoutError(f"HTTP request timeout: {endpoint}") from e
        except httpx.ConnectError as e:
            raise JVConnectionError(f"HTTP connection failed: {e}") from e
        except httpx.NetworkError as e:
            raise JVConnectionError(f"HTTP network error: {e}") from e

    async def _fetch_and_parse_stream(
        self, endpoint: str, payload: dict[str, Any], read_timeout_override: int | None = None
    ) -> tuple[dict[str, Any], AsyncGenerator[dict[str, Any], None]]:
        client = self._require_client()
        read_timeout_value = (
            float(read_timeout_override)
            if read_timeout_override is not None
            else float(self.config.stream_read_timeout)
        )
        stream_timeout = httpx.Timeout(
            timeout=None,
            connect=10.0,
            read=read_timeout_value,
            write=10.0,
            pool=None,
        )
        response_context_manager = client.stream(
            "POST",
            self._build_url(endpoint),
            json=payload,
            timeout=stream_timeout,
        )
        response_entered = False
        response_closed = False
        close_lock = asyncio.Lock()

        async def close_response() -> None:
            nonlocal response_closed
            if response_closed or not response_entered:
                return
            async with close_lock:
                if response_closed or not response_entered:
                    return
                try:
                    await response_context_manager.__aexit__(None, None, None)
                except RuntimeError as e:
                    message = str(e)
                    if "asynchronous generator is already running" not in message:
                        raise
                    logger.debug("Ignored stream close race condition: %s", message)
                finally:
                    response_closed = True

        async def parse_http_status_error(error: httpx.HTTPStatusError) -> tuple[str, int, int | None]:
            error_message = f"HTTP communication error (status {error.response.status_code})"
            error_code = error.response.status_code
            retry_after = self._parse_retry_after(error.response)
            try:
                error_text = await error.response.aread()
                decoded_error = error_text.decode("utf-8", errors="replace")
                if decoded_error:
                    error_message += f": {decoded_error}"
                try:
                    error_body = json.loads(error_text)
                except json.JSONDecodeError:
                    return error_message, error_code, retry_after

                if not isinstance(error_body, dict):
                    return error_message, error_code, retry_after

                error_info = error_body.get("error")
                if not isinstance(error_info, dict):
                    return error_message, error_code, retry_after

                parsed_message = error_info.get("message")
                if isinstance(parsed_message, str) and parsed_message.strip():
                    error_message = f"JVLinkServer error: {parsed_message}"
                parsed_code = error_info.get("code")
                if isinstance(parsed_code, int):
                    error_code = parsed_code
            except (httpx.StreamError, UnicodeDecodeError) as e:
                logger.debug("Failed to read error response body: %s", e)
            return error_message, error_code, retry_after

        try:
            response = await response_context_manager.__aenter__()
            response_entered = True

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                error_message, error_code, retry_after = await parse_http_status_error(e)
                await close_response()
                raise build_error_for_code(
                    error_code,
                    error_message,
                    default_exc=JVServerError,
                    retry_after=retry_after,
                ) from e

            line_iterator = response.aiter_lines()

            try:
                while True:
                    first_line = await line_iterator.__anext__()
                    if first_line and first_line.strip():
                        break
                meta_data = json.loads(first_line)
            except StopAsyncIteration as e:
                raise JVDataError("Streaming response was empty.") from e
            except json.JSONDecodeError as e:
                raise JVDataError(f"Invalid JSON in metadata line: {e}") from e

            if "error" in meta_data:
                error_info = meta_data["error"]
                raise JVServerError(
                    f"JVLinkServer stream error: {error_info.get('message', 'Unknown error')}",
                    error_code=error_info.get("code"),
                )

            if "meta" not in meta_data:
                raise JVDataError("Missing 'meta' in streaming response header.")

            meta = meta_data["meta"]

            if "error_code" in meta and meta["error_code"] != 0:
                error_code = meta["error_code"]
                if error_code == -1:
                    await close_response()

                    async def empty_generator() -> AsyncGenerator[dict[str, Any], None]:
                        if False:
                            yield {}

                    return meta, empty_generator()
                error_message = meta.get("error_message", f"JVOpen error (code: {error_code})")
                raise_for_error_code(error_code, error_message)

            async def record_generator() -> AsyncGenerator[dict[str, Any], None]:
                try:
                    async for line in line_iterator:
                        if not line:
                            continue
                        try:
                            payload = json.loads(line)
                            if isinstance(payload, dict) and "error" in payload:
                                error_info = payload.get("error")
                                if isinstance(error_info, dict):
                                    raise JVServerError(
                                        f"JVLinkServer stream error: {error_info.get('message', 'Unknown error')}",
                                        error_code=error_info.get("code"),
                                    )
                                raise JVServerError("JVLinkServer stream error: Unknown error")
                            yield payload
                        except json.JSONDecodeError as e:
                            line_preview = line[:100]
                            if len(line) > 100:
                                line_preview += "..."
                            raise JVDataError(f"Invalid JSON in data stream: {e}. Line preview: {line_preview}") from e
                finally:
                    await close_response()

            return meta, record_generator()
        except httpx.TimeoutException as e:
            await close_response()
            raise JVTimeoutError("HTTP request timeout - server may be overloaded") from e
        except httpx.ConnectError as e:
            await close_response()
            raise JVConnectionError(f"HTTP connection failed - JVLinkServer not responding: {e}") from e
        except httpx.NetworkError as e:
            await close_response()
            raise JVConnectionError(f"HTTP network error - Python <-> C++ communication failed: {e}") from e
        except (json.JSONDecodeError, KeyError) as e:
            await close_response()
            raise JVDataError(f"Invalid JSON response from JVLinkServer: {e}") from e
        except Exception:
            await close_response()
            raise

    async def query_stored(
        self,
        dataspec: str,
        from_datetime: str,
        option: int,
        max_records: int = -1,
        to_date: str | None = None,
        record_types: list[str] | None = None,
        auto_retry: bool | None = None,
        max_retries: int | None = None,
        retry_delay_ms: int | None = None,
        exclude_deletions: bool = False,
        stream_read_timeout: int | None = None,
    ) -> tuple[dict[str, Any], AsyncGenerator[dict[str, Any], None]]:
        if auto_retry is None:
            auto_retry = self.config.auto_retry
        if max_retries is None:
            max_retries = self.config.max_retries
        if retry_delay_ms is None:
            retry_delay_ms = self.config.retry_delay_ms

        from_date = f"{from_datetime}-{to_date}" if to_date else from_datetime
        payload: dict[str, Any] = {
            "data_spec": dataspec,
            "from_date": from_date,
            "option": option,
            "max_records": max_records,
            "auto_retry": auto_retry,
            "max_retries": max_retries,
            "retry_delay_ms": retry_delay_ms,
        }
        if record_types is not None:
            payload["record_types"] = record_types

        meta, gen = await self._fetch_and_parse_stream(
            "/query/stored",
            payload,
            read_timeout_override=stream_read_timeout,
        )

        if not exclude_deletions:
            return meta, gen

        async def filtered() -> AsyncGenerator[dict[str, Any], None]:
            async for rec in gen:
                if not isinstance(rec, dict):
                    logger.warning("Unexpected stream record type: %s", type(rec).__name__)
                    continue
                data = rec.get("data")
                if not isinstance(data, dict):
                    logger.warning("Unexpected stream record shape (missing dict 'data'): %s", rec)
                    continue
                if data.get("data_code") == "0":
                    continue
                yield rec

        return meta, filtered()

    async def query_realtime(
        self,
        dataspec: str,
        key: str,
    ) -> tuple[dict[str, Any], AsyncGenerator[dict[str, Any], None]]:
        payload = {"dataspec": dataspec, "key": key}
        return await self._fetch_and_parse_stream("/query/realtime", payload)

    async def delete_file(self, filename: str) -> DeleteFileResponse:
        return cast(
            DeleteFileResponse,
            await self._request_json("POST", "/files/delete", payload={"filename": filename}),
        )

    async def get_uniform(self, pattern: str) -> bytes:
        response = await self._request_binary("/uniform/image", payload={"pattern": pattern})
        return response.content

    async def save_uniform(self, pattern: str, filepath: str) -> SaveUniformResponse:
        return cast(
            SaveUniformResponse,
            await self._request_json(
                "POST",
                "/uniform/file",
                payload={"pattern": pattern, "filepath": filepath},
            ),
        )

    async def get_course(self, key: str) -> tuple[bytes, str]:
        response = await self._request_binary("/course/image", payload={"key": key})
        explanation_base64 = response.headers.get("X-Course-Explanation-Base64")
        explanation = response.headers.get("X-Course-Explanation", "")
        if explanation_base64:
            try:
                explanation = base64.b64decode(explanation_base64).decode("utf-8")
            except (binascii.Error, ValueError, UnicodeDecodeError):
                logger.warning("Failed to decode X-Course-Explanation-Base64 header")
        return response.content, explanation

    async def get_course_file(self, key: str) -> CourseFileResponse:
        return cast(CourseFileResponse, await self._request_json("POST", "/course/file", payload={"key": key}))

    async def save_course(self, key: str, filepath: str) -> SaveCourseResponse:
        return cast(
            SaveCourseResponse,
            await self._request_json(
                "POST",
                "/course/file2",
                payload={"key": key, "filepath": filepath},
            ),
        )

    async def get_health(self) -> HealthResponse:
        return cast(HealthResponse, await self._request_json("GET", "/health"))

    async def get_version(self) -> VersionResponse:
        return cast(VersionResponse, await self._request_json("GET", "/version"))

    async def start_event_watch(self) -> dict[str, Any]:
        return await self._request_json("POST", "/event/start")

    async def stop_event_watch(self) -> dict[str, Any]:
        return await self._request_json("POST", "/event/stop")

    async def stream_events(self) -> AsyncGenerator[dict[str, Any], None]:
        client = self._require_client()
        stream_timeout = httpx.Timeout(
            timeout=None,
            connect=10.0,
            read=float(self.config.stream_read_timeout),
            write=10.0,
            pool=None,
        )

        try:
            async with client.stream("GET", self._build_url("/events/stream"), timeout=stream_timeout) as response:
                if response.status_code != 200:
                    raise JVServerError(f"Failed to connect to event stream: {response.status_code}")

                event_type: str | None = None
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("event:"):
                        event_type = line[6:].strip()
                        continue
                    if not line.startswith("data:"):
                        continue

                    data = line[5:].strip()
                    if event_type == "connected":
                        event_type = None
                        continue

                    if event_type == "jvlink_event":
                        try:
                            yield cast(dict[str, Any], json.loads(data))
                        except json.JSONDecodeError:
                            logger.warning("Skipping malformed SSE event data: %s", data[:100])
                        event_type = None
        except httpx.TimeoutException as e:
            raise JVTimeoutError("Event stream timeout") from e
        except httpx.ConnectError as e:
            raise JVConnectionError(f"Event stream connection failed: {e}") from e
        except httpx.NetworkError as e:
            raise JVConnectionError(f"Event stream network error: {e}") from e
        except asyncio.CancelledError:
            raise
        except httpx.StreamClosed:
            logger.debug("SSE stream closed")
