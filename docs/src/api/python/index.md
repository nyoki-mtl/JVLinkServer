# Python API 概要

PyJVLink の公開 API は `Client` を中心とした薄い facade です。

## 公開エントリ

```python
from pyjvlink import Client, JVDataSpec, JVServerConfig, QueryOption, RaceKeyParts
```

主要 API:

- [Client](client.md): データ取得・イベント監視
- [Config](config.md): 接続/タイムアウト設定
- [Responses](responses.md): `StoredResult`, `RealtimeResult`, `RecordEnvelope`
- [Types](types.md): `JVDataSpec`, `QueryOption`, DataSpec マッピング
- [Exceptions](exceptions.md): 例外体系
- [Codes](codes.md): コード表の参照

## データ取得 API

- typed: `query_stored`, `query_realtime`
- raw: `query_stored_raw`, `query_realtime_raw`

どちらも `RecordEnvelope` の非同期ストリームを返します。

## レコードモデル

typed query は現在サポートされている全レコード型を domain model にデコードします。
未知のレコード型や将来追加された型は `UnknownRecord` として返ります。
raw payload が必要な場合は `*_raw` または `include_raw=True` を使ってください。

## 公開境界

公開モジュールは以下の 8 つに限定されています。

| モジュール | 内容 |
|---|---|
| `pyjvlink` | `Client`, `JVServerConfig`, `JVDataSpec`, `QueryOption`, exceptions |
| `pyjvlink.api` | `Client`, `StoredResult`, `RealtimeResult` |
| `pyjvlink.records` | 全レコード型 + `UnknownRecord` |
| `pyjvlink.codecs` | `RecordDecoder`, `create_record_from_data`, `decode_record_envelopes` |
| `pyjvlink.codes` | `JRACodeTables` |
| `pyjvlink.formatting` | `format_record`, `format_records` |
| `pyjvlink.types` | `JVDataSpec`, `QueryOption`, `JVServerConfig` |
| `pyjvlink.errors` | 例外階層 |

`pyjvlink._internal` 配下はすべて非公開実装です。互換性は保証されません。

## 移行方針

公開クライアントは `Client` に統一しています。
