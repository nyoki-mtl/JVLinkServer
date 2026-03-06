# JGレコード（競走馬除外情報）

## データ特性

- **配信タイミング**: 出馬投票締切後、抽選後、取消発生時
- **KEY_FIELDS**: `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`, `race_number`, `pedigree_reg_num`, `entry_order`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"JG" |
| 2 | データ区分 | data_code | JGDataCategory | 数値1桁 | 数字ゼロ | 1:初期値、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | そのレース施行回で何日目の開催 |
| 9 | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当レース番号 |
| 10 | 血統登録番号 | pedigree_reg_num | HalfWidthString | 半角10文字 | 数字ゼロ | 生年(西暦)4桁＋品種1桁＋数字5桁 |
| 11 | 馬名 | horse_name | FullWidthString | 全角18文字 | 全角スペース | 全角18字 |
| 12 | 出馬投票受付順番 | entry_order | FixedDigitInteger | 数値3桁 | 数字ゼロ | 同一業務日付で同一馬を受付した順番 |
| 13 | 出走区分 | entry_code | EntryStatus | 数値1桁 | 数字ゼロ | 1:投票馬 2:締切での除外馬 4:再投票馬 5:再投票除外馬 6:馬番を付さない出走取消馬 9:取消馬 |
| 14 | 除外状態区分 | exclusion_code | ExclusionStatus | 数値1桁 | 数字ゼロ | 1:非抽選馬 2:非当選馬 |

## 関連項目

- [DataSpec RACE](../data-specs/storage/race.md)
