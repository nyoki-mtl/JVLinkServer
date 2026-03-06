# RC - レコードマスタ

レコード長: 501 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `record_identification_code` | str | 12 | 1 | レコード識別区分 | KEY |
| 5 | `meet_year` | int | 13 | 4 | 開催年 | KEY |
| 6 | `meet_date` | date_mmdd | 17 | 4 | 開催月日 | KEY |
| 7 | `racecourse_code` | str | 21 | 2 | 競馬場コード | KEY |
| 8 | `meet_round` | int | 23 | 2 | 開催回 | KEY |
| 9 | `meet_day` | int | 25 | 2 | 開催日目 | KEY |
| 10 | `race_number` | int | 27 | 2 | レース番号 | KEY |
| 11 | `special_race_number` | int | 29 | 4 | 特別競走番号 | KEY |
| 12 | `race_name_main` | str | 33 | 60 | 競走名本題 |  |
| 13 | `grade_code` | str | 93 | 1 | グレードコード |  |
| 14 | `race_type_code` | str | 94 | 2 | 競走種別コード | KEY |
| 15 | `distance` | int | 96 | 4 | 距離 | KEY |
| 16 | `track_code` | str | 100 | 2 | トラックコード | KEY |
| 17 | `record_type_code` | str | 102 | 1 | レコード区分 |  |
| 18 | `record_time` | duration_mss_s | 103 | 4 | レコードタイム |  |
| 19 | `weather_code` | str | 107 | 1 | 天候コード |  |
| 20 | `turf_track_condition_code` | str | 108 | 1 | 芝馬場状態コード |  |
| 21 | `dirt_track_condition_code` | str | 109 | 1 | ダート馬場状態コード |  |
| 22 | `record_holders` | array:object[3] | 110 | 390 | レコード保持馬情報 |  |
|  | `  .pedigree_reg_num` | str | +0 | 10 | 血統登録番号 |  |
|  | `  .horse_name` | str | +10 | 36 | 馬名 |  |
|  | `  .horse_symbol_code` | str | +46 | 2 | 馬記号コード |  |
|  | `  .sex_code` | str | +48 | 1 | 性別コード |  |
|  | `  .trainer_code` | str | +49 | 5 | 調教師コード |  |
|  | `  .trainer_name` | str | +54 | 34 | 調教師名 |  |
|  | `  .impost_weight` | float | +88 | 3 | 負担重量 |  |
|  | `  .jockey_code` | str | +91 | 5 | 騎手コード |  |
|  | `  .jockey_name` | str | +96 | 34 | 騎手名 |  |
