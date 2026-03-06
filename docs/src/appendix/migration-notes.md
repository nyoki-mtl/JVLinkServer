# Migration Notes

## 0.8 系 typed contract completion

### 変更の要点

- `query_stored` / `query_realtime` の typed record は、schema 非 reserved フィールドを全件保持するように統一
- `array:object` はすべて専用 item dataclass 化し、公開型から `tuple[dict[str, Any], ...]` を排除
- 公開 record フィールドの配列型を `tuple[...]` に統一（可変 list を非公開化）
- records ドキュメントの型名を canonical naming（`<RecordType><FieldNamePascal>Item`）へ統一

### 破壊的変更（主な例）

- `*Info` 系の旧サブ型名を廃止
  - 例: `WinOddsInfo` -> `O1WinOddsItem`
  - 例: `TrioVotingInfo` -> `H6TrifectaVotesItem`
  - 例: `HorseWeightInfo` -> `WHHorseWeightInfosItem`
- 一部レコードでフィールド名を実装名へ統一
  - `O5`: `trifecta_*` -> `trio_*`
  - `O6`: `trio_*` -> `trifecta_*`
  - `H1`: `*_votes_per_combination` -> `*_votes`, `*_refund_total_votes` -> `*_refund_votes`
  - `H6`: `trio_*` -> `trifecta_*`
  - `WF`: `multi_win_sales_votes` -> `total_tickets_sold`, `payout_info_list` -> `payout_info`
  - `YS`: `featured_races` -> `graded_race_guide`
  - `UM`: `bloodline_info` -> `pedigree_3gen`

### 互換性

- 後方互換の別名吸収は提供しない。旧型名・旧フィールド名を参照しているコードは更新が必要。

## 0.7 系アーキテクチャ再設計

### 変更の要点

- 公開 API の中心を `JVLinkClient` から `Client`（Facade）へ移行
- query 系 API を typed/raw の 2 系統に整理
  - `query_stored` / `query_realtime`（typed）
  - `query_stored_raw` / `query_realtime_raw`（wire）
- 戻り値を `StoredResult` / `RealtimeResult` + `RecordEnvelope` に統一
- `format_details()` を廃止
- `value_objects` / `mixins` を削除

### 互換性

- `JVLinkClient` は削除
- `Client` へ移行

## `_internal` パッケージ移設

### 変更の要点

- `domain`, `protocol`, `transport`, `runtime`, `constants`, `formatting`, `utils`, `codes` を `pyjvlink._internal/` へ移設
- `pyjvlink.records` から `RecordDecoder` / `create_record_from_data` の re-export を削除。decoder API は `pyjvlink.codecs` に集約
- `pyjvlink.records/<record_type>.py` 個別ファイルを削除。レコード型は `pyjvlink.records` からのみ import 可能
- `pyjvlink.formatting` と `pyjvlink.codes` は公開 façade を維持（実装本体は `_internal` へ移設）

### 公開モジュール

| モジュール | 内容 |
|---|---|
| `pyjvlink` | `Client`, `JVServerConfig`, `JVDataSpec`, exceptions |
| `pyjvlink.api` | `Client`, `StoredResult`, `RealtimeResult` |
| `pyjvlink.records` | 全レコード型 + `UnknownRecord` |
| `pyjvlink.codecs` | `RecordDecoder`, `create_record_from_data`, `decode_record_envelopes` |
| `pyjvlink.codes` | `JRACodeTables` |
| `pyjvlink.formatting` | `format_record`, `format_records` |
| `pyjvlink.types` | `JVDataSpec`, `JVServerConfig` |
| `pyjvlink.errors` | 例外階層 |

### 互換性

後方互換性なし。`pyjvlink._internal` 配下のモジュールに互換性の保証はありません。

### 移行例

旧:

```python
meta, records = await client.query_stored(...)
async for record in records:
    print(record["type"], record["data"])
```

新:

```python
result = await client.query_stored(...)
async for envelope in result.records:
    print(envelope.type, envelope.record)
```

### 未対応レコード

typed decoder で未対応のレコード種別は `UnknownRecord` で返ります。必要に応じて raw query を利用してください。
