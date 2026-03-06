# イベント監視

`Client` では以下の手順でイベント監視します。

1. `watch_events()` を開始
2. `async for` で購読

`watch_events()` は監視の開始・停止を自動で行います。

## 基本例

```python
async with client.watch_events() as events:
    async for event in events:
        print(event.type, event.param, event.timestamp)
```

`event.type` は `JVEvtPay`, `JVEvtWeight` などの JV-Link イベント名です。

低レベル制御が必要な場合は、従来どおり `start_event_watch()` / `stream_events()` / `stop_event_watch()` も使えます。

## イベント起点で速報データを取得

```python
event_to_dataspec = {
    "JVEvtPay": "0B12",
    "JVEvtWeight": "0B11",
    "JVEvtJockeyChange": "0B16",
    "JVEvtWeather": "0B16",
    "JVEvtCourseChange": "0B16",
    "JVEvtAvoid": "0B16",
    "JVEvtTimeChange": "0B16",
}

async with client.watch_events() as events:
    async for event in events:
        dataspec = event_to_dataspec.get(event.type)
        if not dataspec or not event.param:
            continue

        result = await client.query_realtime(dataspec=dataspec, key=event.param)
        async for envelope in result.records:
            print("fetched", envelope.type)
```
