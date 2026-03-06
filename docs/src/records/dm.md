# DMレコード（タイム型データマイニング予想）

## データ特性

- **配信タイミング**: レース開催前（前日・当日・直前の3段階）
- **KEY_FIELDS**: `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`, `race_number`

## レースID

- 本レコードは開催年・月日・場・回・日・レース番号を持つレースレコードです。
- `pyjvlink._internal.domain.services.race_id` の `build_race_id()` / `build_race_id_short()` でレースIDを算出できます。

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"DM" |
| 2 | データ区分 | data_code | DMDataCategory | 数値1桁 | 数字ゼロ | DMDataCategory参照 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | そのレース施行回で何日目の開催 |
| 9 | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当レース番号 |
| 10 | データ作成時分 | data_creation_time | TimeHHMM | 数値4桁 | 数字ゼロ | 時分各2桁 |
| 11 | マイニング予想 | mining_data | list[MiningTimeData] | 18要素 | 空リスト | 18頭分のタイム予想データのリスト |

### マイニング予想データ（項番11）

`mining_data`フィールドは18要素のリストで、各要素は`MiningTimeData`クラスのインスタンスです。各`MiningTimeData`オブジェクトは以下のフィールドを持ちます：

| サブ項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数 | 初期値 | 説明 |
|----------|-------------|-------------|-----|------------|--------|------|
| 11a | 馬番 | horse_number | HalfWidthString | 半角2文字 | 半角スペース | 該当馬番01～18 |
| 11b | 予想走破タイム | pred_finish_time | DurationMSS_SS | 数値5桁 | 半角スペース | 9分99秒99で設定 |
| 11c | 予想誤差(信頼度)＋ | pred_err_margin_plus | DurationSS_SS | 数値4桁 | 半角スペース | 99秒99で設定 予想タイムの＋誤差 |
| 11d | 予想誤差(信頼度)－ | pred_err_margin_minus | DurationSS_SS | 数値4桁 | 半角スペース | 99秒99で設定 予想タイムの－誤差を設定(－方向の誤差。予想走破タイムに対して遅くなる方向。予想走破タイムにプラスする) |

## MiningTimeDataクラス

`MiningTimeData`は1頭分のマイニング予想タイムデータを表すクラスです：

```python
@dataclass
class MiningTimeData:
    horse_number: HalfWidthString          # 馬番（01～18）
    pred_finish_time: DurationMSS_SS          # 予想走破タイム（9分99秒99形式）
    pred_err_margin_plus: DurationSS_SS       # 予想誤差(信頼度)＋（99秒99形式）
    pred_err_margin_minus: DurationSS_SS      # 予想誤差(信頼度)－（99秒99形式）
```

各フィールドの詳細：

- **horse_number**: 該当する馬番（01～18）を2桁の半角文字列で格納
- **pred_finish_time**: マイニング予想による走破タイムを9分99秒99形式で格納
- **pred_err_margin_plus**: 予想タイムの＋誤差（予想タイムより早くなる可能性）
- **pred_err_margin_minus**: 予想タイムの－誤差（予想タイムより遅くなる可能性、予想走破タイムにプラスする値）

## 関連項目

- [DataSpec MING](../data-specs/storage/ming.md)
- [DataSpec 0B13](../data-specs/realtime/0b13.md)
