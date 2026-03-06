# HC - 坂路調教

レコード長: 60 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `training_center_code` | str | 12 | 1 | トレセン区分 | KEY |
| 5 | `training_date` | date_yyyymmdd | 13 | 8 | 調教年月日 | KEY |
| 6 | `training_time` | time_hhmm | 21 | 4 | 調教時刻 | KEY |
| 7 | `pedigree_reg_num` | str | 25 | 10 | 血統登録番号 | KEY |
| 8 | `total_time_4f` | duration_ss_s | 35 | 4 | 4ハロンタイム合計 |  |
| 9 | `lap_time_800_600` | duration_ss_s | 39 | 3 | ラップタイム 800M-600M |  |
| 10 | `total_time_3f` | duration_ss_s | 42 | 4 | 3ハロンタイム合計 |  |
| 11 | `lap_time_600_400` | duration_ss_s | 46 | 3 | ラップタイム 600M-400M |  |
| 12 | `total_time_2f` | duration_ss_s | 49 | 4 | 2ハロンタイム合計 |  |
| 13 | `lap_time_400_200` | duration_ss_s | 53 | 3 | ラップタイム 400M-200M |  |
| 14 | `lap_time_200_0` | duration_ss_s | 56 | 3 | ラップタイム 200M-0M |  |
