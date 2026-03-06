"""Tests for runtime process manager behavior."""

from __future__ import annotations

from typing import Any

import pytest

from pyjvlink import JVServerConfig
from pyjvlink._internal.runtime import ProcessManager
from pyjvlink.errors import JVTimeoutError


def test_try_switch_to_container_host_success(monkeypatch) -> None:
    manager = ProcessManager(JVServerConfig(host="127.0.0.1", port=8765))

    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.platform.system", lambda: "Linux")
    monkeypatch.setenv("JVLINK_CONTAINER_HOST", "host.docker.internal")

    def fake_is_server_running(self):  # noqa: ANN001
        return self.config.host == "host.docker.internal"

    monkeypatch.setattr(ProcessManager, "_is_server_running", fake_is_server_running)

    assert manager._try_switch_to_container_host() is True
    assert manager.config.host == "host.docker.internal"


def test_try_switch_to_container_host_failure_restores_original_host(monkeypatch) -> None:
    manager = ProcessManager(JVServerConfig(host="localhost", port=8765))

    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.platform.system", lambda: "Linux")
    monkeypatch.setenv("JVLINK_CONTAINER_HOST", "host.docker.internal")
    monkeypatch.setattr(ProcessManager, "_is_server_running", lambda self: False)

    assert manager._try_switch_to_container_host() is False
    assert manager.config.host == "localhost"


def test_try_switch_to_container_host_is_disabled_on_windows(monkeypatch) -> None:
    manager = ProcessManager(JVServerConfig(host="localhost", port=8765))

    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.platform.system", lambda: "Windows")
    monkeypatch.setenv("JVLINK_CONTAINER_HOST", "host.docker.internal")
    monkeypatch.setattr(ProcessManager, "_is_server_running", lambda self: True)

    assert manager._try_switch_to_container_host() is False
    assert manager.config.host == "localhost"


@pytest.mark.asyncio
async def test_start_cleans_up_local_server_when_wait_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = ProcessManager(JVServerConfig(host="127.0.0.1", port=8765))
    stopped = False

    class _FakeProcess:
        pass

    monkeypatch.setattr("pyjvlink._internal.runtime.process_manager.platform.system", lambda: "Windows")
    monkeypatch.setattr(ProcessManager, "_is_server_running", lambda self: False)

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
