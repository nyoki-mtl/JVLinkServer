# BN - 馬主マスタ

レコード長: 477 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `owner_code` | str | 12 | 6 | 馬主コード | KEY |
| 5 | `owner_name_with_corp` | str | 18 | 64 | 馬主名(法人格有) |  |
| 6 | `owner_name` | str | 82 | 64 | 馬主名(法人格無) |  |
| 7 | `owner_name_kana` | str | 146 | 50 | 馬主名半角カナ |  |
| 8 | `owner_name_english` | str | 196 | 100 | 馬主名欧字 |  |
| 9 | `silk_colors_code` | str | 296 | 60 | 服色標示 |  |
| 10 | `performance_stats` | array:object[2] | 356 | 120 | 本年累計成績情報 |  |
|  | `  .year` | int | +0 | 4 | 設定年 |  |
|  | `  .prize_money` | money_100yen | +4 | 10 | 本賞金合計 |  |
|  | `  .added_money` | money_100yen | +14 | 10 | 付加賞金合計 |  |
|  | `  .placing_counts` | array:int | +24 | 36 | 着回数 |  |
