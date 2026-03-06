"""Custom Hatch build hook for platform-specific wheel metadata."""

from __future__ import annotations

import base64
import csv
import hashlib
import platform
import tempfile
import zipfile
from pathlib import Path

try:
    from hatchling.builders.hooks.plugin.interface import BuildHookInterface
except ModuleNotFoundError:  # pragma: no cover - exercised outside build backends
    class BuildHookInterface:  # type: ignore[override]
        def __init__(self, *args, **kwargs) -> None:
            pass


def _build_record_entry(path: str, data: bytes) -> list[str]:
    digest = hashlib.sha256(data).digest()
    encoded_digest = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return [path, f"sha256={encoded_digest}", str(len(data))]


def inject_bundled_executable_into_wheel(wheel_path: Path, bundled_exe_path: Path) -> None:
    """Inject the Windows server executable into a built wheel and refresh RECORD."""

    target_member = "pyjvlink/lib/JVLinkServer.exe"
    executable_bytes = bundled_exe_path.read_bytes()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".whl", dir=wheel_path.parent) as tmp_file:
        temp_wheel_path = Path(tmp_file.name)

    try:
        with zipfile.ZipFile(wheel_path, "r") as source_wheel, zipfile.ZipFile(
            temp_wheel_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as target_wheel:
            record_name = next(name for name in source_wheel.namelist() if name.endswith(".dist-info/RECORD"))
            record_rows: list[list[str]] = []

            with source_wheel.open(record_name) as record_file:
                decoded_lines = (line.decode("utf-8") for line in record_file)
                for row in csv.reader(decoded_lines):
                    if row and row[0] != target_member:
                        record_rows.append(row)

            for source_info in source_wheel.infolist():
                if source_info.filename in {record_name, target_member}:
                    continue
                target_wheel.writestr(source_info, source_wheel.read(source_info.filename))

            target_wheel.writestr(target_member, executable_bytes)
            record_rows.append(_build_record_entry(target_member, executable_bytes))

            record_bytes = "".join(",".join(row) + "\n" for row in record_rows + [[record_name, "", ""]]).encode("utf-8")
            target_wheel.writestr(record_name, record_bytes)

        temp_wheel_path.replace(wheel_path)
    finally:
        temp_wheel_path.unlink(missing_ok=True)


class CustomBuildHook(BuildHookInterface):
    """Control wheel metadata for Windows bundled builds."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def initialize(self, version: str, build_data: dict) -> None:
        # Editable installs (PEP 660) must keep working on non-Windows
        # for docs/lint workflows.
        if version != "standard":
            return

        bundled_exe = Path("src/pyjvlink/lib/JVLinkServer.exe")

        # Windows build with bundled JVLinkServer.exe should be platform-specific.
        if platform.system() == "Windows":
            if bundled_exe.exists():
                build_data["pure_python"] = False
                build_data["tag"] = "py3-none-win_amd64"

        # On non-Windows, keep default pure-python wheel for remote-server mode.

    def finalize(self, version: str, build_data: dict, artifact_path: str) -> None:
        if version != "standard":
            return

        if platform.system() != "Windows":
            return

        bundled_exe = Path("src/pyjvlink/lib/JVLinkServer.exe")
        if not bundled_exe.exists():
            return

        inject_bundled_executable_into_wheel(Path(artifact_path), bundled_exe)
