# WCレコード（ウッドチップ調教）

## データ特性

- **配信タイミング**: 毎日（月曜除く）
- **KEY_FIELDS**: `training_center`, `training_date`, `training_time`, `pedigree_reg_num`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"WC" |
| 2 | データ区分 | data_code | WCDataCategory | 数値1桁 | 数字ゼロ | 1:初期値、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | トレセン区分 | training_center | TrainingCenterDivision | 数値1桁 | 数字ゼロ | 0:美浦、1:栗東 |
| 5 | 調教年月日 | training_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 6 | 調教時刻 | training_time | TimeHHMM | 数値4桁 | 数字ゼロ | hhmm形式 |
| 7 | 血統登錄番号 | pedigree_reg_num | HalfWidthString | 半角10文字 | 数字ゼロ | 生年(西暦)4桁＋品種1桁＋数字5桁 |
| 8 | コース | course | WoodchipCourse | 数値1桁 | 数字ゼロ | 0:A、1:B、2:C、3:D、4:E |
| 9 | 馬場周り | direction | WoodchipDirection | 数値1桁 | 数字ゼロ | 0:右、1:左 |
| 10 | 予備 | reserved | FixedDigitInteger | 数値1桁 | 数字ゼロ | 予備フィールド |
| 11 | 10ハロンタイム合計 | total_time_10f | WoodchipTotalTime | 数値4桁 | 数字ゼロ | 2000M〜0M（単位:999.9秒） |
| 12 | ラップタイム(10F) | lap_time_10f | WoodchipLapTime | 数値3桁 | 数字ゼロ | 2000M〜1800M（単位:99.9秒） |
| 13 | 9ハロンタイム合計 | total_time_9f | WoodchipTotalTime | 数値4桁 | 数字ゼロ | 1800M〜0M（単位:999.9秒） |
| 14 | ラップタイム(9F) | lap_time_9f | WoodchipLapTime | 数値3桁 | 数字ゼロ | 1800M〜1600M（単位:99.9秒） |
| 15 | 8ハロンタイム合計 | total_time_8f | WoodchipTotalTime | 数値4桁 | 数字ゼロ | 1600M〜0M（単位:999.9秒） |
| 16 | ラップタイム(8F) | lap_time_8f | WoodchipLapTime | 数値3桁 | 数字ゼロ | 1600M〜1400M（単位:99.9秒） |
| 17 | 7ハロンタイム合計 | total_time_7f | WoodchipTotalTime | 数値4桁 | 数字ゼロ | 1400M〜0M（単位:999.9秒） |
| 18 | ラップタイム(7F) | lap_time_7f | WoodchipLapTime | 数値3桁 | 数字ゼロ | 1400M〜1200M（単位:99.9秒） |
| 19 | 6ハロンタイム合計 | total_time_6f | WoodchipTotalTime | 数値4桁 | 数字ゼロ | 1200M〜0M（単位:999.9秒） |
| 20 | ラップタイム(6F) | lap_time_6f | WoodchipLapTime | 数値3桁 | 数字ゼロ | 1200M〜1000M（単位:99.9秒） |
| 21 | 5ハロンタイム合計 | total_time_5f | WoodchipTotalTime | 数値4桁 | 数字ゼロ | 1000M〜0M（単位:999.9秒） |
| 22 | ラップタイム(5F) | lap_time_5f | WoodchipLapTime | 数値3桁 | 数字ゼロ | 1000M〜800M（単位:99.9秒） |
| 23 | 4ハロンタイム合計 | total_time_4f | WoodchipTotalTime | 数値4桁 | 数字ゼロ | 800M〜0M（単位:999.9秒） |
| 24 | ラップタイム(4F) | lap_time_4f | WoodchipLapTime | 数値3桁 | 数字ゼロ | 800M〜600M（単位:99.9秒） |
| 25 | 3ハロンタイム合計 | total_time_3f | WoodchipTotalTime | 数値4桁 | 数字ゼロ | 600M〜0M（単位:999.9秒） |
| 26 | ラップタイム(3F) | lap_time_3f | WoodchipLapTime | 数値3桁 | 数字ゼロ | 600M〜400M（単位:99.9秒） |
| 27 | 2ハロンタイム合計 | total_time_2f | WoodchipTotalTime | 数値4桁 | 数字ゼロ | 400M〜0M（単位:999.9秒） |
| 28 | ラップタイム(2F) | lap_time_2f | WoodchipLapTime | 数値3桁 | 数字ゼロ | 400M〜200M（単位:99.9秒） |
| 29 | ラップタイム(1F) | lap_time_1f | WoodchipLapTime | 数値3桁 | 数字ゼロ | 200M〜0M（単位:99.9秒） |

## 注意事項

### タイム測定に関する特殊値

- **タイム合計フィールド（項番11, 13, 15, 17, 19, 21, 23, 25, 27）**:
  - 測定不良時は`0000`
  - 999.9秒以上は`9999`をセット

- **ラップタイムフィールド（項番12, 14, 16, 18, 20, 22, 24, 26, 28, 29）**:
  - 測定不良時は`000`
  - 99.9秒以上は`999`をセット

## 関連項目

- [DataSpec WOOD](../data-specs/storage/wood.md)