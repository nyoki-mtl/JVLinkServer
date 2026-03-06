# Client

`Client` は `transport` / `runtime` / `codecs` を束ねる facade です。

## コンストラクタ

```python
Client(config: JVServerConfig | None = None, *, decoder: RecordDecoder | None = None)
```

- `config`: 接続設定。未指定時は `JVServerConfig()`。
- `decoder`: 既定は `RecordDecoder()`。

## ライフサイクル

```python
await client.start()
await client.stop()
```

または:

```python
async with Client() as client:
    ...
```

## データ取得メソッド

### typed query

```python
await client.query_stored(
    dataspec: str | JVDataSpec | Sequence[str | JVDataSpec],
    ...,
    option: int | QueryOption,
    include_raw: bool = False,
) -> StoredResult[DomainRecord]
await client.query_realtime(
    ...,
    key: str | date | datetime | RaceKeyParts,
    include_raw: bool = False,
) -> RealtimeResult[DomainRecord]
```

### raw query

```python
await client.query_stored_raw(
    dataspec: str | JVDataSpec | Sequence[str | JVDataSpec],
    ...,
    option: int | QueryOption,
    include_raw: bool = False,
) -> StoredResult[WireRecord]
await client.query_realtime_raw(
    ...,
    key: str | date | datetime | RaceKeyParts,
    include_raw: bool = False,
) -> RealtimeResult[WireRecord]
```

`StoredResult` / `RealtimeResult` は `meta` と `records` を持ちます。`records` は `RecordEnvelope` の非同期イテレータです。
`StoredResult.collect()` / `RealtimeResult.collect()` を使うと、全件を `list[RecordEnvelope[T]]` として取得できます。

`query_stored*()` の `dataspec` は、従来の連結文字列（例: `"RACETOKU"`）に加えて
`["RACE", "TOKU"]` や `[JVDataSpec.RACE, JVDataSpec.TOKU]` も指定できます。

`query_realtime*()` の `key` は必須です。形式は dataspec ごとに異なります。

- `0B14`, `0B51`: `YYYYMMDD`
- `0B11`, `0B13`, `0B15`, `0B17`: `YYYYMMDD` またはレース key
- `0B12`, `0B20`, `0B30`-`0B36`, `0B41`, `0B42`: レース key
- `0B16`: `stream_events()` / `JVWatchEvent()` の `event.param`

date 系 dataspec には `date` / `datetime` を、race key 系 dataspec には `RaceKeyParts` も渡せます。

## イベント関連

```python
client.watch_events() -> AsyncContextManager[AsyncIterator[JVLinkEvent]]
client.watch_events_raw() -> AsyncContextManager[AsyncIterator[dict[str, Any]]]
await client.start_event_watch() -> dict[str, Any]
await client.stop_event_watch() -> dict[str, Any]
await client.stream_events() -> AsyncIterator[JVLinkEvent]
await client.stream_events_raw() -> AsyncIterator[dict[str, Any]]
```

通常は `watch_events()` / `watch_events_raw()` を使います。`stream_events()` / `stream_events_raw()` は
監視開始・停止を自動では行わない低レベル API です。

## サーバー情報

```python
await client.get_health() -> HealthResponse
await client.get_version() -> VersionResponse
```

## ファイル・画像操作

```python
await client.delete_file(filename: str) -> DeleteFileResponse
await client.get_uniform(pattern: str) -> bytes
await client.save_uniform(pattern: str, filepath: str) -> SaveUniformResponse
await client.get_course(key: str) -> tuple[bytes, str]
await client.get_course_file(key: str) -> CourseFileResponse
await client.save_course(key: str, filepath: str) -> SaveCourseResponse
```

## 使用例

```python
import asyncio
from pyjvlink import Client, JVDataSpec, QueryOption

async def main() -> None:
    async with Client() as client:
        result = await client.query_stored(
            dataspec=[JVDataSpec.RACE, JVDataSpec.TOKU],
            from_datetime="20240101",
            option=QueryOption.ACCUMULATED,
            record_types=["RA", "TK"],
        )

        async for envelope in result.records:
            print(envelope.type)

asyncio.run(main())
```
