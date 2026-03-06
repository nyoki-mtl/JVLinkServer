#!/usr/bin/env python3
"""SSE relay example with FastAPI."""

import argparse
import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from pyjvlink import Client, JVServerConfig
from pyjvlink.errors import JVConnectionError, JVDataError

app = FastAPI()


def build_event_payload(event_type: str, payload: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def event_generator(config: JVServerConfig, auto_fetch: bool) -> AsyncIterator[str]:
    event_to_dataspec = {
        "JVEvtPay": "0B12",
        "JVEvtWeight": "0B11",
        "JVEvtJockeyChange": "0B16",
        "JVEvtWeather": "0B16",
        "JVEvtCourseChange": "0B16",
        "JVEvtAvoid": "0B16",
        "JVEvtTimeChange": "0B16",
    }

    try:
        async with Client(config) as client:
            await client.start_event_watch()
            try:
                async for event in client.stream_events():
                    event_payload = {
                        "type": event.type,
                        "param": event.param,
                        "timestamp": event.timestamp,
                    }
                    yield build_event_payload("jvlink_event", event_payload)

                    if not auto_fetch:
                        continue

                    dataspec = event_to_dataspec.get(event.type)
                    if dataspec is None or not event.param:
                        continue

                    try:
                        result = await client.query_realtime(dataspec=dataspec, key=event.param)
                        count = 0
                        async for envelope in result.records:
                            count += 1
                            if count > 3:
                                break
                            yield build_event_payload(
                                "realtime_record",
                                {"type": envelope.type, "record": str(envelope.record)},
                            )
                    except JVDataError as error:
                        yield build_event_payload("error", {"message": str(error), "dataspec": dataspec})
            finally:
                await client.stop_event_watch()
    except JVConnectionError as error:
        yield build_event_payload("error", {"message": str(error)})


@app.get("/events")
async def stream_events(auto_fetch: bool = False):
    config = JVServerConfig()
    return StreamingResponse(
        event_generator(config=config, auto_fetch=auto_fetch),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="JV-Link SSE relay example")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    _ = parser.parse_args()

    try:
        import uvicorn

        uvicorn.run(app, host="127.0.0.1", port=8000)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
