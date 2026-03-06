# WEレコード（天候馬場状態）

## データ特性

- **配信タイミング**: 天候・馬場状態の変更時
- **KEY_FIELDS**: `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`, `announcement_datetime`, `change_identifier`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"WE" |
| 2 | データ区分 | data_code | WEDataCategory | 数値1桁 | 数字ゼロ | 1:初期値 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | そのレース施行回で何日目の開催 |
| 9 | 発表月日時分 | announcement_datetime | DateTimeMMDDHHmm | 数値8桁 | 数字ゼロ | 月日時分各2桁 |
| 10 | 変更識別 | change_identifier | ChangeIdentifier | 数値1桁 | 数字ゼロ | 1:天候馬場初期状態　2:天候変更　3:馬場状態変更 |
| 11 | 天候状態（現在） | weather_condition | Weather | 数値1桁 | 数字ゼロ | [天候コード](../code-tables/condition-codes.md)参照 |
| 12 | 馬場状態・芝（現在） | track_condition_turf | TrackCondition | 数値1桁 | 数字ゼロ | [馬場状態コード](../code-tables/condition-codes.md)参照 |
| 13 | 馬場状態・ダート（現在） | track_condition_dirt | TrackCondition | 数値1桁 | 数字ゼロ | [馬場状態コード](../code-tables/condition-codes.md)参照 |
| 14 | 天候状態（変更前） | prev_weather_condition | Weather | 数値1桁 | 数字ゼロ | [天候コード](../code-tables/condition-codes.md)参照 |
| 15 | 馬場状態・芝（変更前） | prev_track_condition_turf | TrackCondition | 数値1桁 | 数字ゼロ | [馬場状態コード](../code-tables/condition-codes.md)参照 |
| 16 | 馬場状態・ダート（変更前） | prev_track_condition_dirt | TrackCondition | 数値1桁 | 数字ゼロ | [馬場状態コード](../code-tables/condition-codes.md)参照 |

## 関連項目

- [DataSpec 0B14](../data-specs/realtime/0b14.md)
- [DataSpec 0B16](../data-specs/realtime/0b16.md)
