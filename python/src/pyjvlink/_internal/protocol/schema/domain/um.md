# UM - 競走馬マスタ

レコード長: 1609 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `pedigree_reg_num` | str | 12 | 10 | 血統登録番号 | KEY |
| 5 | `deregistration_flag` | str | 22 | 1 | 競走馬抹消区分 |  |
| 6 | `registration_date` | date_yyyymmdd | 23 | 8 | 競走馬登録年月日 |  |
| 7 | `deregistration_date` | date_yyyymmdd | 31 | 8 | 競走馬抹消年月日 |  |
| 8 | `birth_date` | date_yyyymmdd | 39 | 8 | 生年月日 |  |
| 9 | `horse_name` | str | 47 | 36 | 馬名 |  |
| 10 | `horse_name_kana` | str | 83 | 36 | 馬名半角カナ |  |
| 11 | `horse_name_english` | str | 119 | 60 | 馬名欧字 |  |
| 12 | `jra_facility_flag` | str | 179 | 1 | JRA施設在きゅうフラグ |  |
| 14 | `horse_symbol_code` | str | 199 | 2 | 馬記号コード |  |
| 15 | `sex_code` | str | 201 | 1 | 性別コード |  |
| 16 | `breed_code` | str | 202 | 1 | 品種コード |  |
| 17 | `coat_color_code` | str | 203 | 2 | 毛色コード |  |
| 18 | `pedigree_3gen` | array:object[14] | 205 | 644 | 3代血統情報 |  |
|  | `  .breeding_reg_num` | str | +0 | 10 | 繁殖登録番号 |  |
|  | `  .horse_name` | str | +10 | 36 | 馬名 |  |
| 19 | `affiliation_code` | str | 849 | 1 | 東西所属コード |  |
| 20 | `trainer_code` | str | 850 | 5 | 調教師コード |  |
| 21 | `trainer_name_short` | str | 855 | 8 | 調教師名略称 |  |
| 22 | `invitation_area_name` | str | 863 | 20 | 招待地域名 |  |
| 23 | `breeder_code` | str | 883 | 8 | 生産者コード |  |
| 24 | `breeder_name` | str | 891 | 72 | 生産者名 |  |
| 25 | `birthplace_name` | str | 963 | 20 | 産地名 |  |
| 26 | `owner_code` | str | 983 | 6 | 馬主コード |  |
| 27 | `owner_name` | str | 989 | 64 | 馬主名 |  |
| 28 | `flat_prize_money_total` | money_100yen | 1053 | 9 | 平地本賞金累計 |  |
| 29 | `steeplechase_prize_money_total` | money_100yen | 1062 | 9 | 障害本賞金累計 |  |
| 30 | `flat_added_money_total` | money_100yen | 1071 | 9 | 平地付加賞金累計 |  |
| 31 | `steeplechase_added_money_total` | money_100yen | 1080 | 9 | 障害付加賞金累計 |  |
| 32 | `flat_earnings_total` | money_100yen | 1089 | 9 | 平地収得賞金累計 |  |
| 33 | `steeplechase_earnings_total` | money_100yen | 1098 | 9 | 障害収得賞金累計 |  |
| 34 | `overall_placing_counts` | array:int[6] | 1107 | 18 | 総合着回数 |  |
| 35 | `central_placing_counts` | array:int[6] | 1125 | 18 | 中央合計着回数 |  |
| 36 | `turf_straight_placing_counts` | array:int[6] | 1143 | 18 | 芝直着回数 |  |
| 37 | `turf_right_placing_counts` | array:int[6] | 1161 | 18 | 芝右着回数 |  |
| 38 | `turf_left_placing_counts` | array:int[6] | 1179 | 18 | 芝左着回数 |  |
| 39 | `dirt_straight_placing_counts` | array:int[6] | 1197 | 18 | ダ直着回数 |  |
| 40 | `dirt_right_placing_counts` | array:int[6] | 1215 | 18 | ダ右着回数 |  |
| 41 | `dirt_left_placing_counts` | array:int[6] | 1233 | 18 | ダ左着回数 |  |
| 42 | `steeplechase_placing_counts` | array:int[6] | 1251 | 18 | 障害着回数 |  |
| 43 | `turf_good_placing_counts` | array:int[6] | 1269 | 18 | 芝良着回数 |  |
| 44 | `turf_slightly_heavy_placing_counts` | array:int[6] | 1287 | 18 | 芝稍着回数 |  |
| 45 | `turf_heavy_placing_counts` | array:int[6] | 1305 | 18 | 芝重着回数 |  |
| 46 | `turf_bad_placing_counts` | array:int[6] | 1323 | 18 | 芝不着回数 |  |
| 47 | `dirt_good_placing_counts` | array:int[6] | 1341 | 18 | ダ良着回数 |  |
| 48 | `dirt_slightly_heavy_placing_counts` | array:int[6] | 1359 | 18 | ダ稍着回数 |  |
| 49 | `dirt_heavy_placing_counts` | array:int[6] | 1377 | 18 | ダ重着回数 |  |
| 50 | `dirt_bad_placing_counts` | array:int[6] | 1395 | 18 | ダ不着回数 |  |
| 51 | `steeplechase_good_placing_counts` | array:int[6] | 1413 | 18 | 障良着回数 |  |
| 52 | `steeplechase_slightly_heavy_placing_counts` | array:int[6] | 1431 | 18 | 障稍着回数 |  |
| 53 | `steeplechase_heavy_placing_counts` | array:int[6] | 1449 | 18 | 障重着回数 |  |
| 54 | `steeplechase_bad_placing_counts` | array:int[6] | 1467 | 18 | 障不着回数 |  |
| 55 | `turf_short_placing_counts` | array:int[6] | 1485 | 18 | 芝16下着回数 |  |
| 56 | `turf_mid_placing_counts` | array:int[6] | 1503 | 18 | 芝22下着回数 |  |
| 57 | `turf_long_placing_counts` | array:int[6] | 1521 | 18 | 芝22超着回数 |  |
| 58 | `dirt_short_placing_counts` | array:int[6] | 1539 | 18 | ダ16下着回数 |  |
| 59 | `dirt_mid_placing_counts` | array:int[6] | 1557 | 18 | ダ22下着回数 |  |
| 60 | `dirt_long_placing_counts` | array:int[6] | 1575 | 18 | ダ22超着回数 |  |
| 61 | `running_style_counts` | array:int[4] | 1593 | 12 | 脚質傾向 |  |
| 62 | `registered_race_count` | int | 1605 | 3 | 登録レース数 |  |
