# CK - 出走別着度数

レコード長: 6870 バイト

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
| 10 | `pedigree_reg_num` | str | 28 | 10 | 血統登録番号 | KEY |
| 11 | `horse_name` | str | 38 | 36 | 馬名 |  |
| 12 | `flat_purse_total` | money_100yen | 74 | 9 | 平地本賞金累計 |  |
| 13 | `obstacle_purse_total` | money_100yen | 83 | 9 | 障害本賞金累計 |  |
| 14 | `flat_added_money_total` | money_100yen | 92 | 9 | 平地付加賞金累計 |  |
| 15 | `obstacle_added_money_total` | money_100yen | 101 | 9 | 障害付加賞金累計 |  |
| 16 | `flat_earned_money_total` | money_100yen | 110 | 9 | 平地収得賞金累計 |  |
| 17 | `obstacle_earned_money_total` | money_100yen | 119 | 9 | 障害収得賞金累計 |  |
| 18 | `total_placing_counts` | array:int[6] | 128 | 18 | 総合着回数 |  |
| 19 | `jra_total_placing_counts` | array:int[6] | 146 | 18 | 中央合計着回数 |  |
| 20 | `turf_straight_placing_counts` | array:int[6] | 164 | 18 | 芝直着回数 |  |
| 21 | `turf_right_placing_counts` | array:int[6] | 182 | 18 | 芝右着回数 |  |
| 22 | `turf_left_placing_counts` | array:int[6] | 200 | 18 | 芝左着回数 |  |
| 23 | `dirt_straight_placing_counts` | array:int[6] | 218 | 18 | ダ直着回数 |  |
| 24 | `dirt_right_placing_counts` | array:int[6] | 236 | 18 | ダ右着回数 |  |
| 25 | `dirt_left_placing_counts` | array:int[6] | 254 | 18 | ダ左着回数 |  |
| 26 | `obstacle_placing_counts` | array:int[6] | 272 | 18 | 障害着回数 |  |
| 27 | `turf_good_placing_counts` | array:int[6] | 290 | 18 | 芝良着回数 |  |
| 28 | `turf_yielding_placing_counts` | array:int[6] | 308 | 18 | 芝稍着回数 |  |
| 29 | `turf_heavy_placing_counts` | array:int[6] | 326 | 18 | 芝重着回数 |  |
| 30 | `turf_soft_placing_counts` | array:int[6] | 344 | 18 | 芝不着回数 |  |
| 31 | `dirt_good_placing_counts` | array:int[6] | 362 | 18 | ダ良着回数 |  |
| 32 | `dirt_yielding_placing_counts` | array:int[6] | 380 | 18 | ダ稍着回数 |  |
| 33 | `dirt_heavy_placing_counts` | array:int[6] | 398 | 18 | ダ重着回数 |  |
| 34 | `dirt_soft_placing_counts` | array:int[6] | 416 | 18 | ダ不着回数 |  |
| 35 | `obstacle_good_placing_counts` | array:int[6] | 434 | 18 | 障良着回数 |  |
| 36 | `obstacle_yielding_placing_counts` | array:int[6] | 452 | 18 | 障稍着回数 |  |
| 37 | `obstacle_heavy_placing_counts` | array:int[6] | 470 | 18 | 障重着回数 |  |
| 38 | `obstacle_soft_placing_counts` | array:int[6] | 488 | 18 | 障不着回数 |  |
| 39 | `turf_dist_1200_placing_counts` | array:int[6] | 506 | 18 | 芝1200以下着回数 |  |
| 40 | `turf_dist_1201_1400_placing_counts` | array:int[6] | 524 | 18 | 芝1201-1400着回数 |  |
| 41 | `turf_dist_1401_1600_placing_counts` | array:int[6] | 542 | 18 | 芝1401-1600着回数 |  |
| 42 | `turf_dist_1601_1800_placing_counts` | array:int[6] | 560 | 18 | 芝1601-1800着回数 |  |
| 43 | `turf_dist_1801_2000_placing_counts` | array:int[6] | 578 | 18 | 芝1801-2000着回数 |  |
| 44 | `turf_dist_2001_2200_placing_counts` | array:int[6] | 596 | 18 | 芝2001-2200着回数 |  |
| 45 | `turf_dist_2201_2400_placing_counts` | array:int[6] | 614 | 18 | 芝2201-2400着回数 |  |
| 46 | `turf_dist_2401_2800_placing_counts` | array:int[6] | 632 | 18 | 芝2401-2800着回数 |  |
| 47 | `turf_dist_2801_placing_counts` | array:int[6] | 650 | 18 | 芝2801以上着回数 |  |
| 48 | `dirt_dist_1200_placing_counts` | array:int[6] | 668 | 18 | ダ1200以下着回数 |  |
| 49 | `dirt_dist_1201_1400_placing_counts` | array:int[6] | 686 | 18 | ダ1201-1400着回数 |  |
| 50 | `dirt_dist_1401_1600_placing_counts` | array:int[6] | 704 | 18 | ダ1401-1600着回数 |  |
| 51 | `dirt_dist_1601_1800_placing_counts` | array:int[6] | 722 | 18 | ダ1601-1800着回数 |  |
| 52 | `dirt_dist_1801_2000_placing_counts` | array:int[6] | 740 | 18 | ダ1801-2000着回数 |  |
| 53 | `dirt_dist_2001_2200_placing_counts` | array:int[6] | 758 | 18 | ダ2001-2200着回数 |  |
| 54 | `dirt_dist_2201_2400_placing_counts` | array:int[6] | 776 | 18 | ダ2201-2400着回数 |  |
| 55 | `dirt_dist_2401_2800_placing_counts` | array:int[6] | 794 | 18 | ダ2401-2800着回数 |  |
| 56 | `dirt_dist_2801_placing_counts` | array:int[6] | 812 | 18 | ダ2801以上着回数 |  |
| 57 | `sapporo_turf_placing_counts` | array:int[6] | 830 | 18 |  |  |
| 58 | `hakodate_turf_placing_counts` | array:int[6] | 848 | 18 |  |  |
| 59 | `fukushima_turf_placing_counts` | array:int[6] | 866 | 18 |  |  |
| 60 | `niigata_turf_placing_counts` | array:int[6] | 884 | 18 |  |  |
| 61 | `tokyo_turf_placing_counts` | array:int[6] | 902 | 18 |  |  |
| 62 | `nakayama_turf_placing_counts` | array:int[6] | 920 | 18 |  |  |
| 63 | `chukyo_turf_placing_counts` | array:int[6] | 938 | 18 |  |  |
| 64 | `kyoto_turf_placing_counts` | array:int[6] | 956 | 18 |  |  |
| 65 | `hanshin_turf_placing_counts` | array:int[6] | 974 | 18 |  |  |
| 66 | `kokura_turf_placing_counts` | array:int[6] | 992 | 18 |  |  |
| 67 | `sapporo_dirt_placing_counts` | array:int[6] | 1010 | 18 |  |  |
| 68 | `hakodate_dirt_placing_counts` | array:int[6] | 1028 | 18 |  |  |
| 69 | `fukushima_dirt_placing_counts` | array:int[6] | 1046 | 18 |  |  |
| 70 | `niigata_dirt_placing_counts` | array:int[6] | 1064 | 18 |  |  |
| 71 | `tokyo_dirt_placing_counts` | array:int[6] | 1082 | 18 |  |  |
| 72 | `nakayama_dirt_placing_counts` | array:int[6] | 1100 | 18 |  |  |
| 73 | `chukyo_dirt_placing_counts` | array:int[6] | 1118 | 18 |  |  |
| 74 | `kyoto_dirt_placing_counts` | array:int[6] | 1136 | 18 |  |  |
| 75 | `hanshin_dirt_placing_counts` | array:int[6] | 1154 | 18 |  |  |
| 76 | `kokura_dirt_placing_counts` | array:int[6] | 1172 | 18 |  |  |
| 77 | `sapporo_obstacle_placing_counts` | array:int[6] | 1190 | 18 |  |  |
| 78 | `hakodate_obstacle_placing_counts` | array:int[6] | 1208 | 18 |  |  |
| 79 | `fukushima_obstacle_placing_counts` | array:int[6] | 1226 | 18 |  |  |
| 80 | `niigata_obstacle_placing_counts` | array:int[6] | 1244 | 18 |  |  |
| 81 | `tokyo_obstacle_placing_counts` | array:int[6] | 1262 | 18 |  |  |
| 82 | `nakayama_obstacle_placing_counts` | array:int[6] | 1280 | 18 |  |  |
| 83 | `chukyo_obstacle_placing_counts` | array:int[6] | 1298 | 18 |  |  |
| 84 | `kyoto_obstacle_placing_counts` | array:int[6] | 1316 | 18 |  |  |
| 85 | `hanshin_obstacle_placing_counts` | array:int[6] | 1334 | 18 |  |  |
| 86 | `kokura_obstacle_placing_counts` | array:int[6] | 1352 | 18 |  |  |
| 87 | `running_style_counts` | array:int[4] | 1370 | 12 | 脚質傾向 |  |
| 88 | `registered_race_count` | int | 1382 | 3 | 登録レース数 |  |
| 89 | `jockey_code` | str | 1385 | 5 | 騎手コード |  |
| 90 | `jockey_name` | str | 1390 | 34 | 騎手名 |  |
| 91 | `jockey_performance_stats` | array:object[2] | 1424 | 2440 |  |  |
|  | `  .year` | int | +0 | 4 |  |  |
|  | `  .flat_prize_money` | money_100yen | +4 | 10 |  |  |
|  | `  .obstacle_prize_money` | money_100yen | +14 | 10 |  |  |
|  | `  .flat_added_money` | money_100yen | +24 | 10 |  |  |
|  | `  .obstacle_added_money` | money_100yen | +34 | 10 |  |  |
|  | `  .turf_placing_counts` | array:int | +44 | 30 |  |  |
|  | `  .dirt_placing_counts` | array:int | +74 | 30 |  |  |
|  | `  .obstacle_placing_counts` | array:int | +104 | 24 |  |  |
|  | `  .turf_dist_1200_placing_counts` | array:int | +128 | 24 |  |  |
|  | `  .turf_dist_1201_1400_placing_counts` | array:int | +152 | 24 |  |  |
|  | `  .turf_dist_1401_1600_placing_counts` | array:int | +176 | 24 |  |  |
|  | `  .turf_dist_1601_1800_placing_counts` | array:int | +200 | 24 |  |  |
|  | `  .turf_dist_1801_2000_placing_counts` | array:int | +224 | 24 |  |  |
|  | `  .turf_dist_2001_2200_placing_counts` | array:int | +248 | 24 |  |  |
|  | `  .turf_dist_2201_2400_placing_counts` | array:int | +272 | 24 |  |  |
|  | `  .turf_dist_2401_2800_placing_counts` | array:int | +296 | 24 |  |  |
|  | `  .turf_dist_2801_placing_counts` | array:int | +320 | 24 |  |  |
|  | `  .dirt_dist_1200_placing_counts` | array:int | +344 | 24 |  |  |
|  | `  .dirt_dist_1201_1400_placing_counts` | array:int | +368 | 24 |  |  |
|  | `  .dirt_dist_1401_1600_placing_counts` | array:int | +392 | 24 |  |  |
|  | `  .dirt_dist_1601_1800_placing_counts` | array:int | +416 | 24 |  |  |
|  | `  .dirt_dist_1801_2000_placing_counts` | array:int | +440 | 24 |  |  |
|  | `  .dirt_dist_2001_2200_placing_counts` | array:int | +464 | 24 |  |  |
|  | `  .dirt_dist_2201_2400_placing_counts` | array:int | +488 | 24 |  |  |
|  | `  .dirt_dist_2401_2800_placing_counts` | array:int | +512 | 24 |  |  |
|  | `  .dirt_dist_2801_placing_counts` | array:int | +536 | 24 |  |  |
|  | `  .sapporo_turf_placing_counts` | array:int | +560 | 24 |  |  |
|  | `  .hakodate_turf_placing_counts` | array:int | +584 | 24 |  |  |
|  | `  .fukushima_turf_placing_counts` | array:int | +608 | 24 |  |  |
|  | `  .niigata_turf_placing_counts` | array:int | +632 | 24 |  |  |
|  | `  .tokyo_turf_placing_counts` | array:int | +656 | 24 |  |  |
|  | `  .nakayama_turf_placing_counts` | array:int | +680 | 24 |  |  |
|  | `  .chukyo_turf_placing_counts` | array:int | +704 | 24 |  |  |
|  | `  .kyoto_turf_placing_counts` | array:int | +728 | 24 |  |  |
|  | `  .hanshin_turf_placing_counts` | array:int | +752 | 24 |  |  |
|  | `  .kokura_turf_placing_counts` | array:int | +776 | 24 |  |  |
|  | `  .sapporo_dirt_placing_counts` | array:int | +800 | 24 |  |  |
|  | `  .hakodate_dirt_placing_counts` | array:int | +824 | 24 |  |  |
|  | `  .fukushima_dirt_placing_counts` | array:int | +848 | 24 |  |  |
|  | `  .niigata_dirt_placing_counts` | array:int | +872 | 24 |  |  |
|  | `  .tokyo_dirt_placing_counts` | array:int | +896 | 24 |  |  |
|  | `  .nakayama_dirt_placing_counts` | array:int | +920 | 24 |  |  |
|  | `  .chukyo_dirt_placing_counts` | array:int | +944 | 24 |  |  |
|  | `  .kyoto_dirt_placing_counts` | array:int | +968 | 24 |  |  |
|  | `  .hanshin_dirt_placing_counts` | array:int | +992 | 24 |  |  |
|  | `  .kokura_dirt_placing_counts` | array:int | +1016 | 24 |  |  |
|  | `  .sapporo_obstacle_placing_counts` | array:int | +1040 | 18 |  |  |
|  | `  .hakodate_obstacle_placing_counts` | array:int | +1058 | 18 |  |  |
|  | `  .fukushima_obstacle_placing_counts` | array:int | +1076 | 18 |  |  |
|  | `  .niigata_obstacle_placing_counts` | array:int | +1094 | 18 |  |  |
|  | `  .tokyo_obstacle_placing_counts` | array:int | +1112 | 18 |  |  |
|  | `  .nakayama_obstacle_placing_counts` | array:int | +1130 | 18 |  |  |
|  | `  .chukyo_obstacle_placing_counts` | array:int | +1148 | 18 |  |  |
|  | `  .kyoto_obstacle_placing_counts` | array:int | +1166 | 18 |  |  |
|  | `  .hanshin_obstacle_placing_counts` | array:int | +1184 | 18 |  |  |
|  | `  .kokura_obstacle_placing_counts` | array:int | +1202 | 18 |  |  |
| 92 | `trainer_code` | str | 3864 | 5 | 調教師コード |  |
| 93 | `trainer_name` | str | 3869 | 34 | 調教師名 |  |
| 94 | `trainer_performance_stats` | array:object[2] | 3903 | 2440 |  |  |
|  | `  .year` | int | +0 | 4 |  |  |
|  | `  .flat_prize_money` | money_100yen | +4 | 10 |  |  |
|  | `  .obstacle_prize_money` | money_100yen | +14 | 10 |  |  |
|  | `  .flat_added_money` | money_100yen | +24 | 10 |  |  |
|  | `  .obstacle_added_money` | money_100yen | +34 | 10 |  |  |
|  | `  .turf_placing_counts` | array:int | +44 | 30 |  |  |
|  | `  .dirt_placing_counts` | array:int | +74 | 30 |  |  |
|  | `  .obstacle_placing_counts` | array:int | +104 | 24 |  |  |
|  | `  .turf_dist_1200_placing_counts` | array:int | +128 | 24 |  |  |
|  | `  .turf_dist_1201_1400_placing_counts` | array:int | +152 | 24 |  |  |
|  | `  .turf_dist_1401_1600_placing_counts` | array:int | +176 | 24 |  |  |
|  | `  .turf_dist_1601_1800_placing_counts` | array:int | +200 | 24 |  |  |
|  | `  .turf_dist_1801_2000_placing_counts` | array:int | +224 | 24 |  |  |
|  | `  .turf_dist_2001_2200_placing_counts` | array:int | +248 | 24 |  |  |
|  | `  .turf_dist_2201_2400_placing_counts` | array:int | +272 | 24 |  |  |
|  | `  .turf_dist_2401_2800_placing_counts` | array:int | +296 | 24 |  |  |
|  | `  .turf_dist_2801_placing_counts` | array:int | +320 | 24 |  |  |
|  | `  .dirt_dist_1200_placing_counts` | array:int | +344 | 24 |  |  |
|  | `  .dirt_dist_1201_1400_placing_counts` | array:int | +368 | 24 |  |  |
|  | `  .dirt_dist_1401_1600_placing_counts` | array:int | +392 | 24 |  |  |
|  | `  .dirt_dist_1601_1800_placing_counts` | array:int | +416 | 24 |  |  |
|  | `  .dirt_dist_1801_2000_placing_counts` | array:int | +440 | 24 |  |  |
|  | `  .dirt_dist_2001_2200_placing_counts` | array:int | +464 | 24 |  |  |
|  | `  .dirt_dist_2201_2400_placing_counts` | array:int | +488 | 24 |  |  |
|  | `  .dirt_dist_2401_2800_placing_counts` | array:int | +512 | 24 |  |  |
|  | `  .dirt_dist_2801_placing_counts` | array:int | +536 | 24 |  |  |
|  | `  .sapporo_turf_placing_counts` | array:int | +560 | 24 |  |  |
|  | `  .hakodate_turf_placing_counts` | array:int | +584 | 24 |  |  |
|  | `  .fukushima_turf_placing_counts` | array:int | +608 | 24 |  |  |
|  | `  .niigata_turf_placing_counts` | array:int | +632 | 24 |  |  |
|  | `  .tokyo_turf_placing_counts` | array:int | +656 | 24 |  |  |
|  | `  .nakayama_turf_placing_counts` | array:int | +680 | 24 |  |  |
|  | `  .chukyo_turf_placing_counts` | array:int | +704 | 24 |  |  |
|  | `  .kyoto_turf_placing_counts` | array:int | +728 | 24 |  |  |
|  | `  .hanshin_turf_placing_counts` | array:int | +752 | 24 |  |  |
|  | `  .kokura_turf_placing_counts` | array:int | +776 | 24 |  |  |
|  | `  .sapporo_dirt_placing_counts` | array:int | +800 | 24 |  |  |
|  | `  .hakodate_dirt_placing_counts` | array:int | +824 | 24 |  |  |
|  | `  .fukushima_dirt_placing_counts` | array:int | +848 | 24 |  |  |
|  | `  .niigata_dirt_placing_counts` | array:int | +872 | 24 |  |  |
|  | `  .tokyo_dirt_placing_counts` | array:int | +896 | 24 |  |  |
|  | `  .nakayama_dirt_placing_counts` | array:int | +920 | 24 |  |  |
|  | `  .chukyo_dirt_placing_counts` | array:int | +944 | 24 |  |  |
|  | `  .kyoto_dirt_placing_counts` | array:int | +968 | 24 |  |  |
|  | `  .hanshin_dirt_placing_counts` | array:int | +992 | 24 |  |  |
|  | `  .kokura_dirt_placing_counts` | array:int | +1016 | 24 |  |  |
|  | `  .sapporo_obstacle_placing_counts` | array:int | +1040 | 18 |  |  |
|  | `  .hakodate_obstacle_placing_counts` | array:int | +1058 | 18 |  |  |
|  | `  .fukushima_obstacle_placing_counts` | array:int | +1076 | 18 |  |  |
|  | `  .niigata_obstacle_placing_counts` | array:int | +1094 | 18 |  |  |
|  | `  .tokyo_obstacle_placing_counts` | array:int | +1112 | 18 |  |  |
|  | `  .nakayama_obstacle_placing_counts` | array:int | +1130 | 18 |  |  |
|  | `  .chukyo_obstacle_placing_counts` | array:int | +1148 | 18 |  |  |
|  | `  .kyoto_obstacle_placing_counts` | array:int | +1166 | 18 |  |  |
|  | `  .hanshin_obstacle_placing_counts` | array:int | +1184 | 18 |  |  |
|  | `  .kokura_obstacle_placing_counts` | array:int | +1202 | 18 |  |  |
| 95 | `owner_code` | str | 6343 | 6 | 馬主コード |  |
| 96 | `owner_name_with_corp` | str | 6349 | 64 | 馬主名(法人格有) |  |
| 97 | `owner_name_individual` | str | 6413 | 64 | 馬主名(法人格無) |  |
| 98 | `owner_performance_stats` | array:object[2] | 6477 | 120 |  |  |
|  | `  .year` | int | +0 | 4 |  |  |
|  | `  .prize_money` | money_100yen | +4 | 10 |  |  |
|  | `  .added_money` | money_100yen | +14 | 10 |  |  |
|  | `  .placing_counts` | array:int | +24 | 36 |  |  |
| 99 | `breeder_code` | str | 6597 | 8 | 生産者コード |  |
| 100 | `breeder_name_with_corp` | str | 6605 | 72 | 生産者名(法人格有) |  |
| 101 | `breeder_name_individual` | str | 6677 | 72 | 生産者名(法人格無) |  |
| 102 | `breeder_performance_stats` | array:object[2] | 6749 | 120 |  |  |
|  | `  .year` | int | +0 | 4 |  |  |
|  | `  .prize_money` | money_100yen | +4 | 10 |  |  |
|  | `  .added_money` | money_100yen | +14 | 10 |  |  |
|  | `  .placing_counts` | array:int | +24 | 36 |  |  |
