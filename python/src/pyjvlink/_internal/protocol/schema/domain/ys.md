# YS - 開催スケジュール

レコード長: 382 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `meet_year` | int | 12 | 4 | 開催年 | KEY |
| 5 | `meet_date` | date_mmdd | 16 | 4 | 開催月日 | KEY |
| 6 | `racecourse_code` | str | 20 | 2 | 競馬場コード | KEY |
| 7 | `meet_round` | int | 22 | 2 | 開催回 | KEY |
| 8 | `meet_day` | int | 24 | 2 | 開催日目 | KEY |
| 9 | `weekday_code` | str | 26 | 1 | 曜日コード |  |
| 10 | `graded_race_guide` | array:object[3] | 27 | 354 | 重賞案内 |  |
|  | `  .special_race_number` | int | +0 | 4 | 特別競走番号 |  |
|  | `  .race_name_main` | str | +4 | 60 | 競走名本題 |  |
|  | `  .race_short_name_10` | str | +64 | 20 | 競走名略称10文字 |  |
|  | `  .race_short_name_6` | str | +84 | 12 | 競走名略称6文字 |  |
|  | `  .race_short_name_3` | str | +96 | 6 | 競走名略称3文字 |  |
|  | `  .graded_race_round_number` | int | +102 | 3 | 重賞回次 |  |
|  | `  .grade_code` | str | +105 | 1 | グレードコード |  |
|  | `  .race_type_code` | str | +106 | 2 | 競走種別コード |  |
|  | `  .race_symbol_code` | str | +108 | 3 | 競走記号コード |  |
|  | `  .weight_type_code` | str | +111 | 1 | 重量種別コード |  |
|  | `  .distance` | int | +112 | 4 | 距離 |  |
|  | `  .track_code` | str | +116 | 2 | トラックコード |  |
