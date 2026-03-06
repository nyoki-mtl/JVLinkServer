# SKレコード（産駒マスタ）

## データ特性

- **配信タイミング**: 産駒登録時および更新時
- **KEY_FIELDS**: `pedigree_reg_num`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"SK" |
| 2 | データ区分 | data_code | SKDataCategory | 数値1桁 | 数字ゼロ | 1:新規登録、2:更新、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 血統登録番号 | pedigree_reg_num | HalfWidthString | 半角10文字 | 数字ゼロ | 生年(西暦)4桁＋品種1桁＋数字5桁 |
| 5 | 生年月日 | birth_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 6 | 性別コード | sex_code | HorseSex | 数値1桁 | 数字ゼロ | [性別コード](../code-tables/horse-codes.md)参照 |
| 7 | 品種コード | breed_code | Breed | 数値1桁 | 数字ゼロ | [品種コード](../code-tables/horse-codes.md)参照 |
| 8 | 毛色コード | coat_color_code | CoatColor | 数値2桁 | 数字ゼロ | [毛色コード](../code-tables/horse-codes.md)参照 |
| 9 | 産駒持込区分 | foal_import_code | FoalImportCategory | 数値1桁 | 数字ゼロ | 0:内国産、1:持込、2:輸入内国産扱い、3:輸入 |
| 10 | 輸入年 | import_year | FixedDigitInteger | 数値4桁 | 数字ゼロ | 西暦4桁 |
| 11 | 生産者コード | breeder_code | BreederCode | 数値8桁 | 数字ゼロ | 生産者マスタと連携 |
| 12 | 産地名 | birthplace_name | FullWidthString | 全角10文字 | 全角スペース | 生産地の名称 |
| 13 | 3代血統 繁殖登録番号 | pedigree_3gen_breeding_reg_nums | list[BreedingRegistrationNumber] | 数値10桁×14（14要素のリスト） | 数字ゼロ | 14頭分の繁殖登録番号（各10桁） |

## 3代血統繁殖登録番号（項番13）の詳細構造

### 血統順序（14世代の格納順序）

血統情報は`pedigree_3gen_breeding_reg_nums`リストに格納されます。各要素には以下のプロパティでアクセスできます：

| 順序 | 世代 | リストインデックス | プロパティ名 |
|------|------|-----------------|-------------|
| 1 | 父 | `pedigree_3gen_breeding_reg_nums[0]` | `sire_id` |
| 2 | 母 | `pedigree_3gen_breeding_reg_nums[1]` | `dam_id` |
| 3 | 父父 | `pedigree_3gen_breeding_reg_nums[2]` | `sires_sire_id` |
| 4 | 父母 | `pedigree_3gen_breeding_reg_nums[3]` | `sires_dam_id` |
| 5 | 母父 | `pedigree_3gen_breeding_reg_nums[4]` | `dams_sire_id` |
| 6 | 母母 | `pedigree_3gen_breeding_reg_nums[5]` | `dams_dam_id` |
| 7 | 父父父 | `pedigree_3gen_breeding_reg_nums[6]` | `sires_sires_sire_id` |
| 8 | 父父母 | `pedigree_3gen_breeding_reg_nums[7]` | `sires_sires_dam_id` |
| 9 | 父母父 | `pedigree_3gen_breeding_reg_nums[8]` | `sires_dams_sire_id` |
| 10 | 父母母 | `pedigree_3gen_breeding_reg_nums[9]` | `sires_dams_dam_id` |
| 11 | 母父父 | `pedigree_3gen_breeding_reg_nums[10]` | `dams_sires_sire_id` |
| 12 | 母父母 | `pedigree_3gen_breeding_reg_nums[11]` | `dams_sires_dam_id` |
| 13 | 母母父 | `pedigree_3gen_breeding_reg_nums[12]` | `dams_dams_sire_id` |
| 14 | 母母母 | `pedigree_3gen_breeding_reg_nums[13]` | `dams_dams_dam_id` |

### 使用例

```python
# リストのインデックスでアクセス
father_reg_num = record.pedigree_3gen_breeding_reg_nums[0]
mother_reg_num = record.pedigree_3gen_breeding_reg_nums[1]

# プロパティでアクセス（推奨）
father_reg_num = record.sire_id
mother_reg_num = record.dam_id
paternal_grandfather_reg_num = record.sires_sire_id
```

## to_dict() の仕様

このページは JV-Link wire 仕様の説明です。現行の `Client` は dataclass ベースのレコードを返すため、
旧 `BaseRecord.to_dict()` 仕様には依存しません。

## 関連項目

- [DataSpec BLOD](../data-specs/storage/blod.md)
- [DataSpec BLDN](../data-specs/storage/blod.md)
