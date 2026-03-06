"""Tests for metadata-driven pretty formatter."""

import json

from pyjvlink.formatting import format_record, format_records


def test_format_record_with_schema_meta() -> None:
    text = format_record(
        {
            "type": "RA",
            "data_code": "1",
            "race_name_main": "弥生賞",
            "distance": 2000,
        }
    )
    assert "[RA]" in text
    assert "競走名本題: 弥生賞" in text
    assert "距離 (meters): 2000" in text


def test_format_record_falls_back_to_json_for_unknown() -> None:
    text = format_record({"type": "ZZ", "foo": "bar"})
    assert json.loads(text) == {"type": "ZZ", "foo": "bar"}


def test_format_records_joins_output() -> None:
    text = format_records(
        [
            {"type": "RA", "race_name_main": "A"},
            {"type": "RA", "race_name_main": "B"},
        ]
    )
    assert "競走名本題: A" in text
    assert "競走名本題: B" in text
    assert "\n\n" in text
