# HSレコード（競走馬市場取引価格）

## データ特性

- **配信タイミング**: 市場終了後約1ヶ月以内（不定期）
- **KEY_FIELDS**: `pedigree_reg_num`, `organizer_market_code`, `market_period_start_date`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"HS" |
| 2 | データ区分 | data_code | HSDataCategory | 数値1桁 | 数字ゼロ | 1:初期値、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 血統登録番号 | pedigree_reg_num | HalfWidthString | 半角10文字 | 数字ゼロ | 生年(西暦)4桁＋品種1桁＋数字5桁 |
| 5 | 父馬繁殖登録番号 | sire_breeding_reg_num_hn | BreedingRegistrationNumber | 数値10桁 | 数字ゼロ | 父馬の繁殖登録番号 |
| 6 | 母馬繁殖登録番号 | dam_breeding_reg_num_hn | BreedingRegistrationNumber | 数値10桁 | 数字ゼロ | 母馬の繁殖登録番号 |
| 7 | 生年 | birth_year | DateYYYY | 数値4桁 | 数字ゼロ | 競走馬の生年（西暦） |
| 8 | 主催者・市場コード | organizer_market_code | FixedDigitInteger | 数値6桁 | 数字ゼロ | 主催者・市場毎のユニーク値 |
| 9 | 主催者名称 | organizer_name | MixedWidthStringByByte | 40バイト | 全角または半角スペース | 市場の主催者名称 |
| 10 | 市場の名称 | market_name | MixedWidthStringByByte | 80バイト | 全角または半角スペース | 市場の名称 |
| 11 | 市場の開催期間(開始日) | market_period_start_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | 市場開催期間の開始日 |
| 12 | 市場の開催期間(終了日) | market_period_end_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | 市場開催期間の終了日 |
| 13 | 取引時の競走馬の年齢 | horse_age_at_transaction | FixedDigitInteger | 数値1桁 | 数字ゼロ | 0:0歳、1:1歳、2:2歳、3:3歳など |
| 14 | 取引価格 | transaction_price | FixedDigitInteger | 数値10桁 | 数字ゼロ | 取引価格（単位：円） |

## 関連項目

- [DataSpec HOSE](../data-specs/storage/hose.md)
- [DataSpec HOSN](../data-specs/storage/hose.md)