"""Tests for public module exports."""

from __future__ import annotations

import logging
from pathlib import Path

import pyjvlink
from pyjvlink.codecs import create_record_from_data
from pyjvlink.codes import JRACodeTables
from pyjvlink.formatting import format_record, format_records
from pyjvlink.records import UnknownRecord
from pyjvlink.types import RaceKeyParts, build_race_key, build_race_key_short


def test_package_entrypoint_exports_core_symbols_only() -> None:
    assert "Client" in pyjvlink.__all__
    assert "JVServerConfig" in pyjvlink.__all__
    assert "build_race_key" in pyjvlink.__all__
    assert "RARecord" not in pyjvlink.__all__


def test_package_logger_has_null_handler() -> None:
    package_logger = logging.getLogger("pyjvlink")
    assert any(isinstance(handler, logging.NullHandler) for handler in package_logger.handlers)


def test_unknown_record_is_publicly_exported() -> None:
    assert UnknownRecord.__name__ == "UnknownRecord"


def test_create_record_from_data_is_publicly_exported() -> None:
    assert callable(create_record_from_data)


def test_codes_table_is_publicly_exported() -> None:
    assert JRACodeTables.RACECOURSE_CODES["05"] == "東京競馬場"


def test_formatting_helpers_are_publicly_exported() -> None:
    assert callable(format_record)
    assert callable(format_records)


def test_race_key_helpers_are_publicly_exported() -> None:
    parts = RaceKeyParts(
        meet_year=2026,
        meet_month=3,
        meet_day_of_month=1,
        racecourse_code="05",
        meet_round=2,
        meet_day=1,
        race_number=11,
    )

    assert build_race_key(parts) == "2026030105020111"
    assert build_race_key_short(parts) == "202603010511"


def test_records_module_has_no_individual_record_files() -> None:
    """Individual record .py files should be deleted; only __init__.py remains."""
    records_dir = Path(pyjvlink.__file__).parent / "records"
    py_files = [f.name for f in records_dir.glob("*.py") if f.name != "__init__.py"]
    assert py_files == [], f"Unexpected record files found: {py_files}"


def test_records_all_does_not_contain_decoder_symbols() -> None:
    """RecordDecoder and create_record_from_data belong to pyjvlink.codecs, not records."""
    import pyjvlink.records as records_mod

    assert "RecordDecoder" not in records_mod.__all__
    assert "create_record_from_data" not in records_mod.__all__
