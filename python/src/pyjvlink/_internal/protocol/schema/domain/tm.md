# TM - 対戦型データマイニング予想

レコード長: 141 バイト

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
| 10 | `data_creation_time` | time_hhmm | 28 | 4 | データ作成時分 |  |
| 11 | `mining_predictions` | array:object[18] | 32 | 108 | マイニング予想 |  |
|  | `  .horse_number` | int | +0 | 2 | 馬番 |  |
|  | `  .prediction_score` | float | +2 | 4 | 予測スコア |  |
