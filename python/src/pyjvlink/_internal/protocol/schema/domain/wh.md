# WH - 馬体重

レコード長: 847 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `meet_year` | int | 12 | 4 | 開催年 | KEY |
| 5 | `meet_date` | date_mmdd | 16 | 4 | 開催月日 | KEY |
| 6 | `racecourse_code` | str | 20 | 2 | 競馬場コード | KEY |
| 7 | `meet_round` | int | 22 | 2 | 開催回 | KEY |
| 8 | `meet_day` | int | 24 | 2 | 開催日目 | KEY |
| 9 | `race_number` | int | 26 | 2 | レース番号 | KEY |
| 10 | `announcement_datetime` | datetime_mmddhhmm | 28 | 8 | 発表月日時分 |  |
| 11 | `horse_weight_infos` | array:object[18] | 36 | 810 | 馬体重情報 |  |
|  | `  .horse_number` | int | +0 | 2 | 馬番 |  |
|  | `  .horse_name` | str | +2 | 36 | 馬名 |  |
|  | `  .horse_weight` | int | +38 | 3 | 馬体重 |  |
|  | `  .weight_change_sign` | str | +41 | 1 | 増減符号 |  |
|  | `  .weight_change_diff` | int | +42 | 3 | 増減差 |  |
