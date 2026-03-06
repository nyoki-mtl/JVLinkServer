"""Tests for packaged server binary discovery."""

from __future__ import annotations

from pathlib import Path

from pyjvlink._internal.runtime.server_binary import discover_server_binary


def test_discover_server_binary_uses_package_lib_directory() -> None:
    discovered = discover_server_binary()

    expected_suffix = Path("pyjvlink") / "lib" / "JVLinkServer.exe"
    assert discovered.path.as_posix().endswith(expected_suffix.as_posix())


def test_discover_server_binary_reports_existing_binary_with_custom_root(tmp_path: Path) -> None:
    binary_path = tmp_path / "lib" / "JVLinkServer.exe"
    binary_path.parent.mkdir(parents=True, exist_ok=True)
    binary_path.write_bytes(b"dummy")

    discovered = discover_server_binary(root=tmp_path)

    assert discovered.path == binary_path
    assert discovered.exists is True


def test_discover_server_binary_reports_missing_binary_with_custom_root(tmp_path: Path) -> None:
    discovered = discover_server_binary(root=tmp_path)

    assert discovered.path == tmp_path / "lib" / "JVLinkServer.exe"
    assert discovered.exists is False
