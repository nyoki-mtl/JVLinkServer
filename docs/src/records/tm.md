# TMレコード（対戦型データマイニング予想）

## データ特性

- **配信タイミング**: レース開催前（前日・当日・直前の3段階）
- **KEY_FIELDS**: `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`, `race_number`

## レースID

- 本レコードは開催年・月日・場・回・日・レース番号を持つレースレコードです。
- `pyjvlink._internal.domain.services.race_id` の `build_race_id()` / `build_race_id_short()` でレースIDを算出できます。

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"TM" |
| 2 | データ区分 | data_code | TMDataCategory | 数値1桁 | 数字ゼロ | TMDataCategory参照 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | そのレース施行回で何日目の開催 |
| 9 | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当レース番号 |
| 10 | データ作成時分 | data_creation_time | TimeHHMM | 数値4桁 | 数字ゼロ | 時分各2桁 |
| 11 | マイニング予想 | mining_predictions | tuple[[TMMiningPredictionsItem](#tmminingpredictionsitem), ...] | - | - | 18頭分（各頭6バイト） |

### TMMiningPredictionsItem

 | 項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数 | 初期値 | 
|------|-------------|-------------|------|-----|------------|-------|
| 11a | 馬番 | horse_number | 該当馬番01～18 | HalfWidthString | 半角2文字 | 半角スペース |
| 11b | 予測スコア | prediction_score | 勝率予測値、000.0～100.0（小数点第1位まで） | DecimalNumber | 数値4桁 | 数字ゼロ |

## 関連項目

- [DataSpec MING](../data-specs/storage/ming.md)
- [DataSpec 0B17](../data-specs/realtime/0b17.md)
