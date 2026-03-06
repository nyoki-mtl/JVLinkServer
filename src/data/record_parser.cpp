#include "data/record_parser.h"

#include <Windows.h>
#include <spdlog/spdlog.h>

#include <algorithm>
#include <chrono>
#include <codecvt>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <locale>
#include <set>
#include <sstream>
#include <vector>

/**
 * フィールドを抽出して文字エンコーディングを変換する
 *
 * 生データから指定位置のフィールドを抽出し、
 * Shift_JISからUTF-8へ変換する。
 *
 * @param start 開始位置（0ベース）
 * @param length 抽出長
 * @return UTF-8変換済み文字列
 */
std::string ParsedRecord::extractAndConvert(size_t start, size_t length) const {
  std::string extracted = extractField(start, length);
  return convertEncoding(extracted);
}

/**
 * 配列データを抽出して変換する
 *
 * 固定長の要素が連続する配列データを抽出し、
 * JSON配列として返す。
 *
 * @param start_pos 配列の開始位置
 * @param element_size 各要素のサイズ
 * @param count 要素数
 * @return 変換済み文字列のJSON配列
 */
nlohmann::json ParsedRecord::extractAndConvertArray(size_t start_pos, size_t element_size, int count) const {
  nlohmann::json arr = nlohmann::json::array();
  for (int i = 0; i < count; i++) {
    arr.push_back(this->extractAndConvert(start_pos + i * element_size, element_size));
  }
  return arr;
}

/**
 * JV-Linkレコードをパースする
 *
 * 生データからレコードタイプを判別し、
 * 適切なパーサーを呼び出して構造化データを生成する。
 *
 * @param raw_data JV-Linkから取得した生データ
 * @return パース済みレコード
 */
std::unique_ptr<ParsedRecord> RecordParser::parseRecord(const std::string& raw_data) {
  auto record = std::make_unique<ParsedRecord>();
  record->raw_data = raw_data;

  if (raw_data.length() < 2) {
    record->record_type_id.clear();
    record->type = RecordType::UNKNOWN;
  } else {
    record->record_type_id = raw_data.substr(0, 2);
    record->type = ::stringToRecordType(record->record_type_id);
  }

  if (record->type == RecordType::UNKNOWN) {
    return record;
  }

  // レコードタイプに応じた詳細解析を実行
  parseBasicFields(*record);

  return record;
}

/**
 * レコードタイプ別の詳細解析を実行する
 *
 * 各レコードタイプに対応する専用パーサーを呼び出し、
 * 構造化データを生成する。
 *
 * @param record パース対象のレコード
 */
void RecordParser::parseBasicFields(ParsedRecord& record) {
  // レコードタイプ別に専用パーサーを呼び出す
  switch (record.type) {
    // 特別登録馬レコード
    case RecordType::TK:
      ::parseTKFields(record);
      break;
    // レース詳細レコード
    case RecordType::RA:
      ::parseRAFields(record);
      break;
    // 馬毎レース情報レコード
    case RecordType::SE:
      ::parseSEFields(record);
      break;
    // 払戻レコード
    case RecordType::HR:
      ::parseHRFields(record);
      break;
    // 票数1レコード（単複枠）
    case RecordType::H1:
      ::parseH1Fields(record);
      break;
    // 票数6レコード（3連単）
    case RecordType::H6:
      ::parseH6Fields(record);
      break;
    // オッズ1レコード（単複枠）
    case RecordType::O1:
      ::parseO1Fields(record);
      break;
    // オッズ2レコード（馬連）
    case RecordType::O2:
      ::parseO2Fields(record);
      break;
    // オッズ3レコード（ワイド）
    case RecordType::O3:
      ::parseO3Fields(record);
      break;
    // オッズ4レコード（馬単）
    case RecordType::O4:
      ::parseO4Fields(record);
      break;
    // オッズ5レコード（3連複）
    case RecordType::O5:
      ::parseO5Fields(record);
      break;
    // オッズ6レコード（3連単）
    case RecordType::O6:
      ::parseO6Fields(record);
      break;
    // 競走馬マスタレコード
    case RecordType::UM:
      ::parseUMFields(record);
      break;
    // 騎手マスタレコード
    case RecordType::KS:
      ::parseKSFields(record);
      break;
    // 調教師マスタレコード
    case RecordType::CH:
      ::parseCHFields(record);
      break;
    // 生産者マスタレコード
    case RecordType::BR:
      ::parseBRFields(record);
      break;
    // 馬主マスタレコード
    case RecordType::BN:
      ::parseBNFields(record);
      break;
    // 繁殖馬マスタレコード
    case RecordType::HN:
      ::parseHNFields(record);
      break;
    // 産駒マスタレコード
    case RecordType::SK:
      ::parseSKFields(record);
      break;
    // 出走別着度数レコード
    case RecordType::CK:
      ::parseCKFields(record);
      break;
    // レコードマスタ（コースレコード）
    case RecordType::RC:
      ::parseRCFields(record);
      break;
    // 坂路調教レコード
    case RecordType::HC:
      ::parseHCFields(record);
      break;
    // 競走馬市場取引価格レコード
    case RecordType::HS:
      ::parseHSFields(record);
      break;
    // 馬名の意味由来レコード
    case RecordType::HY:
      ::parseHYFields(record);
      break;
    // 開催スケジュールレコード
    case RecordType::YS:
      ::parseYSFields(record);
      break;
    // 系統情報レコード
    case RecordType::BT:
      ::parseBTFields(record);
      break;
    // コース情報レコード
    case RecordType::CS:
      ::parseCSFields(record);
      break;
    // タイム型データマイニング予想レコード
    case RecordType::DM:
      ::parseDMFields(record);
      break;
    // 対戦型データマイニング予想レコード
    case RecordType::TM:
      ::parseTMFields(record);
      break;
    // 重勝式レコード（WIN5）
    case RecordType::WF:
      ::parseWFFields(record);
      break;
    // 競走馬除外情報レコード
    case RecordType::JG:
      ::parseJGFields(record);
      break;
    // ウッドチップ調教レコード
    case RecordType::WC:
      ::parseWCFields(record);
      break;
    // 馬体重レコード（リアルタイム）
    case RecordType::WH:
      ::parseWHFields(record);
      break;
    // 天候馬場状態レコード（リアルタイム）
    case RecordType::WE:
      ::parseWEFields(record);
      break;
    // 出走取消・競走除外レコード（リアルタイム）
    case RecordType::AV:
      ::parseAVFields(record);
      break;
    // 騎手変更レコード（リアルタイム）
    case RecordType::JC:
      ::parseJCFields(record);
      break;
    // 発走時刻変更レコード（リアルタイム）
    case RecordType::TC:
      ::parseTCFields(record);
      break;
    // コース変更レコード（リアルタイム）
    case RecordType::CC:
      ::parseCCFields(record);
      break;
    default:
      break;
  }
}

// ParsedRecordのプライベートメソッド実装
std::string ParsedRecord::extractField(size_t start, size_t length) const {
  if (start + length > raw_data.length()) {
    return "";
  }

  std::string field = raw_data.substr(start, length);

  // 生データをそのまま返す（トリム処理なし）
  return field;
}

std::string ParsedRecord::convertEncoding(const std::string& shift_jis_data) {
  if (shift_jis_data.empty()) {
    return "";
  }

  try {
    // Shift_JIS（コードページ932）からUnicodeに変換
    int wide_size = MultiByteToWideChar(932, 0, shift_jis_data.c_str(), -1, NULL, 0);
    if (wide_size == 0) {
      return shift_jis_data;  // 変換失敗時は元データを返す
    }

    std::vector<wchar_t> wide_buffer(wide_size);
    int result = MultiByteToWideChar(932, 0, shift_jis_data.c_str(), -1, wide_buffer.data(), wide_size);
    if (result == 0) {
      return shift_jis_data;
    }

    // UnicodeからUTF-8に変換
    int utf8_size = WideCharToMultiByte(CP_UTF8, 0, wide_buffer.data(), -1, NULL, 0, NULL, NULL);
    if (utf8_size == 0) {
      return shift_jis_data;
    }

    std::vector<char> utf8_buffer(utf8_size);
    result = WideCharToMultiByte(CP_UTF8, 0, wide_buffer.data(), -1, utf8_buffer.data(), utf8_size, NULL, NULL);
    if (result == 0) {
      return shift_jis_data;
    }

    return std::string(utf8_buffer.data());

  } catch (const std::exception&) {
    return shift_jis_data;  // 例外発生時は元データを返す
  } catch (...) {
    return shift_jis_data;  // 例外発生時は元データを返す
  }
}

// ユーティリティ関数実装
RecordType stringToRecordType(const std::string& type_str) {
  static const std::unordered_map<std::string, RecordType> type_map = {
      {"JG", RecordType::JG}, {"RA", RecordType::RA}, {"RC", RecordType::RC}, {"SE", RecordType::SE},
      {"UM", RecordType::UM}, {"KS", RecordType::KS}, {"CH", RecordType::CH}, {"WE", RecordType::WE},
      {"WH", RecordType::WH}, {"HR", RecordType::HR}, {"H1", RecordType::H1}, {"H6", RecordType::H6},
      {"HY", RecordType::HY}, {"HC", RecordType::HC}, {"WC", RecordType::WC}, {"O1", RecordType::O1},
      {"O2", RecordType::O2}, {"O3", RecordType::O3}, {"O4", RecordType::O4}, {"O5", RecordType::O5},
      {"O6", RecordType::O6}, {"TK", RecordType::TK}, {"BT", RecordType::BT}, {"BR", RecordType::BR},
      {"BN", RecordType::BN}, {"HN", RecordType::HN}, {"SK", RecordType::SK}, {"TC", RecordType::TC},
      {"YS", RecordType::YS}, {"AV", RecordType::AV}, {"JC", RecordType::JC}, {"DM", RecordType::DM},
      {"TM", RecordType::TM}, {"WF", RecordType::WF}, {"CS", RecordType::CS}, {"CC", RecordType::CC},
      {"CK", RecordType::CK}, {"HS", RecordType::HS}};

  auto it = type_map.find(type_str);
  return (it != type_map.end()) ? it->second : RecordType::UNKNOWN;
}

std::string recordTypeToString(RecordType type) {
  switch (type) {
    case RecordType::JG:
      return "JG";
    case RecordType::RA:
      return "RA";
    case RecordType::RC:
      return "RC";
    case RecordType::SE:
      return "SE";
    case RecordType::UM:
      return "UM";
    case RecordType::KS:
      return "KS";
    case RecordType::CH:
      return "CH";
    case RecordType::WE:
      return "WE";
    case RecordType::WH:
      return "WH";
    case RecordType::HR:
      return "HR";
    case RecordType::H1:
      return "H1";
    case RecordType::H6:
      return "H6";
    case RecordType::HY:
      return "HY";
    case RecordType::HC:
      return "HC";
    case RecordType::WC:
      return "WC";
    case RecordType::O1:
      return "O1";
    case RecordType::O2:
      return "O2";
    case RecordType::O3:
      return "O3";
    case RecordType::O4:
      return "O4";
    case RecordType::O5:
      return "O5";
    case RecordType::O6:
      return "O6";
    case RecordType::TK:
      return "TK";
    case RecordType::BT:
      return "BT";
    case RecordType::BR:
      return "BR";
    case RecordType::BN:
      return "BN";
    case RecordType::HN:
      return "HN";
    case RecordType::SK:
      return "SK";
    case RecordType::TC:
      return "TC";
    case RecordType::YS:
      return "YS";
    case RecordType::AV:
      return "AV";
    case RecordType::JC:
      return "JC";
    case RecordType::DM:
      return "DM";
    case RecordType::TM:
      return "TM";
    case RecordType::WF:
      return "WF";
    case RecordType::CS:
      return "CS";
    case RecordType::CC:
      return "CC";
    case RecordType::CK:
      return "CK";
    case RecordType::HS:
      return "HS";
    default:
      return "UNKNOWN";
  }
}
