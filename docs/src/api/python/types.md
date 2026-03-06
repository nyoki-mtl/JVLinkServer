# 型定義

## `JVDataSpec`

`JVDataSpec` は DataSpec を表す `str Enum` です。

例:

- 蓄積系: `RACE`, `TOKU`, `DIFF`, `BLOD`, `MING` など
- 速報系: `0B11`, `0B12`, `0B14`, `0B30` など

```python
from pyjvlink import JVDataSpec

spec = JVDataSpec.RACE
```

## `QueryOption`

`QueryOption` は `query_stored` / `query_stored_raw` の `option` 引数に渡す `IntEnum` です。

```python
from pyjvlink import QueryOption

option = QueryOption.ACCUMULATED
```

- `QueryOption.ACCUMULATED` (`1`): 蓄積系データ
- `QueryOption.WEEKLY` (`2`): 今週データ
- `QueryOption.SETUP` (`3`): セットアップデータ
- `QueryOption.SETUP_NO_DIALOG` (`4`): セットアップ（ダイアログなし）

`int`（`1/2/3/4`）も引き続き利用可能です。

## `JVServerConfig`

接続設定の詳細は [Config](config.md) を参照してください。

## `RaceKeyParts` と race key helper

`RaceKeyParts` は realtime の race key を構築するための dataclass です。

```python
from pyjvlink import RaceKeyParts, build_race_key, build_race_key_short

parts = RaceKeyParts(
    meet_year=2026,
    meet_month=3,
    meet_day_of_month=1,
    racecourse_code="05",
    meet_round=2,
    meet_day=1,
    race_number=11,
)

full_key = build_race_key(parts)          # 2026030105020111
short_key = build_race_key_short(parts)   # 202603010511
```

`query_realtime()` / `query_realtime_raw()` には、この `RaceKeyParts` を `key` としてそのまま渡すこともできます。

## DataSpec 補助定数

`pyjvlink.types` は以下の定数を提供します。

- `DATASPEC_TO_RECORDS`: DataSpec -> レコード種別タプル
- `REALTIME_DATASPECS`: 速報系 DataSpec セット
- `VALID_DATASPECS_BY_OPTION`: option ごとの許可 DataSpec

## option と DataSpec の対応確認

```python
from pyjvlink.types import VALID_DATASPECS_BY_OPTION, JVDataSpec

spec = JVDataSpec.RACE
is_supported = spec in VALID_DATASPECS_BY_OPTION[1]
```

`query_stored()` / `query_stored_raw()` の `dataspec` は、連結文字列だけでなく
`Sequence[str | JVDataSpec]` も受け取ります。

## 関連

- [Client](client.md)
- [Responses](responses.md)
- [DataSpec一覧](../../data-specs/index.md)
