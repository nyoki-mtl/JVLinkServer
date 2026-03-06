# Config

## `JVServerConfig`

`Client` の接続・タイムアウト・リトライ設定を定義する dataclass です。

```python
from pyjvlink import JVServerConfig

config = JVServerConfig(
    host="127.0.0.1",
    port=8765,
    timeout=60,
    stream_read_timeout=300,
)
```

## フィールド

- `host: str`（既定: `127.0.0.1`）
- `port: int`（既定: `8765`）
- `timeout: int`（既定: `60` 秒）
- `stream_read_timeout: int`（既定: `300` 秒）
- `sid: str`（既定: `UNKNOWN`）
- `startup_timeout: int`（既定: `30` 秒）
- `log_level: str`（既定: `warn`。`debug` / `info` / `warn` / `error`）
- `api_version: str`（既定: `v1`）
- `auto_retry: bool`（既定: `True`）
- `max_retries: int`（既定: `3`）
- `retry_delay_ms: int`（既定: `1000`）

## ローカル起動時のみ使う項目

以下は `Client.start()` がローカルで `JVLinkServer.exe` を自動起動する場合にのみ使われます。

- `sid`
- `startup_timeout`
- `log_level`

すでに起動済みのリモートサーバーへ接続する場合、これらの値は接続先サーバーの動作には影響しません。

## 環境変数

- `JVLINK_SERVER_HOST`
- `JVLINK_SERVER_PORT`
- `JVLINK_HTTP_TIMEOUT`
- `JVLINK_STREAM_READ_TIMEOUT`
- `JVLINK_SID`

## バリデーション

`JVServerConfig` 初期化時に主に以下を検証します。

- `port` は `1..65535`
- `host`, `sid`, `log_level`, `api_version` は文字列
- `timeout`, `stream_read_timeout`, `startup_timeout` は正の値
- `port`, `timeout`, `stream_read_timeout`, `startup_timeout`, `max_retries`, `retry_delay_ms` は整数
- `auto_retry` は真偽値
- `sid` は空文字不可、先頭空白不可、UTF-8 で 64 バイト以下
- `log_level` は許可値のみ
