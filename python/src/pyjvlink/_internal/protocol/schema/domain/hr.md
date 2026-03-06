# HR - 払戻

レコード長: 719 バイト

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
| 10 | `num_entries` | int | 28 | 2 | 登録頭数 |  |
| 11 | `num_starters` | int | 30 | 2 | 出走頭数 |  |
| 12 | `win_cancelled_flag` | flag | 32 | 1 | 不成立フラグ 単勝 |  |
| 13 | `place_cancelled_flag` | flag | 33 | 1 | 不成立フラグ 複勝 |  |
| 14 | `bracket_quinella_cancelled_flag` | flag | 34 | 1 | 不成立フラグ 枠連 |  |
| 15 | `quinella_cancelled_flag` | flag | 35 | 1 | 不成立フラグ 馬連 |  |
| 16 | `wide_cancelled_flag` | flag | 36 | 1 | 不成立フラグ ワイド |  |
| 18 | `exacta_cancelled_flag` | flag | 38 | 1 | 不成立フラグ 馬単 |  |
| 19 | `trio_cancelled_flag` | flag | 39 | 1 | 不成立フラグ 3連複 |  |
| 20 | `trifecta_cancelled_flag` | flag | 40 | 1 | 不成立フラグ 3連単 |  |
| 21 | `win_special_payout_flag` | flag | 41 | 1 | 特払フラグ 単勝 |  |
| 22 | `place_special_payout_flag` | flag | 42 | 1 | 特払フラグ 複勝 |  |
| 23 | `bracket_quinella_special_payout_flag` | flag | 43 | 1 | 特払フラグ 枠連 |  |
| 24 | `quinella_special_payout_flag` | flag | 44 | 1 | 特払フラグ 馬連 |  |
| 25 | `wide_special_payout_flag` | flag | 45 | 1 | 特払フラグ ワイド |  |
| 27 | `exacta_special_payout_flag` | flag | 47 | 1 | 特払フラグ 馬単 |  |
| 28 | `trio_special_payout_flag` | flag | 48 | 1 | 特払フラグ 3連複 |  |
| 29 | `trifecta_special_payout_flag` | flag | 49 | 1 | 特払フラグ 3連単 |  |
| 30 | `win_refund_flag` | flag | 50 | 1 | 返還フラグ 単勝 |  |
| 31 | `place_refund_flag` | flag | 51 | 1 | 返還フラグ 複勝 |  |
| 32 | `bracket_quinella_refund_flag` | flag | 52 | 1 | 返還フラグ 枠連 |  |
| 33 | `quinella_refund_flag` | flag | 53 | 1 | 返還フラグ 馬連 |  |
| 34 | `wide_refund_flag` | flag | 54 | 1 | 返還フラグ ワイド |  |
| 36 | `exacta_refund_flag` | flag | 56 | 1 | 返還フラグ 馬単 |  |
| 37 | `trio_refund_flag` | flag | 57 | 1 | 返還フラグ 3連複 |  |
| 38 | `trifecta_refund_flag` | flag | 58 | 1 | 返還フラグ 3連単 |  |
| 39 | `refund_horse_number_info_28` | str | 59 | 28 | 返還馬番情報 |  |
| 40 | `refund_bracket_info` | str | 87 | 8 | 返還枠番情報 |  |
| 41 | `refund_same_bracket_info` | str | 95 | 8 | 返還同枠情報 |  |
| 42 | `win_payback` | array:object[3] | 103 | 39 | 単勝払戻 |  |
|  | `  .number` | str | +0 | 2 | 馬番 |  |
|  | `  .payout` | int | +2 | 9 | 払戻金 |  |
|  | `  .popularity_rank` | int | +11 | 2 | 人気順 |  |
| 43 | `place_payback` | array:object[5] | 142 | 65 | 複勝払戻 |  |
|  | `  .number` | str | +0 | 2 | 馬番 |  |
|  | `  .payout` | int | +2 | 9 | 払戻金 |  |
|  | `  .popularity_rank` | int | +11 | 2 | 人気順 |  |
| 44 | `bracket_quinella_payback` | array:object[3] | 207 | 39 | 枠連払戻 |  |
|  | `  .number` | str | +0 | 2 | 組番 |  |
|  | `  .payout` | int | +2 | 9 | 払戻金 |  |
|  | `  .popularity_rank` | int | +11 | 2 | 人気順 |  |
| 45 | `quinella_payback` | array:object[3] | 246 | 48 | 馬連払戻 |  |
|  | `  .number` | str | +0 | 4 | 組番 |  |
|  | `  .payout` | int | +4 | 9 | 払戻金 |  |
|  | `  .popularity_rank` | int | +13 | 3 | 人気順 |  |
| 46 | `wide_payback` | array:object[7] | 294 | 112 | ワイド払戻 |  |
|  | `  .number` | str | +0 | 4 | 組番 |  |
|  | `  .payout` | int | +4 | 9 | 払戻金 |  |
|  | `  .popularity_rank` | int | +13 | 3 | 人気順 |  |
| 48 | `exacta_payback` | array:object[6] | 454 | 96 | 馬単払戻 |  |
|  | `  .number` | str | +0 | 4 | 組番 |  |
|  | `  .payout` | int | +4 | 9 | 払戻金 |  |
|  | `  .popularity_rank` | int | +13 | 3 | 人気順 |  |
| 49 | `trio_payback` | array:object[3] | 550 | 54 | 3連複払戻 |  |
|  | `  .number` | str | +0 | 6 | 組番 |  |
|  | `  .payout` | int | +6 | 9 | 払戻金 |  |
|  | `  .popularity_rank` | int | +15 | 3 | 人気順 |  |
| 50 | `trifecta_payback` | array:object[6] | 604 | 114 | 3連単払戻 |  |
|  | `  .number` | str | +0 | 6 | 組番 |  |
|  | `  .payout` | int | +6 | 9 | 払戻金 |  |
|  | `  .popularity_rank` | int | +15 | 4 | 人気順 |  |
