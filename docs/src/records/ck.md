# CKレコード（出走別着度数）

## データ特性

- **配信タイミング**: 木曜20:00頃（出馬表作成時）、月曜14:00頃（騎手変更時）
- **KEY_FIELDS**: `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`, `race_number`, `pedigree_reg_num`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"CK" |
| 2 | データ区分 | data_code | CKDataCategory | 数値1桁 | 数字ゼロ | 1:通常、2:削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | yyyy形式 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | mmdd形式 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ |  |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ |  |
| 9 | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ |  |
| 10 | 血統登録番号 | pedigree_reg_num | HalfWidthString | 半角10文字 | 数字ゼロ | 生年(西暦)4桁＋品種1桁＋数字5桁 |
| 11 | 馬名 | horse_name | MixedWidthStringByByte | 全角18文字～半角36文字 | 全角または半角スペース | 通常全角18文字。 |
| 12 | 平地本賞金累計 | flat_purse_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 13 | 障害本賞金累計 | obstacle_purse_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 14 | 平地付加賞金累計 | flat_added_money_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 15 | 障害付加賞金累計 | obstacle_added_money_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 16 | 平地収得賞金累計 | flat_earned_money_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 17 | 障害収得賞金累計 | obstacle_earned_money_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 18 | 総合着回数 | total_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 中央＋地方＋海外、1-5着及び着外 |
| 19 | 中央合計着回数 | jra_total_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 中央のみ、1-5着及び着外 |
| 20 | 芝直・着回数 | turf_straight_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝・直線コース（中央のみ) |
| 21 | 芝右・着回数 | turf_right_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝・右回りコース（中央のみ) |
| 22 | 芝左・着回数 | turf_left_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝・左回りコース（中央のみ) |
| 23 | ダ直・着回数 | dirt_straight_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート・直線コース（中央のみ) |
| 24 | ダ右・着回数 | dirt_right_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート・右回りコース（中央のみ) |
| 25 | ダ左・着回数 | dirt_left_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート・左回りコース（中央のみ) |
| 26 | 障害・着回数 | obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 障害レース（中央のみ) |
| 27 | 芝良・着回数 | turf_good_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝・良馬場（中央のみ) |
| 28 | 芝稍・着回数 | turf_yielding_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝・稍重馬場（中央のみ) |
| 29 | 芝重・着回数 | turf_heavy_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝・重馬場（中央のみ) |
| 30 | 芝不・着回数 | turf_soft_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝・不良馬場（中央のみ) |
| 31 | ダ良・着回数 | dirt_good_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート・良馬場（中央のみ) |
| 32 | ダ稍・着回数 | dirt_yielding_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート・稍重馬場（中央のみ) |
| 33 | ダ重・着回数 | dirt_heavy_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート・重馬場（中央のみ) |
| 34 | ダ不・着回数 | dirt_soft_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート・不良馬場（中央のみ) |
| 35 | 障良・着回数 | obstacle_good_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 障害レース・良馬場（中央のみ) |
| 36 | 障稍・着回数 | obstacle_yielding_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 障害レース・稍重馬場（中央のみ) |
| 37 | 障重・着回数 | obstacle_heavy_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 障害レース・重馬場（中央のみ) |
| 38 | 障不・着回数 | obstacle_soft_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 障害レース・不良馬場（中央のみ) |
| 39 | 芝1200以下・着回数 | turf_dist_1200_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝1200M以下（中央のみ) |
| 40 | 芝1201-1400・着回数 | turf_dist_1201_1400_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝1201-1400M（中央のみ) |
| 41 | 芝1401-1600・着回数 | turf_dist_1401_1600_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝1401-1600M（中央のみ) |
| 42 | 芝1601-1800・着回数 | turf_dist_1601_1800_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝1601-1800M（中央のみ) |
| 43 | 芝1801-2000・着回数 | turf_dist_1801_2000_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝1801-2000M（中央のみ) |
| 44 | 芝2001-2200・着回数 | turf_dist_2001_2200_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝2001-2200M（中央のみ) |
| 45 | 芝2201-2400・着回数 | turf_dist_2201_2400_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝2201-2400M（中央のみ) |
| 46 | 芝2401-2800・着回数 | turf_dist_2401_2800_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝2401-2800M（中央のみ) |
| 47 | 芝2801以上・着回数 | turf_dist_2801_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 芝2801M以上（中央のみ) |
| 48 | ダ1200以下・着回数 | dirt_dist_1200_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート1200M以下（中央のみ) |
| 49 | ダ1201-1400・着回数 | dirt_dist_1201_1400_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート1201-1400M（中央のみ) |
| 50 | ダ1401-1600・着回数 | dirt_dist_1401_1600_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート1401-1600M（中央のみ) |
| 51 | ダ1601-1800・着回数 | dirt_dist_1601_1800_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート1601-1800M（中央のみ) |
| 52 | ダ1801-2000・着回数 | dirt_dist_1801_2000_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート1801-2000M（中央のみ) |
| 53 | ダ2001-2200・着回数 | dirt_dist_2001_2200_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート2001-2200M（中央のみ) |
| 54 | ダ2201-2400・着回数 | dirt_dist_2201_2400_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート2201-2400M（中央のみ) |
| 55 | ダ2401-2800・着回数 | dirt_dist_2401_2800_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート2401-2800M（中央のみ) |
| 56 | ダ2801以上・着回数 | dirt_dist_2801_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | ダート2801M以上（中央のみ) |
| 57 | 札幌芝・着回数 | sapporo_turf_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 札幌・芝 |
| 58 | 函館芝・着回数 | hakodate_turf_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 函館・芝 |
| 59 | 福島芝・着回数 | fukushima_turf_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 福島・芝 |
| 60 | 新潟芝・着回数 | niigata_turf_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 新潟・芝 |
| 61 | 東京芝・着回数 | tokyo_turf_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 東京・芝 |
| 62 | 中山芝・着回数 | nakayama_turf_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 中山・芝 |
| 63 | 中京芝・着回数 | chukyo_turf_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 中京・芝 |
| 64 | 京都芝・着回数 | kyoto_turf_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 京都・芝 |
| 65 | 阪神芝・着回数 | hanshin_turf_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 阪神・芝 |
| 66 | 小倉芝・着回数 | kokura_turf_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 小倉・芝 |
| 67 | 札幌ダ・着回数 | sapporo_dirt_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 札幌・ダート |
| 68 | 函館ダ・着回数 | hakodate_dirt_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 函館・ダート |
| 69 | 福島ダ・着回数 | fukushima_dirt_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 福島・ダート |
| 70 | 新潟ダ・着回数 | niigata_dirt_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 新潟・ダート |
| 71 | 東京ダ・着回数 | tokyo_dirt_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 東京・ダート |
| 72 | 中山ダ・着回数 | nakayama_dirt_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 中山・ダート |
| 73 | 中京ダ・着回数 | chukyo_dirt_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 中京・ダート |
| 74 | 京都ダ・着回数 | kyoto_dirt_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 京都・ダート |
| 75 | 阪神ダ・着回数 | hanshin_dirt_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 阪神・ダート |
| 76 | 小倉ダ・着回数 | kokura_dirt_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 小倉・ダート |
| 77 | 札幌障・着回数 | sapporo_obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 札幌・障害 |
| 78 | 函館障・着回数 | hakodate_obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 函館・障害 |
| 79 | 福島障・着回数 | fukushima_obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 福島・障害 |
| 80 | 新潟障・着回数 | niigata_obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 新潟・障害 |
| 81 | 東京障・着回数 | tokyo_obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 東京・障害 |
| 82 | 中山障・着回数 | nakayama_obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 中山・障害 |
| 83 | 中京障・着回数 | chukyo_obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 中京・障害 |
| 84 | 京都障・着回数 | kyoto_obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 京都・障害 |
| 85 | 阪神障・着回数 | hanshin_obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 阪神・障害 |
| 86 | 小倉障・着回数 | kokura_obstacle_placing_counts | tuple[int, ...] | 各数値3桁×6 | 数字ゼロ | 小倉・障害 |
| 87 | 脚質傾向 | running_style_counts | tuple[int, ...] | 各数値3桁×4 | 数字ゼロ | 逃げ・先行・差し・追込回数 |
| 88 | 登録レース数 | registered_race_count | int | 数値3桁 | 数字ゼロ |  |
| 89 | 騎手コード | jockey_code | str | 数値5桁 | 数字ゼロ | [騎手コード](../code-tables/jockey-codes.md)参照 |
| 90 | 騎手名 | jockey_name | str | 全角17文字 | 全角スペース |  |
| 91 | 騎手成績 | jockey_performance_stats | tuple[[CKJockeyPerformanceStatsItem](#ckjockeyperformancestatsitem-cktrainerperformancestatsitem), ...] | 各項目別×2 | 数字ゼロ | 本年・累計2回繰り返し |
| 92 | 調教師コード | trainer_code | str | 数値5桁 | 数字ゼロ |  |
| 93 | 調教師名 | trainer_name | str | 全角17文字 | 全角スペース |  |
| 94 | 調教師成績 | trainer_performance_stats | tuple[[CKTrainerPerformanceStatsItem](#ckjockeyperformancestatsitem-cktrainerperformancestatsitem), ...] | 各項目別×2 | 数字ゼロ | 本年・累計2回繰り返し |
| 95 | 馬主コード | owner_code | str | 数値6桁 | 数字ゼロ |  |
| 96 | 馬主名(法人格有) | owner_name_with_corp | str | 全角32文字～半角64文字 | 全角または半角スペース |  |
| 97 | 馬主名(法人格無) | owner_name_individual | str | 全角32文字～半角64文字 | 全角または半角スペース |  |
| 98 | 馬主成績 | owner_performance_stats | tuple[[CKOwnerPerformanceStatsItem](#ckownerperformancestatsitem-ckbreederperformancestatsitem), ...] | 各項目別×2 | 数字ゼロ | 本年・累計2回繰り返し |
| 99 | 生産者コード | breeder_code | str | 数値8桁 | 数字ゼロ |  |
| 100 | 生産者名(法人格有) | breeder_name_with_corp | str | 全角36文字～半角72文字 | 全角または半角スペース |  |
| 101 | 生産者名(法人格無) | breeder_name_individual | str | 全角36文字～半角72文字 | 全角または半角スペース |  |
| 102 | 生産者成績 | breeder_performance_stats | tuple[[CKBreederPerformanceStatsItem](#ckownerperformancestatsitem-ckbreederperformancestatsitem), ...] | 各項目別×2 | 数字ゼロ | 本年・累計2回繰り返し |

### CKJockeyPerformanceStatsItem / CKTrainerPerformanceStatsItem

騎手・調教師の年度別成績。両者は同一構造。

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数 | 初期値 |
|----------|-------------|-------------|------|---|----------|----------|
| a | 年度 | year | 成績情報の対象年度 | int | 数値4桁 | 数字ゼロ |
| b | 平地本賞金合計 | flat_prize_money | 単位:百円 | int | 数値10桁 | 数字ゼロ |
| c | 障害本賞金合計 | obstacle_prize_money | 単位:百円 | int | 数値10桁 | 数字ゼロ |
| d | 平地付加賞金合計 | flat_added_money | 単位:百円 | int | 数値10桁 | 数字ゼロ |
| e | 障害付加賞金合計 | obstacle_added_money | 単位:百円 | int | 数値10桁 | 数字ゼロ |
| f | 芝着回数 | turf_placing_counts | 各5桁 | tuple[int, ...] | - | 数字ゼロ |
| g | ダート着回数 | dirt_placing_counts | 各5桁 | tuple[int, ...] | - | 数字ゼロ |
| h | 障害着回数 | obstacle_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| i | 芝1200以下・着回数 | turf_dist_1200_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| j | 芝1201-1400・着回数 | turf_dist_1201_1400_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| k | 芝1401-1600・着回数 | turf_dist_1401_1600_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| l | 芝1601-1800・着回数 | turf_dist_1601_1800_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| m | 芝1801-2000・着回数 | turf_dist_1801_2000_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| n | 芝2001-2200・着回数 | turf_dist_2001_2200_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| o | 芝2201-2400・着回数 | turf_dist_2201_2400_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| p | 芝2401-2800・着回数 | turf_dist_2401_2800_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| q | 芝2801以上・着回数 | turf_dist_2801_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| r | ダ1200以下・着回数 | dirt_dist_1200_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| s | ダ1201-1400・着回数 | dirt_dist_1201_1400_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| t | ダ1401-1600・着回数 | dirt_dist_1401_1600_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| u | ダ1601-1800・着回数 | dirt_dist_1601_1800_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| v | ダ1801-2000・着回数 | dirt_dist_1801_2000_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| w | ダ2001-2200・着回数 | dirt_dist_2001_2200_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| x | ダ2201-2400・着回数 | dirt_dist_2201_2400_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| y | ダ2401-2800・着回数 | dirt_dist_2401_2800_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| z | ダ2801以上・着回数 | dirt_dist_2801_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| aa | 札幌芝・着回数 | sapporo_turf_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ab | 函館芝・着回数 | hakodate_turf_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ac | 福島芝・着回数 | fukushima_turf_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ad | 新潟芝・着回数 | niigata_turf_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ae | 東京芝・着回数 | tokyo_turf_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| af | 中山芝・着回数 | nakayama_turf_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ag | 中京芝・着回数 | chukyo_turf_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ah | 京都芝・着回数 | kyoto_turf_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ai | 阪神芝・着回数 | hanshin_turf_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| aj | 小倉芝・着回数 | kokura_turf_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ak | 札幌ダ・着回数 | sapporo_dirt_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| al | 函館ダ・着回数 | hakodate_dirt_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| am | 福島ダ・着回数 | fukushima_dirt_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| an | 新潟ダ・着回数 | niigata_dirt_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ao | 東京ダ・着回数 | tokyo_dirt_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ap | 中山ダ・着回数 | nakayama_dirt_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| aq | 中京ダ・着回数 | chukyo_dirt_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| ar | 京都ダ・着回数 | kyoto_dirt_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| as | 阪神ダ・着回数 | hanshin_dirt_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| at | 小倉ダ・着回数 | kokura_dirt_placing_counts | 各4桁 | tuple[int, ...] | - | 数字ゼロ |
| au | 札幌障・着回数 | sapporo_obstacle_placing_counts | 各3桁 | tuple[int, ...] | - | 数字ゼロ |
| av | 函館障・着回数 | hakodate_obstacle_placing_counts | 各3桁 | tuple[int, ...] | - | 数字ゼロ |
| aw | 福島障・着回数 | fukushima_obstacle_placing_counts | 各3桁 | tuple[int, ...] | - | 数字ゼロ |
| ax | 新潟障・着回数 | niigata_obstacle_placing_counts | 各3桁 | tuple[int, ...] | - | 数字ゼロ |
| ay | 東京障・着回数 | tokyo_obstacle_placing_counts | 各3桁 | tuple[int, ...] | - | 数字ゼロ |
| az | 中山障・着回数 | nakayama_obstacle_placing_counts | 各3桁 | tuple[int, ...] | - | 数字ゼロ |
| ba | 中京障・着回数 | chukyo_obstacle_placing_counts | 各3桁 | tuple[int, ...] | - | 数字ゼロ |
| bb | 京都障・着回数 | kyoto_obstacle_placing_counts | 各3桁 | tuple[int, ...] | - | 数字ゼロ |
| bc | 阪神障・着回数 | hanshin_obstacle_placing_counts | 各3桁 | tuple[int, ...] | - | 数字ゼロ |
| bd | 小倉障・着回数 | kokura_obstacle_placing_counts | 各3桁 | tuple[int, ...] | - | 数字ゼロ |

### CKOwnerPerformanceStatsItem / CKBreederPerformanceStatsItem

馬主・生産者の年度別成績。両者は同一構造。

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数 | 初期値 |
|----------|-------------|-------------|------|---|----------|----------|
| a | 年度 | year | 成績情報の対象年度 | int | 数値4桁 | 数字ゼロ |
| b | 本賞金合計 | prize_money | 中央の本賞金合計（単位:百円） | int | 数値10桁 | 数字ゼロ |
| c | 付加賞金合計 | added_money | 中央の付加賞金合計（単位:百円） | int | 数値10桁 | 数字ゼロ |
| d | 着回数 | placing_counts | 各6桁 | tuple[int, ...] | - | 数字ゼロ |

## 関連項目

- [DataSpec SNAP](../data-specs/storage/snap.md)
- [DataSpec SNPN](../data-specs/storage/snap.md)
