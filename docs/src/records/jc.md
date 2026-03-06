# JCレコード（騎手変更）

## データ特性

- **配信タイミング**: 騎手変更の発生時
- **KEY_FIELDS**: `meet_year`, `meet_date`, `racecourse_code`, `meet_round`, `meet_day`, `race_number`, `announcement_datetime`, `horse_number`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"JC" |
| 2 | データ区分 | data_code | JCDataCategory | 数値1桁 | 数字ゼロ | 1:初期値 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | そのレース施行回で何日目の開催 |
| 9 | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当レース番号 |
| 10 | 発表月日時分 | announcement_datetime | DateTimeMMDDHHmm | 数値8桁 | 数字ゼロ | 月日時分各2桁 |
| 11 | 馬番 | horse_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当馬番01～18 |
| 12 | 馬名 | horse_name | FullWidthString | 全角18文字 | 全角スペース | 全角18文字（当面は9文字のみ設定） |
| 13 | 負担重量（変更後） | carrying_weight_after | CarryingWeight | 数値3桁 | 数字ゼロ | 単位:0.1kg |
| 14 | 騎手コード（変更後） | jockey_code_after_ks | FixedDigitInteger | 数値5桁 | 数字ゼロ | 騎手マスタへリンク（未定の場合は00000） |
| 15 | 騎手名（変更後） | jockey_name_after | FullWidthString | 全角17文字 | 全角スペース | 全角17文字（当面は8文字のみ設定。未定の場合は、「未定」と設定） |
| 16 | 騎手見習コード（変更後） | jockey_apprentice_code_after | ApprenticeJockey | 数値1桁 | 数字ゼロ | [騎手見習コード](../code-tables/jockey-codes.md)参照 |
| 17 | 負担重量（変更前） | carrying_weight_before | CarryingWeight | 数値3桁 | 数字ゼロ | 単位:0.1kg |
| 18 | 騎手コード（変更前） | jockey_code_before_ks | FixedDigitInteger | 数値5桁 | 数字ゼロ | 騎手マスタへリンク |
| 19 | 騎手名（変更前） | jockey_name_before | FullWidthString | 全角17文字 | 全角スペース | 全角17文字（当面は8文字のみ設定） |
| 20 | 騎手見習コード（変更前） | jockey_apprentice_code_before | ApprenticeJockey | 数値1桁 | 数字ゼロ | [騎手見習コード](../code-tables/jockey-codes.md)参照 |

## 命名ポリシーと to_dict() 出力

- 命名ポリシー:
  - `*_id`: 桁数を満たすゼロパディング済みの文字列（例: 騎手IDは5桁）
  - `*_code`: 生のコード値（数値としての値）
- このページは wire 仕様の説明です。現行の `Client` は dataclass ベースのレコードを返すため、
  旧 `to_dict()` 出力仕様には依存しません。

## 関連項目

- [DataSpec 0B14](../data-specs/realtime/0b14.md)
- [DataSpec 0B16](../data-specs/realtime/0b16.md)
