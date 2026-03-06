# BT - 系統情報

レコード長: 6889 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `breeding_reg_num` | str | 12 | 10 | 繁殖登録番号 | KEY |
| 5 | `lineage_id` | str | 22 | 30 | 系統ID |  |
| 6 | `lineage_name` | str | 52 | 36 | 系統名 |  |
| 7 | `lineage_description` | str | 88 | 6800 | 系統説明 |  |
