# クイックスタート

## 1. クライアント初期化

```python
from pyjvlink import Client, JVServerConfig

config = JVServerConfig(
    host="127.0.0.1",
    port=8765,
    timeout=60,
)

client = Client(config)
```

`async with` を使うと `start()` / `stop()` が自動実行されます。

## 2. typed query（推奨）

```python
import asyncio
from pyjvlink import Client, JVDataSpec, QueryOption
from pyjvlink.records import RARecord

async def main() -> None:
    async with Client() as client:
        result = await client.query_stored(
            dataspec=[JVDataSpec.RACE],
            from_datetime="20240101",
            option=QueryOption.ACCUMULATED,
            record_types=["RA"],
        )

        print(result.meta)

        async for envelope in result.records:
            if isinstance(envelope.record, RARecord):
                print(envelope.record.race_id, envelope.record.race_name_main)

asyncio.run(main())
```

## 3. raw query（wire payload）

```python
result = await client.query_realtime_raw(
    dataspec="0B12",
    key="202401070511",
    include_raw=True,
)

async for envelope in result.records:
    print(envelope.type, envelope.record)
    print("raw付き:", envelope.raw is not None)
```

## 4. イベント監視

```python
async with client.watch_events() as events:
    async for event in events:
        print(event.type, event.param, event.timestamp)
```

## 次のステップ

- [データ取得の基本](../guides/dataspec-usage.md)
- [イベント監視](../guides/event-monitoring.md)
- [Python API リファレンス](../api/python/index.md)
