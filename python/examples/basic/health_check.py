#!/usr/bin/env python3
"""Health check example."""

import asyncio
import sys

from pyjvlink import Client, JVServerConfig


async def main() -> None:
    print("JVLink Server ヘルスチェック")
    print("=" * 40)

    config = JVServerConfig(port=8765)

    try:
        async with Client(config) as client:
            health = await client.get_health()
            if health.get("status") != "healthy":
                print(f"サーバーステータス: {health.get('status', 'unknown')}")
                sys.exit(1)

            print("サーバーは正常に稼働しています")

            version = await client.get_version()
            print(f"API version: {version.get('api_version', 'unknown')}")
    except Exception as error:
        print(f"エラー: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
