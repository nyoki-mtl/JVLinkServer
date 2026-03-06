# TK - 特別登録馬

レコード長: 21657 バイト

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
| 10 | `weekday_code` | str | 28 | 1 | 曜日コード |  |
| 11 | `special_race_number` | int | 29 | 4 | 特別競走番号 |  |
| 12 | `race_name_main` | str | 33 | 60 | 競走名本題 |  |
| 13 | `race_name_subtitle` | str | 93 | 60 | 競走名副題 |  |
| 14 | `race_name_parentheses` | str | 153 | 60 | 競走名カッコ内 |  |
| 15 | `race_name_main_english` | str | 213 | 120 | 競走名本題欧字 |  |
| 16 | `race_name_subtitle_english` | str | 333 | 120 | 競走名副題欧字 |  |
| 17 | `race_name_parentheses_english` | str | 453 | 120 | 競走名カッコ内欧字 |  |
| 18 | `race_short_name_10` | str | 573 | 20 | 競走名略称10文字 |  |
| 19 | `race_short_name_6` | str | 593 | 12 | 競走名略称6文字 |  |
| 20 | `race_short_name_3` | str | 605 | 6 | 競走名略称3文字 |  |
| 21 | `race_name_code` | str | 611 | 1 | 競走名区分 |  |
| 22 | `graded_race_round_number` | int | 612 | 3 | 重賞回次 |  |
| 23 | `grade_code` | str | 615 | 1 | グレードコード |  |
| 24 | `race_type_code` | str | 616 | 2 | 競走種別コード |  |
| 25 | `race_symbol_code` | str | 618 | 3 | 競走記号コード |  |
| 26 | `weight_type_code` | str | 621 | 1 | 重量種別コード |  |
| 27 | `race_cond_code_2yo` | str | 622 | 3 | 競走条件コード 2歳条件 |  |
| 28 | `race_cond_code_3yo` | str | 625 | 3 | 競走条件コード 3歳条件 |  |
| 29 | `race_cond_code_4yo` | str | 628 | 3 | 競走条件コード 4歳条件 |  |
| 30 | `race_cond_code_5yo_up` | str | 631 | 3 | 競走条件コード 5歳以上条件 |  |
| 31 | `race_cond_code_youngest` | str | 634 | 3 | 競走条件コード 最若年条件 |  |
| 32 | `distance` | int | 637 | 4 | 距離 |  |
| 33 | `track_code` | str | 641 | 2 | トラックコード |  |
| 34 | `course_code` | str | 643 | 2 | コース区分 |  |
| 35 | `handicap_announcement_date` | date_yyyymmdd | 645 | 8 | ハンデ発表日 |  |
| 36 | `num_entries` | int | 653 | 3 | 登録頭数 |  |
| 37 | `entry_horses` | array:object[300] | 656 | 21000 | 登録馬毎情報 |  |
|  | `  .serial_number` | int | +0 | 3 | 連番 |  |
|  | `  .pedigree_reg_num` | str | +3 | 10 | 血統登録番号 |  |
|  | `  .horse_name` | str | +13 | 36 | 馬名 |  |
|  | `  .horse_symbol_code` | str | +49 | 2 | 馬記号コード |  |
|  | `  .sex_code` | str | +51 | 1 | 性別コード |  |
|  | `  .trainer_affiliation_code` | str | +52 | 1 | 調教師東西所属コード |  |
|  | `  .trainer_code` | str | +53 | 5 | 調教師コード |  |
|  | `  .trainer_short_name` | str | +58 | 8 | 調教師名略称 |  |
|  | `  .impost_weight` | int | +66 | 3 | 負担重量 |  |
|  | `  .exchange_code` | str | +69 | 1 | 交流区分 |  |
