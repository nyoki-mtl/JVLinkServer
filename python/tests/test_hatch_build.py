from __future__ import annotations

import csv
import importlib.util
import zipfile
from pathlib import Path

_MODULE_PATH = Path(__file__).resolve().parents[1] / "hatch_build.py"
_SPEC = importlib.util.spec_from_file_location("hatch_build", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

inject_bundled_executable_into_wheel = _MODULE.inject_bundled_executable_into_wheel


def test_inject_bundled_executable_into_wheel_updates_record(tmp_path: Path) -> None:
    wheel_path = tmp_path / "pyjvlink-0.8.0-py3-none-win_amd64.whl"
    bundled_exe_path = tmp_path / "JVLinkServer.exe"
    bundled_exe_path.write_bytes(b"fake-exe")

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as wheel:
        wheel.writestr("pyjvlink/__init__.py", "__version__ = '0.8.0'\n")
        wheel.writestr(
            "pyjvlink-0.8.0.dist-info/RECORD",
            "pyjvlink/__init__.py,,\npyjvlink-0.8.0.dist-info/RECORD,,\n",
        )

    inject_bundled_executable_into_wheel(wheel_path, bundled_exe_path)

    with zipfile.ZipFile(wheel_path) as wheel:
        assert wheel.read("pyjvlink/lib/JVLinkServer.exe") == b"fake-exe"

        rows = list(csv.reader(wheel.read("pyjvlink-0.8.0.dist-info/RECORD").decode("utf-8").splitlines()))
        record_map = {row[0]: row[1:] for row in rows}

    assert "pyjvlink/lib/JVLinkServer.exe" in record_map
    assert record_map["pyjvlink/lib/JVLinkServer.exe"][0].startswith("sha256=")
    assert record_map["pyjvlink/lib/JVLinkServer.exe"][1] == str(len(b"fake-exe"))
