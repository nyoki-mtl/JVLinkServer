# JVLinkServer

JVLinkServer は、JRA-VAN の JV-Link（Windows 専用 32-bit COM）を HTTP サーバーでラップし、
Python から非同期 API で利用できるようにするプロジェクトです。

## アーキテクチャ

```
Python App <--> pyjvlink.api.Client <--> transport/runtime/codecs <--> JVLinkServer.exe <--> JV-Link COM
```

## Python クライアントの公開 API

- `Client`: 新アーキテクチャの facade API（推奨）
- `JVServerConfig`: 接続・タイムアウト・リトライ設定
- `JVDataSpec`: DataSpec Enum
- 主要例外: `JVConnectionError`, `JVDataError`, `JVValidationError` など

## 最小サンプル

```python
import asyncio
from pyjvlink import Client, QueryOption

async def main() -> None:
    async with Client() as client:
        result = await client.query_stored(
            dataspec="RACE",
            from_datetime="20240101",
            option=QueryOption.ACCUMULATED,
            record_types=["RA"],
        )
        async for envelope in result.records:
            print(envelope.type)

asyncio.run(main())
```

## API 方針

公開クライアントは `Client` に統一しています。

詳しくは [インストール](getting-started/installation.md) と [クイックスタート](getting-started/quickstart.md) を参照してください。
