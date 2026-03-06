# CC - コース変更

レコード長: 50 バイト

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
| 11 | `after_distance` | int | 36 | 4 | 変更後距離 |  |
| 12 | `after_track_code` | str | 40 | 2 | 変更後トラックコード |  |
| 13 | `before_distance` | int | 42 | 4 | 変更前距離 |  |
| 14 | `before_track_code` | str | 46 | 2 | 変更前トラックコード |  |
| 15 | `reason_code` | str | 48 | 1 | 事由区分 |  |
