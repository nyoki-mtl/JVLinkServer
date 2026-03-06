# HS - 競走馬市場取引価格

レコード長: 200 バイト

| 項番 | フィールド名 | 型 | 位置 | サイズ | ラベル | KEY |
|---:|---|---|---:|---:|---|---|
| 2 | `data_code` | str | 3 | 1 | データ区分 |  |
| 3 | `data_creation_date` | date_yyyymmdd | 4 | 8 | データ作成年月日 |  |
| 4 | `pedigree_reg_num` | str | 12 | 10 | 血統登録番号 | KEY |
| 5 | `sire_breeding_reg_num` | str | 22 | 10 | 父馬 繁殖登録番号 |  |
| 6 | `dam_breeding_reg_num` | str | 32 | 10 | 母馬 繁殖登録番号 |  |
| 7 | `birth_year` | int | 42 | 4 | 生年 |  |
| 8 | `market_code` | str | 46 | 6 | 主催者・市場コード | KEY |
| 9 | `organizer_name` | str | 52 | 40 | 主催者名称 |  |
| 10 | `market_name` | str | 92 | 80 | 市場の名称 |  |
| 11 | `market_start_date` | date_yyyymmdd | 172 | 8 | 市場の開催期間(開始日) | KEY |
| 12 | `market_end_date` | date_yyyymmdd | 180 | 8 | 市場の開催期間(終了日) |  |
| 13 | `horse_age_at_trade` | int | 188 | 1 | 取引時の競走馬の年齢 |  |
| 14 | `trade_price` | int | 189 | 10 | 取引価格 |  |
