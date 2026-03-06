# データ取得の基本

PyJVLink の `Client` は、蓄積系と速報系で API を分けています。

- 蓄積系: `query_stored` / `query_stored_raw`
- 速報系: `query_realtime` / `query_realtime_raw`

戻り値はいずれも `StoredResult` / `RealtimeResult` で、`meta` と `records` を持ちます。

## 蓄積系データ

```python
from pyjvlink import JVDataSpec

result = await client.query_stored(
    dataspec=[JVDataSpec.RACE, "TOKU"],
    from_datetime="20240101",
    option=1,
    to_date="20240131",
    record_types=["RA", "SE", "TK"],
)

print(result.meta)
async for envelope in result.records:
    print(envelope.type)
```

### 主なパラメータ

- `dataspec`: 例 `RACE`, `DIFF`, `TOKU`
  - 連結指定も可能（例: `RACETOKU`）
  - sequence 指定も可能（例: `["RACE", "TOKU"]`）
  - 重複指定（例: `RACERACE`）は不正として扱う
- `from_datetime`: `YYYYMMDD` または `YYYYMMDDHHMMSS`
- `option`: `1/2/3/4`
- `to_date`: 任意（DataSpec により指定可否あり）
- `record_types`: 取得するレコード種別をサーバー側でフィルタ
- `include_raw`: `RecordEnvelope.raw` を保持するか

連結 DataSpec を指定した場合、クライアントは DataSpec ごとに内部実行し、
結果ストリームと `meta` を集約して返します。

## 速報系データ

```python
from pyjvlink import RaceKeyParts

result = await client.query_realtime(
    dataspec="0B12",
    key=RaceKeyParts(
        meet_year=2024,
        meet_month=1,
        meet_day_of_month=7,
        racecourse_code="05",
        meet_round=1,
        meet_day=1,
        race_number=11,
    ),
)

async for envelope in result.records:
    print(envelope.type, envelope.record)
```

### realtime key の使い分け

- `0B14`, `0B51`: `YYYYMMDD`
- `0B11`, `0B13`, `0B15`, `0B17`: `YYYYMMDD` または `YYYYMMDDJJRR` / `YYYYMMDDJJKKHHRR`
- `0B12`, `0B20`, `0B30`-`0B36`, `0B41`, `0B42`: `YYYYMMDDJJRR` または `YYYYMMDDJJKKHHRR`
- `0B16`: `stream_events()` / `JVWatchEvent()` で受け取った `event.param`

文字列の代わりに以下も利用できます。

- date 系 DataSpec: `date` / `datetime`
- race key 系 DataSpec: `RaceKeyParts`

## option と DataSpec

`pyjvlink.types` の対応表定数で判定できます。

```python
from pyjvlink.types import VALID_DATASPECS_BY_OPTION, JVDataSpec

spec = JVDataSpec("RACE")
option = next(
    (o for o in (1, 2, 3, 4) if spec in VALID_DATASPECS_BY_OPTION.get(o, set())),
    None,
)
```

## raw query の使い所

- 未対応レコード種別を扱う
- wire payload をそのまま永続化する
- デバッグで生データを確認する

```python
raw_result = await client.query_stored_raw(
    dataspec="RACE",
    from_datetime="20240101",
    option=1,
    include_raw=True,
)
```
