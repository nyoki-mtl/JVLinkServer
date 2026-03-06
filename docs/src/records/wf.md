# WFレコード（重勝式WIN5）

## データ特性

- **配信タイミング**: WIN5開催日に配信（木曜詳細発表〜日曜確定）
- **KEY_FIELDS**: `meet_year`, `meet_date`

## フィールド仕様

| 項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数・繰り返し | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 1 | レコード種別ID | record_type | str | 半角2文字 |  | 固定値"WF" |
| 2 | データ区分 | data_code | WFDataCategory | 数値1桁 | 数字ゼロ | 1:重勝式詳細発表時　2:重勝式対象1レース目確定時 3:重勝式払戻発表時　7:成績(月曜)　9:重勝式中止時 0:該当レコード削除(提供ミスなどの理由による) |
| 3 | データ作成年月日 | data_creation_date | DateYYYYMMDD | 数値8桁 | 数字ゼロ | yyyymmdd形式 |
| 4 | 開催年 | meet_year | DateYYYY | 数値4桁 | 数字ゼロ | 該当レース施行年 |
| 5 | 開催月日 | meet_date | DateMMDD | 数値4桁 | 数字ゼロ | 該当レース施行月日 |
| 6 | 予備 | reserved_1 | ReservedField | 数値2桁 | 数字ゼロ |  |
| 7 | 重勝式対象レース情報 | target_races | tuple[[WFTargetRacesItem](#wftargetracesitem), ...] | - | - | 5レース分の対象レース情報 |
| 8 | 予備 | reserved_2 | ReservedField | 数値6桁 | 数字ゼロ |  |
| 9 | 重勝式発売票数 | total_tickets_sold | FixedDigitInteger | 数値11桁 | 数字ゼロ | 重勝式の発売票数 |
| 10 | 有効票数情報 | valid_ticket_counts | tuple[int, ...] | 数値11桁×5 | 数字ゼロ | 各レース確定後の的中可能性のある残り票数（5レース分） |
| 11 | 返還フラグ | refund_flag | Flag | 数値1桁 | 数字ゼロ | 0:返還無、1:返還有 |
| 12 | 不成立フラグ | void_flag | Flag | 数値1桁 | 数字ゼロ | 0:不成立無、1:不成立有 |
| 13 | 的中無フラグ | no_winner_flag | Flag | 数値1桁 | 数字ゼロ | 0:的中有、1:的中無 |
| 14 | キャリーオーバー金額初期 | carryover_initial | FixedDigitInteger | 数値15桁 | 数字ゼロ | 開催日当日開始時のキャリーオーバー金額（単位:円） |
| 15 | キャリーオーバー金額残高 | carryover_remaining | FixedDigitInteger | 数値15桁 | 数字ゼロ | 次回へのキャリーオーバー金額（単位:円） |
| 16 | 重勝式払戻情報 | payout_info | tuple[[WFPayoutInfoItem](#wfpayoutinfoitem), ...] | - | - | 最大243通りの払戻情報 |

### WFTargetRacesItem（重勝式対象レース情報）

`target_races`フィールドは、5レース分の対象レース情報を格納するタプルです。各要素は以下の構造を持つ`WFTargetRacesItem`オブジェクトです：

| サブ項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数 | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 7a | 競馬場コード | racecourse_code | Racecourse | 半角2文字 | スペース | 該当レース施行競馬場 |
| 7b | 開催回[第N回] | meet_round | FixedDigitInteger | 数値2桁 | 数字ゼロ | その競馬場でその年の何回目の開催かを示す |
| 7c | 開催日目[N日目] | meet_day | FixedDigitInteger | 数値2桁 | 数字ゼロ | そのレース施行回で何日目の開催かを示す |
| 7d | レース番号 | race_number | FixedDigitInteger | 数値2桁 | 数字ゼロ | 該当レース番号 |

### WFPayoutInfoItem（重勝式払戻情報）

`payout_info`フィールドは、最大243通りの払戻情報を格納するタプルです。各要素は以下の構造を持つ`WFPayoutInfoItem`オブジェクトです：

| サブ項番 | フィールド名 | Python変数名 | 型 | 桁数・文字数 | 初期値 | 説明 |
| --- | ------ | --------- | --- | ----------- | --- | --- |
| 16a | 組番 | combination | str | 半角10文字 | スペース | 重勝式的中馬番組合（的中無の場合も設定） |
| 16b | 重勝式払戻金 | payout | FixedDigitInteger | 数値9桁 | 数字ゼロ | 重勝式払戻金（的中無の場合000000000を設定） |
| 16c | 的中票数 | winning_tickets | FixedDigitInteger | 数値10桁 | 数字ゼロ | 重勝式的中票数（的中無の場合0000000000を設定） |

## 関連項目

- [DataSpec RACE](../data-specs/storage/race.md)
- [DataSpec 0B51](../data-specs/realtime/0b51.md)