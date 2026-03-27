# コマンドラインインターフェース (CLI)

## 概要

PyJVLinkは、JV-Linkサーバーと対話するためのコマンドラインインターフェース（CLI）を提供します。`pyjvlink`コマンドを通じて、ターミナルから直接JV-Linkのデータにアクセスしたり、サーバーの状態を確認したりできます。

ローカルホスト（127.0.0.1 / localhost）に接続する場合、CLIは必要に応じて`JVLinkServer.exe`を自動起動します。リモートホストを指定する際は、接続先でサーバーが稼働していることを確認してください。

## インストールとヘルプ

```bash
# PyJVLinkをインストール
pip install pyjvlink

# CLIのヘルプメッセージを表示
pyjvlink --help
```

## コマンド一覧

### health - サーバーヘルスチェック

サーバーが正常に起動し、応答しているかを確認します。

```bash
pyjvlink health
```

**出力例:**

- **正常時:**
  ```
  [OK] Server is healthy
  ```
- **エラー時:**
  ```
  [FAIL] Cannot connect to JVLinkServer
  ```

### version - バージョン情報取得

JVLinkラッパーサーバー、API、およびJV-Linkコンポーネント自体のバージョン情報を表示します。

```bash
pyjvlink version
```

**出力例:**

```
API version: 1.0.0
Server version: unknown
Build date: 2024-04-01
```

### query-stored - 蓄積系データクエリ

指定した条件で蓄積系データを検索し、取得します。

```bash
pyjvlink query-stored <dataspec> <from_datetime> <option> [オプション]
```

**必須引数:**

- `<dataspec>`: データ種別ID（例: `RACE`, `TOKU`）。詳細は[データ種別](../guides/dataspec-usage.md)を参照。
- `<from_datetime>`: 取得を開始する日時 (`YYYYMMDD` または `YYYYMMDDHHMMSS` 形式)。
- `<option>`: クエリオプション (`1`: 蓄積, `2`: 今週, `3`: セットアップ, `4`: セットアップ(ダイアログなし))。

**オプション引数:**

- `--sid <SESSION_ID>`: セッションID（デフォルト: `"UNKNOWN"`）。
- `--max-records <N>`: 取得する最大レコード数（デフォルト: `-1`で全件取得）。
- `--to-date <DATETIME>`: 取得を終了する日時 (`YYYYMMDD` または `YYYYMMDDHHMMSS` 形式)。
- `--record-types <TYPE> [TYPE ...]` : 取得するレコード種別をスペース区切りで指定（例: `RA SE HR`）。
- `--auto-retry`: `JV-Data-0B-File-Damaged`エラー時に自動でリトライします。
- `--max-retries <N>`: 自動リトライの最大回数。
- `--retry-delay-ms <MS>`: リトライ時の待機時間（ミリ秒）。
- `--format <FORMAT>`: 出力形式（`json` | `raw`、デフォルト: `json`）。

**使用例:**

```bash
# 2024年4月1日のレース情報を取得
pyjvlink query-stored RACE 20240401 1

# レコード種別をフィルタリング（レース情報と出走馬情報のみ）
pyjvlink query-stored RACE 20240401 1 --record-types RA SE

# 期間を指定し、最大100件まで取得
pyjvlink query-stored RACE 20240401 1 --to-date 20240407 --max-records 100

# 自動リトライを設定して実行
pyjvlink query-stored RACE 20240401 1 --auto-retry --max-retries 5
```

### query-realtime - リアルタイム系データクエリ

リアルタイムで提供されるデータを取得します。

```bash
pyjvlink query-realtime <dataspec> [オプション]
```

**必須引数:**

- `<dataspec>`: データ種別ID（例: `0B12`, `0B15`）。詳細は[データ種別](../guides/dataspec-usage.md)を参照。

**オプション引数:**

- `--key <KEY>`: 必須。レースキーや開催日キーなど、データ種別に応じたキー。
- `--format <FORMAT>`: 出力形式（`json` | `raw`、デフォルト: `json`）。

**使用例:**

```bash
# 速報レース結果を取得 (キーを指定)
pyjvlink query-realtime 0B12 --key 202401070511

# 速報馬体重を開催日単位で取得
pyjvlink query-realtime 0B11 --key 20240107
```

## 出力形式

### JSON形式（デフォルト）

取得したデータは、メタ情報とレコードのリストを含むJSONオブジェクトとして標準出力に書き出されます。

```bash
pyjvlink query-stored RACE 20240401 1 --max-records 1
```

**出力例:**

```json
{
  "meta": {
    "read_count": 1,
    "download_count": 0,
    "last_file_timestamp": "20240401123456"
  },
  "records": [
    {
      "type": "RA",
      "data": {
        "race_key": "20240401050301",
        "race_name": "桜花賞",
        "distance": 1600
      }
    }
  ]
}
```

### Raw形式

`--format raw` を指定すると、JV-Linkから取得した生のレコード文字列がそのまま出力されます。

```bash
pyjvlink query-stored RACE 20240401 1 --format raw --max-records 2
```

**出力例:**

```
RA20240401050101...
SE20240401050101...
```

## 環境変数

CLIの一部の動作は、環境変数で設定できます。

- `JVLINK_SERVER_HOST`: 接続先ホスト名。DevContainerやWSL2では`host.docker.internal`等を指定。
- `JVLINK_SERVER_PORT`: JVLinkラッパーサーバーのポート番号。
- `JVLINK_HTTP_TIMEOUT`: HTTPリクエスト全体のタイムアウト秒。
- `JVLINK_STREAM_READ_TIMEOUT`: ストリーミング読み取りタイムアウト秒。
- `JVLINK_LOG_LEVEL`: ログレベル (`debug`, `info`, `warn`, `error`)。
- `JVLINK_SERVER_STREAM_HEARTBEAT_SEC`: ストリーミング時に空行を定期送信する間隔（秒）。既定は30、`0` で無効。
- `GITHUB_TOKEN`: サーバー実行ファイルをダウンロードする際に使用するGitHubトークン。

## エラーハンドリングと終了コード

CLIは、処理の成功または失敗を示す終了コードを返します。

- `0`: 正常終了
- `1`: エラー（接続失敗、無効なパラメータ、データエラーなど）

エラーが発生した場合、詳細は標準エラー出力に表示されます。

**エラー例:**

```bash
$ pyjvlink query-stored INVALID_SPEC 20240401 1
[FAIL] Error: Unknown dataspec: 'INVALID_SPEC'. ...
$ echo $?
1
```

## 実装について

CLIは `pyjvlink.cli` モジュールで実装されており、Pythonの `Client` クラスを利用しています。CLIコマンドは、`Client` の対応メソッドを呼び出す薄いラッパーとして機能します。

例えば、以下のCLIコマンドは、

```bash
pyjvlink query-stored RACE 20240401 1 --record-types RA SE
```

内部的には、以下のようなPythonコードを実行するのと同等です。

```python
import asyncio
from pyjvlink import Client

async def main():
    async with Client() as client:
        result = await client.query_stored(
            dataspec="RACE",
            from_datetime="20240401",
            option=1,
            record_types=["RA", "SE"]
        )
        async for envelope in result.records:
            print(envelope.type)

asyncio.run(main())
```
