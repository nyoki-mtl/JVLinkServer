# DataSpec一覧

DataSpecは、JV-Linkからデータを取得する際に指定するデータの種別を表すコードです。DataSpecの使い方については[データ取得の基本](../guides/dataspec-usage.md)を参照してください。

## 蓄積系DataSpec

過去のレース結果や馬情報などの確定データを取得します。`query_stored()` メソッドで使用します。

| DataSpec | 説明 | レコード種別 | 更新タイミング |
|----------|------|-------------|--------------|
| [RACE](storage/race.md) | レース情報 | RA, SE, HR, H1, H6, O1, O2, O3, O4, O5, O6, WF, JG | 木曜15:00頃（特定G1）<br/>木曜16:30頃・20:00頃（出走馬名表）<br/>金土12:00頃（出馬表）<br/>月曜14:00頃（確定） |
| [DIFF](storage/diff.md) | 差分データ | UM, KS, CH, BR, BN, RC, RA, SE | 月曜14:00頃<br/>木曜20:00頃 |
| [DIFN](storage/diff.md) | 差分データ（拡張版） | UM, KS, CH, BR, BN, RC, RA, SE | DIFFと同じ ※1 |
| [BLOD](storage/blod.md) | 血統情報 | HN, SK, BT | 月曜14:00頃<br/>木曜20:00頃 |
| [BLDN](storage/blod.md) | 血統情報（拡張版） | HN, SK, BT | BLODと同じ ※1 |
| [TOKU](storage/toku.md) | 特別登録馬情報 | TK | 日曜夕刻（ハンデ前）<br/>月曜夕刻（ハンデ後） |
| [SNAP](storage/snap.md) | 出走時点情報 | CK | 木曜20:00頃<br/>月曜14:00頃（騎手変更時） |
| [SNPN](storage/snap.md) | 出走時点情報（拡張版） | CK | SNAPと同じ ※1 |
| [MING](storage/ming.md) | マイニング情報 | DM, TM | 月曜14:00頃 |
| [SLOP](storage/slop.md) | 坂路調教 | HC | 毎日（月曜除く） |
| [WOOD](storage/wood.md) | ウッドチップ調教 | WC | 毎日（月曜除く） |
| [YSCH](storage/ysch.md) | 開催スケジュール | YS | 年末（翌年分）<br/>月曜14:00頃（更新） |
| [HOSE](storage/hose.md) | 競走馬市場取引価格 | HS | 不定期（市場終了後1ヶ月以内） |
| [HOSN](storage/hose.md) | 競走馬市場取引価格（拡張版） | HS | HOSEと同じ ※1 |
| [HOYU](storage/hoyu.md) | 馬名の意味由来 | HY | 火曜不定期 |
| [COMM](storage/comm.md) | 各種解説情報 | CS | 不定期 |
| [TCOV](storage/tcov.md) | 補てん情報（特別登録馬） | UM, CH, BR, BN, RC, RA, SE | 月曜14:00頃 |
| [TCVN](storage/tcov.md) | 補てん情報（特別登録馬・拡張版） | UM, CH, BR, BN, RC, RA, SE | TCOVと同じ ※1 |
| [RCOV](storage/rcov.md) | 補てん情報（レース情報） | JG, UM, KS, CH, BR, BN, RC, RA, SE | 木曜20:00頃 |
| [RCVN](storage/rcov.md) | 補てん情報（レース情報・拡張版） | JG, UM, KS, CH, BR, BN, RC, RA, SE | RCOVと同じ ※1 |

※1 拡張版（末尾N）は2023年8月8日以降のデータで、繁殖登録番号・生産者コード・生産者名のサイズ拡張に対応。詳細は[JV-Linkの制限事項](../appendix/jvlink-limitations.md)を参照。

## リアルタイム系DataSpec

レース当日の速報データを取得します。`query_realtime()` メソッドで使用します。

| DataSpec | 説明 | レコード種別 | 更新タイミング |
|----------|------|-------------|--------------|
| [0B11](realtime/0b11.md) | 速報馬体重 | WH | レース発走約1時間前 |
| [0B12](realtime/0b12.md) | 速報レース情報（成績確定後） | RA, SE, HR | レース確定後（段階的） |
| [0B13](realtime/0b13.md) | 速報タイム型データマイニング予想 | DM | 前日・当日・直前の3段階 |
| [0B14](realtime/0b14.md) | 速報開催情報（一括） | WE, AV, JC, TC, CC | 開催中随時 |
| [0B15](realtime/0b15.md) | 速報レース情報（出走馬名表～） | RA, SE, HR | 木曜出走馬名表後～確定 |
| [0B16](realtime/0b16.md) | 速報開催情報（指定） | WE, AV, JC, TC, CC | イベント発生時 |
| [0B17](realtime/0b17.md) | 速報対戦型データマイニング予想 | TM | 前日・当日・直前の3段階 |
| [0B20](realtime/0b20.md) | 速報票数（全賭式） | H1, H6 | 前日売最終・レース確定後 |
| [0B30](realtime/0b30.md) | 速報オッズ（全賭式） | O1, O2, O3, O4, O5, O6 | 発売中随時 |
| [0B31](realtime/0b31.md) | 速報オッズ（単複枠） | O1 | 発売中随時 |
| [0B32](realtime/0b32.md) | 速報オッズ（馬連） | O2 | 発売中随時 |
| [0B33](realtime/0b33.md) | 速報オッズ（ワイド） | O3 | 発売中随時 |
| [0B34](realtime/0b34.md) | 速報オッズ（馬単） | O4 | 発売中随時 |
| [0B35](realtime/0b35.md) | 速報オッズ（3連複） | O5 | 発売中随時 |
| [0B36](realtime/0b36.md) | 速報オッズ（3連単） | O6 | 発売中随時 |
| [0B41](realtime/0b41.md) | 時系列オッズ（単複枠） | O1 | 発売中定期的 |
| [0B42](realtime/0b42.md) | 時系列オッズ（馬連） | O2 | 発売中定期的 |
| [0B51](realtime/0b51.md) | 速報重勝式（WIN5） | WF | 重勝式詳細発表後 |

## optionパラメータとDataSpecの組み合わせ

蓄積系DataSpecは、`query_stored()` の `option` パラメータによって利用可能な組み合わせが制限されます。

| option | 意味 | 利用可能なDataSpec |
|--------|------|-------------------|
| 1 | 通常データ | TOKU, RACE, DIFF, BLOD, SNAP, SLOP, WOOD, YSCH, HOSE, HOYU, COMM, MING, DIFN, BLDN, SNPN, HOSN |
| 2 | 今週データ | TOKU, RACE, TCOV, RCOV, SNAP, TCVN, RCVN, SNPN |
| 3, 4 | セットアップデータ | TOKU, RACE, DIFF, BLOD, SNAP, SLOP, WOOD, YSCH, HOSE, HOYU, COMM, MING, DIFN, BLDN, SNPN, HOSN |

## 終了日時を指定できないDataSpec

以下のDataSpecは `to_date` パラメータを指定できません。

- TOKU（特別登録馬情報）
- DIFF、DIFN（差分データ）
- HOSE、HOSN（競走馬市場取引価格）
- HOYU（馬名の意味由来）
- COMM（各種解説情報）

## セットアップデータの収録期間

option=3,4 でセットアップデータを取得する場合、DataSpecによって収録開始時期が異なります。

| 収録開始時期 | DataSpec |
|-------------|----------|
| 1986年以降 | RACE（RA, SE, HR, H1）、DIFF/DIFN（UM, BR, BN, RC）、BLOD/BLDN |
| 1997年以降 | HOSE/HOSN（競走馬市場取引価格） |
| 2000年以降 | YSCH（開催スケジュール）、HOYU（馬名の意味由来） |
| 2003年以降 | SLOP（坂路調教） |
| 2021年7月27日以降 | WOOD（ウッドチップ調教） |

## データ保存期間

| 分類 | DataSpec | 保存期間 |
|------|----------|----------|
| 蓄積系（一般） | RACE, DIFF, BLOD, TOKU, SNAP, MING, SLOP, WOOD, YSCH, HOYU 等 | 1年間 |
| 蓄積系（無期限） | HOSE/HOSN, COMM | 削除されない |
| リアルタイム系（一般） | 0B11～0B36, 0B51 | 1週間 |
| リアルタイム系（長期） | 0B41, 0B42（時系列オッズ） | 1年間 |

## 関連情報

- [データ取得の基本](../guides/dataspec-usage.md) - DataSpecの使い方とAPIの使用方法
- [レコード仕様](../records/index.md) - 各レコードのフォーマット
- [コード表](../code-tables/index.md) - 各種コードの意味
- [配信スケジュール](../appendix/delivery-schedule.md) - データ配信の詳細タイミング
- [JV-Linkの制限事項](../appendix/jvlink-limitations.md) - 拡張版DataSpec等の制限事項
