# コード表

## 概要

`pyjvlink.codes.JRACodeTables` は、JRA コード値を日本語名称へ変換するための辞書を提供します。

```python
from pyjvlink.codes import JRACodeTables

print(JRACodeTables.RACECOURSE_CODES["05"])  # 東京競馬場
print(JRACodeTables.WEATHER_CODES["1"])     # 晴
```

## 主なコード表

- `RACECOURSE_CODES`
- `WEEKDAY_CODES`
- `WEATHER_CODES`
- `GRADE_CODES`
- `RACE_TYPE_CODES`
- `RACE_SYMBOL_CODES`
- `TRACK_CODES`
- `TRACK_CONDITION_CODES`
- `BREED_CODES`
- `HORSE_SEX_CODES`

詳細は [コード表リファレンス](../../code-tables/index.md) を参照してください。
