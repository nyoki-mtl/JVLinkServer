# RCレコード（レコードマスタ）

## データ特性

- **配信タイミング**: レコード樹立時に随時更新
- **KEY_FIELDS**: `record_identification_code`, `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`, `race_number`, `special_race_number`, `race_type_code`, `distance`, `track_code`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"RC" |
| 2 | データ区分 | data_code | RCDataCategory | 数値1桁 | 数字ゼロ | 1:初期値、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | レコード識別区分 | record_identification_code | RecordIdentificationCategory | 数値1桁 | 数字ゼロ | 1:コースレコード、2:GⅠレコード |
| 5 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年 |
| 6 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 7 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 8 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 9 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | そのレース施行回で何日目の開催 |
| 10 | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当レース番号 |
| 11 | 特別競走番号 | special_race_number | FixedDigitInteger | 数値4桁 | 数字ゼロ | GⅠレコードのみのキー |
| 12 | 競走名本題 | race_name_main | MixedWidthStringByByte | 全角30文字 | 全角または半角スペース | 競走名の本題部分 |
| 13 | グレードコード | grade_code | Grade | 半角1文字 | 半角スペース | [グレードコード](../code-tables/basic-codes.md)参照 |
| 14 | 競走種別コード | race_type_code | RaceType | 数値2桁 | 数字ゼロ | [競走種別コード](../code-tables/race-codes.md)参照 |
| 15 | 距離 | distance | FixedDigitInteger | 数値4桁 | 数字ゼロ | 単位:メートル |
| 16 | トラックコード | track_code | Track | 数値2桁 | 数字ゼロ | [トラックコード](../code-tables/race-codes.md)参照 |
| 17 | レコード区分 | record_identification_code | RecordCategory | 数値1桁 | 数字ゼロ | 1:基準タイム、2:レコードタイム、3:参考タイム、4:備考タイム |
| 18 | レコードタイム | record_time | DurationMSS_S | 数値4桁 | 数字ゼロ | 9分99秒9形式 |
| 19 | 天候コード | weather_code | Weather | 数値1桁 | 数字ゼロ | [天候コード](../code-tables/condition-codes.md)参照 |
| 20 | 芝馬場状態コード | turf_track_condition_code | TrackCondition | 数値1桁 | 数字ゼロ | [馬場状態コード](../code-tables/condition-codes.md)参照 |
| 21 | ダート馬場状態コード | dirt_track_condition_code | TrackCondition | 数値1桁 | 数字ゼロ | [馬場状態コード](../code-tables/condition-codes.md)参照 |
| 22 | レコード保持馬情報 | record_holders | tuple[[RCRecordHoldersItem](#rcrecordholdersitem), ...] | 3要素 | 空リスト | 同着考慮3回繰り返し。最大3要素のリスト |

### RCRecordHoldersItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|-------------|------|------------------|-------|
| 22a | 血統登録番号 | pedigree_reg_num | 生年4桁＋品種1桁＋数字5桁 | HalfWidthString | 半角10文字 | 数字ゼロ |
| 22b | 馬名 | horse_name | 競走馬名 | MixedWidthStringByByte | 全角18文字 | 全角または半角スペース |
| 22c | 馬記号コード | horse_symbol_code | [馬記号コード](../code-tables/horse-codes.md)参照 | HorseSymbol | 数値2桁 | 数字ゼロ |
| 22d | 性別コード | sex_code | [性別コード](../code-tables/horse-codes.md)参照 | HorseSex | 数値1桁 | 数字ゼロ |
| 22e | 調教師コード | trainer_code | 調教師の識別コード | TrainerCode | 数値5桁 | 数字ゼロ |
| 22f | 調教師名 | trainer_name | 姓＋全角空白＋名 | MixedWidthStringByByte | 34バイト（全角17文字） | 全角または半角スペース |
| 22g | 負担重量 | impost_weight | 単位:0.1kg | CarryingWeight | 数値3桁 | 数字ゼロ |
| 22h | 騎手コード | jockey_code | 騎手の識別コード | JockeyCode | 数値5桁 | 数字ゼロ |
| 22i | 騎手名 | jockey_name | 姓＋全角空白＋名 | MixedWidthStringByByte | 34バイト（全角17文字） | 全角または半角スペース |


## 関連項目

- [DataSpec DIFF](../data-specs/storage/diff.md)
- [DataSpec DIFN](../data-specs/storage/diff.md)
- [DataSpec TCOV](../data-specs/storage/toku.md)
- [DataSpec TCVN](../data-specs/storage/toku.md)
- [DataSpec RCOV](../data-specs/storage/race.md)
- [DataSpec RCVN](../data-specs/storage/race.md)
