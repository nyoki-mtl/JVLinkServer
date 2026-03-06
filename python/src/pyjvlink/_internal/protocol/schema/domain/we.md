# WE - 天候馬場状態

レコード長: 42 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `meet_year` | int | 12 | 4 | 開催年 | KEY |
| 5 | `meet_date` | date_mmdd | 16 | 4 | 開催月日 | KEY |
| 6 | `racecourse_code` | str | 20 | 2 | 競馬場コード | KEY |
| 7 | `meet_round` | int | 22 | 2 | 開催回 | KEY |
| 8 | `meet_day` | int | 24 | 2 | 開催日目 | KEY |
| 9 | `announcement_datetime` | datetime_mmddhhmm | 26 | 8 | 発表月日時分 | KEY |
| 10 | `change_identifier` | str | 34 | 1 | 変更識別 | KEY |
| 11 | `weather_code` | str | 35 | 1 | 天候状態 |  |
| 12 | `turf_track_condition_code` | str | 36 | 1 | 馬場状態・芝 |  |
| 13 | `dirt_track_condition_code` | str | 37 | 1 | 馬場状態・ダート |  |
| 14 | `before_weather_code` | str | 38 | 1 | 変更前天候状態 |  |
| 15 | `before_turf_track_condition_code` | str | 39 | 1 | 変更前馬場状態・芝 |  |
| 16 | `before_dirt_track_condition_code` | str | 40 | 1 | 変更前馬場状態・ダート |  |
