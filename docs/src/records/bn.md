# BNレコード（馬主マスタ）

## データ特性

- **配信タイミング**: 新規馬主登録時、所有馬成績更新時（週次）、馬主情報変更時
- **KEY_FIELDS**: `owner_code`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"BN" |
| 2 | データ区分 | data_code | BNDataCategory | 数値1桁 | 数字ゼロ | 1:新規登録、2:更新、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 馬主コード | owner_code | OwnerCode | 数値6桁 | 数字ゼロ | 馬主を一意に識別 |
| 5 | 馬主名(法人格有) | owner_name_with_corp | MixedWidthStringByByte | 全角32文字 ~ 半角64文字 | 全角または半角スペース | 法人格を含む正式名称 |
| 6 | 馬主名(法人格無) | owner_name | MixedWidthStringByByte | 全角32文字 ~ 半角64文字 | 全角または半角スペース | 法人格を除いた名称 |
| 7 | 馬主名半角カナ | owner_name_kana | HalfWidthString | 半角50文字 | 半角スペース | カナ表記 |
| 8 | 馬主名欧字 | owner_name_english | MixedWidthStringByByte | 全角50文字 ~ 半角100文字 | 全角または半角スペース | 英語表記 |
| 9 | 服色標示 | silk_colors_code | FullWidthString | 60バイト（全角30文字） | 全角スペース | 勝負服の色・模様（例："水色，赤山形一本輪，水色袖"） |
| 10 | 本年・累計成績情報 | performance_stats | tuple[[BNPerformanceStatsItem](#bnperformancestatsitem), ...] |  |  | 2回繰り返し（本年・累計） |

### BNPerformanceStatsItem（項番10: 本年・累計成績情報）

| 項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数 | 初期値 |
|------|-------------|-------------|------|-----|------------|-------|
| 10a | 設定年 | year | 成績年（累計は"0000"） | DateYYYY | 数値4桁 | 数字ゼロ |
| 10b | 本賞金合計 | prize_money | 単位:百円 | MoneyIn100Yen | 数値10桁 | 数字ゼロ |
| 10c | 付加賞金合計 | added_money | 単位:百円 | MoneyIn100Yen | 数値10桁 | 数字ゼロ |
| 10d | 着回数 | placing_counts | 1着～5着,着外の回数（6要素） | list[FixedDigitInteger] | 数値6桁×6 | 数字ゼロ |

## 注意事項

- 項番5: 外国馬主の場合は、8.馬主名欧字の頭64バイトを設定。
- 項番6: 株式会社、有限会社などの法人格を示す文字列が頭もしくは末尾にある場合にそれを削除したものを設定。また、外国馬主の場合は、8.馬主名欧字の頭64バイトを設定。
- 項番7: 外国馬主については設定しない。
- 項番8: アルファベット等以外の特殊文字については、全角で設定。

## 関連項目

- [DataSpec DIFF](../data-specs/storage/diff.md)
- [DataSpec DIFN](../data-specs/storage/diff.md)
- [DataSpec TCOV](../data-specs/storage/diff.md)
- [DataSpec TCVN](../data-specs/storage/diff.md)
- [DataSpec RCOV](../data-specs/storage/diff.md)
- [DataSpec RCVN](../data-specs/storage/diff.md)
