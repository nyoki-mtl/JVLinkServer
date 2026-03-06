"""Tests for API facade client."""

from collections.abc import AsyncIterator
from datetime import date
from typing import Any

import pytest

from pyjvlink.api.client import Client
from pyjvlink.errors import (
    JVInvalidDataSpecError,
    JVInvalidFromTimeError,
    JVInvalidKeyError,
    JVInvalidOptionError,
    JVInvalidParameterError,
)
from pyjvlink.records import RARecord, UnknownRecord
from pyjvlink.types import JVDataSpec, QueryOption, RaceKeyParts


async def _iter_rows(rows: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for row in rows:
        yield row


class _ClosableAsyncIterator:
    def __init__(self, values: list[Any]) -> None:
        self._values = values
        self._index = 0
        self.closed = False

    def __aiter__(self) -> "_ClosableAsyncIterator":
        return self

    async def __anext__(self) -> Any:
        if self._index >= len(self._values):
            raise StopAsyncIteration
        value = self._values[self._index]
        self._index += 1
        return value

    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_start_calls_runtime_then_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    calls: list[str] = []

    async def fake_runtime_start() -> None:
        calls.append("runtime_start")

    async def fake_transport_start() -> None:
        calls.append("transport_start")

    monkeypatch.setattr(client._runtime, "start", fake_runtime_start)
    monkeypatch.setattr(client._transport, "start", fake_transport_start)

    await client.start()
    assert calls == ["runtime_start", "transport_start"]


@pytest.mark.asyncio
async def test_start_rolls_back_runtime_when_transport_start_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    calls: list[str] = []

    async def fake_runtime_start() -> None:
        calls.append("runtime_start")

    async def fake_runtime_stop() -> None:
        calls.append("runtime_stop")

    async def fake_transport_start() -> None:
        calls.append("transport_start")
        raise RuntimeError("transport failed")

    monkeypatch.setattr(client._runtime, "start", fake_runtime_start)
    monkeypatch.setattr(client._runtime, "stop", fake_runtime_stop)
    monkeypatch.setattr(client._transport, "start", fake_transport_start)

    with pytest.raises(RuntimeError, match="transport failed"):
        await client.start()

    assert calls == ["runtime_start", "transport_start", "runtime_stop"]


@pytest.mark.asyncio
async def test_stop_calls_transport_then_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    calls: list[str] = []

    async def fake_transport_stop() -> None:
        calls.append("transport_stop")

    async def fake_runtime_stop() -> None:
        calls.append("runtime_stop")

    monkeypatch.setattr(client._transport, "stop", fake_transport_stop)
    monkeypatch.setattr(client._runtime, "stop", fake_runtime_stop)

    await client.stop()
    assert calls == ["transport_stop", "runtime_stop"]


@pytest.mark.asyncio
async def test_stop_runs_runtime_cleanup_when_transport_stop_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    calls: list[str] = []

    async def fake_transport_stop() -> None:
        calls.append("transport_stop")
        raise RuntimeError("transport stop failed")

    async def fake_runtime_stop() -> None:
        calls.append("runtime_stop")

    monkeypatch.setattr(client._transport, "stop", fake_transport_stop)
    monkeypatch.setattr(client._runtime, "stop", fake_runtime_stop)

    with pytest.raises(RuntimeError, match="transport stop failed"):
        await client.stop()

    assert calls == ["transport_stop", "runtime_stop"]


@pytest.mark.asyncio
async def test_query_stored_raw_include_raw(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        return {"read_count": 1}, _iter_rows([{"type": "RA", "data": {"data_code": "1"}}])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1, include_raw=True)
    records = [record async for record in result.records]

    assert records[0].type == "RA"
    assert records[0].record["data_code"] == "1"
    assert records[0].raw == {"type": "RA", "data": {"data_code": "1"}}
    assert result.meta["fanout"] is False
    assert result.meta["completed"] is True
    assert result.meta["streamed_records"] == 1
    assert result.meta["resume_from_datetime_by_dataspec"] == {"RACE": None}


@pytest.mark.asyncio
async def test_query_stored_raw_early_close_updates_meta(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        return {"read_count": 1}, _iter_rows([{"type": "RA", "data": {"data_code": "1"}}])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1, include_raw=True)
    first = await result.records.__anext__()

    assert first.type == "RA"

    await result.records.aclose()
    assert result.meta["streamed_records"] == 1
    assert result.meta["completed"] is False


@pytest.mark.asyncio
async def test_query_stored_raw_normalizes_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: dict[str, Any] = {}

    async def fake_query_stored(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.update(kwargs)
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    await client.query_stored_raw(
        dataspec="race",
        from_datetime="20260301",
        option=1,
        to_date="20260302",
        record_types=["ra", "SE", "ra"],
    )

    assert captured["dataspec"] == "RACE"
    assert captured["from_datetime"] == "20260301000000"
    assert captured["to_date"] == "20260302235959"
    assert captured["record_types"] == ["RA", "SE"]


@pytest.mark.asyncio
async def test_query_stored_raw_accepts_query_option_enum(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: dict[str, Any] = {}

    async def fake_query_stored(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.update(kwargs)
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    await client.query_stored_raw(
        dataspec="RACE",
        from_datetime="20260301",
        option=QueryOption.ACCUMULATED,
    )

    assert captured["option"] == 1


@pytest.mark.asyncio
async def test_query_stored_raw_validates_before_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    with pytest.raises(JVInvalidDataSpecError):
        await client.query_stored_raw(dataspec="XXXX", from_datetime="20260301", option=1)

    assert called is False


@pytest.mark.asyncio
async def test_query_stored_raw_rejects_non_string_from_datetime(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    with pytest.raises(JVInvalidFromTimeError, match="from_datetime must be a string"):
        await client.query_stored_raw(dataspec="RACE", from_datetime=20260301, option=1)  # type: ignore[arg-type]

    assert called is False


@pytest.mark.asyncio
async def test_query_stored_raw_rejects_non_integer_option(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    with pytest.raises(JVInvalidOptionError, match="option must be an integer"):
        await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option="1")  # type: ignore[arg-type]

    assert called is False


@pytest.mark.asyncio
async def test_query_stored_raw_rejects_negative_retry_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    with pytest.raises(JVInvalidParameterError):
        await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1, max_retries=-1)

    with pytest.raises(JVInvalidParameterError):
        await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1, retry_delay_ms=-1)

    assert called is False


@pytest.mark.asyncio
async def test_query_stored_raw_rejects_non_integer_retry_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    with pytest.raises(JVInvalidParameterError, match="max_retries must be an integer"):
        await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1, max_retries="3")  # type: ignore[arg-type]

    with pytest.raises(JVInvalidParameterError, match="retry_delay_ms must be an integer"):
        await client.query_stored_raw(
            dataspec="RACE",
            from_datetime="20260301",
            option=1,
            retry_delay_ms="500",  # type: ignore[arg-type]
        )

    assert called is False


@pytest.mark.asyncio
async def test_query_stored_raw_rejects_invalid_max_records(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    with pytest.raises(JVInvalidParameterError, match="max_records must be an integer"):
        await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1, max_records="10")  # type: ignore[arg-type]

    with pytest.raises(JVInvalidParameterError, match="max_records must be >= -1"):
        await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1, max_records=-2)

    assert called is False


@pytest.mark.asyncio
async def test_query_stored_raw_accepts_concatenated_dataspec(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: list[dict[str, Any]] = []

    async def fake_query_stored(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.append(kwargs)
        dataspec = kwargs["dataspec"]
        if dataspec == "RACE":
            return {"read_count": 2, "download_count": 1, "last_file_timestamp": "20260301120000"}, _iter_rows([])
        if dataspec == "TOKU":
            return {"read_count": 1, "download_count": 0, "last_file_timestamp": "20260302120000"}, _iter_rows([])
        raise AssertionError(f"unexpected dataspec: {dataspec}")

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(dataspec="RACETOKU", from_datetime="20260301", option=1)
    _ = [record async for record in result.records]

    assert [call["dataspec"] for call in captured] == ["RACE", "TOKU"]
    assert result.meta["fanout"] is True
    assert result.meta["dataspecs"] == ["RACE", "TOKU"]
    assert result.meta["read_count"] == 3
    assert result.meta["download_count"] == 1
    assert result.meta["last_file_timestamp"] == "20260302120000"
    assert result.meta["completed"] is True
    assert result.meta["resume_from_datetime_by_dataspec"] == {
        "RACE": "20260301120000",
        "TOKU": "20260302120000",
    }
    assert [entry["dataspec"] for entry in result.meta["per_dataspec"]] == ["RACE", "TOKU"]


@pytest.mark.asyncio
async def test_query_stored_raw_accepts_dataspec_sequence(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: list[dict[str, Any]] = []

    async def fake_query_stored(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.append(kwargs)
        return {"read_count": 1}, _iter_rows([{"type": "RA", "data": {"data_code": "1"}}])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(
        dataspec=[JVDataSpec.RACE, "TOKU"],
        from_datetime="20260301",
        option=1,
        max_records=1,
    )
    rows = [record async for record in result.records]

    assert [call["dataspec"] for call in captured] == ["RACE"]
    assert rows[0].type == "RA"
    assert result.meta["dataspec"] == "RACETOKU"
    assert result.meta["dataspecs"] == ["RACE", "TOKU"]


@pytest.mark.asyncio
async def test_query_stored_raw_fanout_early_close_keeps_completed_false(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: list[dict[str, Any]] = []

    async def fake_query_stored(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.append(kwargs)
        dataspec = kwargs["dataspec"]
        if dataspec == "RACE":
            return {"read_count": 2}, _iter_rows(
                [
                    {"type": "RA", "data": {"data_code": "1"}},
                    {"type": "SE", "data": {"data_code": "1"}},
                ]
            )
        if dataspec == "TOKU":
            return {"read_count": 1}, _iter_rows([{"type": "TK", "data": {"data_code": "1"}}])
        raise AssertionError(f"unexpected dataspec: {dataspec}")

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(dataspec=["RACE", "TOKU"], from_datetime="20260301", option=1)
    first = await result.records.__anext__()

    assert first.type == "RA"

    await result.records.aclose()
    assert [call["dataspec"] for call in captured] == ["RACE"]
    assert result.meta["completed"] is False
    assert result.meta["per_dataspec"] == [{"dataspec": "RACE", "read_count": 2}, {"dataspec": "TOKU", "pending": True}]


@pytest.mark.asyncio
async def test_query_stored_raw_fanout_applies_global_max_records(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: list[dict[str, Any]] = []

    async def fake_query_stored(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.append(kwargs)
        dataspec = kwargs["dataspec"]
        if dataspec == "RACE":
            return {"read_count": 2}, _iter_rows(
                [
                    {"type": "RA", "data": {"data_code": "1"}},
                    {"type": "SE", "data": {"data_code": "1"}},
                ]
            )
        if dataspec == "TOKU":
            return {"read_count": 2}, _iter_rows(
                [
                    {"type": "TK", "data": {"data_code": "1"}},
                    {"type": "TK", "data": {"data_code": "1"}},
                ]
            )
        raise AssertionError(f"unexpected dataspec: {dataspec}")

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(dataspec="RACETOKU", from_datetime="20260301", option=1, max_records=3)
    rows = [record async for record in result.records]

    assert [call["dataspec"] for call in captured] == ["RACE", "TOKU"]
    assert captured[0]["max_records"] == 3
    assert captured[1]["max_records"] == 1
    assert [row.type for row in rows] == ["RA", "SE", "TK"]
    assert result.meta["streamed_records"] == 3


@pytest.mark.asyncio
async def test_query_stored_raw_fanout_max_records_zero_yields_no_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: list[dict[str, Any]] = []

    async def fake_query_stored(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.append(kwargs)
        dataspec = kwargs["dataspec"]
        if dataspec == "RACE":
            return {"read_count": 2}, _iter_rows(
                [
                    {"type": "RA", "data": {"data_code": "1"}},
                    {"type": "SE", "data": {"data_code": "1"}},
                ]
            )
        raise AssertionError(f"unexpected dataspec: {dataspec}")

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(dataspec="RACETOKU", from_datetime="20260301", option=1, max_records=0)
    rows = [record async for record in result.records]

    assert [call["dataspec"] for call in captured] == ["RACE"]
    assert captured[0]["max_records"] == 0
    assert rows == []
    assert result.meta["streamed_records"] == 0


@pytest.mark.asyncio
async def test_query_stored_raw_fanout_skips_dataspec_without_matching_record_types(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Client()
    captured: list[dict[str, Any]] = []

    async def fake_query_stored(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.append(kwargs)
        return {"read_count": 1}, _iter_rows([{"type": "TK", "data": {"data_code": "1"}}])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(
        dataspec="RACETOKU",
        from_datetime="20260301",
        option=1,
        record_types=["TK"],
    )
    rows = [record async for record in result.records]

    assert [call["dataspec"] for call in captured] == ["TOKU"]
    assert captured[0]["record_types"] == ["TK"]
    assert [row.type for row in rows] == ["TK"]
    assert [entry["dataspec"] for entry in result.meta["per_dataspec"]] == ["RACE", "TOKU"]
    assert result.meta["per_dataspec"][0]["skipped"] is True
    assert result.meta["resume_from_datetime_by_dataspec"] == {"RACE": None, "TOKU": None}


@pytest.mark.asyncio
async def test_query_stored_raw_rejects_duplicate_dataspec(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    with pytest.raises(JVInvalidDataSpecError, match="Duplicate dataspec"):
        await client.query_stored_raw(dataspec="RACERACE", from_datetime="20260301", option=1)

    assert called is False


@pytest.mark.asyncio
async def test_query_stored_raw_normalizes_record_type(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        return {"read_count": 1}, _iter_rows([{"type": "ra", "data": {"data_code": "1"}}])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1, include_raw=True)
    records = [record async for record in result.records]

    assert records[0].type == "RA"
    assert records[0].raw == {"type": "RA", "data": {"data_code": "1"}}


@pytest.mark.asyncio
async def test_query_stored_decodes_domain_records(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        return {"read_count": 2}, _iter_rows(
            [
                {
                    "type": "RA",
                    "data": {
                        "data_code": "1",
                        "data_creation_date": "20260301",
                        "meet_year": "2026",
                        "meet_date": "0301",
                        "racecourse_code": "05",
                        "meet_round": "02",
                        "meet_day": "01",
                        "race_number": "11",
                    },
                },
                {"type": "ZZ", "data": {"foo": "bar"}},
            ]
        )

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored(dataspec="RACE", from_datetime="20260301", option=1)
    records = [record async for record in result.records]

    assert isinstance(records[0].record, RARecord)
    assert isinstance(records[1].record, UnknownRecord)


@pytest.mark.asyncio
async def test_stored_result_collect(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        return {"read_count": 2}, _iter_rows(
            [
                {"type": "RA", "data": {"data_code": "1"}},
                {"type": "SE", "data": {"data_code": "1"}},
            ]
        )

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1)
    records = await result.collect()

    assert [record.type for record in records] == ["RA", "SE"]


@pytest.mark.asyncio
async def test_query_stored_raw_handles_non_mapping_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_query_stored(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        return {"read_count": 2}, _iter_rows([["not", "mapping"], {"type": "RA", "data": {"data_code": "1"}}])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1, include_raw=True)
    records = [record async for record in result.records]

    assert records[0].type == "UNKNOWN"
    assert records[0].record == {}
    assert records[0].raw == {"type": "UNKNOWN", "data": {}, "raw_row": ["not", "mapping"]}
    assert records[1].type == "RA"


@pytest.mark.asyncio
async def test_query_stored_raw_single_max_records_zero_yields_no_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: dict[str, Any] = {}

    async def fake_query_stored(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.update(kwargs)
        return {"read_count": 2}, _iter_rows(
            [
                {"type": "RA", "data": {"data_code": "1"}},
                {"type": "SE", "data": {"data_code": "1"}},
            ]
        )

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    result = await client.query_stored_raw(dataspec="RACE", from_datetime="20260301", option=1, max_records=0)
    rows = [record async for record in result.records]

    assert captured["max_records"] == 0
    assert rows == []
    assert result.meta["streamed_records"] == 0


@pytest.mark.asyncio
async def test_query_realtime_raw_normalizes_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: dict[str, Any] = {}

    async def fake_query_realtime(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.update(kwargs)
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    await client.query_realtime_raw(
        dataspec="0b16",
        key="we20240101a20120240101123456",
    )

    assert captured["dataspec"] == "0B16"
    assert captured["key"] == "WE20240101A20120240101123456"


@pytest.mark.asyncio
async def test_query_realtime_raw_accepts_date_key(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: dict[str, Any] = {}

    async def fake_query_realtime(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.update(kwargs)
        return {"count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    await client.query_realtime_raw(dataspec=JVDataSpec.SOKHO_KAISAI_BATCH, key=date(2026, 3, 1))

    assert captured["dataspec"] == "0B14"
    assert captured["key"] == "20260301"


@pytest.mark.asyncio
async def test_query_realtime_raw_accepts_race_key_parts(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    captured: dict[str, Any] = {}

    async def fake_query_realtime(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        captured.update(kwargs)
        return {"count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    await client.query_realtime_raw(
        dataspec="0B12",
        key=RaceKeyParts(
            meet_year=2026,
            meet_month=3,
            meet_day_of_month=1,
            racecourse_code="05",
            meet_round=2,
            meet_day=1,
            race_number=11,
        ),
    )

    assert captured["dataspec"] == "0B12"
    assert captured["key"] == "2026030105020111"


@pytest.mark.asyncio
async def test_realtime_result_collect(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_query_realtime(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        return {"read_count": 2}, _iter_rows(
            [
                {"type": "WE", "data": {"data_code": "1"}},
                {"type": "WE", "data": {"data_code": "2"}},
            ]
        )

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    result = await client.query_realtime_raw(dataspec="0B14", key="20240101")
    records = await result.collect()

    assert len(records) == 2
    assert records[0].type == "WE"


@pytest.mark.asyncio
async def test_query_realtime_raw_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_realtime(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    with pytest.raises(JVInvalidKeyError, match="key is required"):
        await client.query_realtime_raw(dataspec="0B12", key=None)  # type: ignore[arg-type]

    assert called is False


@pytest.mark.asyncio
async def test_query_realtime_raw_rejects_date_key_for_race_only_dataspec(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Client()
    called = False

    async def fake_query_realtime(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    with pytest.raises(JVInvalidKeyError, match="YYYYMMDDJJRR or YYYYMMDDJJKKHHRR"):
        await client.query_realtime_raw(dataspec="0B12", key="20240101")

    assert called is False


@pytest.mark.asyncio
async def test_query_realtime_raw_rejects_race_key_for_date_only_dataspec(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Client()
    called = False

    async def fake_query_realtime(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    with pytest.raises(JVInvalidKeyError, match="Use YYYYMMDD"):
        await client.query_realtime_raw(dataspec="0B14", key="202401010101")

    assert called is False


@pytest.mark.asyncio
async def test_query_realtime_raw_rejects_non_event_key_for_0b16(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_realtime(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    with pytest.raises(JVInvalidKeyError, match="TTYYYYMMDDJJRRNNNNNNNNNNNNNN"):
        await client.query_realtime_raw(dataspec="0B16", key="20240101")

    assert called is False


@pytest.mark.asyncio
async def test_query_realtime_raw_validates_before_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_realtime(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    with pytest.raises(JVInvalidKeyError):
        await client.query_realtime_raw(dataspec="0B16", key="2024/01/01")

    assert called is False


@pytest.mark.asyncio
async def test_query_realtime_raw_rejects_non_string_dataspec(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_query_realtime(**_: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        nonlocal called
        called = True
        return {"read_count": 0}, _iter_rows([])

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    with pytest.raises(JVInvalidDataSpecError):
        await client.query_realtime_raw(dataspec=1234, key="20240101")  # type: ignore[arg-type]

    assert called is False


@pytest.mark.asyncio
async def test_watch_events_controls_watch_lifecycle(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    calls: list[str] = []
    stream = _ClosableAsyncIterator(["event-1"])

    async def fake_start_event_watch() -> dict[str, Any]:
        calls.append("start")
        return {"status": "ok"}

    async def fake_stop_event_watch() -> dict[str, Any]:
        calls.append("stop")
        return {"status": "ok"}

    def fake_stream_events() -> _ClosableAsyncIterator:
        return stream

    monkeypatch.setattr(client, "start_event_watch", fake_start_event_watch)
    monkeypatch.setattr(client, "stop_event_watch", fake_stop_event_watch)
    monkeypatch.setattr(client, "stream_events", fake_stream_events)

    async with client.watch_events() as events:
        seen = [event async for event in events]

    assert seen == ["event-1"]
    assert calls == ["start", "stop"]
    assert stream.closed is True


@pytest.mark.asyncio
async def test_watch_events_stops_when_body_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    calls: list[str] = []
    stream = _ClosableAsyncIterator([])

    async def fake_start_event_watch() -> dict[str, Any]:
        calls.append("start")
        return {"status": "ok"}

    async def fake_stop_event_watch() -> dict[str, Any]:
        calls.append("stop")
        return {"status": "ok"}

    def fake_stream_events() -> _ClosableAsyncIterator:
        return stream

    monkeypatch.setattr(client, "start_event_watch", fake_start_event_watch)
    monkeypatch.setattr(client, "stop_event_watch", fake_stop_event_watch)
    monkeypatch.setattr(client, "stream_events", fake_stream_events)

    with pytest.raises(RuntimeError, match="boom"):
        async with client.watch_events():
            raise RuntimeError("boom")

    assert calls == ["start", "stop"]
    assert stream.closed is True


@pytest.mark.asyncio
async def test_delete_file_delegates_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_delete_file(filename: str) -> dict[str, Any]:
        return {"status": "success", "filename": filename}

    monkeypatch.setattr(client._transport, "delete_file", fake_delete_file)

    result = await client.delete_file("RACE20240101.jvd")
    assert result["status"] == "success"
    assert result["filename"] == "RACE20240101.jvd"


@pytest.mark.asyncio
async def test_delete_file_validates_non_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_delete_file(filename: str) -> dict[str, Any]:
        nonlocal called
        called = True
        return {"status": "success", "filename": filename}

    monkeypatch.setattr(client._transport, "delete_file", fake_delete_file)

    with pytest.raises(JVInvalidParameterError):
        await client.delete_file("  ")

    assert called is False


@pytest.mark.asyncio
async def test_delete_file_rejects_non_string(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_delete_file(filename: str) -> dict[str, Any]:
        nonlocal called
        called = True
        return {"status": "success", "filename": filename}

    monkeypatch.setattr(client._transport, "delete_file", fake_delete_file)

    with pytest.raises(JVInvalidParameterError, match="filename must be a string"):
        await client.delete_file(None)  # type: ignore[arg-type]

    assert called is False


@pytest.mark.asyncio
async def test_get_health_delegates_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_get_health() -> dict[str, Any]:
        return {"status": "healthy", "timestamp": 1711111111}

    monkeypatch.setattr(client._transport, "get_health", fake_get_health)

    result = await client.get_health()
    assert result["status"] == "healthy"


@pytest.mark.asyncio
async def test_get_version_delegates_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_get_version() -> dict[str, Any]:
        return {"api_version": "v1"}

    monkeypatch.setattr(client._transport, "get_version", fake_get_version)

    result = await client.get_version()
    assert result["api_version"] == "v1"


@pytest.mark.asyncio
async def test_get_uniform_delegates_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_get_uniform(pattern: str) -> bytes:
        return pattern.encode("utf-8")

    monkeypatch.setattr(client._transport, "get_uniform", fake_get_uniform)

    data = await client.get_uniform("水色，赤山形一本輪，水色袖")
    assert isinstance(data, bytes)
    assert data


@pytest.mark.asyncio
async def test_save_course_delegates_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_save_course(key: str, filepath: str) -> dict[str, Any]:
        return {"status": "success", "key": key, "filepath": filepath}

    monkeypatch.setattr(client._transport, "save_course", fake_save_course)

    result = await client.save_course("9999999905240011", "/tmp/course.gif")
    assert result["status"] == "success"
    assert result["key"] == "9999999905240011"


@pytest.mark.asyncio
async def test_get_course_file_delegates_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_get_course_file(key: str) -> dict[str, Any]:
        return {"status": "success", "key": key, "filepath": "C:/tmp/course.gif", "explanation": "sample"}

    monkeypatch.setattr(client._transport, "get_course_file", fake_get_course_file)

    result = await client.get_course_file("9999999905240011")
    assert result["status"] == "success"
    assert result["key"] == "9999999905240011"


@pytest.mark.asyncio
async def test_get_course_validates_non_empty_key(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_get_course(key: str) -> tuple[bytes, str]:
        nonlocal called
        called = True
        return b"", key

    monkeypatch.setattr(client._transport, "get_course", fake_get_course)

    with pytest.raises(JVInvalidParameterError):
        await client.get_course("")

    assert called is False


@pytest.mark.asyncio
async def test_get_course_file_validates_non_empty_key(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()
    called = False

    async def fake_get_course_file(key: str) -> dict[str, Any]:
        nonlocal called
        called = True
        return {"status": "success", "key": key}

    monkeypatch.setattr(client._transport, "get_course_file", fake_get_course_file)

    with pytest.raises(JVInvalidParameterError):
        await client.get_course_file(" ")

    assert called is False
