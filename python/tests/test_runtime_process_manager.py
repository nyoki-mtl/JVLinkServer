"""Tests for runtime process manager behavior."""

from __future__ import annotations

from typing import Any

import pytest

from pyjvlink import JVServerConfig
from pyjvlink._internal.runtime import ProcessManager
from pyjvlink.errors import JVConnectionError, JVServerError, JVTimeoutError


@pytest.mark.asyncio
async def test_start_requires_remote_host_on_non_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = ProcessManager(JVServerConfig(host="127.0.0.1", port=8765))

    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.platform.system", lambda: "Linux")
    monkeypatch.setattr(ProcessManager, "_probe_server", lambda self: (False, False, None))

    with pytest.raises(JVConnectionError, match="set JVLINK_SERVER_HOST / JVLINK_SERVER_PORT"):
        await manager.start()


@pytest.mark.asyncio
async def test_start_uses_remote_host_without_local_autostart(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = ProcessManager(JVServerConfig(host="192.168.10.20", port=8765))
    started = False
    waited = False

    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.platform.system", lambda: "Linux")
    monkeypatch.setattr(ProcessManager, "_probe_server", lambda self: (True, True, {"status": "healthy"}))

    async def fake_start_server() -> None:
        nonlocal started
        started = True

    async def fake_wait_for_server() -> None:
        nonlocal waited
        waited = True

    monkeypatch.setattr(manager, "_start_server", fake_start_server)
    monkeypatch.setattr(manager, "_wait_for_server", fake_wait_for_server)

    await manager.start()

    assert started is False
    assert waited is True


@pytest.mark.asyncio
async def test_start_cleans_up_local_server_when_wait_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = ProcessManager(JVServerConfig(host="127.0.0.1", port=8765))
    stopped = False

    class _FakeProcess:
        pass

    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.platform.system", lambda: "Windows")
    monkeypatch.setattr(ProcessManager, "_probe_server", lambda self: (False, False, None))

    async def fake_start_server() -> None:
        manager._server_process = _FakeProcess()  # type: ignore[assignment]

    async def fake_wait_for_server() -> None:
        raise JVTimeoutError("Server startup timeout after 5 seconds")

    async def fake_stop_server() -> None:
        nonlocal stopped
        stopped = True
        manager._server_process = None

    monkeypatch.setattr(manager, "_start_server", fake_start_server)
    monkeypatch.setattr(manager, "_wait_for_server", fake_wait_for_server)
    monkeypatch.setattr(manager, "_stop_server", fake_stop_server)

    with pytest.raises(JVTimeoutError, match="5 seconds"):
        await manager.start()

    assert stopped is True


class _HealthyResponse:
    status_code = 200

    @staticmethod
    def json() -> dict[str, str]:
        return {"status": "healthy"}


class _HealthyAsyncClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        _ = (args, kwargs)

    async def __aenter__(self) -> _HealthyAsyncClient:
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        _ = (exc_type, exc, tb)

    async def get(self, url: str) -> _HealthyResponse:
        _ = url
        return _HealthyResponse()


class _UnhealthyResponse:
    status_code = 503

    @staticmethod
    def json() -> dict[str, Any]:
        return {
            "status": "unhealthy",
            "components": {"jvlink": {"last_fault_message": "JV-Link COM task timed out during jvrt_open"}},
        }


@pytest.mark.asyncio
async def test_wait_for_server_returns_without_extra_sleep_on_healthy(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = ProcessManager(JVServerConfig(startup_timeout=5))
    sleep_calls: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.httpx.AsyncClient", _HealthyAsyncClient)
    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.asyncio.sleep", fake_sleep)

    await manager._wait_for_server()
    assert sleep_calls == []


@pytest.mark.asyncio
async def test_start_raises_when_server_is_running_but_unhealthy(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = ProcessManager(JVServerConfig(host="127.0.0.1", port=8765))

    monkeypatch.setattr(
        ProcessManager,
        "_probe_server",
        lambda self: (True, False, {"status": "unhealthy"}),
    )

    with pytest.raises(JVServerError, match="but is unhealthy"):
        await manager.start()


class _UnhealthyAsyncClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        _ = (args, kwargs)

    async def __aenter__(self) -> _UnhealthyAsyncClient:
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        _ = (exc_type, exc, tb)

    async def get(self, url: str) -> _UnhealthyResponse:
        _ = url
        return _UnhealthyResponse()


@pytest.mark.asyncio
async def test_wait_for_server_fails_fast_on_unhealthy_status(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = ProcessManager(JVServerConfig(startup_timeout=5))

    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.httpx.AsyncClient", _UnhealthyAsyncClient)

    with pytest.raises(JVServerError, match="timed out during jvrt_open"):
        await manager._wait_for_server()


class _FailingAsyncClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        _ = (args, kwargs)

    async def __aenter__(self) -> _FailingAsyncClient:
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        _ = (exc_type, exc, tb)

    async def get(self, url: str) -> None:
        _ = url
        raise RuntimeError("unreachable")


@pytest.mark.asyncio
async def test_wait_for_server_uses_configured_startup_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = ProcessManager(JVServerConfig(startup_timeout=5))
    now = 0

    def fake_time() -> int:
        nonlocal now
        now += 1
        return now

    async def fake_sleep(seconds: float) -> None:
        _ = seconds

    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.httpx.AsyncClient", _FailingAsyncClient)
    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.time.time", fake_time)
    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.asyncio.sleep", fake_sleep)

    with pytest.raises(JVTimeoutError, match="5 seconds"):
        await manager._wait_for_server()
