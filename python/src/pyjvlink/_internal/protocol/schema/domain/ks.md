# KS - 騎手マスタ

レコード長: 4173 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `jockey_code` | str | 12 | 5 | 騎手コード | KEY |
| 5 | `deregistration_flag` | str | 17 | 1 | 騎手抹消区分 |  |
| 6 | `license_issue_date` | date_yyyymmdd | 18 | 8 | 騎手免許交付年月日 |  |
| 7 | `license_revoked_date` | date_yyyymmdd | 26 | 8 | 騎手免許抹消年月日 |  |
| 8 | `birth_date` | date_yyyymmdd | 34 | 8 | 生年月日 |  |
| 9 | `jockey_name` | str | 42 | 34 | 騎手名 |  |
| 10 | `reserved_10` | reserved | 76 | 34 | 予備 |  |
| 11 | `jockey_name_kana` | str | 110 | 30 | 騎手名半角カナ |  |
| 12 | `jockey_name_short` | str | 140 | 8 | 騎手名略称 |  |
| 13 | `jockey_name_english` | str | 148 | 80 | 騎手名欧字 |  |
| 14 | `sex_code` | str | 228 | 1 | 性別区分 |  |
| 15 | `riding_qualification_code` | str | 229 | 1 | 騎乗資格コード |  |
| 16 | `jockey_apprentice_code` | str | 230 | 1 | 騎手見習コード |  |
| 17 | `affiliation_code` | str | 231 | 1 | 騎手東西所属コード |  |
| 18 | `invitation_area_name` | str | 232 | 20 | 招待地域名 |  |
| 19 | `affiliated_trainer_code` | str | 252 | 5 | 所属調教師コード |  |
| 20 | `affiliated_trainer_name_short` | str | 257 | 8 | 所属調教師名略称 |  |
| 21 | `first_ride_info` | array:object[2] | 265 | 134 | 初騎乗情報 |  |
|  | `  .race_key` | str | +0 | 16 | 年月日場回日R |  |
|  | `  .num_starters` | int | +16 | 2 | 出走頭数 |  |
|  | `  .pedigree_reg_num` | str | +18 | 10 | 血統登録番号 |  |
|  | `  .horse_name` | str | +28 | 36 | 馬名 |  |
|  | `  .confirmed_placing` | int | +64 | 2 | 確定着順 |  |
|  | `  .abnormality_code` | str | +66 | 1 | 異常区分コード |  |
| 22 | `first_win_info` | array:object[2] | 399 | 128 | 初勝利情報 |  |
|  | `  .race_key` | str | +0 | 16 | 年月日場回日R |  |
|  | `  .num_starters` | int | +16 | 2 | 出走頭数 |  |
|  | `  .pedigree_reg_num` | str | +18 | 10 | 血統登録番号 |  |
|  | `  .horse_name` | str | +28 | 36 | 馬名 |  |
| 23 | `recent_graded_wins` | array:object[3] | 527 | 489 | 最近重賞勝利情報 |  |
|  | `  .race_key` | str | +0 | 16 | 年月日場回日R |  |
|  | `  .race_name_main` | str | +16 | 60 | 競走名本題 |  |
|  | `  .race_short_name_10` | str | +76 | 20 | 競走名略称10文字 |  |
|  | `  .race_short_name_6` | str | +96 | 12 | 競走名略称6文字 |  |
|  | `  .race_short_name_3` | str | +108 | 6 | 競走名略称3文字 |  |
|  | `  .grade_code` | str | +114 | 1 | グレードコード |  |
|  | `  .num_starters` | int | +115 | 2 | 出走頭数 |  |
|  | `  .pedigree_reg_num` | str | +117 | 10 | 血統登録番号 |  |
|  | `  .horse_name` | str | +127 | 36 | 馬名 |  |
| 24 | `performance_stats` | array:object[3] | 1016 | 3156 | 本年前年累計成績情報 |  |
|  | `  .year` | int | +0 | 4 | 設定年 |  |
|  | `  .flat_prize_money` | money_100yen | +4 | 10 | 平地本賞金合計 |  |
|  | `  .steeplechase_prize_money` | money_100yen | +14 | 10 | 障害本賞金合計 |  |
|  | `  .flat_added_money` | money_100yen | +24 | 10 | 平地付加賞金合計 |  |
|  | `  .steeplechase_added_money` | money_100yen | +34 | 10 | 障害付加賞金合計 |  |
|  | `  .flat_placing_counts` | array:int | +44 | 36 | 平地着回数 |  |
|  | `  .steeplechase_placing_counts` | array:int | +80 | 36 | 障害着回数 |  |
|  | `  .sapporo_flat_placing_counts` | array:int | +116 | 36 |  |  |
|  | `  .sapporo_steeplechase_placing_counts` | array:int | +152 | 36 |  |  |
|  | `  .hakodate_flat_placing_counts` | array:int | +188 | 36 |  |  |
|  | `  .hakodate_steeplechase_placing_counts` | array:int | +224 | 36 |  |  |
|  | `  .fukushima_flat_placing_counts` | array:int | +260 | 36 |  |  |
|  | `  .fukushima_steeplechase_placing_counts` | array:int | +296 | 36 |  |  |
|  | `  .niigata_flat_placing_counts` | array:int | +332 | 36 |  |  |
|  | `  .niigata_steeplechase_placing_counts` | array:int | +368 | 36 |  |  |
|  | `  .tokyo_flat_placing_counts` | array:int | +404 | 36 |  |  |
|  | `  .tokyo_steeplechase_placing_counts` | array:int | +440 | 36 |  |  |
|  | `  .nakayama_flat_placing_counts` | array:int | +476 | 36 |  |  |
|  | `  .nakayama_steeplechase_placing_counts` | array:int | +512 | 36 |  |  |
|  | `  .chukyo_flat_placing_counts` | array:int | +548 | 36 |  |  |
|  | `  .chukyo_steeplechase_placing_counts` | array:int | +584 | 36 |  |  |
|  | `  .kyoto_flat_placing_counts` | array:int | +620 | 36 |  |  |
|  | `  .kyoto_steeplechase_placing_counts` | array:int | +656 | 36 |  |  |
|  | `  .hanshin_flat_placing_counts` | array:int | +692 | 36 |  |  |
|  | `  .hanshin_steeplechase_placing_counts` | array:int | +728 | 36 |  |  |
|  | `  .kokura_flat_placing_counts` | array:int | +764 | 36 |  |  |
|  | `  .kokura_steeplechase_placing_counts` | array:int | +800 | 36 |  |  |
|  | `  .turf_class_d_placing_counts` | array:int | +836 | 36 |  |  |
|  | `  .turf_class_e_placing_counts` | array:int | +872 | 36 |  |  |
|  | `  .turf_gt2200_placing_counts` | array:int | +908 | 36 |  |  |
|  | `  .dirt_class_d_placing_counts` | array:int | +944 | 36 |  |  |
|  | `  .dirt_class_e_placing_counts` | array:int | +980 | 36 |  |  |
|  | `  .dirt_gt2200_placing_counts` | array:int | +1016 | 36 |  |  |
