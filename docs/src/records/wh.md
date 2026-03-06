# WHレコード（馬体重）

## データ特性

- **配信タイミング**: レース当日の馬体重発表時（通常レース1時間前）
- **KEY_FIELDS**: `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`, `race_number`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"WH" |
| 2 | データ区分 | data_code | WHDataCategory | 数値1桁 | 数字ゼロ | 初期値のみ |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | そのレース施行回で何日目の開催 |
| 9 | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当レース番号 |
| 10 | 発表月日時分 | announcement_at | DateTimeMMDDHHmm | 数値8桁 | 数字ゼロ | MMDDHHMM形式 |
| 11 | 馬体重情報（18頭） | horse_weight_infos | tuple[[WHHorseWeightInfosItem](#whhorseweightinfositem), ...] | 18頭分 | 全角スペース | 馬番、馬名、体重、増減の18頭分の情報（計量中止や出走取消の場合は特定値を設定） |

### WHHorseWeightInfosItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| 11a | 馬番 | horse_number | 01～18の馬番号 | FixedDigitInteger | 数値2桁 | 数字ゼロ |
| 11b | 馬名 | horse_name | 全角18文字（現在は９文字が最長） | FullWidthString | 全角18文字 | 全角スペース |
| 11c | 馬体重 | horse_weight | 単位:kg（002～998:通常、999:計量不能、000:出走取消） | HorseWeight | 数値3桁 | 数字ゼロ |
| 11d | 増減符号 | weight_change_sign | +:増加、-:減少、空白:その他 | WeightChangeSign | 半角1文字 | 半角スペース |
| 11e | 増減差 | weight_change_diff | 単位:kg（001～998:通常、999:計量不能、000:前差なし） | WeightChangeDiff | 数値3桁 | 数字ゼロ |

#### to_dict() の出力

- `to_dict()` は次のキーを返します:
  - `horse_number`, `horse_name`, `horse_weight`, `weight_change_sign`, `weight_change_diff`, `weight_change`
- `weight_change` は `weight_change_sign` と `weight_change_diff` から合成した符号付き整数です。
  - 符号が `+` または `-` かつ差が通常値の場合のみ整数を返します。
  - 上記以外（空白や特殊値）の場合は `None` を返します。

## 関連項目

- [DataSpec 0B11](../data-specs/realtime/0b11.md)
- [AVレコード](av.md)
