# JC - 騎手変更

レコード長: 161 バイト

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
| 10 | `announcement_datetime` | datetime_mmddhhmm | 28 | 8 | 発表月日時分 |  |
| 11 | `horse_number` | int | 36 | 2 | 馬番 | KEY |
| 12 | `horse_name` | str | 38 | 36 | 馬名 |  |
| 13 | `after_weight_carried` | int | 74 | 3 | 変更後負担重量 |  |
| 14 | `after_jockey_code` | str | 77 | 5 | 変更後騎手コード |  |
| 15 | `after_jockey_name` | str | 82 | 34 | 変更後騎手名 |  |
| 16 | `after_apprentice_code` | str | 116 | 1 | 変更後騎手見習コード |  |
| 17 | `before_weight_carried` | int | 117 | 3 | 変更前負担重量 |  |
| 18 | `before_jockey_code` | str | 120 | 5 | 変更前騎手コード |  |
| 19 | `before_jockey_name` | str | 125 | 34 | 変更前騎手名 |  |
| 20 | `before_apprentice_code` | str | 159 | 1 | 変更前騎手見習コード |  |
