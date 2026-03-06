# HRレコード（払戻）

## データ特性

- **配信タイミング**: レース確定後（データ区分により段階的に更新）
- **KEY_FIELDS**: `racecourse_code`, `meet_round`, `meet_day`, `race_number`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"HR" |
| 2 | データ区分 | data_code | HRDataCategory | 数値1桁 | 数字ゼロ | 1:速報成績(払戻金確定)、2:成績(月曜)、9:レース中止、0:該当レコード削除 |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | レース施行年 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | レース施行月日 |
| 6 | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | 数字ゼロ | [競馬場コード](../code-tables/racecourse-codes.md)参照 |
| 7 | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催 |
| 8 | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | その開催回で何日目 |
| 9 | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | レース番号（通常1〜12） |
| 10 | 登録頭数 | num_entries | FixedDigitInteger | 数値2桁 | 数字ゼロ | 出走登録頭数 |
| 11 | 出走頭数 | num_starters | FixedDigitInteger | 数値2桁 | 数字ゼロ | 実際に出走した頭数 |
| 12 | 単勝不成立フラグ | win_cancelled_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:不成立 |
| 13 | 複勝不成立フラグ | place_cancelled_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:不成立 |
| 14 | 枠連不成立フラグ | bracket_quinella_cancelled_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:不成立 |
| 15 | 馬連不成立フラグ | quinella_cancelled_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:不成立 |
| 16 | ワイド不成立フラグ | wide_cancelled_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:不成立 |
| 17 | 予備 | reserved_1 | Flag | 数値1桁 | 数字ゼロ |  |
| 18 | 馬単不成立フラグ | exacta_cancelled_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:不成立 |
| 19 | 3連複不成立フラグ | trifecta_cancelled_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:不成立 |
| 20 | 3連単不成立フラグ | trio_cancelled_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:不成立 |
| 21 | 単勝特払フラグ | win_special_payout_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:特払発生 |
| 22 | 複勝特払フラグ | place_special_payout_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:特払発生 |
| 23 | 枠連特払フラグ | bracket_quinella_special_payout_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:特払発生 |
| 24 | 馬連特払フラグ | quinella_special_payout_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:特払発生 |
| 25 | ワイド特払フラグ | wide_special_payout_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:特払発生 |
| 26 | 予備 | reserved_3 | Flag | 数値1桁 | 数字ゼロ |  |
| 27 | 馬単特払フラグ | exacta_special_payout_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:特払発生 |
| 28 | 3連複特払フラグ | trifecta_special_payout_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:特払発生 |
| 29 | 3連単特払フラグ | trio_special_payout_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:特払発生 |
| 30 | 単勝返還フラグ | win_refund_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:返還あり |
| 31 | 複勝返還フラグ | place_refund_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:返還あり |
| 32 | 枠連返還フラグ | bracket_quinella_refund_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:返還あり |
| 33 | 馬連返還フラグ | quinella_refund_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:返還あり |
| 34 | ワイド返還フラグ | wide_refund_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:返還あり |
| 35 | 予備 | reserved_4 | Flag | 数値1桁 | 数字ゼロ |  |
| 36 | 馬単返還フラグ | exacta_refund_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:返還あり |
| 37 | 3連複返還フラグ | trifecta_refund_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:返還あり |
| 38 | 3連単返還フラグ | trio_refund_flag | Flag | 数値1桁 | 数字ゼロ | 0:通常、1:返還あり |
| 39 | 返還馬番情報 | refund_horse_number_info_28 | RefundFlags | 半角28文字 | 数字ゼロ | 馬番1〜28の返還状況（1:返還あり） |
| 40 | 返還枠番情報 | refund_bracket_info | RefundFlags | 半角8文字 | 数字ゼロ | 枠番1〜8の返還状況（1:返還あり） |
| 41 | 返還同枠情報 | refund_same_bracket_info | RefundFlags | 半角8文字 | 数字ゼロ | 同枠1〜8の返還状況（1:返還あり） |
| 42 | 単勝払戻 | win_payback | tuple[[HRWinPaybackItem](#hrwinpaybackitem), ...] | 3回×13 |  | 3同着まで考慮し繰返し3回 |
| 43 | 複勝払戻 | place_payback | tuple[[HRPlacePaybackItem](#hrplacepaybackitem), ...] | 5回×13 |  | 5同着まで考慮し繰返し5回 |
| 44 | 枠連払戻 | bracket_quinella_payback | tuple[[HRBracketQuinellaPaybackItem](#hrbracketquinellapaybackitem), ...] | 3回×13 |  | 3同着まで考慮し繰返し3回 |
| 45 | 馬連払戻 | quinella_payback | tuple[[HRQuinellaPaybackItem](#hrquinellapaybackitem), ...] | 3回×16 |  | 3同着まで考慮し繰返し3回 |
| 46 | ワイド払戻 | wide_payback | tuple[[HRWidePaybackItem](#hrwidepaybackitem), ...] | 7回×16 |  | 7同着まで考慮し繰返し7回 |
| 47 | 予備 | reserved_payback | reserved (typed非公開) | 3回×16 |  | 予備領域 |
| 48 | 馬単払戻 | exacta_payback | tuple[[HRExactaPaybackItem](#hrexactapaybackitem), ...] | 6回×16 |  | 6同着まで考慮し繰返し6回 |
| 49 | 3連複払戻 | trio_payback | tuple[[HRTrioPaybackItem](#hrtriopaybackitem), ...] | 3回×18 |  | 3同着まで考慮し繰返し3回 |
| 50 | 3連単払戻 | trifecta_payback | tuple[[HRTrifectaPaybackItem](#hrtrifectapaybackitem), ...] | 6回×19 |  | 6同着まで考慮し繰返し6回 |

### HRWinPaybackItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|-------------|------|------------------|-------|
| 42a | 馬番 | number | 単勝的中馬番（00:発売なし、特払、不成立） | PayoutHorseNumber | 半角2文字 | 数字ゼロ |
| 42b | 払戻金 | payout | 単勝払戻金（特払、不成立の金額が入る）単位:円 | FixedDigitInteger | 数値9桁 | 数字ゼロ |
| 42c | 人気順 | popularity_rank | 単勝人気順 | FixedDigitInteger | 数値2桁 | 数字ゼロ |

### HRPlacePaybackItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|-------------|------|------------------|-------|
| 43a | 馬番 | number | 複勝的中馬番（00:発売なし、特払、不成立） | PayoutHorseNumber | 半角2文字 | 数字ゼロ |
| 43b | 払戻金 | payout | 複勝払戻金（特払、不成立の金額が入る）単位:円 | FixedDigitInteger | 数値9桁 | 数字ゼロ |
| 43c | 人気順 | popularity_rank | 複勝人気順 | FixedDigitInteger | 数値2桁 | 数字ゼロ |

### HRBracketQuinellaPaybackItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|-------------|------|------------------|-------|
| 44a | 組番 | number | 枠連的中組番（00:発売なし、特払、不成立） | PayoutCombinationNumber2 | 半角2文字 | 数字ゼロ |
| 44b | 払戻金 | payout | 枠連払戻金（特払、不成立の金額が入る）単位:円 | FixedDigitInteger | 数値9桁 | 数字ゼロ |
| 44c | 人気順 | popularity_rank | 枠連人気順 | FixedDigitInteger | 数値2桁 | 数字ゼロ |

### HRQuinellaPaybackItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|-------------|------|------------------|-------|
| 45a | 組番 | number | 馬連的中馬番組合（0000:発売なし、特払、不成立） | PayoutCombinationNumber4 | 半角4文字 | 数字ゼロ |
| 45b | 払戻金 | payout | 馬連払戻金（特払、不成立の金額が入る）単位:円 | FixedDigitInteger | 数値9桁 | 数字ゼロ |
| 45c | 人気順 | popularity_rank | 馬連人気順 | FixedDigitInteger | 数値3桁 | 数字ゼロ |

### HRWidePaybackItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|-------------|------|------------------|-------|
| 46a | 組番 | number | ワイド的中馬番組合（0000:発売なし、特払、不成立） | PayoutCombinationNumber4 | 半角4文字 | 数字ゼロ |
| 46b | 払戻金 | payout | ワイド払戻金（特払、不成立の金額が入る）単位:円 | FixedDigitInteger | 数値9桁 | 数字ゼロ |
| 46c | 人気順 | popularity_rank | ワイド人気順 | FixedDigitInteger | 数値3桁 | 数字ゼロ |

### reserved_payback（typed非公開）

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|-------------|------|------------------|-------|
| 47a | 組番 | number | 予備組番（0000:発売なし、特払、不成立） | PayoutCombinationNumber4 | 半角4文字 | 数字ゼロ |
| 47b | 払戻金 | payout | 予備払戻金（特払、不成立の金額が入る）単位:円 | FixedDigitInteger | 数値9桁 | 数字ゼロ |
| 47c | 人気順 | popularity_rank | 予備人気順 | FixedDigitInteger | 数値3桁 | 数字ゼロ |

### HRExactaPaybackItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|-------------|------|------------------|-------|
| 48a | 組番 | number | 馬単的中馬番組合（0000:発売なし、特払、不成立） | PayoutCombinationNumber4 | 半角4文字 | 数字ゼロ |
| 48b | 払戻金 | payout | 馬単払戻金（特払、不成立の金額が入る）単位:円 | FixedDigitInteger | 数値9桁 | 数字ゼロ |
| 48c | 人気順 | popularity_rank | 馬単人気順 | FixedDigitInteger | 数値3桁 | 数字ゼロ |

### HRTrioPaybackItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|-------------|------|------------------|-------|
| 49a | 組番 | number | 3連複的中馬番組合（000000:発売なし、特払、不成立） | PayoutCombinationNumber6 | 半角6文字 | 数字ゼロ |
| 49b | 払戻金 | payout | 3連複払戻金（特払、不成立の金額が入る）単位:円 | FixedDigitInteger | 数値9桁 | 数字ゼロ |
| 49c | 人気順 | popularity_rank | 3連複人気順 | FixedDigitInteger | 数値3桁 | 数字ゼロ |

### HRTrifectaPaybackItem

| サブ項番 | フィールド名 | Python変数名 | 説明 | 型 | 桁数・文字数・繰り返し | 初期値 |
|----------|-------------|-------------|-------------|------|------------------|-------|
| 50a | 組番 | number | 3連単的中馬番組合（000000:発売なし、特払、不成立） | PayoutCombinationNumber6 | 半角6文字 | 数字ゼロ |
| 50b | 払戻金 | payout | 3連単払戻金（特払、不成立の金額が入る）単位:円 | FixedDigitInteger | 数値9桁 | 数字ゼロ |
| 50c | 人気順 | popularity_rank | 3連単人気順 | FixedDigitInteger | 数値4桁 | 数字ゼロ |

## 特記事項

### 特払フラグ・返還フラグ（項番21-25, 30-34）について

これらのフィールドは2002年6月15日以降設定されます。それ以前のデータでは初期値が設定されています。

### 複勝払戻馬番（項番43a）について

複勝2着払いの際、3回目の馬番には"00"が設定されます。

## 関連項目

- [DataSpec RACE](../data-specs/storage/race.md)
- [DataSpec 0B12](../data-specs/realtime/0b12.md)
- [DataSpec 0B15](../data-specs/realtime/0b15.md)
