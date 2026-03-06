# TKレコード（特別登録馬）

## データ特性

- **配信タイミング**: 通常日曜日（ハンデ発表前）、通常月曜日（ハンデ発表後）
- **KEY_FIELDS**: `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`, `race_number`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"TK" |
| 2 | データ区分 | data_code | TKDataCategory | 数値1桁 | 数字ゼロ | 1:ハンデ発表前、2:ハンデ発表後、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | そのレース施行回で何日目の開催 |
| 9 | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当レース番号 |
| 10 | 曜日コード | weekday_code | Weekday | 数値1桁 | 数字ゼロ | [曜日コード](../code-tables/basic-codes.md)参照 |
| 11 | 特別競走番号 | special_race_number | FixedDigitInteger | 数値4桁 | 数字ゼロ | 重賞レースのみ設定 原則的には過去の同一レースと一致する番号(多数例外有り) |
| 12 | 競走名本題 | race_name_main | FullWidthString | 全角30文字 | 全角スペース | レース名の本題 |
| 13 | 競走名副題 | race_name_subtitle | FullWidthString | 全角30文字 | 全角スペース | レース名の副題 |
| 14 | 競走名カッコ内 | race_name_parentheses | FullWidthString | 全角30文字 | 全角スペース | レースの条件など |
| 15 | 競走名本題欧字 | race_name_main_english | HalfWidthString | 半角120文字 | 半角スペース | レース名本題の英語表記 |
| 16 | 競走名副題欧字 | race_name_subtitle_english | HalfWidthString | 半角120文字 | 半角スペース | レース名副題の英語表記 |
| 17 | 競走名カッコ内欧字 | race_name_parentheses_english | HalfWidthString | 半角120文字 | 半角スペース | レース名カッコ内の英語表記 |
| 18 | 競走名略称10文字 | race_short_name_10 | FullWidthString | 全角10文字 | 全角スペース | 全角10文字 |
| 19 | 競走名略称6文字 | race_short_name_6 | FullWidthString | 全角6文字 | 全角スペース | 全角6文字 |
| 20 | 競走名略称3文字 | race_short_name_3 | FullWidthString | 全角3文字 | 全角スペース | 全角3文字 |
| 21 | 競走名区分 | race_name_code | RaceNameCategory | 数値1桁 | 数字ゼロ | 重賞回次を本題・副題・カッコ内のうちどれに設定するか |
| 22 | 重賞回次[第N回] | graded_race_round_number | FixedDigitInteger | 数値3桁 | 数字ゼロ | そのレースの重賞としての通算回数 |
| 23 | グレードコード | grade_code | Grade | 文字1桁 | 半角スペース | [グレードコード](../code-tables/basic-codes.md)参照 ※国際グレード表記(G)またはその他の重賞表記(Jpn)の判別方法については、特記事項を参照 |
| 24 | 競走種別コード | race_type_code | RaceType | 数値2桁 | 数字ゼロ | [競走種別コード](../code-tables/race-codes.md)参照 |
| 25 | 競走記号コード | race_symbol_code | RaceSymbol | 数値3桁 | 数字ゼロ | [競走記号コード](../code-tables/race-codes.md)参照 |
| 26 | 重量種別コード | weight_type_code | WeightType | 数値1桁 | 数字ゼロ | [重量種別コード](../code-tables/race-codes.md)参照 |
| 27 | 競走条件コード 2歳条件 | race_cond_code_2yo | RaceCondition | 数値3桁 | 数字ゼロ | 2歳馬の競走条件 |
| 28 | 競走条件コード 3歳条件 | race_cond_code_3yo | RaceCondition | 数値3桁 | 数字ゼロ | 3歳馬の競走条件 |
| 29 | 競走条件コード 4歳条件 | race_cond_code_4yo | RaceCondition | 数値3桁 | 数字ゼロ | 4歳馬の競走条件 |
| 30 | 競走条件コード 5歳以上条件 | race_cond_code_5yo_up | RaceCondition | 数値3桁 | 数字ゼロ | 5歳以上馬の競走条件 |
| 31 | 競走条件コード 最若年条件 | race_cond_code_youngest | RaceCondition | 数値3桁 | 数字ゼロ | 出走可能な最も馬齢が若い馬に対する条件 |
| 32 | 距離 | distance | FixedDigitInteger | 数値4桁 | 数字ゼロ | 単位:メートル |
| 33 | トラックコード | track_code | Track | 数値2桁 | 数字ゼロ | [トラックコード](../code-tables/race-codes.md)参照 |
| 34 | コース区分 | course_code | CourseCategory | 半角2文字 | 半角スペース | 使用するコースを設定（"A "～"E "） 尚、2002年以前の東京競馬場は"A1"、"A2"も存在 |
| 35 | ハンデ発表日 | handicap_announcement_date | DateYYYYMMDD | 8 | 数字ゼロ | ハンデキャップレースにおいてハンデが発表された日 |
| 36 | 登録頭数 | num_entries | FixedDigitInteger | 数値3桁 | 数字ゼロ | 特別登録頭数 |
| 37 | 登録馬毎情報（300項目） | entry_horses | tuple[[TKEntryHorsesItem](#tkentryhorsesitem), ...] | 300×70 | 半角スペース | 登録馬の詳細情報（最大300頭分） |

### TKEntryHorsesItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|--------------|------|-----|------------------|-------|
| 37a | 連番 | serial_number | 連番 1～300 | FixedDigitInteger | 数値3桁 | 数字ゼロ |
| 37b | 血統登録番号 | pedigree_reg_num | 生年（西暦）4桁＋品種1桁([品種コード](../code-tables/horse-codes.md)参照)＋数字5桁 | HalfWidthString | 半角10文字 | 数字ゼロ |
| 37c | 馬名 | horse_name | 全角18文字 | FullWidthString | 全角18文字 | 全角スペース |
| 37d | 馬記号コード | horse_symbol_code | [馬記号コード](../code-tables/horse-codes.md)参照 | HorseSymbol | 数値2桁 | 数字ゼロ |
| 37e | 性別コード | sex_code | [性別コード](../code-tables/horse-codes.md)参照 | HorseSex | 数値1桁 | 数字ゼロ |
| 37f | 調教師東西所属コード | trainer_affiliation_code | [東西所属コード](../code-tables/basic-codes.md)参照 | EastWestAffiliation | 数値1桁 | 数字ゼロ |
| 37g | 調教師コード | trainer_code | 調教師マスタへリンク | TrainerCode | 数値5桁 | 数字ゼロ |
| 37h | 調教師名略称 | trainer_short_name | 全角4文字 | FullWidthString | 全角4文字 | 全角スペース |
| 37i | 負担重量 | impost_weight | 単位:0.1kg（ハンディキャップレースについては月曜以降に設定） | CarryingWeight | 数値3桁 | 数字ゼロ |
| 37j | 交流区分 | exchange_code | 中央交流登録馬の場合に設定（0:初期値、1:地方馬、2:外国馬） | InterleagueRaceCategory | 数値1桁 | 数字ゼロ |

## 特記事項

### グレードコード（項番23）について

2007年から2009年の間、中央競馬の重賞競走の格付け表記は以下のルールで運用されていました：

- 国際格付けを持つ競走：「G」表記
- 国際格付けを持たない競走：「Jpn」表記

ただし、以下の点にご注意ください：

- 2006年以前：国際格付けの有無に関係なく全て「G」表記
- 2010年以降：格付けのない競走を除き全てが国際格付けを得られ「G」表記

JV-Data仕様では2007-2009年の間の「G」表記と「Jpn」表記を判定する基準（国際格付けの有無）を判別できません。このため、競馬ソフト側で別途国際格付けを持つ競走一覧を保有し判定する必要があります。

2007-2010年間の国際格付けを持つ競走（G表記）の特別競走番号一覧は以下のCSVファイルで提供されています：
http://dl.cdn.jra-van.ne.jp/datalab/grade/International.csv
※1行目はファイルの更新日付、2行目以降は年度とその年に国際格付けを持つ競走の特別競走番号

### 競走条件コード（項番27-31）について

#### 平成18年度夏季競馬以降の変更

収得賞金の変更に伴い、競走条件が以下のように変更されました：

**サラ系3歳以上の場合**
| 平成18年度夏季競馬以前 | 平成18年度夏季競馬以降 |
|----------------------|---------------------|
| 3歳500万下 4歳以上1000万下<br>（3歳に"005"、4歳5歳以上に"010"を設定） | 3歳以上500万下<br>（3歳4歳5歳以上ともに"005"を設定） |
| 3歳1000万下 4歳以上2000万下<br>（3歳に"010"、4歳5歳以上に"020"を設定） | 3歳以上1000万下<br>（3歳4歳5歳以上ともに"010"を設定） |
| 3歳1600万下 4歳以上3200万下<br>（3歳に"016"、4歳5歳以上に"032"を設定） | 3歳以上1600万下<br>（3歳4歳5歳以上ともに"016"を設定） |

**サラ系4歳以上の場合**
| 平成18年度夏季競馬以前 | 平成18年度夏季競馬以降 |
|----------------------|---------------------|
| 4歳以上500万下<br>（4歳に"005"、5歳以上に"010"を設定） | 4歳以上500万下<br>（4歳5歳以上ともに"005"を設定） |
| 4歳以上1000万下<br>（4歳に"010"、5歳以上に"020"を設定） | 4歳以上1000万下<br>（4歳5歳以上ともに"010"を設定） |
| 4歳以上1600万下<br>（4歳に"016"、5歳以上に"032"を設定） | 4歳以上1600万下<br>（4歳5歳以上ともに"016"を設定） |

※最若年条件（項番31）には影響がないため変更はありません

#### 平成31年度夏競馬以降の呼称変更

競走条件の呼称が以下のように変更されました（コード値は変更なし）：

| 平成31年度夏季競馬以前 | 平成31年度夏季競馬以降 |
|----------------------|---------------------|
| 500万下（"005"を設定） | 1勝クラス（"005"を設定） |
| 1000万下（"010"を設定） | 2勝クラス（"010"を設定） |
| 1600万下（"016"を設定） | 3勝クラス（"016"を設定） |

## 関連項目

- [DataSpec TOKU](../data-specs/storage/toku.md)
