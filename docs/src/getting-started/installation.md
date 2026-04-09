# インストール

## 要件

- Python 3.10 以上
- JVLinkServer への接続先
  - Windows: ローカルで自動起動
  - Linux/macOS: Windows ホスト上の JVLinkServer へ接続
- JV-Link（JRA-VAN 提供）が Windows 側にインストール済み

## pip インストール

```bash
pip install pyjvlink
```

GitHub 版を使う場合:

```bash
pip install git+https://github.com/nyoki-mtl/JVLinkServer.git#subdirectory=python
```

## リモート Windows サーバーへの接続

```powershell
$env:JVLINK_SERVER_HOST = "192.168.10.20"
$env:JVLINK_SERVER_PORT = "8765"
```

## 動作確認

```python
import asyncio
from pyjvlink import Client

async def check() -> None:
    async with Client() as client:
        health = await client.get_health()
        print(health)

asyncio.run(check())
```

## 補足

- `Client()` は `host=127.0.0.1` 接続時にサーバー起動を試みます。
- Linux/macOS ではローカル自動起動は行わず、接続先サーバーが必要です。
