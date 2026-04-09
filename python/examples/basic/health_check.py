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
            status = health.get("status", "unknown")
            if status != "healthy":
                print(f"サーバーステータス: {status}")
                jvlink = health.get("components", {}).get("jvlink", {})
                fault_message = jvlink.get("last_fault_message") if isinstance(jvlink, dict) else None
                if fault_message:
                    print(f"JV-Link 障害詳細: {fault_message}")
                sys.exit(1)

            print("サーバーは正常に稼働しています")
            components = health.get("components", {})
            http_server = components.get("http_server", {})
            jvlink = components.get("jvlink", {})
            print(f"  - HTTPサーバー: {http_server.get('status', 'unknown')} (ポート: {http_server.get('port', 'unknown')})")
            print(
                "  - JV-Link: "
                f"{jvlink.get('status', 'unknown')} "
                f"(初期化済み: {'はい' if jvlink.get('initialized') else 'いいえ'})"
            )
            current_operation = jvlink.get("current_operation")
            if current_operation:
                print(f"  - 実行中オペレーション: {current_operation}")

            version = await client.get_version()
            print(f"API version: {version.get('api_version', 'unknown')}")
    except Exception as error:
        print(f"エラー: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
