# JV-Link の制限事項

JV-Linkのデータ仕様に関する制限事項や注意事項をまとめています。

## 1994年7月以前のデータ整備状況

1994年7月以前のJV-Dataには未整備項目が多数あります。

- データ提供元（JRA等）での入力不備や未設定項目が含まれる
- 未整備項目は将来的に整備される場合があるが、現時点では不完全
- データの欠損や不正確な値を想定した処理が必要

```python
# 1994年7月以前のデータを扱う際の注意
if race_date < "19940701":
    # 多くのフィールドが未設定の可能性がある
    if field_value in ["", "   ", "000"]:
        # 未設定値として処理
        pass
```

## データ訂正に関する方針

JRA-VAN Data Lab.では以下の方針でデータを提供しています：

- **データ提供元の入力値をそのまま提供** - 疑わしい値でも基本的に訂正しない
- **主催者側で訂正があった場合のみ** - 訂正データを含めた形で再提供
- **ソフト側での検証が重要** - データの妥当性チェックを実装することを推奨

## 地方競馬・海外競馬データの制限

JRA-VAN Data Lab.で提供する地方競馬・海外国際レース情報は、中央競馬に関係する以下のものに限定されます。

**地方競馬情報**:

- 2000年以降の地方競馬における中央交流競走
- 2000年以降に中央競馬に出走した地方馬の中央競馬出走時点での馬柱（過去走）となる地方レース

**海外国際レース情報**:

- 2000年以降に中央所属馬の出走した海外国際レース

JRA以外のデータでは多くのJRA固有フィールドが未設定となります：

```python
# 地方競馬・海外レースでの未設定項目の処理例
if racecourse_code in ["00"] or racecourse_code >= "30":
    # 地方競馬または海外レースの可能性
    if jra_specific_field == "00":
        # 未設定として処理
        pass
```

## 拡張版DataSpec（DIFN、BLDN等）について

2023年8月8日以降、以下のフィールドサイズが拡張された新しいDataSpecが追加されました：

| 標準版 | 拡張版 | 拡張されたフィールド |
|--------|--------|-------------------|
| DIFF | DIFN | 繁殖登録番号、生産者コード、生産者名 |
| BLOD | BLDN | 同上 |
| SNAP | SNPN | 同上 |
| HOSE | HOSN | 同上 |
| TCOV | TCVN | 同上 |
| RCOV | RCVN | 同上 |

拡張版は2023年8月8日以降に提供しているデータが取得対象となります。

## 新しいレコード種別への対応

データ種別に含まれるレコード種別は、仕様の追加によって増える可能性があります。**不明なレコード種別IDを読み飛ばす処理**を考慮してください。

PyJVLinkは基本的にこの処理を内部で行いますが、レコード処理でエラーが発生した場合は以下のように対処してください：

```python
async for record in records:
    try:
        # レコード処理
        process_record(record)
    except RecordParseError as e:
        # 未知のレコード種別の可能性
        logger.warning(f"Unknown record type: {e}")
        continue
```

## optionパラメータとDataSpecの関係

optionパラメータによって利用可能なDataSpecが異なります：

| option | 意味 | 利用可能なDataSpec |
|--------|------|-------------------|
| 1 | 通常データ | TOKU, RACE, DIFF, BLOD, SNAP, SLOP, WOOD, YSCH, HOSE, HOYU, COMM, MING, DIFN, BLDN, SNPN, HOSN |
| 2 | 今週データ | TOKU, RACE, TCOV, RCOV, SNAP, TCVN, RCVN, SNPN |
| 3, 4 | セットアップデータ | TOKU, RACE, DIFF, BLOD, SNAP, SLOP, WOOD, YSCH, HOSE, HOYU, COMM, MING, DIFN, BLDN, SNPN, HOSN |

## 関連情報

- [歴史的変更点](historical-changes.md) - コード表やルールの年代別変更
- [エラーコード一覧](error-codes.md) - エラーの詳細
- [DataSpec 概要](../data-specs/index.md) - 各DataSpecの仕様
