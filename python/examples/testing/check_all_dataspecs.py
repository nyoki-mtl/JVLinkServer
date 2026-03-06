#!/usr/bin/env python3
"""Smoke test for multiple dataspecs with the new Client API."""

import asyncio

from pyjvlink import Client, JVServerConfig


STORED_SPECS = ["TOKU", "RACE", "DIFF", "BLOD", "MING"]
REALTIME_SPECS = ["0B11", "0B12", "0B14", "0B30"]


async def probe_stored(client: Client, dataspec: str) -> None:
    result = await client.query_stored_raw(
        dataspec=dataspec,
        from_datetime="20240101",
        option=1,
        max_records=5,
    )
    count = 0
    async for _ in result.records:
        count += 1
    print(f"stored {dataspec}: {count} records")


async def probe_realtime(client: Client, dataspec: str) -> None:
    key = "20240107"
    if dataspec in {"0B11", "0B12", "0B30"}:
        key = "202401070511"

    result = await client.query_realtime_raw(dataspec=dataspec, key=key)
    count = 0
    async for _ in result.records:
        count += 1
    print(f"realtime {dataspec}: {count} records")


async def main() -> None:
    config = JVServerConfig(port=8765)
    async with Client(config) as client:
        for dataspec in STORED_SPECS:
            try:
                await probe_stored(client, dataspec)
            except Exception as error:
                print(f"stored {dataspec}: error: {error}")

        for dataspec in REALTIME_SPECS:
            try:
                await probe_realtime(client, dataspec)
            except Exception as error:
                print(f"realtime {dataspec}: error: {error}")


if __name__ == "__main__":
    asyncio.run(main())
