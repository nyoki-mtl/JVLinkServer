"""Minimum E2E regression tests per dataspec (stored/realtime)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest

from pyjvlink.api.client import Client
from pyjvlink.records import UnknownRecord
from pyjvlink.types import DATASPEC_TO_RECORDS, REALTIME_DATASPECS, VALID_DATASPECS_BY_OPTION, JVDataSpec


async def _iter_rows(rows: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for row in rows:
        yield row


def _realtime_key_for(spec: JVDataSpec) -> str:
    if spec in {JVDataSpec.SOKHO_KAISAI_BATCH, JVDataSpec.SOKHO_WIN5}:
        return "20260301"
    if spec == JVDataSpec.SOKHO_KAISAI_SHITEI:
        return "WE20260301A20120260301123456"
    if spec in {
        JVDataSpec.BATAI,
        JVDataSpec.SOKHO_DATA_MINING,
        JVDataSpec.SOKHO_RACE_UMA,
        JVDataSpec.SOKHO_DM_TAISEN,
    }:
        return "20260301"
    return "202603010101"


@pytest.mark.asyncio
async def test_stored_dataspecs_minimum_e2e_decode(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_query_stored(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        spec = JVDataSpec(kwargs["dataspec"])
        first_record_type = DATASPEC_TO_RECORDS[spec][0]
        return {"read_count": 1}, _iter_rows([{"type": first_record_type, "data": {}}])

    monkeypatch.setattr(client._transport, "query_stored", fake_query_stored)

    stored_specs = sorted(
        (spec for spec in DATASPEC_TO_RECORDS if spec not in REALTIME_DATASPECS), key=lambda s: s.value
    )
    for spec in stored_specs:
        option = next((o for o in [1, 2, 3, 4] if spec in VALID_DATASPECS_BY_OPTION.get(o, set())), None)
        assert option is not None

        result = await client.query_stored(spec.value, "20260301", option)
        records = [record async for record in result.records]

        assert len(records) == 1
        assert records[0].type == DATASPEC_TO_RECORDS[spec][0]
        assert not isinstance(records[0].record, UnknownRecord)


@pytest.mark.asyncio
async def test_realtime_dataspecs_minimum_e2e_decode(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client()

    async def fake_query_realtime(**kwargs: Any) -> tuple[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        spec = JVDataSpec(kwargs["dataspec"])
        first_record_type = DATASPEC_TO_RECORDS[spec][0]
        return {"count": 1}, _iter_rows([{"type": first_record_type, "data": {}}])

    monkeypatch.setattr(client._transport, "query_realtime", fake_query_realtime)

    realtime_specs = sorted(REALTIME_DATASPECS, key=lambda s: s.value)
    for spec in realtime_specs:
        result = await client.query_realtime(spec.value, key=_realtime_key_for(spec))
        records = [record async for record in result.records]

        assert len(records) == 1
        assert records[0].type == DATASPEC_TO_RECORDS[spec][0]
        assert not isinstance(records[0].record, UnknownRecord)
