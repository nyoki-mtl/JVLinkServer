#pragma once

#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

#include "json.hpp"

// レコードタイプ定義
enum class RecordType {
  UNKNOWN = 0,
  JG,  // JRA General（新形式レコード）
  RA,  // レース詳細
  RC,  // レース詳細（地方）
  SE,  // 馬毎レース情報
  UM,  // 馬基本情報
  KS,  // 騎手情報
  CH,  // 調教師情報
  WE,  // 勝馬投票券
  WH,  // 勝馬投票券（地方）
  HR,  // 配当
  H1,  // 票数（全賭式）
  HC,  // 調教師コメント
  WC,  // ウッドチップ調教
  O1,  // 単勝・複勝オッズ
  O2,  // 枠連オッズ
  O3,  // 馬連オッズ
  O4,  // ワイドオッズ
  O5,  // 馬単オッズ
  O6,  // 三連複・三連単オッズ
  TK,  // 特別登録馬
  BT,  // 種牡馬情報
  BR,  // 繁殖牝馬情報
  BN,  // 馬主マスタ
  HN,  // 馬名情報
  SK,  // 坂路調教
  TC,  // 調教師コメント
  YS,  // 開催スケジュール
  AV,  // 場別発売情報
  JC,  // 重量ハンデ情報
  DM,  // 特別レース名
  TM,  // 対戦型データマイニング予想
  WF,  // 重勝式(WIN5)
  CS,  // コース情報
  CC,  // レース情報詳細（地方）
  H6,  // 三連単オッズ（三連勝単式）
  HY,  // 馬名の意味由来
  CK,  // 出走別着度数
  HS,  // 競走馬市場取引価格
};

// パースされたレコード情報
struct ParsedRecord {
  RecordType type;
  std::string record_type_id;  // Raw 2-byte record type ID (kept even when type is UNKNOWN)
  std::string raw_data;
  nlohmann::json structured_data;  // 構造化データ（配列等）のサポート

  std::string extractAndConvert(size_t start, size_t length) const;
  nlohmann::json extractAndConvertArray(size_t start_pos, size_t element_size, int count) const;

 private:
  // ユーティリティメソッド
  std::string extractField(size_t start, size_t length) const;
  static std::string convertEncoding(const std::string& shift_jis_data);
};

// レコードパーサーのベースクラス
class RecordParser {
 public:
  // レコードをパースして構造化データに変換
  static std::unique_ptr<ParsedRecord> parseRecord(const std::string& raw_data);

 private:
  RecordParser() = default;
  ~RecordParser() = default;
  // レコード解析ヘルパー
  static void parseBasicFields(ParsedRecord& record);
};

// 外部レコードパーサー関数の宣言
void parseTKFields(ParsedRecord& record);
void parseRAFields(ParsedRecord& record);
void parseSEFields(ParsedRecord& record);
void parseHRFields(ParsedRecord& record);
void parseH1Fields(ParsedRecord& record);
void parseH6Fields(ParsedRecord& record);
void parseO1Fields(ParsedRecord& record);
void parseO2Fields(ParsedRecord& record);
void parseO3Fields(ParsedRecord& record);
void parseO4Fields(ParsedRecord& record);
void parseO5Fields(ParsedRecord& record);
void parseO6Fields(ParsedRecord& record);
void parseUMFields(ParsedRecord& record);
void parseKSFields(ParsedRecord& record);
void parseCHFields(ParsedRecord& record);
void parseBRFields(ParsedRecord& record);
void parseBNFields(ParsedRecord& record);
void parseHNFields(ParsedRecord& record);
void parseSKFields(ParsedRecord& record);
void parseCKFields(ParsedRecord& record);
void parseRCFields(ParsedRecord& record);
void parseHCFields(ParsedRecord& record);
void parseHSFields(ParsedRecord& record);
void parseHYFields(ParsedRecord& record);
void parseYSFields(ParsedRecord& record);
void parseBTFields(ParsedRecord& record);
void parseCSFields(ParsedRecord& record);
void parseDMFields(ParsedRecord& record);
void parseTMFields(ParsedRecord& record);
void parseWFFields(ParsedRecord& record);
void parseJGFields(ParsedRecord& record);
void parseWCFields(ParsedRecord& record);
void parseWHFields(ParsedRecord& record);
void parseWEFields(ParsedRecord& record);
void parseAVFields(ParsedRecord& record);
void parseJCFields(ParsedRecord& record);
void parseTCFields(ParsedRecord& record);
void parseCCFields(ParsedRecord& record);

// ユーティリティ関数
RecordType stringToRecordType(const std::string& type_str);
std::string recordTypeToString(RecordType type);
