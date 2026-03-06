# RA - レース詳細

レコード長: 1272 バイト

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
| 24 | `before_grade_code` | str | 616 | 1 | 変更前グレードコード |  |
| 25 | `race_type_code` | str | 617 | 2 | 競走種別コード |  |
| 26 | `race_symbol_code` | str | 619 | 3 | 競走記号コード |  |
| 27 | `weight_type_code` | str | 622 | 1 | 重量種別コード |  |
| 28 | `race_cond_code_2yo` | str | 623 | 3 | 競走条件コード 2歳条件 |  |
| 29 | `race_cond_code_3yo` | str | 626 | 3 | 競走条件コード 3歳条件 |  |
| 30 | `race_cond_code_4yo` | str | 629 | 3 | 競走条件コード 4歳条件 |  |
| 31 | `race_cond_code_5yo_up` | str | 632 | 3 | 競走条件コード 5歳以上条件 |  |
| 32 | `race_cond_code_youngest` | str | 635 | 3 | 競走条件コード 最若年条件 |  |
| 33 | `race_condition_name` | str | 638 | 60 | 競走条件名称 |  |
| 34 | `distance` | int | 698 | 4 | 距離 |  |
| 35 | `before_distance` | int | 702 | 4 | 変更前距離 |  |
| 36 | `track_code` | str | 706 | 2 | トラックコード |  |
| 37 | `before_track_code` | str | 708 | 2 | 変更前トラックコード |  |
| 38 | `course_code` | str | 710 | 2 | コース区分 |  |
| 39 | `before_course_code` | str | 712 | 2 | 変更前コース区分 |  |
| 40 | `purse_money` | array:money_100yen[7] | 714 | 56 | 本賞金 |  |
| 41 | `before_purse_money` | array:money_100yen[5] | 770 | 40 | 変更前本賞金 |  |
| 42 | `added_money` | array:money_100yen[5] | 810 | 40 | 付加賞金 |  |
| 43 | `before_added_money` | array:money_100yen[3] | 850 | 24 | 変更前付加賞金 |  |
| 44 | `post_time` | time_hhmm | 874 | 4 | 発走時刻 |  |
| 45 | `before_post_time` | time_hhmm | 878 | 4 | 変更前発走時刻 |  |
| 46 | `num_entries` | int | 882 | 2 | 登録頭数 |  |
| 47 | `num_starters` | int | 884 | 2 | 出走頭数 |  |
| 48 | `num_finishers` | int | 886 | 2 | 入線頭数 |  |
| 49 | `weather_code` | str | 888 | 1 | 天候コード |  |
| 50 | `turf_track_condition_code` | str | 889 | 1 | 芝馬場状態コード |  |
| 51 | `dirt_track_condition_code` | str | 890 | 1 | ダート馬場状態コード |  |
| 52 | `lap_times` | array:duration_ss_s[25] | 891 | 75 | ラップタイム |  |
| 53 | `mile_time` | duration_mss_s | 966 | 4 | 障害マイルタイム |  |
| 54 | `first_3f_time` | duration_ss_s | 970 | 3 | 前3ハロン |  |
| 55 | `first_4f_time` | duration_ss_s | 973 | 3 | 前4ハロン |  |
| 56 | `last_3f_time` | duration_ss_s | 976 | 3 | 後3ハロン |  |
| 57 | `last_4f_time` | duration_ss_s | 979 | 3 | 後4ハロン |  |
| 58 | `corner_passing_order` | array:object[4] | 982 | 288 | コーナー通過順位 |  |
|  | `  .corner` | int | +0 | 1 | コーナー番号 |  |
|  | `  .lap_count` | int | +1 | 1 | 周回数 |  |
|  | `  .passing_order` | str | +2 | 70 | 通過順位 |  |
| 59 | `record_update_code` | str | 1270 | 1 | レコード更新区分 |  |
