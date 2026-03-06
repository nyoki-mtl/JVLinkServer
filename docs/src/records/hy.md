# HYレコード（馬名の意味由来）

## データ特性

- **配信タイミング**: 火曜不定期
- **KEY_FIELDS**: `pedigree_reg_num`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"HY" |
| 2 | データ区分 | data_code | HYDataCategory | 数値1桁 | 数字ゼロ | 1:初期値、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 血統登録番号 | pedigree_reg_num | HalfWidthString | 半角10文字 | 数字ゼロ | 生年(西暦)4桁＋品種1桁＋数字5桁 |
| 5 | 馬名 | horse_name | FullWidthString | 36バイト（全角18文字） | 全角スペース | 競走馬の正式名称 |
| 6 | 馬名の意味由来 | horse_name_meaning_origin | FullWidthString | 64バイト（全角32文字） | 全角スペース | 馬名の意味や命名の由来 |

## 関連項目

- [DataSpec HOYU](../data-specs/storage/hoyu.md)
