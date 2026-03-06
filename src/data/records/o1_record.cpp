#include "data/record_parser.h"
#include "json.hpp"

void parseO1Fields(ParsedRecord& record) {
  // O1レコード（オッズ1：単複枠）の解析
  // レコード長: 962バイト

  // 項番2: データ区分 (位置3, 1バイト)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置4, 8バイト)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 開催年 (位置12, 4バイト)
  record.structured_data["meet_year"] = record.extractAndConvert(11, 4);
  // 項番5: 開催月日 (位置16, 4バイト)
  record.structured_data["meet_date"] = record.extractAndConvert(15, 4);
  // 項番6: 競馬場コード (位置20, 2バイト)
  record.structured_data["racecourse_code"] = record.extractAndConvert(19, 2);
  // 項番7: 開催回 (位置22, 2バイト)
  record.structured_data["meet_round"] = record.extractAndConvert(21, 2);
  // 項番8: 開催日目 (位置24, 2バイト)
  record.structured_data["meet_day"] = record.extractAndConvert(23, 2);
  // 項番9: レース番号 (位置26, 2バイト)
  record.structured_data["race_number"] = record.extractAndConvert(25, 2);
  // 項番10: 発表月日時分 (位置28, 8バイト)
  record.structured_data["announcement_datetime"] = record.extractAndConvert(27, 8);
  // 項番11: 登録頭数 (位置36, 2バイト)
  record.structured_data["num_entries"] = record.extractAndConvert(35, 2);
  // 項番12: 出走頭数 (位置38, 2バイト)
  record.structured_data["num_starters"] = record.extractAndConvert(37, 2);
  // 項番13: 発売フラグ 単勝 (位置40, 1バイト)
  record.structured_data["win_sales_flag"] = record.extractAndConvert(39, 1);
  // 項番14: 発売フラグ 複勝 (位置41, 1バイト)
  record.structured_data["place_sales_flag"] = record.extractAndConvert(40, 1);
  // 項番15: 発売フラグ 枠連 (位置42, 1バイト)
  record.structured_data["bracket_quinella_sales_flag"] = record.extractAndConvert(41, 1);
  // 項番16: 複勝着払キー (位置43, 1バイト)
  record.structured_data["place_payout_key"] = record.extractAndConvert(42, 1);
  // 項番17: 単勝オッズ (位置44からの28頭 × 8バイト = 224バイト)
  nlohmann::json win_odds_list = nlohmann::json::array();
  for (int i = 0; i < 28; i++) {
    size_t base_pos = 43 + (i * 8);
    nlohmann::json odds_obj;
    odds_obj["horse_number"] = record.extractAndConvert(base_pos + 0, 2);
    odds_obj["odds"] = record.extractAndConvert(base_pos + 2, 4);
    odds_obj["popularity_rank"] = record.extractAndConvert(base_pos + 6, 2);
    win_odds_list.push_back(odds_obj);
  }
  record.structured_data["win_odds"] = win_odds_list;
  // 項番18: 複勝オッズ (位置268からの28頭 × 12バイト = 336バイト)
  nlohmann::json place_odds_list = nlohmann::json::array();
  for (int i = 0; i < 28; i++) {
    size_t base_pos = 267 + (i * 12);
    nlohmann::json odds_obj;
    odds_obj["horse_number"] = record.extractAndConvert(base_pos + 0, 2);
    odds_obj["min_odds"] = record.extractAndConvert(base_pos + 2, 4);
    odds_obj["max_odds"] = record.extractAndConvert(base_pos + 6, 4);
    odds_obj["popularity_rank"] = record.extractAndConvert(base_pos + 10, 2);
    place_odds_list.push_back(odds_obj);
  }
  record.structured_data["place_odds"] = place_odds_list;
  // 項番19: 枠連オッズ (位置604からの36組 × 9バイト = 324バイト)
  nlohmann::json bracket_quinella_odds_list = nlohmann::json::array();
  for (int i = 0; i < 36; i++) {
    size_t base_pos = 603 + (i * 9);
    nlohmann::json odds_obj;
    odds_obj["combination"] = record.extractAndConvert(base_pos + 0, 2);
    odds_obj["odds"] = record.extractAndConvert(base_pos + 2, 5);
    odds_obj["popularity_rank"] = record.extractAndConvert(base_pos + 7, 2);
    bracket_quinella_odds_list.push_back(odds_obj);
  }
  record.structured_data["bracket_quinella_odds"] = bracket_quinella_odds_list;
  // 項番20: 単勝票数合計 (位置928, 11バイト)
  record.structured_data["win_total_votes"] = record.extractAndConvert(927, 11);
  // 項番21: 複勝票数合計 (位置939, 11バイト)
  record.structured_data["place_total_votes"] = record.extractAndConvert(938, 11);
  // 項番22: 枠連票数合計 (位置950, 11バイト)
  record.structured_data["bracket_quinella_total_votes"] = record.extractAndConvert(949, 11);
}
