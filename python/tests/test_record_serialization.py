"""Tests for domain record serialization."""

import json
from dataclasses import asdict

from pyjvlink._internal.codecs.record_decoder import RecordDecoder
from pyjvlink.records import RARecord


def test_domain_record_asdict_and_json() -> None:
    decoder = RecordDecoder()
    record = decoder.decode(
        "RA",
        {
            "data_code": "1",
            "data_creation_date": "20260301",
            "meet_year": "2026",
            "meet_date": "0301",
            "racecourse_code": "05",
            "meet_round": "02",
            "meet_day": "01",
            "race_number": "11",
            "race_name_main": "弥生賞",
            "distance": "2000",
            "track_code": "11",
            "post_time": "1545",
        },
    )
    assert isinstance(record, RARecord)

    payload = asdict(record)
    assert payload["race_name_main"] == "弥生賞"
    assert payload["distance"] == 2000

    encoded = json.dumps(payload, ensure_ascii=False, default=str)
    assert "弥生賞" in encoded
