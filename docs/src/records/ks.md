# KSレコード（騎手マスタ）

## データ特性

- **配信タイミング**: 月曜14:00頃、木曜20:00頃（DIFFまたはRCOVデータに含まれる）
- **KEY_FIELDS**: `jockey_code`

## フィールド仕様

### 基本情報

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"KS" |
| 2 | データ区分 | data_code | KSDataCategory | 数値1桁 | 数字ゼロ | 1:新規登録、2:更新、0:削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 騎手コード | jockey_code | FixedDigitInteger | 数値5桁 | 数字ゼロ | 騎手を一意に識別 |
| 5 | 騎手抹消区分 | deregistration_flag | Flag | 数値1桁 | 数字ゼロ | 0:現役、1:抹消 |
| 6 | 騎手免許交付年月日 | license_issue_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | 免許取得日 |
| 7 | 騎手免許抹消年月日 | license_revoked_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | 引退日（現役は00000000） |
| 8 | 生年月日 | birth_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | 誕生日 |
| 9 | 騎手名 | jockey_name | FullWidthString | 全角17文字 | 全角スペース | 姓名（外国人は連続） |
| 10 | 予備 | reserved_34 | ReservedField | 半角34文字 | 半角スペース |  |
| 11 | 騎手名半角カナ | jockey_name_kana | HalfWidthString | 半角30文字 | 半角スペース | カナ表記 |
| 12 | 騎手名略称 | jockey_name_short | FullWidthString | 全角4文字 | 全角スペース | 略称 |
| 13 | 騎手名欧字 | jockey_name_english | HalfWidthString | 半角80文字 | 半角スペース | 英語表記 |
| 14 | 性別区分 | sex_code | PersonSex | 数値1桁 | 数字ゼロ | 1:男性、2:女性 |
| 15 | 騎乗資格コード | riding_qualification_code | RidingQualification | 数値1桁 | 数字ゼロ | [騎乗資格コード](../code-tables/jockey-codes.md)参照 |
| 16 | 騎手見習コード | jockey_apprentice_code | ApprenticeJockey | 数値1桁 | 数字ゼロ | [騎手見習コード](../code-tables/jockey-codes.md)参照 |
| 17 | 騎手東西所属コード | affiliation_code | EastWestAffiliation | 数値1桁 | 数字ゼロ | [東西所属コード](../code-tables/basic-codes.md)参照 |
| 18 | 招待地域名 | invitation_area_name | FullWidthString | 全角10文字 | 全角スペース | 招待騎手の地域 |
| 19 | 所属調教師コード | affiliated_trainer_code | TrainerCode | 数値5桁 | 数字ゼロ | 所属厩舎（フリーは00000） |
| 20 | 所属調教師名略称 | affiliated_trainer_name_short | FullWidthString | 全角4文字 | 全角スペース | 調教師略称 |
| 21 | 初騎乗情報 | first_ride_info | tuple[[KSFirstRideInfoItem](#ksfirstrideinfoitem), ...] | 108バイト（54バイト×2） | - | 平地・障害の初騎乗情報 |
| 22 | 初勝利情報 | first_win_info | tuple[[KSFirstWinInfoItem](#ksfirstwininfoitem), ...] | 84バイト（42バイト×2） | - | 平地・障害の初勝利情報 |
| 23 | 最近重賞勝利情報 | recent_graded_wins | tuple[[KSRecentGradedWinsItem](#ksrecentgradedwinsitem), ...] | 163バイト×3 | - | 直近の重賞勝利から新しい順に3件 |
| 24 | 本年・前年・累計成績情報 | performance_stats | tuple[[KSPerformanceStatsItem](#ksperformancestatsitem), ...] | 1052バイト×3 | - | 本年・前年・累計の3つの年度別成績情報 |

### KSFirstRideInfoItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| 21-a | レース識別キー | race_key | 年月日場回日R | FixedDigitInteger | 数値16桁 | 数字ゼロ |
| 21-b | 出走頭数 | num_starters | 該当レースの出走頭数 | FixedDigitInteger | 数値2桁 | 数字ゼロ |
| 21-c | 血統登録番号 | pedigree_reg_num | 騎乗馬の血統登録番号 | HalfWidthString | 半角10文字 | 数字ゼロ |
| 21-d | 馬名 | horse_name | 騎乗馬名 | FullWidthString | 全角18文字 | 全角スペース |
| 21-e | 確定着順 | confirmed_placing | 該当レースの確定着順 | FixedDigitInteger | 数値2桁 | 数字ゼロ |
| 21-f | 異常区分コード | abnormality_code | [異常区分コード](../code-tables/result-codes.md)参照 | AbnormalityCategory | 数値1桁 | 数字ゼロ |

### FirstRideCollection

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| 21a | 平地初騎乗情報 | flat | 平地での初騎乗情報 | [KSFirstRideInfoItem](#ksfirstrideinfoitem) | - | - |
| 21b | 障害初騎乗情報 | steeplechase | 障害での初騎乗情報 | [KSFirstRideInfoItem](#ksfirstrideinfoitem) | - | - |

### KSFirstWinInfoItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| 22-a | レース識別キー | race_key | 年月日場回日R | FixedDigitInteger | 数値16桁 | 数字ゼロ |
| 22-b | 出走頭数 | num_starters | 該当レースの出走頭数 | FixedDigitInteger | 数値2桁 | 数字ゼロ |
| 22-c | 血統登録番号 | pedigree_reg_num | 騎乗馬の血統登録番号 | HalfWidthString | 半角10文字 | 数字ゼロ |
| 22-d | 馬名 | horse_name | 騎乗馬名 | FullWidthString | 全角18文字 | 全角スペース |

### FirstWinCollection

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| 22a | 平地初勝利情報 | flat | 平地での初勝利情報 | [KSFirstWinInfoItem](#ksfirstwininfoitem) | - | - |
| 22b | 障害初勝利情報 | steeplechase | 障害での初勝利情報 | [KSFirstWinInfoItem](#ksfirstwininfoitem) | - | - |

### KSRecentGradedWinsItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| 23a | レース識別キー | race_key | 年月日場回日R | FixedDigitInteger | 数値16桁 | 数字ゼロ |
| 23b | 競走名本題 | race_name_main | 競走名の本題部分 | FullWidthString | 全角30文字 | 全角スペース |
| 23c | 競走名略称10文字 | race_short_name_10 | 10文字の競走名略称 | FullWidthString | 全角10文字 | 全角スペース |
| 23d | 競走名略称6文字 | race_short_name_6 | 6文字の競走名略称 | FullWidthString | 全角6文字 | 全角スペース |
| 23e | 競走名略称3文字 | race_short_name_3 | 3文字の競走名略称 | FullWidthString | 全角3文字 | 全角スペース |
| 23f | グレードコード | grade_code | [グレードコード](../code-tables/basic-codes.md)参照 | Grade | 半角1文字 | 半角スペース |
| 23g | 出走頭数 | num_starters | 該当レースの出走頭数 | FixedDigitInteger | 数値2桁 | 数字ゼロ |
| 23h | 血統登録番号 | pedigree_reg_num | 騎乗馬の血統登録番号 | HalfWidthString | 半角10文字 | 数字ゼロ |
| 23i | 馬名 | horse_name | 騎乗馬名 | FullWidthString | 全角18文字 | 全角スペース |

### RaceResultStat

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| - | 1着回数 | first | 1着の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |
| - | 2着回数 | second | 2着の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |
| - | 3着回数 | third | 3着の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |
| - | 4着回数 | fourth | 4着の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |
| - | 5着回数 | fifth | 5着の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |
| - | 着外回数 | other | 6着以下の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |

### KSPerformanceStatsItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| 24a | 設定年 | setting_year | 成績情報の対象年度 | DateYYYY | 数値4桁 | 数字ゼロ |
| 24b | 平地本賞金合計 | flat_total_purse_money | 中央の平地本賞金合計（単位:百円） | MoneyIn100Yen | 数値10桁 | 数字ゼロ |
| 24c | 障害本賞金合計 | steeplechase_total_purse_money | 中央の障害本賞金合計（単位:百円） | MoneyIn100Yen | 数値10桁 | 数字ゼロ |
| 24d | 平地付加賞金合計 | flat_total_added_money | 中央の平地付加賞金合計（単位:百円） | MoneyIn100Yen | 数値10桁 | 数字ゼロ |
| 24e | 障害付加賞金合計 | steeplechase_total_added_money | 中央の障害付加賞金合計（単位:百円） | MoneyIn100Yen | 数値10桁 | 数字ゼロ |
| 24f | 平地着回数 | flat_placing_counts_6 | 平地での着回数（中央のみ） | [RaceResultStat](#raceresultstat) | - | - |
| 24g | 障害着回数 | steeplechase_placing_counts_6 | 障害での着回数（中央のみ） | [RaceResultStat](#raceresultstat) | - | - |
| 24h | 札幌平地着回数 | sapporo_flat_placing_counts_6 | 札幌競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24i | 札幌障害着回数 | sapporo_steeplechase_placing_counts_6 | 札幌競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24j | 函館平地着回数 | hakodate_flat_placing_counts_6 | 函館競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24k | 函館障害着回数 | hakodate_steeplechase_placing_counts_6 | 函館競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24l | 福島平地着回数 | fukushima_flat_placing_counts_6 | 福島競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24m | 福島障害着回数 | fukushima_steeplechase_placing_counts_6 | 福島競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24n | 新潟平地着回数 | niigata_flat_placing_counts_6 | 新潟競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24o | 新潟障害着回数 | niigata_steeplechase_placing_counts_6 | 新潟競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24p | 東京平地着回数 | tokyo_flat_placing_counts_6 | 東京競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24q | 東京障害着回数 | tokyo_steeplechase_placing_counts_6 | 東京競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24r | 中山平地着回数 | nakayama_flat_placing_counts_6 | 中山競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24s | 中山障害着回数 | nakayama_steeplechase_placing_counts_6 | 中山競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24t | 中京平地着回数 | chukyo_flat_placing_counts_6 | 中京競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24u | 中京障害着回数 | chukyo_steeplechase_placing_counts_6 | 中京競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24v | 京都平地着回数 | kyoto_flat_placing_counts_6 | 京都競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24w | 京都障害着回数 | kyoto_steeplechase_placing_counts_6 | 京都競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24x | 阪神平地着回数 | hanshin_flat_placing_counts_6 | 阪神競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24y | 阪神障害着回数 | hanshin_steeplechase_placing_counts_6 | 阪神競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24z | 小倉平地着回数 | kokura_flat_placing_counts_6 | 小倉競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24aa | 小倉障害着回数 | kokura_steeplechase_placing_counts_6 | 小倉競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24ab | 芝1600m以下着回数 | turf_class_d_placing_counts | 芝1600m以下での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24ac | 芝1601-2200m着回数 | turf_class_e_placing_counts | 芝1601-2200mでの着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24ad | 芝2201m以上着回数 | turf_gt2200_placing_counts | 芝2201m以上での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24ae | ダート1600m以下着回数 | dirt_class_d_placing_counts | ダート1600m以下での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24af | ダート1601-2200m着回数 | dirt_class_e_placing_counts | ダート1601-2200mでの着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 24ag | ダート2201m以上着回数 | dirt_gt2200_placing_counts | ダート2201m以上での着回数 | [RaceResultStat](#raceresultstat) | - | - |

## 関連項目

- [DataSpec DIFF](../data-specs/storage/diff.md)
- [DataSpec DIFN](../data-specs/storage/diff.md)
- [DataSpec RCOV](../data-specs/storage/diff.md)
- [DataSpec RCVN](../data-specs/storage/diff.md)