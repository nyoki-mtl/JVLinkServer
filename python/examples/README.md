# PyJVLink サンプルコード集

このディレクトリには、PyJVLinkライブラリの使用方法を示すサンプルコードが整理されています。
初心者から上級者まで、目的に応じて段階的に学習できる構成になっています。

## ディレクトリ構成

### basic/ - 基本的な使用例（3ファイル）

初めてPyJVLinkを使う方向けの、シンプルで理解しやすいサンプル集です。

- **[health_check.py](basic/health_check.py)** - サーバーの稼働確認とシステム情報の取得
  - ヘルスチェックAPI の使用方法
  - サーバーとJV-Linkコンポーネントの状態確認
  - バージョン情報の取得

- **[data_retrieval.py](basic/data_retrieval.py)** - 蓄積データの基本的な取得方法
  - 競走馬マスタ（TOKU）データの取得例
  - `record_types` パラメータによるフィルタリング
  - レコードオブジェクトの基本的な操作

- **[event_streaming.py](basic/event_streaming.py)** - リアルタイムイベント監視の基本
  - Server-Sent Events (SSE) の使用方法
  - イベントタイプ別の処理
  - シグナルハンドリング

### advanced/ - 高度な使用例（1ファイル）

実際のアプリケーション開発で使える、より実践的なサンプルです。

- **[event_streaming_sse.py](advanced/event_streaming_sse.py)** - 高度なイベント監視とデータ自動取得
  - イベント発生時の自動データ取得機能
  - データ種別（dataspec）の自動選択
  - レコード詳細情報の表示（`format_details()` 使用）
  - エラーハンドリングとリトライ機能

### testing/ - 調査・診断ツール（1ファイル）

システムの動作確認や問題の診断に使用するツールです。

- **[check_all_dataspecs.py](testing/check_all_dataspecs.py)** - 包括的なシステムテスト
  - 全データ種別（dataspec）の動作確認
  - Option 1～7 の各モードテスト
  - リアルタイム系データの取得テスト
  - レコード種別と件数の分布確認

### tools/ - ユーティリティツール（2ファイル）

特定の機能をテストしたり、開発支援を行うツール群です。

- **[generate_course_images.py](tools/generate_course_images.py)** - コース図画像の生成
  - JVCourseFile2 API の動作確認
  - 各競馬場のコース図取得
  - 画像ファイルの保存機能

- **[generate_uniform_images.py](tools/generate_uniform_images.py)** - 勝負服画像の生成
  - JVFukuFile API の動作確認
  - 勝負服パターンによる画像生成
  - ファイル保存とエラーハンドリング

## クイックスタート

### Step 1: サーバーの動作確認

まず最初に、JVLinkServerが正常に動作していることを確認します。

```bash
python basic/health_check.py
```

**期待される出力：**
```
サーバーは正常に稼働しています
  - サービス名: JVLinkServer
  - バージョン: 1.0.0
  - HTTPサーバー: healthy (ポート: 8765)
  - JV-Link: healthy (初期化済み: はい)
```

`/health` が `unhealthy` の場合は、サンプルは `JV-Link 障害詳細` を表示します。

### Step 2: データ取得の基本を学ぶ

競走馬マスタデータを取得して、基本的な使い方を理解します。

```bash
python basic/data_retrieval.py
```

### Step 3: イベント監視を試す

リアルタイムイベントの監視機能を体験します。

```bash
python basic/event_streaming.py
```

### Step 4: 高度なイベント監視（自動データ取得付き）

イベント発生時に自動的に関連データを取得する機能を試します。

```bash
python advanced/event_streaming_sse.py --auto-fetch
```

### Step 5: システム全体のテスト

全データ種別の動作確認を行います（オプション）。

```bash
python testing/check_all_dataspecs.py
```

## 実行環境

### 必要な環境

- **OS**: Windows 10/11（JV-Link要件）
- **Python**: 3.9以上
- **パッケージ**: PyJVLinkがインストール済み
- **サービス**: JVLinkServerが起動中（デフォルトポート: 8765）

### インストール方法

```bash
# PyJVLinkをインストール
pip install pyjvlink

# または開発版を使用
cd python/
pip install -e .
```

## 重要な注意事項

### データ配信時間

- **配信停止時間**: 月曜日の深夜〜火曜日のAM 6:00（メンテナンス）
- **リアルタイムデータ**: 競馬開催日のみ利用可能
- **日曜日**: データ配信なし

### システム要件

- JV-Linkは**Windows専用**のCOMコンポーネントです
- JRA-VANへの契約とJV-Linkのインストールが必要です
- JVLinkServerはバックグラウンドで動作している必要があります

## トラブルシューティング

### よくある問題と解決方法

| 問題 | 確認事項 | 解決方法 |
|------|----------|----------|
| **接続エラー** | JVLinkServerが起動しているか | `health_check.py` で確認 |
| **ポートエラー** | ポート8765が使用中でないか | `--port` オプションで変更 |
| **データが取得できない** | JV-Linkが正しくインストールされているか | JV-Linkの再インストール |
| **イベントが来ない** | 開催日かどうか | 競馬開催スケジュールを確認 |

### デバッグ方法

詳細なログを確認するには：

```bash
# デバッグログを有効にして実行
python basic/health_check.py --log-level debug

# イベント監視のデバッグ
python advanced/event_streaming_sse.py --auto-fetch --log-level debug
```

### サポート

- **ドキュメント**: `docs/` ディレクトリ
- **詳細テスト**: `python/tests/` のpytestテストスイート
- **API仕様**: `docs/src/api/` ディレクトリ

## 学習の進め方

1. **基礎編**: `basic/` のサンプルを順番に実行
2. **応用編**: `advanced/` でより実践的な使い方を学習
3. **診断編**: `testing/` でシステム全体の動作を確認
4. **開発編**: `tools/` で開発支援ツールを活用

各サンプルは独立して動作するため、興味のある部分から始めることができます。
