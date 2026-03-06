# 使用例・サンプルコード

実行可能なサンプルは `python/examples` 配下を参照してください。

## 最小サンプル（蓄積系）

```python
import asyncio
from pyjvlink import Client

async def main() -> None:
    async with Client() as client:
        result = await client.query_stored(
            dataspec="RACE",
            from_datetime="20240101",
            option=1,
            record_types=["RA"],
            max_records=10,
        )

        async for envelope in result.records:
            print(envelope.type)

asyncio.run(main())
```

## raw + include_raw

```python
raw_result = await client.query_stored_raw(
    dataspec="RACE",
    from_datetime="20240101",
    option=1,
    include_raw=True,
)

async for envelope in raw_result.records:
    print(envelope.type, envelope.raw)
```

## レコードデコード（単発）

```python
from pyjvlink.codecs import create_record_from_data

row = {"type": "RA", "data": {"meet_year": "2024"}}
record = create_record_from_data(row)
print(record)
```
