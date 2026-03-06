# UMレコード（競走馬マスタ）

## データ特性

- **配信タイミング**: 月曜14:00頃、木曜20:00頃（変更・追加分）
- **KEY_FIELDS**: `pedigree_reg_num`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"UM" |
| 2 | データ区分 | data_code | UMDataCategory | 数値1桁 | 数字ゼロ | 1:新規馬名登録、2:馬名変更、3:再登録(抹消後の再登録)、4:その他更新、9:抹消、0:該当レコード削除(提供ミスなどの理由による) |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 血統登録番号 | pedigree_reg_num | HalfWidthString | 半角10文字 | 数字ゼロ | 生年(4桁)+品種(1桁)+連番(5桁) |
| 5 | 競走馬抹消区分 | deregistration_flag | Flag | 数値1桁 | 数字ゼロ | 0:現役、1:抹消 |
| 6 | 競走馬登録年月日 | registration_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 7 | 競走馬抹消年月日 | deregistration_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 8 | 生年月日 | birth_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 9 | 馬名 | horse_name | FullWidthString | 全角18文字 | 全角スペース | 馬名 |
| 10 | 馬名半角カナ | horse_name_kana | HalfWidthString | 半角36文字 | 半角スペース | 馬名の半角カナ表記 |
| 11 | 馬名欧字 | horse_name_english | MixedWidthStringByByte | 60バイト（半角基準、曖昧幅含む） | 半角スペース | 馬名の英語表記 |
| * | *補足* |  |  |  |  | ※ 公式仕様上は「半角60文字固定」だが、実データには `―` (U+2015) のような曖昧幅の英馬名が少数含まれる。PyJVLink では Shift_JIS 換算で60バイト以内に収まる混在幅文字列として受け入れる。 |
| 12 | JRA施設在きゅうフラグ | jra_facility_flag | JRAFacilityFlag | 数値1桁 | 半角スペース | 0:JRA施設に在きゅうしていない。1:JRA施設の在きゅうしている。 JRA施設とは競馬場およびトレセンなどを指す。　(平成18年6月6日以降設定) |
| 13 | 予備 | reserved_19 | HalfWidthString | 半角19文字 | 半角スペース | 予備 |
| 14 | 馬記号コード | horse_symbol_code | HorseSymbol | 数値2桁 | 数字ゼロ | 外、地、持、抽、父、市、権、母 |
| 15 | 性別コード | sex_code | HorseSex | 数値1桁 | 数字ゼロ | 牡、牝、セ |
| 16 | 品種コード | breed_code | Breed | 数値1桁 | 数字ゼロ | サラ系、アラ系等 |
| 17 | 毛色コード | coat_color_code | CoatColor | 数値2桁 | 数字ゼロ | 栗毛、鹿毛、黒鹿毛等 |
| 18 | 3代血統情報 | pedigree_3gen | tuple[[UMPedigree3GenItem](#umpedigree3genitem), ...] | 複合型（14要素のリスト） | - | 3代14頭の血統（繁殖登録番号+馬名） |
| 19 | 東西所属コード | affiliation_code | EastWestAffiliation | 数値1桁 | 数字ゼロ | 1:関東、2:関西等 |
| 20 | 調教師コード | trainer_code | TrainerCode | 数値5桁 | 数字ゼロ | 調教師識別番号 |
| 21 | 調教師名略称 | trainer_name_short | FullWidthString | 全角4文字 | 全角スペース | 調教師名の略称 |
| 22 | 招待地域名 | invitation_area_name | FullWidthString | 全角10文字 | 全角スペース | 招待地域 |
| 23 | 生産者コード | breeder_code | BreederCode | 数値8桁 | 数字ゼロ | 生産者識別番号 |
| 24 | 生産者名(法人格無) | breeder_name | MixedWidthStringByByte | 全角36文字～半角72文字 | 全角または半角スペース | 法人格を除いた生産者名 |
| 25 | 産地名 | birthplace_name | MixedWidthStringByByte | 全角10文字～半角20文字 | 全角または半角スペース | 生産地 |
| 26 | 馬主コード | owner_code | OwnerCode | 数値6桁 | 数字ゼロ | 馬主識別番号 |
| 27 | 馬主名(法人格無) | owner_name | MixedWidthStringByByte | 全角32文字～半角64文字 | 全角または半角スペース | 法人格を除いた馬主名 |
| 28 | 平地本賞金累計 | flat_prize_money_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 29 | 障害本賞金累計 | steeplechase_prize_money_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 30 | 平地付加賞金累計 | flat_added_money_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 31 | 障害付加賞金累計 | steeplechase_added_money_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 32 | 平地収得賞金累計 | flat_earnings_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 33 | 障害収得賞金累計 | steeplechase_earnings_total | MoneyIn100Yen | 数値9桁 | 数字ゼロ | 単位:百円 |
| 34 | 総合着回数 | overall_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数。6つのフィールド(first, second, third, fourth, fifth, other)を持つ |
| 35 | 中央合計着回数 | central_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数（JRA競走のみ） |
| 36 | 芝直・着回数 | turf_straight_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 37 | 芝右・着回数 | turf_right_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 38 | 芝左・着回数 | turf_left_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 39 | ダ直・着回数 | dirt_straight_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 40 | ダ右・着回数 | dirt_right_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 41 | ダ左・着回数 | dirt_left_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 42 | 障害・着回数 | steeplechase_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 43 | 芝良・着回数 | turf_good_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 44 | 芝稍・着回数 | turf_slightly_heavy_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 45 | 芝重・着回数 | turf_heavy_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 46 | 芝不・着回数 | turf_bad_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 47 | ダ良・着回数 | dirt_good_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 48 | ダ稍・着回数 | dirt_slightly_heavy_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 49 | ダ重・着回数 | dirt_heavy_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 50 | ダ不・着回数 | dirt_bad_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 51 | 障良・着回数 | steeplechase_good_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 52 | 障稍・着回数 | steeplechase_slightly_heavy_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 53 | 障重・着回数 | steeplechase_heavy_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 54 | 障不・着回数 | steeplechase_bad_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 1～5着及び着外の回数 |
| 55 | 芝16下・着回数 | turf_class_d_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 芝1600m以下 1～5着及び着外の回数 |
| 56 | 芝22下・着回数 | turf_class_e_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 芝1601-2200m 1～5着及び着外の回数 |
| 57 | 芝22超・着回数 | turf_gt2200_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | 芝2201m以上 1～5着及び着外の回数 |
| 58 | ダ16下・着回数 | dirt_class_d_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | ダート1600m以下 1～5着及び着外の回数 |
| 59 | ダ22下・着回数 | dirt_class_e_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | ダート1601-2200m 1～5着及び着外の回数 |
| 60 | ダ22超・着回数 | dirt_gt2200_placing_counts | [RaceResultStat](#raceresultstat) | 複合型 | - | ダート2201m以上 1～5着及び着外の回数 |
| 61 | 脚質傾向 | running_style_counts | [RunningStyleStat](#runningstylestat) | 複合型 | - | 逃げ・先行・差し・追込回数。4つのフィールド(front_runner, stalker, closer, deep_closer)を持つ |
| 62 | 登録レース数 | registered_race_count | FixedDigitInteger | 数値3桁 | 数字ゼロ | レース登録数 |

### UMPedigree3GenItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|----------|-------------|------|------------------|-------|
| 18a | 繁殖登録番号 | breeding_reg_num | 繁殖馬マスタへリンク | BreedingRegistrationNumber | 数値10桁 | 数字ゼロ |
| 18b | 馬名 | horse_name | 外国の繁殖馬の場合は、繁殖馬マスタの馬名欧字の頭36バイトを設定 | MixedWidthStringByByte | 全角18文字～半角36文字 | 全角または半角スペース |

### 血統順序（14世代の格納順序）

血統情報は`pedigree_3gen`リストに格納されます。各要素へはインデックスでアクセスできます：

| 順序 | 世代 | インデックス | 備考 |
|------|------|-----------------|-------------|
| 1 | 父 | `pedigree_3gen[0]` | - |
| 2 | 母 | `pedigree_3gen[1]` | - |
| 3 | 父父 | `pedigree_3gen[2]` | - |
| 4 | 父母 | `pedigree_3gen[3]` | - |
| 5 | 母父 | `pedigree_3gen[4]` | - |
| 6 | 母母 | `pedigree_3gen[5]` | - |
| 7 | 父父父 | `pedigree_3gen[6]` | - |
| 8 | 父父母 | `pedigree_3gen[7]` | - |
| 9 | 父母父 | `pedigree_3gen[8]` | - |
| 10 | 父母母 | `pedigree_3gen[9]` | - |
| 11 | 母父父 | `pedigree_3gen[10]` | - |
| 12 | 母父母 | `pedigree_3gen[11]` | - |
| 13 | 母母父 | `pedigree_3gen[12]` | - |
| 14 | 母母母 | `pedigree_3gen[13]` | - |

### 使用例

```python
# リストのインデックスでアクセス
father = record.pedigree_3gen[0]
mother = record.pedigree_3gen[1]

```

### RaceResultStat

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|----------|-------------|------|------------------|-------|
| - | 1着回数 | first | 1着の回数 | FixedDigitInteger | 数値3桁 | 数字ゼロ |
| - | 2着回数 | second | 2着の回数 | FixedDigitInteger | 数値3桁 | 数字ゼロ |
| - | 3着回数 | third | 3着の回数 | FixedDigitInteger | 数値3桁 | 数字ゼロ |
| - | 4着回数 | fourth | 4着の回数 | FixedDigitInteger | 数値3桁 | 数字ゼロ |
| - | 5着回数 | fifth | 5着の回数 | FixedDigitInteger | 数値3桁 | 数字ゼロ |
| - | 着外回数 | other | 6着以下の回数 | FixedDigitInteger | 数値3桁 | 数字ゼロ |

### RunningStyleStat

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|----------|-------------|------|------------------|-------|
| - | 逃げ回数 | front_runner | 逃げの回数 | FixedDigitInteger | 数値3桁 | 数字ゼロ |
| - | 先行回数 | stalker | 先行の回数 | FixedDigitInteger | 数値3桁 | 数字ゼロ |
| - | 差し回数 | closer | 差しの回数 | FixedDigitInteger | 数値3桁 | 数字ゼロ |
| - | 追込回数 | deep_closer | 追込の回数 | FixedDigitInteger | 数値3桁 | 数字ゼロ |

## 特記事項

### JRA施設在きゅうフラグ（項番12）について

平成18年6月6日以降設定。それ以前のものには初期値スペースを設定

### 各種賞金累計（項番28-33）について

- **平地本賞金累計（項番28）**: JRAの平地競走において獲得した本賞金の累計
- **障害本賞金累計（項番29）**: JRAの障害競走において獲得した本賞金の累計
- **平地付加賞金累計（項番30）**: JRAの平地競走において獲得した付加賞金の累計
- **障害付加賞金累計（項番31）**: JRAの障害競走において獲得した付加賞金の累計

一般的には平地・障害の本賞金と付加賞金の合計額（項番28～31の合計）を獲得賞金という

#### 収得賞金について

- **平地収得賞金累計（項番32）**: 
  - 収得賞金とは、本賞金をJRAの定める規定に従って加算したものでクラス分けの基準となる賞金額
  - 平地競走において獲得した収得賞金額の合計（ただし、1999年以前は障害競走で獲得した収得賞金も平地収得賞金に含む）
  - 4歳夏季競馬以降については、4歳春季競馬まで獲得した収得賞金の2分の1とした額に、4歳夏季競馬以降に獲得した収得賞金を加算した額とする（毎年春季競馬終了後、夏季競馬開始までの間に全4歳馬について収得賞金を2分の1にしたものを提供する）
  - ただし平成18年度夏季競馬開始時点については4歳以上の全ての馬について、その時点の収得賞金の2分の1を設定する
  - 平成31年度夏季競馬以降は降級処理廃止のため、平成18年度夏季競馬より行われていた、平地収得賞金累計の再計算は行わない

- **障害収得賞金累計（項番33）**: 
  - 収得賞金とは、本賞金をJRAの定める規定に従って加算したものでクラス分けの基準となる賞金額
  - 障害競走において獲得した収得賞金額の合計

### 各着回数（項番34-62）について

1986年以降についてのみカウント

#### 障害レース馬場状態別着回数（項番51-54）について

トラックが「芝→ダート」となるものはダートの馬場状態でカウントする

### 脚質傾向（項番61）について

過去レースでの位置取りを[逃･先･差･追]の4段階のどれに当てはまるかを以下の方法で判定し、それをカウントしたもの：

- **逃げ**: 最終コーナー以外のいずれかのコーナーを1位で通過した場合、その馬のそのレースでの脚質を逃げとします
- **先行**: 逃げに該当しない馬で、最終コーナーを4位以内で通過した場合、その馬のそのレースでの脚質を先行とします
- **差し**: 逃げ･先行に該当しない馬で、最終コーナーの通過順位がそのレースの出走頭数の3分の2以内だった場合、その馬のそのレースでの脚質を差しとします。尚、出走頭数が8頭未満のレースでは、差しは該当なしとします
- **追込**: 逃げ･先行･差しに該当しない馬のそのレースでの脚質を追込とします

直線コースの場合は走破タイムから後3ハロンタイムを引いて算出した値により以下の通り脚質を判定します：

- **逃げ**: 算出した値が最小の場合、その馬のそのレースでの脚質を逃げとします
- **先行**: 逃げに該当しない馬で、算出した値の順位が出走頭数中下位3頭の場合、その馬のそのレースでの脚質を先行とします
- **差し**: 逃げ･先行に該当しない馬で、算出した値の順位がそのレースの出走頭数の3分の2以内だった場合、その馬のそのレースでの脚質を差しとします。尚、出走頭数が8頭未満のレースでは、差しは該当なしとします
- **追込**: 逃げ･先行･差しに該当しない馬のそのレースでの脚質を追込とします

※レース中止、出走取消し等はカウント対象外とします

## 関連項目

- [DataSpec DIFF](../data-specs/storage/diff.md)
- [DataSpec DIFN](../data-specs/storage/diff.md)
- [DataSpec TCOV](../data-specs/storage/toku.md)
- [DataSpec TCVN](../data-specs/storage/toku.md)
- [DataSpec RCOV](../data-specs/storage/diff.md)
- [DataSpec RCVN](../data-specs/storage/diff.md)
