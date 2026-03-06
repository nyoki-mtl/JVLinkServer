#!/usr/bin/env python3
"""Basic stored-data retrieval example."""

import asyncio
from datetime import datetime, timedelta

from pyjvlink import Client, JVServerConfig
from pyjvlink.formatting import format_record


async def main() -> None:
    print("JVLink データ取得サンプル")
    print("=" * 40)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    from_datetime = start_date.strftime("%Y%m%d")

    print(f"取得期間: {start_date.strftime('%Y/%m/%d')} 以降")
    print("データ種別: RACE")
    print()

    config = JVServerConfig(port=8765)

    async with Client(config) as client:
        print("データを取得中...")
        result = await client.query_stored(
            dataspec="RACE",
            from_datetime=from_datetime,
            option=1,
            max_records=10,
            record_types=["RA"],
        )

        print(f"read_count={result.meta.get('read_count', 0)}")
        print(f"download_count={result.meta.get('download_count', 0)}")
        print()

        shown = 0
        async for envelope in result.records:
            print(format_record(envelope.record, record_type=envelope.type))
            shown += 1
            if shown >= 3:
                break


if __name__ == "__main__":
    asyncio.run(main())
