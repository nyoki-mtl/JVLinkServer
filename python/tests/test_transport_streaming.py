"""Tests for transport streaming lifecycle."""

from __future__ import annotations

import base64
import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx
import pytest

from pyjvlink._internal.transport import HttpTransport
from pyjvlink._internal.transport.stream import wire_record_envelopes
from pyjvlink.errors import (
    JVBusyError,
    JVConnectionError,
    JVDataError,
    JVInvalidKeyError,
    JVServerError,
    JVTimeoutError,
    JVUnavailableError,
)
from pyjvlink.types import JVServerConfig


class _FakeStreamContext:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.closed = False

    async def __aenter__(self) -> Any:
        return self.response

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        _ = (exc_type, exc, tb)
        self.closed = True


class _RaceyCloseStreamContext(_FakeStreamContext):
    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        _ = (exc_type, exc, tb)
        self.closed = True
        raise RuntimeError("aclose(): asynchronous generator is already running")


class _FakeAsyncClient:
    def __init__(self, stream_context: _FakeStreamContext) -> None:
        self._stream_context = stream_context

    async def request(self, method: str, endpoint: str, json: dict[str, Any] | None = None) -> httpx.Response:
        _ = (method, endpoint, json)
        raise AssertionError("request() should not be called in this test")

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        _ = (endpoint, json, timeout)
        raise AssertionError("post() should not be called in this test")

    def stream(self, method: str, endpoint: str, **kwargs: Any) -> _FakeStreamContext:
        _ = (method, endpoint, kwargs)
        return self._stream_context


class _SequenceStreamClient:
    def __init__(self, stream_contexts: list[_FakeStreamContext]) -> None:
        self._stream_contexts = stream_contexts

    async def request(self, method: str, endpoint: str, json: dict[str, Any] | None = None) -> httpx.Response:
        _ = (method, endpoint, json)
        raise AssertionError("request() should not be called in this test")

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        _ = (endpoint, json, timeout)
        raise AssertionError("post() should not be called in this test")

    def stream(self, method: str, endpoint: str, **kwargs: Any) -> _FakeStreamContext:
        _ = (method, endpoint, kwargs)
        if not self._stream_contexts:
            raise AssertionError("No remaining stream contexts")
        return self._stream_contexts.pop(0)


class _FakeRequestClient:
    def __init__(
        self,
        *,
        request_response: httpx.Response | None = None,
        request_exception: Exception | None = None,
        post_response: httpx.Response | None = None,
        post_exception: Exception | None = None,
    ) -> None:
        self._request_response = request_response
        self._request_exception = request_exception
        self._post_response = post_response
        self._post_exception = post_exception

    async def request(self, method: str, endpoint: str, json: dict[str, Any] | None = None) -> httpx.Response:
        _ = (method, endpoint, json)
        if self._request_exception is not None:
            raise self._request_exception
        if self._request_response is None:
            raise AssertionError("request_response is required")
        return self._request_response

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        _ = (endpoint, json, timeout)
        if self._post_exception is not None:
            raise self._post_exception
        if self._post_response is None:
            raise AssertionError("post_response is required")
        return self._post_response

    def stream(self, method: str, endpoint: str, **kwargs: Any) -> _FakeStreamContext:
        _ = (method, endpoint, kwargs)
        raise AssertionError("stream() should not be called in this test")


class _FakeJSONLResponse:
    def __init__(self, lines: list[str], status_code: int = 200) -> None:
        self._lines = lines
        self.status_code = status_code

    def raise_for_status(self) -> None:
        return None

    def aiter_lines(self) -> AsyncGenerator[str, None]:
        async def _gen() -> AsyncGenerator[str, None]:
            for line in self._lines:
                yield line

        return _gen()


class _ClosableAsyncIterator:
    def __init__(self, values: list[Any]) -> None:
        self._values = values
        self._index = 0
        self.closed = False

    def __aiter__(self) -> _ClosableAsyncIterator:
        return self

    async def __anext__(self) -> Any:
        if self._index >= len(self._values):
            raise StopAsyncIteration
        value = self._values[self._index]
        self._index += 1
        return value

    async def aclose(self) -> None:
        self.closed = True


class _FakeHTTPErrorResponse:
    def __init__(self, status_code: int, body: Any, headers: dict[str, str] | None = None) -> None:
        self.status_code = status_code
        self._response = httpx.Response(
            status_code,
            json=body,
            headers=headers,
            request=httpx.Request("POST", "http://example.local/query"),
        )

    def raise_for_status(self) -> None:
        self._response.raise_for_status()


@pytest.mark.asyncio
async def test_fetch_stream_no_data_closes_context() -> None:
    response = _FakeJSONLResponse([json.dumps({"meta": {"error_code": -1}})])
    stream_context = _FakeStreamContext(response)

    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    meta, records = await transport._fetch_and_parse_stream("/query/stored", payload={})

    assert meta["error_code"] == -1
    assert stream_context.closed is True

    seen = [record async for record in records]
    assert seen == []


@pytest.mark.asyncio
async def test_fetch_stream_http_status_reads_body_before_close() -> None:
    error_body = {"error": {"message": "boom", "code": -201}}
    response = _FakeHTTPErrorResponse(status_code=500, body=error_body)
    stream_context = _FakeStreamContext(response)

    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    with pytest.raises(JVServerError, match="boom") as exc_info:
        await transport._fetch_and_parse_stream("/query/stored", payload={})

    assert stream_context.closed is True
    assert exc_info.value.error_code == -201


@pytest.mark.asyncio
async def test_fetch_stream_busy_503_maps_to_busy_error_with_retry_after() -> None:
    error_body = {
        "error": {"message": "JV-Link session is busy", "code": -202},
        "operation": "query_stored",
        "session": {
            "busy": True,
            "operation": "query_stored",
            "path": "/query/stored",
            "request_id": "req-1",
            "started_at": 1711111111,
            "elapsed_ms": 2500,
            "dataspec": "RACE",
            "watch_active": False,
        },
    }
    response = _FakeHTTPErrorResponse(
        status_code=503,
        body=error_body,
        headers={
            "Retry-After": "1",
            "X-JVLink-Busy": "1",
            "X-JVLink-Operation": "query_stored",
            "X-JVLink-Session-Request-Id": "req-1",
            "X-JVLink-Session-Path": "/query/stored",
            "X-JVLink-Session-Started-At": "1711111111",
            "X-JVLink-Session-Elapsed-Ms": "2500",
        },
    )
    stream_context = _FakeStreamContext(response)

    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    with pytest.raises(JVBusyError, match="JV-Link session is busy") as exc_info:
        await transport._fetch_and_parse_stream("/query/stored", payload={})

    assert stream_context.closed is True
    assert exc_info.value.error_code == -202
    assert exc_info.value.retry_after == 1
    assert exc_info.value.operation == "query_stored"
    assert exc_info.value.path == "/query/stored"
    assert exc_info.value.request_id == "req-1"
    assert exc_info.value.started_at == 1711111111
    assert exc_info.value.elapsed_ms == 2500
    assert exc_info.value.dataspec == "RACE"


@pytest.mark.asyncio
async def test_fetch_stream_unavailable_503_maps_to_unavailable_error() -> None:
    error_body = {"error": {"message": "JV-Link wrapper is not operational", "code": -50301}}
    response = _FakeHTTPErrorResponse(
        status_code=503,
        body=error_body,
        headers={"X-JVLink-Unavailable": "1"},
    )
    stream_context = _FakeStreamContext(response)

    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    with pytest.raises(JVUnavailableError, match="JV-Link wrapper is not operational") as exc_info:
        await transport._fetch_and_parse_stream("/query/stored", payload={})

    assert stream_context.closed is True
    assert exc_info.value.error_code == -50301


@pytest.mark.asyncio
async def test_fetch_stream_http_status_with_non_object_json_body_uses_fallback_error() -> None:
    response = _FakeHTTPErrorResponse(status_code=500, body=123)
    stream_context = _FakeStreamContext(response)

    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    with pytest.raises(JVServerError, match="HTTP communication error") as exc_info:
        await transport._fetch_and_parse_stream("/query/stored", payload={})

    assert stream_context.closed is True
    assert exc_info.value.error_code == 500


@pytest.mark.asyncio
async def test_fetch_stream_http_4xx_maps_to_validation_error() -> None:
    error_body = {"error": {"message": "invalid key", "code": -114}}
    response = _FakeHTTPErrorResponse(status_code=400, body=error_body)
    stream_context = _FakeStreamContext(response)

    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    with pytest.raises(JVInvalidKeyError, match="invalid key"):
        await transport._fetch_and_parse_stream("/query/realtime", payload={})

    assert stream_context.closed is True


@pytest.mark.asyncio
async def test_fetch_stream_skips_blank_lines_before_meta() -> None:
    response = _FakeJSONLResponse(
        [
            "",
            "",
            json.dumps({"meta": {"read_count": 1}}),
            json.dumps({"type": "RA", "data": {"data_code": "1"}}),
        ]
    )
    stream_context = _FakeStreamContext(response)

    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    meta, records = await transport._fetch_and_parse_stream("/query/stored", payload={})
    seen = [record async for record in records]

    assert meta["read_count"] == 1
    assert seen == [{"type": "RA", "data": {"data_code": "1"}}]
    assert stream_context.closed is True


@pytest.mark.asyncio
async def test_fetch_stream_raises_server_error_from_error_row() -> None:
    response = _FakeJSONLResponse(
        [
            json.dumps({"meta": {}}),
            json.dumps({"error": {"message": "download failed", "code": -502}}),
        ]
    )
    stream_context = _FakeStreamContext(response)

    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    _, records = await transport._fetch_and_parse_stream("/query/stored", payload={})
    with pytest.raises(JVServerError, match="download failed") as exc_info:
        _ = [record async for record in records]

    assert exc_info.value.error_code == -502
    assert stream_context.closed is True


@pytest.mark.asyncio
async def test_fetch_stream_raises_unavailable_error_from_error_row() -> None:
    response = _FakeJSONLResponse(
        [
            json.dumps({"meta": {}}),
            json.dumps({"error": {"message": "JV-Link became unavailable", "code": -50301}}),
        ]
    )
    stream_context = _FakeStreamContext(response)

    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    _, records = await transport._fetch_and_parse_stream("/query/stored", payload={})
    with pytest.raises(JVUnavailableError, match="JV-Link became unavailable") as exc_info:
        _ = [record async for record in records]

    assert exc_info.value.error_code == -50301
    assert stream_context.closed is True


@pytest.mark.asyncio
async def test_fetch_stream_close_race_does_not_raise() -> None:
    response = _FakeJSONLResponse(
        [
            json.dumps({"meta": {"read_count": 1}}),
            json.dumps({"type": "RA", "data": {"data_code": "1"}}),
        ]
    )
    stream_context = _RaceyCloseStreamContext(response)

    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    _, records = await transport._fetch_and_parse_stream("/query/stored", payload={})
    first = await records.__anext__()
    assert first["type"] == "RA"

    await records.aclose()
    assert stream_context.closed is True


@pytest.mark.asyncio
async def test_wire_record_envelopes_closes_source_when_closed_early() -> None:
    rows = _ClosableAsyncIterator([{"type": "RA", "data": {"data_code": "1"}}])

    envelopes = wire_record_envelopes(rows, include_raw=False)
    first = await envelopes.__anext__()

    assert first.type == "RA"

    await envelopes.aclose()
    assert rows.closed is True


class _EventProbeTransport(HttpTransport):
    def __init__(self, stream_context: _FakeStreamContext) -> None:
        super().__init__(JVServerConfig())
        self._client = _FakeAsyncClient(stream_context)  # type: ignore[assignment]

    async def start_event_watch(self) -> dict[str, Any]:
        raise AssertionError("start_event_watch() must not be called by stream_events()")

    async def stop_event_watch(self) -> dict[str, Any]:
        raise AssertionError("stop_event_watch() must not be called by stream_events()")


@pytest.mark.asyncio
async def test_stream_events_does_not_control_watch_lifecycle() -> None:
    response = _FakeJSONLResponse(
        [
            "event: connected",
            "data: {}",
            "event: jvlink_event",
            'data: {"type":"JVEvtPay","param":"20240101","timestamp":1704067200}',
        ]
    )
    stream_context = _FakeStreamContext(response)
    transport = _EventProbeTransport(stream_context)

    events = [event async for event in transport.stream_events()]

    assert events == [{"type": "JVEvtPay", "param": "20240101", "timestamp": 1704067200}]


@pytest.mark.asyncio
async def test_request_json_rejects_non_object_body() -> None:
    response = httpx.Response(
        200,
        json=[{"ok": True}],
        request=httpx.Request("GET", "http://example.local/health"),
    )
    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeRequestClient(request_response=response)  # type: ignore[assignment]

    with pytest.raises(JVDataError, match="expected object"):
        await transport.get_health()


@pytest.mark.asyncio
async def test_request_json_rejects_invalid_json() -> None:
    response = httpx.Response(
        200,
        text="not-json",
        request=httpx.Request("GET", "http://example.local/version"),
    )
    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeRequestClient(request_response=response)  # type: ignore[assignment]

    with pytest.raises(JVDataError, match="Invalid JSON response"):
        await transport.get_version()


@pytest.mark.asyncio
async def test_request_json_maps_network_error_to_connection_error() -> None:
    exc = httpx.ReadError("boom", request=httpx.Request("GET", "http://example.local/health"))
    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeRequestClient(request_exception=exc)  # type: ignore[assignment]

    with pytest.raises(JVConnectionError, match="HTTP network error"):
        await transport.get_health()


@pytest.mark.asyncio
async def test_request_json_busy_503_maps_to_busy_error_with_retry_after() -> None:
    response = httpx.Response(
        503,
        json={
            "error": {"message": "JV-Link session is busy", "code": -202},
            "session": {
                "busy": True,
                "operation": "query_realtime",
                "path": "/query/realtime",
                "request_id": "req-2",
                "started_at": 1711112222,
                "elapsed_ms": 1500,
                "key": "202401070511",
                "watch_active": False,
            },
        },
        headers={"Retry-After": "1", "X-JVLink-Busy": "1", "X-JVLink-Operation": "query_realtime"},
        request=httpx.Request("GET", "http://example.local/version"),
    )
    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeRequestClient(request_response=response)  # type: ignore[assignment]

    with pytest.raises(JVBusyError, match="JV-Link session is busy") as exc_info:
        await transport.get_version()

    assert exc_info.value.error_code == -202
    assert exc_info.value.retry_after == 1
    assert exc_info.value.operation == "query_realtime"
    assert exc_info.value.path == "/query/realtime"
    assert exc_info.value.request_id == "req-2"
    assert exc_info.value.key == "202401070511"


@pytest.mark.asyncio
async def test_query_stored_retries_busy_response_when_enabled() -> None:
    busy_context = _FakeStreamContext(
        _FakeHTTPErrorResponse(
            status_code=503,
            body={"error": {"message": "JV-Link session is busy", "code": -202}},
            headers={"Retry-After": "0", "X-JVLink-Busy": "1", "X-JVLink-Operation": "query_stored"},
        )
    )
    success_context = _FakeStreamContext(
        _FakeJSONLResponse(
            [json.dumps({"meta": {"read_count": 1}}), json.dumps({"type": "RA", "data": {"data_code": "1"}})]
        )
    )

    transport = HttpTransport(JVServerConfig())
    transport._client = _SequenceStreamClient([busy_context, success_context])  # type: ignore[assignment]

    meta, records = await transport.query_stored(
        dataspec="RACE",
        from_datetime="20240101",
        option=1,
        busy_retry_enabled=True,
        busy_max_retries=1,
        busy_backoff_ms=0,
        respect_retry_after=False,
    )

    assert meta["read_count"] == 1
    assert [record async for record in records] == [{"type": "RA", "data": {"data_code": "1"}}]


@pytest.mark.asyncio
async def test_query_realtime_retries_busy_response_when_enabled() -> None:
    busy_context = _FakeStreamContext(
        _FakeHTTPErrorResponse(
            status_code=503,
            body={"error": {"message": "JV-Link session is busy", "code": -202}},
            headers={"Retry-After": "0", "X-JVLink-Busy": "1", "X-JVLink-Operation": "query_realtime"},
        )
    )
    success_context = _FakeStreamContext(
        _FakeJSONLResponse([json.dumps({"meta": {}}), json.dumps({"type": "RA", "data": {"data_code": "1"}})])
    )

    transport = HttpTransport(JVServerConfig())
    transport._client = _SequenceStreamClient([busy_context, success_context])  # type: ignore[assignment]

    meta, records = await transport.query_realtime(
        dataspec="0B12",
        key="202401070511",
        busy_retry_enabled=True,
        busy_max_retries=1,
        busy_backoff_ms=0,
        respect_retry_after=False,
    )

    assert meta == {}
    assert [record async for record in records] == [{"type": "RA", "data": {"data_code": "1"}}]


@pytest.mark.asyncio
async def test_get_health_returns_unhealthy_payload_on_503() -> None:
    response = httpx.Response(
        503,
        json={
            "status": "unhealthy",
            "components": {"jvlink": {"last_fault_message": "JV-Link wrapper is not operational"}},
        },
        headers={"X-JVLink-Unavailable": "1"},
        request=httpx.Request("GET", "http://example.local/health"),
    )
    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeRequestClient(request_response=response)  # type: ignore[assignment]

    payload = await transport.get_health()

    assert payload["status"] == "unhealthy"
    assert payload["components"]["jvlink"]["last_fault_message"] == "JV-Link wrapper is not operational"


@pytest.mark.asyncio
async def test_get_session_returns_snapshot_payload() -> None:
    response = httpx.Response(
        200,
        json={"busy": True, "operation": "query_stored", "request_id": "req-3", "watch_active": False},
        request=httpx.Request("GET", "http://example.local/session"),
    )
    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeRequestClient(request_response=response)  # type: ignore[assignment]

    payload = await transport.get_session()

    assert payload["busy"] is True
    assert payload["request_id"] == "req-3"


@pytest.mark.asyncio
async def test_reset_session_returns_admin_payload() -> None:
    response = httpx.Response(
        200,
        json={"status": "success", "action": "worker_restarted", "session": {"busy": False, "watch_active": False}},
        request=httpx.Request("POST", "http://example.local/session/reset"),
    )
    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeRequestClient(request_response=response)  # type: ignore[assignment]

    payload = await transport.reset_session()

    assert payload["status"] == "success"
    assert payload["action"] == "worker_restarted"


@pytest.mark.asyncio
async def test_request_json_unavailable_503_maps_to_unavailable_error() -> None:
    response = httpx.Response(
        503,
        json={"error": {"message": "JV-Link wrapper is not operational", "code": -50301}},
        headers={"X-JVLink-Unavailable": "1"},
        request=httpx.Request("GET", "http://example.local/version"),
    )
    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeRequestClient(request_response=response)  # type: ignore[assignment]

    with pytest.raises(JVUnavailableError, match="JV-Link wrapper is not operational") as exc_info:
        await transport.get_version()

    assert exc_info.value.error_code == -50301


@pytest.mark.asyncio
async def test_request_binary_maps_network_error_to_connection_error() -> None:
    exc = httpx.ReadError("boom", request=httpx.Request("POST", "http://example.local/uniform/image"))
    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeRequestClient(post_exception=exc)  # type: ignore[assignment]

    with pytest.raises(JVConnectionError, match="HTTP network error"):
        await transport.get_uniform("水色，赤山形一本輪，水色袖")


@pytest.mark.asyncio
async def test_get_course_prefers_base64_encoded_explanation_header() -> None:
    encoded_explanation = base64.b64encode("中山芝2000m".encode()).decode("ascii")
    response = httpx.Response(
        200,
        content=b"GIF89a",
        headers={
            "X-Course-Explanation": "garbled",
            "X-Course-Explanation-Base64": encoded_explanation,
        },
        request=httpx.Request("POST", "http://example.local/course/image"),
    )
    transport = HttpTransport(JVServerConfig())
    transport._client = _FakeRequestClient(post_response=response)  # type: ignore[assignment]

    image, explanation = await transport.get_course("9999999905240011")

    assert image == b"GIF89a"
    assert explanation == "中山芝2000m"


class _TimeoutStreamContext:
    async def __aenter__(self) -> Any:
        raise httpx.ReadTimeout("timed out")

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        _ = (exc_type, exc, tb)


class _TimeoutStreamClient:
    async def request(self, method: str, endpoint: str, json: dict[str, Any] | None = None) -> httpx.Response:
        _ = (method, endpoint, json)
        raise AssertionError("request() should not be called in this test")

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        _ = (endpoint, json, timeout)
        raise AssertionError("post() should not be called in this test")

    def stream(self, method: str, endpoint: str, **kwargs: Any) -> _TimeoutStreamContext:
        _ = (method, endpoint, kwargs)
        return _TimeoutStreamContext()


@pytest.mark.asyncio
async def test_stream_events_maps_timeout_to_jv_timeout_error() -> None:
    transport = HttpTransport(JVServerConfig())
    transport._client = _TimeoutStreamClient()  # type: ignore[assignment]

    with pytest.raises(JVTimeoutError, match="Event stream timeout"):
        _ = [event async for event in transport.stream_events()]
