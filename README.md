# JVLinkServer

JRA-VAN Data Lab の JV-Link を HTTP API でラップし、Python から扱いやすくするための C++ サーバーと Python クライアントです。

[オンラインドキュメント](https://nyoki-mtl.github.io/JVLinkServer/) | [PyPI](https://pypi.org/project/pyjvlink/) | [Releases](https://github.com/nyoki-mtl/JVLinkServer/releases)

## 概要

JV-Link は JRA-VAN が提供する Windows 専用の 32-bit COM コンポーネントです。JVLinkServer はこれを C++ HTTP サーバーでラップし、`pyjvlink` から非同期 API として利用できるようにします。

```
Python App <--> pyjvlink.api.Client <--> transport/runtime/codecs <--> JVLinkServer.exe <--> JV-Link COM
```

## 主な機能

- JV-Link データ取得の HTTP API 化
- `pyjvlink.Client` による非同期アクセス
- NDJSON ストリーミングと typed record decoding
- リアルタイム監視、勝負服画像、コース図取得
- Windows 同梱 wheel と Linux/macOS 向け portable wheel の両対応

## 前提条件

- Windows 10/11（サーバー実行環境）
- JRA-VAN Data Lab ソフトウェア（JV-Link 含む）
- Python 3.10 以上（PyJVLink 利用時）

## インストール

```bash
pip install pyjvlink
```

## 使用方法

最小例:

```python
import asyncio
from pyjvlink import Client

async def main() -> None:
    async with Client() as client:
        result = await client.query_stored(
            dataspec="RACE",
            from_datetime="20240101",
        )
        async for envelope in result.records:
            print(envelope.type, envelope.record)

if __name__ == "__main__":
    asyncio.run(main())
```

詳細な使い方、対応 DataSpec、CLI、API リファレンスはオンラインドキュメントを参照してください。

## リポジトリ構成

- `src/`, `include/`: Windows 32-bit C++ サーバー
- `python/`: `pyjvlink` パッケージとテスト
- `docs/`: MkDocs ドキュメント
- `agent-docs/`: 内部向け仕様書と開発メモ

## ライセンス

MIT License. 詳細は [LICENSE](LICENSE) を参照。
