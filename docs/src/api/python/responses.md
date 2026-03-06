# レスポンスと戻り値

## 概要

`Client` の query 系メソッドは以下を返します。

- `StoredResult[T]`
- `RealtimeResult[T]`

`T` は typed query では `DomainRecord`、raw query では `WireRecord` です。

## `StoredResult` / `RealtimeResult`

```python
@dataclass(frozen=True, slots=True)
class StoredResult(Generic[T]):
    meta: StoredQueryMeta
    records: AsyncIterator[RecordEnvelope[T]]
    async def collect(self) -> list[RecordEnvelope[T]]: ...
```

`RealtimeResult` は `meta: RealtimeQueryMeta` を持ち、同様に `collect()` を提供します。

## `StoredResult.meta` の主なキー

`query_stored` / `query_stored_raw` の `meta` は、単一 DataSpec・複数 DataSpec の両方で
同じ形を返します。

- `fanout`: `bool`
- `dataspec`: `str`（連結済み DataSpec 文字列）
- `dataspecs`: `list[str]`（4文字 DataSpec の配列）
- `read_count`: `int`
- `download_count`: `int`
- `last_file_timestamp`: `str`
- `resume_from_datetime_by_dataspec`: `dict[str, str | None]`
- `per_dataspec`: `list[dict[str, Any]]`
- `streamed_records`: `int`
- `completed`: `bool`
  - `True`: 全件読み切った、または `max_records` に達した
  - `False`: 利用側が途中で stream を閉じたため、まだ読めるデータが残っている

## `RecordEnvelope`

```python
@dataclass(frozen=True, slots=True)
class RecordEnvelope(Generic[T]):
    type: str
    record: T
    raw: dict[str, Any] | None = None
```

- `type`: 正規化済みレコード種別（例: `RA`）
- `record`: typed または raw payload
- `raw`: `include_raw=True` のときのみ保持

typed query の場合は、通常 `envelope.type` と `envelope.record.type` は同じ値です。  
レコード種別の分岐には `envelope.type` を使うと、raw/typed で同じ書き方にできます。

## typed query の例

```python
result = await client.query_stored("RACE", "20240101", 1)

async for envelope in result.records:
    print(envelope.type, envelope.record)
```

## raw query の例

```python
result = await client.query_stored_raw(
    dataspec="RACE",
    from_datetime="20240101",
    option=1,
    include_raw=True,
)

async for envelope in result.records:
    print(envelope.type, envelope.record, envelope.raw)
```
