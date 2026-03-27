# 変更履歴

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づいており、
このプロジェクトは [セマンティックバージョニング](https://semver.org/lang/ja/) に準拠しています。

## [0.8.1] - 2026-03-27

### 修正
- `JV-Link session is busy` による HTTP 503 を generic error ログから分離し、`path` / `operation` / `remote_addr` を含む `warning` ログとして記録するよう変更。
- busy 503 レスポンスに `Retry-After`、`X-JVLink-Busy`、`X-JVLink-Operation` ヘッダーを追加し、既存の 503 status と error body 互換性を維持したまま retry hint を機械可読化。
- `/health` に busy の累積回数と直近発生時刻を追加し、single-session 競合の観測性を改善。
- `pyjvlink` で `-202` を `JVBusyError` として扱い、`Retry-After` を例外に保持できるようにした。

### テスト
- busy 503 の header / error mapping / stream 経路をカバーする Python テストを追加。

## [0.8.0] - 2026-03-06

### 追加
- DataSpec とレースキーの取り扱いを強化し、`QueryOption` 列挙体や race key ヘルパーを追加。
- イベントストリーミング、course file 取得、保存済み結果メタデータなど API 機能を拡張。
- 型付きレコードモデルの対応範囲を拡大し、コード生成基盤を導入。

### 変更
- レコード/モデル/プロトコル間の命名規約を統一し、フィールド名とデータ型の整合性を改善。
- エラー処理、ログ出力、CLI/transport 設定を見直し、バリデーションと診断性を強化。
- ドキュメント構成を再整理し、スキーマ・型・パッケージ境界に関する内部仕様を更新。

### 修正
- realtime query key の検証、イベント配信、ダウンロード処理、JSON シリアライズの不整合を修正。
- public export スクリプトの remote fetch と orphan export 時の除外パス処理を安定化。

### テスト
- Python テスト実装を現行 API に合わせて更新し、検証ケースを整理。

## [0.7.10] - 2025-10-09

### 修正
- UM レコードの英馬名フィールドを `MixedWidthStringByByte(60)` に変更し、曖昧幅のダッシュなどを含む実データが `ParseError` にならないよう調整。

### ドキュメント
- UM レコード仕様に英馬名の曖昧幅ケースとバイト長扱いの補足を追加。

### テスト
- 曖昧幅ダッシュを含む英馬名について、半角検証の失敗と混在幅検証の成功を確認するユニットテストを追加。

## [0.7.9] - 2025-10-04

### 変更
- `099999` で提供されるオッズ値をレース施行日に応じて解釈できるよう、`WinOdds` 系の特殊値処理と O2/O4/O5 レコードを更新。
- `RaceIdentifiable` ミックスインのレース日抽出を拡張し、オッズ値のカットオーバー判定に利用できるよう調整。

### ドキュメント
- PyJVLink API / CLI / クイックスタート等のドキュメントを現行のレスポンス形式と設定項目に合わせて全面的に更新。

## [0.7.8] - 2025-10-02

### 修正
- overseasレースでレース番号が未設定のケースにおいて、決定的なサロゲート番号（01-99）で `race_id` を生成するよう変更。

### テスト
- レース番号サロゲート生成をカバーするユニットテストを追加。

## [0.7.7] - 2025-10-01

### 修正
- overseasレースで開催回・開催日が未設定初期値の場合でも `KK=00` / `HH=00` で race_id を生成するよう変更。

### 追加
- `pyjvlink.utils.is_surrogate_race_id` ユーティリティを追加。

### ドキュメント
- DM / TM レコードの race_id サロゲート生成仕様を追記。

### テスト
- race_id サロゲート生成およびユーティリティの単体テストを追加。

## [0.7.5] - 2025-09-22

### 変更
- COMPUTED_PROPERTIES の整理と一貫化
  - mixin 側に `announcement_at` を含める既定へ復帰し、DM/TM のみ非対応として除外
  - 各レコードにあった冗長な `COMPUTED_PROPERTIES = RaceIdentifiable.COMPUTED_PROPERTIES` の再代入を削除
  - 実装していない計算プロパティ（例: DM/TM の `announcement_at`）は各クラスで公開しない方針を徹底

### 修正
- 重複・冗長な定義を削除して可読性を向上
- announcement_at 対応レコード群での挙動を mixin 仕様に統一

## [0.7.4] - 2025-09-17

### 変更
- race_id 生成の厳格化（全レコード）
  - 未設定初期値（年=None、月日=None、場="00"/空、回・日・番=0/None/不正）を含む場合は `ValueError` を送出
  - 競馬場コードはコード表に存在する2文字コードのみ許容（正規化の廃止）
- `announcement_at` の仕様統一
  - `announcement_datetime` 未設定/非保持のレコードでは `AttributeError` を送出

### 修正
- DM/TM レコードに RaceIdentifiable を適用し、`race_id`/`race_id_short` を提供
- 不要なユーティリティ関数・緩和処理を削除してコードを簡潔化

### ドキュメント
- DM/TM のレースID/計算フィールド仕様を更新（厳格化の注意書きを追加）

## [0.7.3] - 2025-09-16

### 修正
- race_id の JJ（場コード）を整数扱いから「半角2文字の文字列」扱いに変更し、JVRTOpen の key 仕様（YYYYMMDDJJ[KKHH]RR）と整合。
- 海外の英字混在コード（例: A4, C0）でレースID生成が失敗する不具合を修正。

### ドキュメント
- 競馬場コードの表記を「数値2桁」から「半角2文字」に統一（海外コード英字混在を明示）。
- Quickstart のキー例に JJ が英字混在可である旨を追記。
- data_specs に JJ が半角2文字であること、海外コード例を補足。

### テスト
- 海外の英字混在コード（A4/C0）に関するテストケースを追加。

## [0.7.2] - 2025-09-15

### 変更
- テストスイートの整理（不要なケース削除、現行APIに整合）
- 計算プロパティ定義の型注釈調整（mypyの警告解消）
- CLIの長行修正と軽微な整形

## [0.6.4] - 2025-08-26

### 追加
- workers 向けフィールド追加と出力オプションの拡充
  - WHRecord: `HorseWeightInfo.to_dict()` に `weight_change`（符号付き整数）を追加
  - JCRecord: `to_dict()` に `jockey_id_before/after`（5桁ゼロパディング文字列）を追加
  - SKRecord: `to_dict(include_computed_fields=False, include_aggregates=True)` を追加し、
    `include_aggregates=False` で `pedigree_3gen_breeding_reg_nums` を非出力化可能に

### ドキュメント
- 命名ポリシーを明記（`*_id`: ゼロパディング済み文字列、`*_code`: 生コード）
- SKRecord の `to_dict()` 仕様（プロパティ出力と集約非出力オプション）を追記

## [0.6.1] - 2025-01-23

### 追加
- **歴史的日付対応**: 1900年未満の日付を許容（1〜9999年）
  - 調教師レコード等で1897年、1892年生まれの個体に対応
  - 実在しない日付（2月30日等）の検証を強化
- **環境変数によるタイムアウト設定**
  - `JVLINK_HTTP_TIMEOUT`: HTTPタイムアウト（デフォルト60秒）
  - `JVLINK_STREAM_READ_TIMEOUT`: ストリーミング読み取りタイムアウト（デフォルト300秒）
- **DataSpec対応表**: READMEに現行実装で使用可能なDataSpec名の一覧を追加

### 改善
- **正規化出力の必須フィールド保証**
  - CH（調教師）、KS（騎手）、UM（馬）、BR（生産者）、BN（馬主）レコードで名前フィールドを常に出力
  - `include_computed_fields=False`でも人名・馬名が確実に取得可能に
- **DataSpec名称の整合性改善**
  - 旧版（BLOD, HOSE）から新版（BLDN, HOSN）への移行を推奨
  - ドキュメントとサンプルコードの表記を統一

### 修正
- UMレコードの重複した`to_dict`メソッドを修正
- 例外チェーンの適切な実装（`raise ... from e`）
- BN/BRレコードの名前フィールド取得ロジックを改善

## [0.1.3] - 2025-01-07

### 改善
- C++のログ出力先を実行ファイルと同じディレクトリに固定
  - 配布版: `%LOCALAPPDATA%\pyjvlink\logs\`
  - 開発版: `python/src/pyjvlink/lib/logs\`
  - ユーザーの作業ディレクトリを汚染しない設計に改善

### ドキュメント
- CHANGELOG.mdを日本語化
- インストール方法とトラブルシューティングの改善

## [0.1.2] - 2025-07-08

### 追加
- Windows環境での初回実行時設定の改善
- 自動ダウンロード機能の強化: GitHubリリースからのJVLinkServer.exe取得を安定化
- インストール検証ガイドの追加

### 修正
- JVLinkServer.exe検出ロジックの安定性向上
- パス処理におけるWindows互換性の改善
- 自動ダウンロード機能のエラーハンドリング強化

## [0.1.1] - 2025-07-07

### 追加
- JVLinkServer.exeの自動ダウンロード機能
  - GitHubリリースからの自動取得
  - GITHUB_TOKEN環境変数によるプライベートリポジトリ対応
  - ダウンロード進捗表示

### 改善
- 初回起動時のユーザーエクスペリエンス
- エラーメッセージの明確化・日本語化
- ログ出力の最適化

## [0.1.0] - 2025-07-07

### 初回リリース

#### C++ サーバー (JVLinkServer)
- JV-Link COMコンポーネントのHTTPラッパー
- 40種類以上のレコード形式を自動解析
- Shift_JIS → UTF-8自動変換
- NDJSONストリーミング対応
- Server-Sent Events (SSE) によるイベント配信

#### Python クライアント (PyJVLink)
- async/awaitをサポートした非同期HTTPクライアント
- Pydanticを使用した構造化データモデル
- すべての主要なJV-Linkレコードタイプのデータモデル
- JVLinkServer.exeの自動起動・停止
- コマンドラインインターフェース（CLI）

#### 実装済み JV-Link メソッド
- JVInit, JVOpen, JVRTOpen, JVRead/JVGets, JVStatus, JVClose
- JVSkip, JVWatchEvent/JVWatchEventClose, JVFiledelete
- JVFukuFile/JVFuku, JVCourseFile/JVCourseFile2

#### API エンドポイント
- `/health`, `/version`, `/query`, `/realtime/open`
- `/events/stream` (SSE), `/uniform/image`, `/course/file`

## [0.0.1] - 2024-12-20

- プロジェクト開始
- 基本的なCOMラッパー実装
- HTTPサーバーのプロトタイプ
