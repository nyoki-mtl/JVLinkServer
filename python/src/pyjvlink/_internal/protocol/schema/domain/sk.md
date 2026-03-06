# SK - 産駒マスタ

レコード長: 208 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `pedigree_reg_num` | str | 12 | 10 | 血統登録番号 | KEY |
| 5 | `birth_date` | date_yyyymmdd | 22 | 8 | 生年月日 |  |
| 6 | `sex_code` | str | 30 | 1 | 性別コード |  |
| 7 | `breed_code` | str | 31 | 1 | 品種コード |  |
| 8 | `coat_color_code` | str | 32 | 2 | 毛色コード |  |
| 9 | `import_code` | str | 34 | 1 | 産駒持込区分 |  |
| 10 | `import_year` | int | 35 | 4 | 輸入年 |  |
| 11 | `breeder_code` | str | 39 | 8 | 生産者コード |  |
| 12 | `birthplace_name` | str | 47 | 20 | 産地名 |  |
| 13 | `three_gen_pedigree_breeding_reg_nums` | array:str[14] | 67 | 140 | 3代血統 繁殖登録番号 |  |
