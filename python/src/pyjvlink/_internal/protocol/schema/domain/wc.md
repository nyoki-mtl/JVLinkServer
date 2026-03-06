# WC - ウッドチップ調教

レコード長: 105 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `training_center_code` | str | 12 | 1 | トレセン区分 | KEY |
| 5 | `training_date` | date_yyyymmdd | 13 | 8 | 調教年月日 | KEY |
| 6 | `training_time` | time_hhmm | 21 | 4 | 調教時刻 | KEY |
| 7 | `pedigree_reg_num` | str | 25 | 10 | 血統登録番号 | KEY |
| 8 | `course` | str | 35 | 1 | コース |  |
| 9 | `track_direction` | str | 36 | 1 | 馬場周り |  |
| 11 | `total_time_10f` | duration_ss_s | 38 | 4 | 10ハロンタイム合計 |  |
| 12 | `lap_time_2000_1800` | duration_ss_s | 42 | 3 | ラップタイム 2000M-1800M |  |
| 13 | `total_time_9f` | duration_ss_s | 45 | 4 | 9ハロンタイム合計 |  |
| 14 | `lap_time_1800_1600` | duration_ss_s | 49 | 3 | ラップタイム 1800M-1600M |  |
| 15 | `total_time_8f` | duration_ss_s | 52 | 4 | 8ハロンタイム合計 |  |
| 16 | `lap_time_1600_1400` | duration_ss_s | 56 | 3 | ラップタイム 1600M-1400M |  |
| 17 | `total_time_7f` | duration_ss_s | 59 | 4 | 7ハロンタイム合計 |  |
| 18 | `lap_time_1400_1200` | duration_ss_s | 63 | 3 | ラップタイム 1400M-1200M |  |
| 19 | `total_time_6f` | duration_ss_s | 66 | 4 | 6ハロンタイム合計 |  |
| 20 | `lap_time_1200_1000` | duration_ss_s | 70 | 3 | ラップタイム 1200M-1000M |  |
| 21 | `total_time_5f` | duration_ss_s | 73 | 4 | 5ハロンタイム合計 |  |
| 22 | `lap_time_1000_800` | duration_ss_s | 77 | 3 | ラップタイム 1000M-800M |  |
| 23 | `total_time_4f` | duration_ss_s | 80 | 4 | 4ハロンタイム合計 |  |
| 24 | `lap_time_800_600` | duration_ss_s | 84 | 3 | ラップタイム 800M-600M |  |
| 25 | `total_time_3f` | duration_ss_s | 87 | 4 | 3ハロンタイム合計 |  |
| 26 | `lap_time_600_400` | duration_ss_s | 91 | 3 | ラップタイム 600M-400M |  |
| 27 | `total_time_2f` | duration_ss_s | 94 | 4 | 2ハロンタイム合計 |  |
| 28 | `lap_time_400_200` | duration_ss_s | 98 | 3 | ラップタイム 400M-200M |  |
| 29 | `lap_time_200_0` | duration_ss_s | 101 | 3 | ラップタイム 200M-0M |  |
