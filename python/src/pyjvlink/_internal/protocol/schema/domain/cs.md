# CS - コース情報

レコード長: 6829 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `racecourse_code` | str | 12 | 2 | 競馬場コード | KEY |
| 5 | `distance` | int | 14 | 4 | 距離 | KEY |
| 6 | `track_code` | str | 18 | 2 | トラックコード | KEY |
| 7 | `course_revision_date` | date_yyyymmdd | 20 | 8 | コース改修年月日 | KEY |
| 8 | `course_description` | str | 28 | 6800 | コース説明 |  |
