# エラーコード一覧

PyJVLink使用時に発生する可能性のあるエラーの一覧です。

## PyJVLink例外クラス

PyJVLinkが発生させる例外とその対処法です。

### 基本例外クラス階層

```
JVLinkError (基底クラス)
├── JVServerError        # サーバー関連エラー
│   └── JVOpenError      # JVOpen関連エラー
├── JVConnectionError    # 接続エラー
├── JVDataError          # データ処理エラー
│   ├── JVValidationError       # 入力検証エラー
│   │   ├── JVInvalidDataSpecError  # 無効なデータ種別
│   │   ├── JVInvalidOptionError    # 無効なオプション値
│   │   ├── JVInvalidFromTimeError  # 無効な開始時刻
│   │   ├── JVInvalidKeyError       # 無効なキー
│   │   └── JVInvalidParameterError # その他の入力不正
│   └── JVNoDataError           # 互換用。現行 query API は通常 raise しない
└── JVTimeoutError       # タイムアウトエラー
```

### 接続関連

| 例外クラス | 説明 | 対処法 |
|-----------|------|--------|
| `JVConnectionError` | JVLinkServerに接続できない | JVLinkServerが起動しているか確認、ポート番号が正しいか確認、ファイアウォール設定を確認 |
| `JVTimeoutError` | リクエストタイムアウト | タイムアウト値を延長、サーバーの負荷を確認、大量データの場合はストリーミングを使用 |

### サーバー関連

| 例外クラス | 説明 | 対処法 |
|-----------|------|--------|
| `JVServerError` | サーバー側のエラー（HTTP 5xx） | サーバーログを確認、JV-Linkの状態を確認 |
| `JVOpenError` | JVOpen関数のエラー（エラーコード付き） | エラーコードを確認（下記参照）、パラメータを確認 |

### データ関連

| 例外クラス | 説明 | 対処法 |
|-----------|------|--------|
| `JVDataError` | データ処理の一般的エラー | レスポンス形式を確認、データの整合性を確認 |
| `JVInvalidDataSpecError` | 無効なデータ種別指定 | 有効なDataSpec名を使用、スペルミスを確認 |
| `JVInvalidOptionError` | 無効なオプション値 | オプションは1, 2, 3, 4のいずれか |
| `JVInvalidFromTimeError` | 無効な開始時刻 | `YYYYMMDD` または `YYYYMMDDHHMMSS` 形式を使用 |
| `JVNoDataError` | 互換用の no-data 例外 | 現行の `query_stored*` / `query_realtime*` は no-data を空結果で返す |

## JVOpenエラーコード

JVOpen関数の戻り値（エラーコード）は`JVOpenError`例外の`error_code`属性で取得できます。

**注意**: エラーコード `-1`（該当データなし）は、現行の `query_stored*` / `query_realtime*` では正常な空結果として扱われ、例外は発生しません。

```python
try:
    result = await client.query_stored(
        dataspec="RACE",
        from_datetime="20240101",
        option=1,
    )
    records = [envelope async for envelope in result.records]
    if not records:
        print("該当データなし")
except JVOpenError as e:
    print(f"JVOpenエラー: {e.error_code} - {e}")
    if e.error_code == -301:
        print("認証エラー: サービスキーを確認してください")
except JVServerError as e:
    print(f"サーバーエラー: {e}")
```

### 認証関連エラー

| コード | 意味 | 対処法 |
|--------|------|--------|
| -301 | 認証エラー | サービスキーが正しくない、複数のマシンで同一サービスキーを使用、サービスキーが未設定。[前提条件](../getting-started/prerequisites.md)を参照 |
| -302 | サービス有効期限切れ | Data Lab.サービスの有効期限が切れている |
| -303 | サービスキーが設定されていない | JVSetServiceKey関数でキーを設定 |
| -304 | レーシングビュアー認証エラー | JRAレーシングビュアー連携機能の利用申請が必要 |

### 共通コード

| コード | 意味 | 対処法 |
|--------|------|--------|
| -1 | 該当データなし | `query_stored*` / `query_realtime*` では空結果として扱われる |
| -2 | 不正なリクエスト | リクエスト全体の前提条件を確認 |
| -3 | ダウンロード中 | 通常はサーバー側で吸収される。継続する場合はサーバーログを確認 |

### パラメータエラー

| コード | 意味 | 対処法 |
|--------|------|--------|
| -100 | 汎用パラメータエラー | パラメータ全体を確認 |
| -111 | `dataspec` が不正 | 有効な DataSpec を使用 |
| -112 | その他パラメータが不正 | 入力値の形式を確認 |
| -113 | `from_datetime` / `to_date` が不正 | `YYYYMMDD` または `YYYYMMDDHHMMSS` を使用 |
| -114 | `key` が不正 | realtime key の形式を確認 |
| -115 | `option` が不正 | 1, 2, 3, 4 のいずれかを使用 |
| -116 | `dataspec` の指定数が不正 | 連結指定の個数を確認 |
| -118 | `filepath` が不正 | 保存先パスを確認 |

### 状態エラー

| コード | 意味 | 対処法 |
|--------|------|--------|
| -201 | `JVInit` が行われていない | サーバーを再起動し、JV-Link 初期化を確認 |
| -202 | 前回の `JVOpen` が継続中 | 前のクエリが完了するまで待機 |
| -203 | `JVOpen` が行われていない | サーバー状態と呼び出し順序を確認 |
| -211 | レジストリ内容不正 | レジストリが不正に変更された、または保存パスが存在しない |

### ファイル・ダウンロードエラー

| コード | 意味 | 対処法 |
|--------|------|--------|
| -401 | JV-Link内部エラー | サーバーを再起動、エラーログを確認 |
| -402 | ダウンロードファイルのヘッダが異常 | `delete_file()` で削除して再試行 |
| -403 | ダウンロードファイルの内容が異常 | `delete_file()` で削除して再試行 |
| -411 | サーバー HTTP 404 | エンドポイントやサーバー設定を確認 |
| -412 | サーバー HTTP 403 | 認可設定やサーバー状態を確認 |
| -413 | その他のサーバー HTTP エラー | サーバーログを確認 |
| -421 | サーバーレスポンス不正 | レスポンス整合性とサーバーログを確認 |
| -431 | サーバーアプリ内部エラー | サーバー側の例外を確認 |
| -501 | セットアップ用スタートキット不正 | セットアップ環境を確認 |
| -502 | ダウンロード失敗（通信/ディスクエラーなど） | ネットワーク接続やディスク状態を確認、`auto_retry=True` を使用 |
| -503 | ファイルが見つからない | ダウンロード先や保存先を確認 |
| -504 | サーバーメンテナンス中 | メンテナンス時間を避けて利用 |

### ファイル読み取り時の特殊な戻り値

| 戻り値 | 意味 | 説明 |
|--------|------|------|
| -1 | ファイル切り替わり | 物理ファイルの終わりを示す（エラーではない） |
| 0 | 全ファイル読み取り完了 | すべてのデータを読み終えた |

## HTTPステータスコード

JVLinkServerが返すHTTPステータスコードです。

### 成功

| コード | 説明 |
|--------|------|
| 200 | OK - 正常にデータを取得 |
| 204 | No Content - データは存在しないが正常 |

### クライアントエラー（4xx）

| コード | 説明 | 対処法 |
|--------|------|--------|
| 400 | Bad Request | リクエストパラメータを確認 |
| 404 | Not Found | エンドポイントURLを確認 |
| 422 | Unprocessable Entity | パラメータの形式を確認 |

### サーバーエラー（5xx）

| コード | 説明 | 対処法 |
|--------|------|--------|
| 500 | Internal Server Error | JVLinkServerのログを確認 |
| 502 | Bad Gateway | JV-Linkの状態を確認 |
| 503 | Service Unavailable | サーバーを再起動 |

## よくあるエラーパターン

### サービスキー未設定

```
AuthenticationError: JV-Link authentication failed (code: -301)
```

→ [JV-Link 前提条件](../getting-started/prerequisites.md)を参照してサービスキーを設定

### データが見つからない

```
結果は空です（例外なし）
```

→ `async for` や `collect()` の結果件数、配信スケジュール、日付範囲を確認

### サーバー接続失敗

```
JVConnectionError: HTTP connection failed: ...
```

→ JVLinkServerが起動しているか確認

## 関連項目

- [トラブルシューティング](../guides/troubleshooting.md) - 問題解決ガイド
- [APIリファレンス - 例外](../api/python/exceptions.md) - 例外クラスの詳細仕様
- [JV-Link 前提条件](../getting-started/prerequisites.md) - サービスキー等の設定
