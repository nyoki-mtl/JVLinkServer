#!/usr/bin/env python3
"""Basic event streaming example."""

import asyncio
from datetime import datetime

from pyjvlink import Client, JVServerConfig


async def main() -> None:
    print("JVLink イベント監視サンプル")
    print("=" * 40)
    print("イベント監視を開始します... (Ctrl+C で終了)")

    config = JVServerConfig(port=8765)
    event_count = 0

    async with Client(config) as client:
        await client.start_event_watch()
        try:
            async for event in client.stream_events():
                event_count += 1
                event_time = (
                    datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S")
                    if event.timestamp is not None
                    else "unknown"
                )
                print(f"[{event_time}] {event.type} param={event.param}")
        except asyncio.CancelledError:
            pass
        finally:
            await client.stop_event_watch()

    print(f"受信イベント数: {event_count}")


if __name__ == "__main__":
    asyncio.run(main())
