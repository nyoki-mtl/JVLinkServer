# HNレコード（繁殖馬マスタ）

## データ特性

- **配信タイミング**: 蓄積系データ（月曜14:00頃、木曜20:00頃）
- **KEY_FIELDS**: `breeding_reg_num`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"HN" |
| 2 | データ区分 | data_code | HNDataCategory | 数値1桁 | 数字ゼロ | 1:新規登録、2:更新、0:削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 繁殖登録番号 | breeding_reg_num | BreedingRegistrationNumber | 数値10桁 | 数字ゼロ | 繁殖馬の登録番号 |
| 5 | 予備 | reserved_1 | ReservedField | 数値8桁 | 数字ゼロ | 予備領域 |
| 6 | 血統登録番号 | pedigree_reg_num | HalfWidthString | 半角10文字 | 数字ゼロ | 血統登録番号 |
| 7 | 予備 | reserved_2 | ReservedField | 数値1桁 | 数字ゼロ | "0"を設定 |
| 8 | 馬名 | horse_name | MixedWidthStringByByte | 36バイト | 全角または半角スペース | 繁殖馬名（全角・半角混在） |
| 9 | 馬名半角カナ | horse_name_kana | HalfWidthString | 半角40文字 | 半角スペース | 繁殖馬名の半角カナ表記 |
| 10 | 馬名欧字 | horse_name_english | MixedWidthStringByByte | 80バイト | 全角または半角スペース | 繁殖馬名の欧字表記 |
| 11 | 生年 | birth_year | DateYYYY | 数値4桁 | 数字ゼロ | 生まれ年（西暦） |
| 12 | 性別コード | sex_code | HorseSex | 数値1桁 | 数字ゼロ | [性別コード](../code-tables/horse-codes.md)参照 |
| 13 | 品種コード | breed_code | Breed | 数値1桁 | 数字ゼロ | [品種コード](../code-tables/horse-codes.md)参照 |
| 14 | 毛色コード | coat_color_code | CoatColor | 数値2桁 | 数字ゼロ | [毛色コード](../code-tables/horse-codes.md)参照 |
| 15 | 繁殖馬持込区分 | broodmare_import_code | BreedingImportCategory | 数値1桁 | 数字ゼロ | 0:内国産、1:持込、2:輸入内国産扱い、3:輸入、9:その他 |
| 16 | 輸入年 | import_year | FixedDigitInteger | 数値4桁 | 数字ゼロ | 輸入された年（西暦） |
| 17 | 産地名 | birthplace_name | MixedWidthStringByByte | 20バイト（全角10文字） | 全角スペース | 繁殖馬の産地名 |
| 18 | 父馬繁殖登録番号 | sire_breeding_reg_num_hn | BreedingRegistrationNumber | 数値10桁 | 数字ゼロ | 父馬の繁殖登録番号 |
| 19 | 母馬繁殖登録番号 | dam_breeding_reg_num_hn | BreedingRegistrationNumber | 数値10桁 | 数字ゼロ | 母馬の繁殖登録番号 |

## 注意事項

- 項番8 馬名: 外国の繁殖馬の場合は、10.馬名欧字の頭36バイトを設定。
- 項番9 馬名半角カナ: 日本語半角カナを設定（半角カナ以外の文字は設定しない）。外国繁殖馬については設定しない。
- 項番10 馬名欧字: アルファベット等以外の特殊文字については、全角で設定。

## 関連項目

- [DataSpec BLOD](../data-specs/storage/blod.md)
- [DataSpec BLDN](../data-specs/storage/blod.md)
