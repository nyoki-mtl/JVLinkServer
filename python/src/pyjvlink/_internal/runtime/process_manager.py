"""Runtime process manager."""

from __future__ import annotations

import asyncio
import logging
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import httpx

from pyjvlink.errors import JVConnectionError, JVServerError, JVTimeoutError
from pyjvlink.types import JVServerConfig

from .server_binary import discover_server_binary

logger = logging.getLogger(__name__)


class ProcessManager:
    """Lifecycle manager for local JVLinkServer process."""

    def __init__(self, config: JVServerConfig) -> None:
        self.config = config
        self._server_process: subprocess.Popen[Any] | None = None

    def _build_url(self, endpoint: str) -> str:
        version_agnostic_endpoints = {"/health", "/version", "/openapi.json"}
        if endpoint in version_agnostic_endpoints:
            return endpoint
        if self.config.api_version and self.config.api_version != "v1":
            return f"/{self.config.api_version}/{endpoint.lstrip('/')}"
        return endpoint

    def _base_url(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    def _probe_server(self) -> tuple[bool, bool, dict[str, Any] | None]:
        try:
            timeout = httpx.Timeout(timeout=5.0, connect=1.0, read=1.0, write=1.0, pool=5.0)
            with httpx.Client(timeout=timeout) as client:
                response = client.get(f"{self._base_url()}{self._build_url('/health')}")
                health_data = response.json()
                if not isinstance(health_data, dict):
                    return False, False, None
                status = health_data.get("status")
                return True, bool(status == "healthy"), health_data
        except (httpx.ConnectError, httpx.TimeoutException):
            return False, False, None
        except Exception as e:
            logger.warning("Unexpected error during health check: %s", e)
            return False, False, None

    def _is_server_running(self) -> bool:
        alive, healthy, _ = self._probe_server()
        return alive and healthy

    async def start(self) -> None:
        server_alive, server_healthy, health_data = self._probe_server()
        started_local_server = False

        if not server_alive and self.config.host in ("127.0.0.1", "localhost"):
            if platform.system() == "Windows":
                await self._start_server()
                started_local_server = True
            else:
                raise JVConnectionError(
                    "JVLinkServer is not running on localhost in this non-Windows environment.\n"
                    "Run JVLinkServer.exe on a Windows machine and set JVLINK_SERVER_HOST / JVLINK_SERVER_PORT "
                    "to that server."
                )
        elif not server_alive:
            raise JVConnectionError(
                f"JVLinkServer is not running on {self.config.host}:{self.config.port}\n"
                "Please start JVLinkServer on the remote host first."
            )
        elif not server_healthy:
            status = "unknown"
            if isinstance(health_data, dict):
                status = str(health_data.get("status", "unknown"))
            raise JVServerError(
                f"JVLinkServer is running on {self.config.host}:{self.config.port} but is unhealthy "
                f"(status={status}). Check /health and restart the server if needed."
            )

        try:
            await self._wait_for_server()
        except Exception:
            if started_local_server and self._server_process is not None:
                await self._stop_server()
            raise

    async def stop(self) -> None:
        if self._server_process is None:
            return
        await self._stop_server()

    def _find_server_executable(self) -> Path:
        if platform.system() != "Windows":
            raise JVServerError(
                "Local JVLinkServer is only supported on Windows.\n"
                "JV-Link is a Windows-specific COM component.\n"
                "To use PyJVLink on non-Windows systems, you must connect to a remote JVLinkServer.\n"
            )

        discovered = discover_server_binary()
        if discovered.exists:
            return discovered.path

        path_from_path = shutil.which("JVLinkServer.exe")
        if path_from_path:
            return Path(path_from_path)

        raise JVServerError(
            "JVLinkServer executable not found.\nPlace JVLinkServer.exe in pyjvlink/lib or make it available in PATH."
        )

    async def _start_server(self) -> None:
        server_exe = self._find_server_executable()
        if not server_exe.exists():
            raise JVServerError(f"Server executable not found: {server_exe}")

        try:
            kwargs: dict[str, Any] = {
                "stdout": None,
                "stderr": None,
            }
            if platform.system() == "Windows":
                kwargs["creationflags"] = 0

            self._server_process = subprocess.Popen(
                [
                    str(server_exe),
                    "--port",
                    str(self.config.port),
                    "--log-level",
                    self.config.log_level,
                    "--sid",
                    self.config.sid,
                ],
                **kwargs,
            )
            await asyncio.sleep(1.0)
        except Exception as e:
            raise JVServerError(f"Failed to start server: {e}") from e

    async def _stop_server(self) -> None:
        if self._server_process is None:
            return
        try:
            try:
                async with httpx.AsyncClient(base_url=self._base_url()) as client:
                    await client.post(self._build_url("/shutdown"), timeout=3.0)
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.warning("Graceful shutdown request failed (will force-kill): %s", e)

            if self._server_process.poll() is None:
                self._server_process.terminate()
                try:
                    await asyncio.wait_for(asyncio.to_thread(self._server_process.wait), timeout=3)
                except asyncio.TimeoutError:
                    self._server_process.kill()
                    await asyncio.wait_for(asyncio.to_thread(self._server_process.wait), timeout=2)
        finally:
            self._server_process = None

    async def _wait_for_server(self) -> None:
        start_time = time.time()
        startup_timeout = self.config.startup_timeout

        while time.time() - start_time < startup_timeout:
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    response = await client.get(f"{self._base_url()}{self._build_url('/health')}")
                    health_data = response.json()
                    if response.status_code == 200 and health_data.get("status") == "healthy":
                        return
                    if isinstance(health_data, dict) and health_data.get("status") == "unhealthy":
                        jvlink_info = health_data.get("components", {}).get("jvlink", {})
                        fault_message = jvlink_info.get("last_fault_message") if isinstance(jvlink_info, dict) else None
                        detail = f": {fault_message}" if isinstance(fault_message, str) and fault_message else ""
                        raise JVServerError(f"JVLinkServer started but reported unhealthy status{detail}")
            except Exception as e:
                logger.debug("Health check attempt failed: %s", e)
                if isinstance(e, JVServerError):
                    raise

            await asyncio.sleep(1.0)

        raise JVTimeoutError(f"Server startup timeout after {startup_timeout} seconds")
