# JG - 競走馬除外情報

レコード長: 80 バイト

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
| 10 | `pedigree_reg_num` | str | 28 | 10 | 血統登録番号 | KEY |
| 11 | `horse_name` | str | 38 | 36 | 馬名 |  |
| 12 | `entry_order` | int | 74 | 3 | 出馬投票受付順番 | KEY |
| 13 | `entry_code` | str | 77 | 1 | 出走区分 |  |
| 14 | `exclusion_code` | str | 78 | 1 | 除外状態区分 |  |
