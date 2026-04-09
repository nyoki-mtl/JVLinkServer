# PyJVLink

JRA-VAN Data Lab JV-Link を Python から利用するための非同期クライアントライブラリ。

Windows では `JVLinkServer.exe` の自動起動に対応し、Linux/macOS ではリモート接続モードで利用できます。

[オンラインドキュメント](https://nyoki-mtl.github.io/JVLinkServer/) | [PyPI](https://pypi.org/project/pyjvlink/) | [Releases](https://github.com/nyoki-mtl/JVLinkServer/releases)

## 特徴

- `async/await` ベースの API
- NDJSON ストリーミング対応
- typed query / raw query の両系統
- `RecordEnvelope` で一貫した戻り値
- `Sequence[JVDataSpec | str]` を受け取る柔軟な DataSpec 指定
- realtime race key helper (`RaceKeyParts`, `build_race_key*`)
- SSE イベント監視 (`watch_events`, `stream_events`)

## 前提条件

- Python 3.10 以上
- 接続先の JVLinkServer
  - Windows: ローカル自動起動
  - Linux/macOS: Windows 上の JVLinkServer へ接続

## インストール

```bash
pip install git+https://github.com/nyoki-mtl/JVLinkServer.git#subdirectory=python
```

## クイックスタート

```python
import asyncio
from pyjvlink import Client

async def main() -> None:
    async with Client() as client:
        result = await client.query_stored(
            dataspec=["RACE", "TOKU"],
            from_datetime="20240101",
            option=1,
            record_types=["RA", "TK"],
        )

        print(result.meta)

        async for envelope in result.records:
            print(envelope.type)

if __name__ == "__main__":
    asyncio.run(main())
```

## 主要API

- `Client.query_stored(...) -> StoredResult[DomainRecord]`
- `Client.query_realtime(...) -> RealtimeResult[DomainRecord]`
- `Client.query_stored_raw(...) -> StoredResult[WireRecord]`
- `Client.query_realtime_raw(...) -> RealtimeResult[WireRecord]`
- `Client.watch_events() -> AsyncContextManager[AsyncIterator[JVLinkEvent]]`
- `Client.stream_events() -> AsyncIterator[JVLinkEvent]`
- `Client.delete_file(filename) -> dict`
- `Client.get_uniform(pattern) -> bytes`
- `Client.save_uniform(pattern, filepath) -> dict`
- `Client.get_course(key) -> tuple[bytes, str]`
- `Client.get_course_file(key) -> dict`
- `Client.save_course(key, filepath) -> dict`

`StoredResult` / `RealtimeResult` は次の構造です。

- `meta`: サーバーからのメタ情報
- `records`: `RecordEnvelope` の非同期イテレータ

realtime 系では `key` に文字列だけでなく `date` / `datetime` / `RaceKeyParts` も渡せます。

## API 方針

公開クライアントは `Client` を使用します。

## CLI

```bash
pyjvlink health
pyjvlink version
pyjvlink query-stored RACE 20240101 1 --max-records 10
pyjvlink query-realtime 0B12 --key 202401070511
```

`pyjvlink health` が `unhealthy` を返した場合は、`components.jvlink.last_fault_message` を確認してください。

## 開発

Windows ネイティブ環境を前提とします。

```powershell
uv sync --all-extras
uv run ruff check src tests
uv run ty check src/pyjvlink
uv run pytest tests -v
```
