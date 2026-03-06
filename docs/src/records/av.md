# AVレコード（出走取消・競走除外）

## データ特性

- **配信タイミング**: 出走取消・競走除外の発生時
- **KEY_FIELDS**: `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`, `race_number`, `horse_number`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"AV" |
| 2 | データ区分 | data_code | AVDataCategory | 数値1桁 | 数字ゼロ | 1:出走取消、2:競走除外 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | そのレース施行回で何日目の開催 |
| 9 | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当レース番号 |
| 10 | 発表月日時分 | announcement_datetime | DateTimeMMDDHHmm | 数値8桁 | 数字ゼロ | 月日時分各2桁 |
| 11 | 馬番 | horse_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当馬番01～18 |
| 12 | 馬名 | horse_name | FullWidthString | 全角18文字 | 全角スペース | 全角18文字 |
| 13 | 事由区分 | exclusion_reason_code | CancelReason | 数値3桁 | 半角スペース | 000:初期値　001:疾病　002:事故　003:その他 |

## 注意事項

- 項番12: 当面は全角9文字のみ設定（9文字を超える馬名は9文字までとする） 

## 関連項目

- [DataSpec 0B14](../data-specs/realtime/0b14.md)
- [DataSpec 0B16](../data-specs/realtime/0b16.md)
