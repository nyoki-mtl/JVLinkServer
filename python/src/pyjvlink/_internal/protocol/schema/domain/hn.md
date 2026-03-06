# HN - 繁殖馬マスタ

レコード長: 251 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `breeding_reg_num` | str | 12 | 10 | 繁殖登録番号 | KEY |
| 6 | `pedigree_reg_num` | str | 30 | 10 | 血統登録番号 |  |
| 8 | `horse_name` | str | 41 | 36 | 馬名 |  |
| 9 | `horse_name_kana` | str | 77 | 40 | 馬名半角カナ |  |
| 10 | `horse_name_english` | str | 117 | 80 | 馬名欧字 |  |
| 11 | `birth_year` | int | 197 | 4 | 生年 |  |
| 12 | `sex_code` | str | 201 | 1 | 性別コード |  |
| 13 | `breed_code` | str | 202 | 1 | 品種コード |  |
| 14 | `coat_color_code` | str | 203 | 2 | 毛色コード |  |
| 15 | `import_code` | str | 205 | 1 | 繁殖馬持込区分 |  |
| 16 | `import_year` | int | 206 | 4 | 輸入年 |  |
| 17 | `birthplace_name` | str | 210 | 20 | 産地名 |  |
| 18 | `sire_breeding_reg_num` | str | 230 | 10 | 父馬繁殖登録番号 |  |
| 19 | `dam_breeding_reg_num` | str | 240 | 10 | 母馬繁殖登録番号 |  |
