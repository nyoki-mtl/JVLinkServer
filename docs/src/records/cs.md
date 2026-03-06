# CSレコード（コース情報）

## データ特性

- **配信タイミング**: 随時（コース改修時等）
- **KEY_FIELDS**: `racecourse_code`, `distance`, `track_code`, `course_renovation_date`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"CS" |
| 2 | データ区分 | data_code | CSDataCategory | 数値1桁 | 数字ゼロ | 1:新規登録、2:更新、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 5 | 距離 | distance | FixedDigitInteger | 数値4桁 | 数字ゼロ | 単位:メートル |
| 6 | トラックコード | track_code | Track | 数値2桁 | 数字ゼロ | [トラックコード](../code-tables/race-codes.md)参照 |
| 7 | コース改修年月日 | course_renovation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 8 | コース説明 | course_description | MixedWidthStringByByte | 6800バイト | 半角スペース | テキスト(6800バイト) |

## 関連項目

- [DataSpec COMM](../data-specs/storage/comm.md) - 各種解説情報（コース情報を含む）
