# CHレコード（調教師マスタ）

## データ特性

- **配信タイミング**: 月曜14:00頃、木曜20:00頃（変更・追加分）
- **KEY_FIELDS**: `trainer_code`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"CH" |
| 2 | データ区分 | data_code | CHDataCategory | 数値1桁 | 数字ゼロ | 1:新規登録、2:更新、0:削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 調教師コード | trainer_code | TrainerCode | 数値5桁 | 数字ゼロ | 調教師を一意に識別 |
| 5 | 調教師抹消区分 | deregistration_flag | Flag | 数値1桁 | 数字ゼロ | 0:現役、1:抹消 |
| 6 | 調教師免許交付年月日 | license_issue_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 7 | 調教師免許抹消年月日 | license_revoked_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式（現役は"00000000"） |
| 8 | 生年月日 | birth_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 9 | 調教師名 | trainer_name | FullWidthString | 全角17文字 | 全角スペース | 姓＋全角空白1文字＋名（外国人は連続17文字） |
| 10 | 調教師名半角カナ | trainer_name_kana | HalfWidthString | 半角30文字 | 半角スペース | 姓15文字＋名15文字（外国人は連続30文字） |
| 11 | 調教師名略称 | trainer_name_short | FullWidthString | 全角4文字 | 全角スペース | 全角4文字 |
| 12 | 調教師名欧字 | trainer_name_english | HalfWidthString | 半角80文字 | 半角スペース | 姓＋半角空白1文字＋名 フルネーム |
| 13 | 性別区分 | sex_code | PersonSex | 数値1桁 | 数字ゼロ | 1:男性、2:女性 |
| 14 | 調教師東西所属コード | affiliation_code | EastWestAffiliation | 数値1桁 | 数字ゼロ | [東西所属コード](../code-tables/basic-codes.md)参照 |
| 15 | 招待地域名 | invitation_area_name | FullWidthString | 全角10文字 | 全角スペース | 招待調教師の所属国・地域名 |
| 16 | 最近重賞勝利情報 | recent_graded_wins | tuple[[CHRecentGradedWinsItem](#chrecentgradedwinsitem), ...] | 163バイト×3 | - | 直近の重賞勝利から新しい順に3件 |
| 17 | 本年・前年・累計成績情報 | performance_stats | tuple[[CHPerformanceStatsItem](#chperformancestatsitem), ...] | 1052バイト×3 | - | 現役は本年・前年・累計、引退は引退年・引退前年・累計 |

### CHRecentGradedWinsItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| 16a | レース識別キー | race_key | 年月日場回日R | FixedDigitInteger | 数値16桁 | 数字ゼロ |
| 16b | 競走名本題 | race_name_main | 競走名の本題部分 | FullWidthString | 全角30文字 | 全角スペース |
| 16c | 競走名略称10文字 | race_short_name_10 | 10文字の競走名略称 | FullWidthString | 全角10文字 | 全角スペース |
| 16d | 競走名略称6文字 | race_short_name_6 | 6文字の競走名略称 | FullWidthString | 全角6文字 | 全角スペース |
| 16e | 競走名略称3文字 | race_short_name_3 | 3文字の競走名略称 | FullWidthString | 全角3文字 | 全角スペース |
| 16f | グレードコード | grade_code | [グレードコード](../code-tables/basic-codes.md)参照 | Grade | 半角1文字 | 半角スペース |
| 16g | 出走頭数 | num_starters | 該当レースの出走頭数 | FixedDigitInteger | 数値2桁 | 数字ゼロ |
| 16h | 血統登録番号 | pedigree_reg_num | 勝利馬の血統登録番号 | HalfWidthString | 半角10文字 | 数字ゼロ |
| 16i | 馬名 | horse_name | 勝利馬名 | FullWidthString | 全角18文字 | 全角スペース |

### RaceResultStat

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| - | 1着回数 | first | 1着の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |
| - | 2着回数 | second | 2着の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |
| - | 3着回数 | third | 3着の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |
| - | 4着回数 | fourth | 4着の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |
| - | 5着回数 | fifth | 5着の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |
| - | 着外回数 | other | 6着以下の回数 | FixedDigitInteger | 数値6桁 | 数字ゼロ |

### CHPerformanceStatsItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|------|------------------|----------|----------|
| 17a | 設定年 | setting_year | 成績情報の対象年度 | DateYYYY | 数値4桁 | 数字ゼロ |
| 17b | 平地本賞金合計 | flat_total_purse_money | 中央の平地本賞金合計（単位:百円） | MoneyIn100Yen | 数値10桁 | 数字ゼロ |
| 17c | 障害本賞金合計 | steeplechase_total_purse_money | 中央の障害本賞金合計（単位:百円） | MoneyIn100Yen | 数値10桁 | 数字ゼロ |
| 17d | 平地付加賞金合計 | flat_total_added_money | 中央の平地付加賞金合計（単位:百円） | MoneyIn100Yen | 数値10桁 | 数字ゼロ |
| 17e | 障害付加賞金合計 | steeplechase_total_added_money | 中央の障害付加賞金合計（単位:百円） | MoneyIn100Yen | 数値10桁 | 数字ゼロ |
| 17f | 平地着回数 | flat_placing_counts_6 | 平地での着回数（中央のみ） | [RaceResultStat](#raceresultstat) | - | - |
| 17g | 障害着回数 | steeplechase_placing_counts_6 | 障害での着回数（中央のみ） | [RaceResultStat](#raceresultstat) | - | - |
| 17h | 札幌平地着回数 | sapporo_flat_placing_counts_6 | 札幌競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17i | 札幌障害着回数 | sapporo_steeplechase_placing_counts_6 | 札幌競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17j | 函館平地着回数 | hakodate_flat_placing_counts_6 | 函館競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17k | 函館障害着回数 | hakodate_steeplechase_placing_counts_6 | 函館競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17l | 福島平地着回数 | fukushima_flat_placing_counts_6 | 福島競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17m | 福島障害着回数 | fukushima_steeplechase_placing_counts_6 | 福島競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17n | 新潟平地着回数 | niigata_flat_placing_counts_6 | 新潟競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17o | 新潟障害着回数 | niigata_steeplechase_placing_counts_6 | 新潟競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17p | 東京平地着回数 | tokyo_flat_placing_counts_6 | 東京競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17q | 東京障害着回数 | tokyo_steeplechase_placing_counts_6 | 東京競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17r | 中山平地着回数 | nakayama_flat_placing_counts_6 | 中山競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17s | 中山障害着回数 | nakayama_steeplechase_placing_counts_6 | 中山競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17t | 中京平地着回数 | chukyo_flat_placing_counts_6 | 中京競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17u | 中京障害着回数 | chukyo_steeplechase_placing_counts_6 | 中京競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17v | 京都平地着回数 | kyoto_flat_placing_counts_6 | 京都競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17w | 京都障害着回数 | kyoto_steeplechase_placing_counts_6 | 京都競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17x | 阪神平地着回数 | hanshin_flat_placing_counts_6 | 阪神競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17y | 阪神障害着回数 | hanshin_steeplechase_placing_counts_6 | 阪神競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17z | 小倉平地着回数 | kokura_flat_placing_counts_6 | 小倉競馬場平地での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17aa | 小倉障害着回数 | kokura_steeplechase_placing_counts_6 | 小倉競馬場障害での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17ab | 芝1600M以下着回数 | turf_class_d_placing_counts_6 | 芝1600m以下での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17ac | 芝1601-2200M着回数 | turf_class_e_placing_counts_6 | 芝1601-2200mでの着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17ad | 芝2201M以上着回数 | turf_gt2200_placing_counts_6 | 芝2201m以上での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17ae | ダート1600M以下着回数 | dirt_class_d_placing_counts_6 | ダート1600m以下での着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17af | ダート1601-2200M着回数 | dirt_class_e_placing_counts_6 | ダート1601-2200mでの着回数 | [RaceResultStat](#raceresultstat) | - | - |
| 17ag | ダート2201M以上着回数 | dirt_gt2200_placing_counts_6 | ダート2201m以上での着回数 | [RaceResultStat](#raceresultstat) | - | - |

## 関連項目

- [DataSpec DIFF](../data-specs/storage/diff.md)
- [DataSpec DIFN](../data-specs/storage/diff.md)