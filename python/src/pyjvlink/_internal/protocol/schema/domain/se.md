# SE - 馬毎レース情報

レコード長: 555 バイト

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
| 10 | `bracket_number` | int | 28 | 1 | 枠番 |  |
| 11 | `horse_number` | int | 29 | 2 | 馬番 | KEY |
| 12 | `pedigree_reg_num` | str | 31 | 10 | 血統登録番号 | KEY |
| 13 | `horse_name` | str | 41 | 36 | 馬名 |  |
| 14 | `horse_symbol_code` | str | 77 | 2 | 馬記号コード |  |
| 15 | `horse_sex_code` | str | 79 | 1 | 性別コード |  |
| 16 | `breed_code` | str | 80 | 1 | 品種コード |  |
| 17 | `coat_color_code` | str | 81 | 2 | 毛色コード |  |
| 18 | `horse_age` | int | 83 | 2 | 馬齢 |  |
| 19 | `east_west_affiliation_code` | str | 85 | 1 | 東西所属コード |  |
| 20 | `trainer_code` | str | 86 | 5 | 調教師コード |  |
| 21 | `trainer_short_name` | str | 91 | 8 | 調教師名略称 |  |
| 22 | `owner_code` | str | 99 | 6 | 馬主コード |  |
| 23 | `owner_name_individual` | str | 105 | 64 | 馬主名(法人格無) |  |
| 24 | `silk_colors` | str | 169 | 60 | 服色標示 |  |
| 26 | `carrying_weight` | float | 289 | 3 | 負担重量 |  |
| 27 | `before_carrying_weight` | float | 292 | 3 | 変更前負担重量 |  |
| 28 | `blinker_usage_code` | str | 295 | 1 | ブリンカー使用区分 |  |
| 30 | `jockey_code` | str | 297 | 5 | 騎手コード |  |
| 31 | `before_jockey_code` | str | 302 | 5 | 変更前騎手コード |  |
| 32 | `jockey_short_name` | str | 307 | 8 | 騎手名略称 |  |
| 33 | `before_jockey_short_name` | str | 315 | 8 | 変更前騎手名略称 |  |
| 34 | `jockey_apprentice_code` | str | 323 | 1 | 騎手見習コード |  |
| 35 | `before_jockey_apprentice_code` | str | 324 | 1 | 変更前騎手見習コード |  |
| 36 | `horse_weight` | int | 325 | 3 | 馬体重 |  |
| 37 | `weight_change_sign` | str | 328 | 1 | 増減符号 |  |
| 38 | `weight_change_diff` | int | 329 | 3 | 増減差 |  |
| 39 | `abnormality_code` | str | 332 | 1 | 異常区分コード |  |
| 40 | `finish_order` | int | 333 | 2 | 入線順位 |  |
| 41 | `confirmed_placing` | int | 335 | 2 | 確定着順 |  |
| 42 | `dead_heat_code` | str | 337 | 1 | 同着区分 |  |
| 43 | `dead_heat_count` | int | 338 | 1 | 同着頭数 |  |
| 44 | `finish_time` | duration_mss_s | 339 | 4 | 走破タイム |  |
| 45 | `margin_code` | str | 343 | 3 | 着差コード |  |
| 46 | `margin_code_plus` | str | 346 | 3 | +着差コード |  |
| 47 | `margin_code_plus_plus` | str | 349 | 3 | ++着差コード |  |
| 48 | `corner1_position` | int | 352 | 2 | 1コーナーでの順位 |  |
| 49 | `corner2_position` | int | 354 | 2 | 2コーナーでの順位 |  |
| 50 | `corner3_position` | int | 356 | 2 | 3コーナーでの順位 |  |
| 51 | `corner4_position` | int | 358 | 2 | 4コーナーでの順位 |  |
| 52 | `win_odds` | float | 360 | 4 | 単勝オッズ |  |
| 53 | `win_popularity_rank` | int | 364 | 2 | 単勝人気順 |  |
| 54 | `earned_purse_money` | money_100yen | 366 | 8 | 獲得本賞金 |  |
| 55 | `earned_added_money` | money_100yen | 374 | 8 | 獲得付加賞金 |  |
| 58 | `last_4f_time` | duration_ss_s | 388 | 3 | 後4ハロンタイム |  |
| 59 | `last_3f_time` | duration_ss_s | 391 | 3 | 後3ハロンタイム |  |
| 60 | `opponent_horses` | array:object[3] | 394 | 138 | 1着馬(相手馬)情報 |  |
|  | `  .pedigree_reg_num` | str | +0 | 10 | 血統登録番号 |  |
|  | `  .horse_name` | str | +10 | 36 | 馬名 |  |
| 61 | `time_diff` | int | 532 | 4 | タイム差 |  |
| 62 | `record_update_code` | str | 536 | 1 | レコード更新区分 |  |
| 63 | `mining_code` | str | 537 | 1 | マイニング区分 |  |
| 64 | `mining_pred_finish_time` | duration_mss_ss | 538 | 5 | マイニング予想走破タイム |  |
| 65 | `mining_pred_err_margin_plus` | duration_ss_ss | 543 | 4 | マイニング予想誤差+ |  |
| 66 | `mining_pred_err_margin_minus` | duration_ss_ss | 547 | 4 | マイニング予想誤差- |  |
| 67 | `mining_pred_rank` | int | 551 | 2 | マイニング予想順位 |  |
| 68 | `current_race_running_style_judgement` | str | 553 | 1 | 今回レース脚質判定 |  |
