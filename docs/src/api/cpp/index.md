# C++ サーバー API リファレンス

JVLinkServer は JV-Link COM コンポーネントをラップする C++ HTTP サーバーです。Python クライアント (PyJVLink) から利用されることを前提としていますが、HTTP API を直接呼び出すこともできます。

## HTTP エンドポイント

すべてのエンドポイントは `/` と `/v1/` の両方のプレフィックスで利用可能です。

### サーバー情報

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/health` | GET | サーバーヘルスチェック（JV-Link 状態を含む） |
| `/version` | GET | API バージョン、サーバービルド情報 |
| `/openapi.json` | GET | OpenAPI 3.0 仕様 |

### データクエリ

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/query/stored` | POST | 蓄積系データのクエリ（NDJSON ストリーム） |
| `/query/realtime` | POST | リアルタイム系データのクエリ |

### イベント

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/event/start` | POST | JV-Link イベント監視の開始 |
| `/event/stop` | POST | JV-Link イベント監視の停止 |
| `/events/stream` | GET | Server-Sent Events ストリーム |

### ファイル・画像操作

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/files/delete` | POST | JV-Link ダウンロードファイルの削除 |
| `/uniform/file` | POST | 勝負服画像の生成（ファイル保存） |
| `/uniform/image` | POST | 勝負服画像の生成（バイナリ応答） |
| `/course/file` | POST | コース図の取得（説明文付き、ファイル保存） |
| `/course/file2` | POST | コース図の取得（ファイル保存） |
| `/course/image` | POST | コース図の取得（バイナリ応答） |

### サーバー管理

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/shutdown` | POST | サーバーのグレースフルシャットダウン |

## レスポンス形式

### ストリーミングレスポンス（query/stored）

NDJSON (Newline-Delimited JSON) 形式で応答します。

```
{"meta": {"read_count": 10, "download_count": 0, "last_file_timestamp": "20240401123456"}}
{"type": "RA", "data": {...}}
{"type": "SE", "data": {...}}
```

1行目はメタデータ、2行目以降がレコードデータです。

### イベントストリーム（events/stream）

Server-Sent Events (SSE) 形式で応答します。ハートビートは 30 秒間隔で送信されます。

## CLI オプション

| オプション | 環境変数 | デフォルト | 説明 |
|---|---|---|---|
| `-p, --port` | `JVLINK_SERVER_PORT` | `8765` | リッスンポート |
| `-l, --log-level` | `JVLINK_LOG_LEVEL` | `info` | ログレベル（debug, info, warn, error） |
| `-v, --version` | - | - | バージョン情報を表示 |
| `-h, --help` | - | - | ヘルプメッセージを表示 |

### その他の環境変数

| 環境変数 | デフォルト | 説明 |
|---|---|---|
| `JVLINK_SERVER_READ_TIMEOUT` | `65` | ソケット読み取りタイムアウト（秒） |
| `JVLINK_SERVER_WRITE_TIMEOUT` | `65` | ソケット書き込みタイムアウト（秒） |
| `JVLINK_SERVER_STREAM_HEARTBEAT_SEC` | `30` | ストリーミング時のハートビート間隔（秒、0 で無効） |

## 技術仕様

- **言語**: C++17
- **HTTP ライブラリ**: cpp-httplib
- **JSON ライブラリ**: nlohmann/json
- **ログライブラリ**: spdlog
- **プラットフォーム**: Windows 32-bit（JV-Link COM 依存）
- **文字エンコーディング**: JV-Link データは Shift_JIS から UTF-8 に自動変換
- **レコードパーサー**: 38 種類の固定長レコードに対応
