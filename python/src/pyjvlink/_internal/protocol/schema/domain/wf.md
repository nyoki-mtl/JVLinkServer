# WF - 重勝式(WIN5)

レコード長: 7215 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `meet_year` | int | 12 | 4 | 開催年 | KEY |
| 5 | `meet_date` | date_mmdd | 16 | 4 | 開催月日 | KEY |
| 6 | `racecourse_code` | str | 20 | 2 | 競馬場コード | KEY |
| 7 | `meet_round` | int | 22 | 2 | 開催回 | KEY |
| 8 | `meet_day` | int | 24 | 2 | 開催日目 | KEY |
| 9 | `race_number` | int | 26 | 2 | レース番号 | KEY |
| 7 | `target_races` | array:object[5] | 22 | 40 | 重勝式対象レース情報 |  |
|  | `  .racecourse_code` | str | +0 | 2 | 競馬場コード |  |
|  | `  .meet_round` | int | +2 | 2 | 開催回 |  |
|  | `  .meet_day` | int | +4 | 2 | 開催日目 |  |
|  | `  .race_number` | int | +6 | 2 | レース番号 |  |
| 9 | `total_tickets_sold` | int | 68 | 11 | 重勝式発売票数 |  |
| 10 | `valid_ticket_counts` | array:int[5] | 79 | 55 | 有効票数情報 |  |
| 11 | `refund_flag` | flag | 134 | 1 | 返還フラグ |  |
| 12 | `void_flag` | flag | 135 | 1 | 不成立フラグ |  |
| 13 | `no_winner_flag` | flag | 136 | 1 | 的中無フラグ |  |
| 14 | `carryover_initial` | int | 137 | 15 | キャリーオーバー金額初期 |  |
| 15 | `carryover_remaining` | int | 152 | 15 | キャリーオーバー金額残高 |  |
| 16 | `payout_info` | array:object[243] | 167 | 7047 | 重勝式払戻情報 |  |
|  | `  .combination` | str | +0 | 10 | 組番 |  |
|  | `  .payout` | int | +10 | 9 | 重勝式払戻金 |  |
|  | `  .winning_tickets` | int | +19 | 10 | 的中票数 |  |
