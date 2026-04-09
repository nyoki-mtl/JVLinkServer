# トラブルシューティング

## 接続できない

症状: `JVConnectionError`

確認項目:

1. Windows 側で `JVLinkServer.exe` が起動しているか
2. `JVLINK_SERVER_HOST` / `JVLINK_SERVER_PORT` が正しいか
3. ファイアウォールでポートが遮断されていないか

```python
from pyjvlink import Client, JVServerConfig

config = JVServerConfig(host="192.168.10.20", port=8765)
async with Client(config) as client:
    print(await client.get_health())
```

## 入力検証エラー

症状: `JVInvalidDataSpecError`, `JVInvalidOptionError`, `JVInvalidFromTimeError`, `JVInvalidKeyError`

確認項目:

- `dataspec` が正しいか
- `option` と `dataspec` の組み合わせが正しいか
- 日付/キー形式が正しいか

## タイムアウト

症状: `JVTimeoutError`

対策:

- `JVServerConfig.timeout` を延長
- `query_stored(..., stream_read_timeout=...)` を調整
- 長いストリーミングでは `JVLINK_SERVER_STREAM_HEARTBEAT_SEC` を確認する（既定: `30` 秒、`0` で無効）
- `record_types` を指定して取得量を絞る

## サーバーは応答するが JV-Link が利用できない

症状: `JVUnavailableError`, `/health` が `503` かつ `status: "unhealthy"`

確認項目:

- `/health` の `components.jvlink.last_fault_message`
- `components.jvlink.current_operation`
- `metrics.unavailable`

対応:

- `last_fault_message` に `timed out` が含まれる場合は、JV-Link 内部処理が停止した可能性が高いです
- この状態は自動回復しないため、`JVLinkServer.exe` を再起動してください
- 再発する場合はサーバーログの直前の `JVRTOpen` / `JVOpen` を確認してください

## 認証・JVOpenエラー

症状: `JVOpenError`（例: `-301`）

確認項目:

- JRA-VAN 契約状態
- JV-Link のサービスキー設定
- Windows 環境で JV-Link が正常に初期化できているか

## 補足

- Linux/macOS では JV-Link 自体は動作しません。Windows 上のサーバーが必須です。
- 公開クライアントは `Client` です。
