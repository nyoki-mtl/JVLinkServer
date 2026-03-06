# BR - 生産者マスタ

レコード長: 545 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `breeder_code` | str | 12 | 8 | 生産者コード | KEY |
| 5 | `breeder_name_with_corp` | str | 20 | 72 | 生産者名(法人格有) |  |
| 6 | `breeder_name` | str | 92 | 72 | 生産者名(法人格無) |  |
| 7 | `breeder_name_kana` | str | 164 | 72 | 生産者名半角カナ |  |
| 8 | `breeder_name_english` | str | 236 | 168 | 生産者名欧字 |  |
| 9 | `address` | str | 404 | 20 | 生産者住所自治省名 |  |
| 10 | `performance_stats` | array:object[2] | 424 | 120 | 本年累計成績情報 |  |
|  | `  .year` | int | +0 | 4 | 設定年 |  |
|  | `  .prize_money` | money_100yen | +4 | 10 | 本賞金合計 |  |
|  | `  .added_money` | money_100yen | +14 | 10 | 付加賞金合計 |  |
|  | `  .placing_counts` | array:int | +24 | 36 | 着回数 |  |
