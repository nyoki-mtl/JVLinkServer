# YSレコード（開催スケジュール）

## データ特性

- **配信タイミング**: 年末（翌年分）、月曜14:00頃（更新）
- **KEY_FIELDS**: `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"YS" |
| 2 | データ区分 | data_code | YSDataCategory | 数値1桁 | 数字ゼロ | 1:開催予定(年末時点)　2:開催予定(開催直前時点)　3:開催終了(成績確定時点) 9:開催中止　0:該当レコード削除(提供ミスなどの理由による) |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年（西暦） |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | その開催回で何日目の開催 |
| 9 | 曜日コード | weekday_code | Weekday | 数値1桁 | 数字ゼロ | [曜日コード](../code-tables/basic-codes.md)参照 |
| 10 | 重賞案内 | graded_race_guide | tuple[YSGradedRaceGuideItem, ...] | 可変長 | 空リスト | 重賞レース情報のリスト |

### YSGradedRaceGuideItem（重賞レース情報）

| サブ項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数 | 初期値 | 説明 |
|----------|-------------|-------------|-----|------------|--------|------|
| 10a | 特別競走番号 | special_race_number | FixedDigitInteger | 数値4桁 | 数字ゼロ | 重賞レースのみ設定 |
| 10b | 競走名本題 | race_name_main | MixedWidthStringByByte | 全角30文字 | 全角または半角スペース | レース名の本題 |
| 10c | 競走名略称10文字 | race_short_name_10 | MixedWidthStringByByte | 全角10文字 | 全角または半角スペース | 競走名略称 |
| 10d | 競走名略称6文字 | race_short_name_6 | MixedWidthStringByByte | 全角6文字 | 全角または半角スペース | 競走名略称 |
| 10e | 競走名略称3文字 | race_short_name_3 | MixedWidthStringByByte | 全角3文字 | 全角または半角スペース | 競走名略称 |
| 10f | 重賞回次[第N回] | graded_race_round_number | FixedDigitInteger | 数値3桁 | 数字ゼロ | 重賞としての通算回数 |
| 10g | グレードコード | grade_code | Grade | 半角1文字 | 半角スペース | [グレードコード](../code-tables/basic-codes.md)参照※ |
| 10h | 競走種別コード | race_type_code | RaceType | 数値2桁 | 数字ゼロ | [競走種別コード](../code-tables/race-codes.md)参照 |
| 10i | 競走記号コード | race_symbol_code | RaceSymbol | 数値3桁 | 数字ゼロ | [競走記号コード](../code-tables/race-codes.md)参照 |
| 10j | 重量種別コード | weight_type_code | WeightType | 数値1桁 | 数字ゼロ | [重量種別コード](../code-tables/race-codes.md)参照 |
| 10k | 距離 | distance | FixedDigitInteger | 数値4桁 | 数字ゼロ | 単位：メートル |
| 10l | トラックコード | track_code | Track | 数値2桁 | 数字ゼロ | [トラックコード](../code-tables/race-codes.md)参照 |

## 注意事項

- ※ 項番10g グレードコード: グレード表記(G) または その他の重賞表記（Jpn）の判別方法については、特記事項を参照。

## 関連項目

- [DataSpec YSCH](../data-specs/storage/ysch.md)
