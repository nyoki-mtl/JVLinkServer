# JV-Link 前提条件

## 1. 実行環境

- JV-Link は Windows 専用 32-bit COM コンポーネントです。
- JVLinkServer は Windows 32-bit で実行する必要があります。
- 開発・ビルド・テストも Windows ネイティブ環境を前提とします。

## 2. 認証・初期化

- JV-Link の利用には JRA-VAN の契約・サービスキー設定が必要です。
- `JVServerConfig.sid` は `JVInit` 時の SID として使われます（既定値: `UNKNOWN`）。

```python
from pyjvlink import Client, JVServerConfig

config = JVServerConfig(sid="YOUR_SOFTWARE_ID")
client = Client(config)
```

## 3. 配信スケジュール

- データ供給がない時間帯があります。
- 詳細は [配信スケジュール](../appendix/delivery-schedule.md) を参照してください。

## 4. リソース管理

`Client` はコンテキストマネージャで使うことを推奨します。

```python
async with Client() as client:
    ...
```

これにより終了時のクリーンアップが自動化されます。
