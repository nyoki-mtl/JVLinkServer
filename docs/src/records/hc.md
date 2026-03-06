# HCレコード（坂路調教）

## データ特性

- **配信タイミング**: 毎日（月曜除く）、トレセン単位
- **KEY_FIELDS**: `training_center_code`, `training_date`, `training_time`, `pedigree_reg_num`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"HC" |
| 2 | データ区分 | data_code | HCDataCategory | 数値1桁 | 数字ゼロ | 1:初期値、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | トレセン区分 | training_center_code | TrainingCenterDivision | 数値1桁 | 数字ゼロ | 0:美浦、1:栗東 |
| 5 | 調教年月日 | training_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 6 | 調教時刻 | training_time | TimeHHMM | 数値4桁 | 数字ゼロ | hhmm形式 |
| 7 | 血統登録番号 | pedigree_reg_num | HalfWidthString | 半角10文字 | 数字ゼロ | 生年(西暦)4桁＋品種1桁＋数字5桁 |
| 8 | 4ハロンタイム合計 | total_time_4f | DurationSSS_S | 数値4桁 | 数字ゼロ | 800M～0M、単位:0.1秒 |
| 9 | ラップタイム（800M～600M） | lap_time_800_600 | DurationSS_S | 数値3桁 | 数字ゼロ | 単位:0.1秒 |
| 10 | 3ハロンタイム合計 | total_time_3f | DurationSSS_S | 数値4桁 | 数字ゼロ | 600M～0M、単位:0.1秒 |
| 11 | ラップタイム（600M～400M） | lap_time_600_400 | DurationSS_S | 数値3桁 | 数字ゼロ | 単位:0.1秒 |
| 12 | 2ハロンタイム合計 | total_time_2f | DurationSSS_S | 数値4桁 | 数字ゼロ | 400M～0M、単位:0.1秒 |
| 13 | ラップタイム（400M～200M） | lap_time_400_200 | DurationSS_S | 数値3桁 | 数字ゼロ | 単位:0.1秒 |
| 14 | ラップタイム（200M～0M） | lap_time_200_0 | DurationSS_S | 数値3桁 | 数字ゼロ | 単位:0.1秒 |

## 関連項目

- [DataSpec SLOP](../data-specs/storage/slop.md)