"""Runtime process manager."""

from __future__ import annotations

import asyncio
import logging
import os
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

    def _is_server_running(self) -> bool:
        try:
            timeout = httpx.Timeout(timeout=5.0, connect=1.0, read=1.0, write=1.0, pool=5.0)
            with httpx.Client(timeout=timeout) as client:
                response = client.get(f"{self._base_url()}{self._build_url('/health')}")
                if response.status_code != 200:
                    return False
                health_data = response.json()
                return bool(health_data.get("status") == "healthy")
        except (httpx.ConnectError, httpx.TimeoutException):
            return False
        except Exception as e:
            logger.warning("Unexpected error during health check: %s", e)
            return False

    def _try_switch_to_container_host(self) -> bool:
        if platform.system() == "Windows":
            return False

        fallback_host = os.environ.get("JVLINK_CONTAINER_HOST", "host.docker.internal").strip()
        if not fallback_host or fallback_host in ("127.0.0.1", "localhost"):
            return False

        original_host = self.config.host
        self.config.host = fallback_host
        if self._is_server_running():
            return True
        self.config.host = original_host
        return False

    async def start(self) -> None:
        server_running = self._is_server_running()
        started_local_server = False

        if not server_running and self.config.host in ("127.0.0.1", "localhost"):
            if platform.system() == "Windows":
                await self._start_server()
                started_local_server = True
            else:
                server_running = self._try_switch_to_container_host()
                if not server_running:
                    raise JVConnectionError(
                        "JVLinkServer is not running on localhost in this non-Windows environment.\n"
                        "Run JVLinkServer.exe on the host and set JVLINK_SERVER_HOST=host.docker.internal.\n"
                        "You can also set JVLINK_CONTAINER_HOST to customize the fallback host."
                    )
        elif not server_running:
            raise JVConnectionError(
                f"JVLinkServer is not running on {self.config.host}:{self.config.port}\n"
                "Please start JVLinkServer on the remote host first."
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
                    if response.status_code == 200 and response.json().get("status") == "healthy":
                        return
            except Exception as e:
                logger.debug("Health check attempt failed: %s", e)

            await asyncio.sleep(1.0)

        raise JVTimeoutError(f"Server startup timeout after {startup_timeout} seconds")
