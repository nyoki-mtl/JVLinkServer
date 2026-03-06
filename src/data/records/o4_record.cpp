#include "data/record_parser.h"
#include "json.hpp"

void parseO4Fields(ParsedRecord& record) {
  // O4レコード（オッズ4：馬単）の解析
  // レコード長: 4031バイト

  // 項番2: データ区分 (位置:3, バイト:1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置:4, バイト:8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 開催年 (位置:12, バイト:4)
  record.structured_data["meet_year"] = record.extractAndConvert(11, 4);
  // 項番5: 開催月日 (位置:16, バイト:4)
  record.structured_data["meet_date"] = record.extractAndConvert(15, 4);
  // 項番6: 競馬場コード (位置:20, バイト:2)
  record.structured_data["racecourse_code"] = record.extractAndConvert(19, 2);
  // 項番7: 開催回 (位置:22, バイト:2)
  record.structured_data["meet_round"] = record.extractAndConvert(21, 2);
  // 項番8: 開催日目 (位置:24, バイト:2)
  record.structured_data["meet_day"] = record.extractAndConvert(23, 2);
  // 項番9: レース番号 (位置:26, バイト:2)
  record.structured_data["race_number"] = record.extractAndConvert(25, 2);
  // 項番10: 発表月日時分 (位置:28, バイト:8)
  record.structured_data["announcement_datetime"] = record.extractAndConvert(27, 8);
  // 項番11: 登録頭数 (位置:36, バイト:2)
  record.structured_data["num_entries"] = record.extractAndConvert(35, 2);
  // 項番12: 出走頭数 (位置:38, バイト:2)
  record.structured_data["num_starters"] = record.extractAndConvert(37, 2);
  // 項番13: 発売フラグ（馬単）(位置:40, バイト:1)
  record.structured_data["exacta_sales_flag"] = record.extractAndConvert(39, 1);
  // 項番14: 馬単オッズ（位置:41, 3978バイト(13バイト×306組)）
  nlohmann::json exacta_odds_array = nlohmann::json::array();
  for (int i = 0; i < 306; i++) {
    size_t base_pos = 40 + (i * 13);
    nlohmann::json odds_entry;
    // 項番14a: 組番 (ブロック内位置1, 4バイト)
    odds_entry["combination"] = record.extractAndConvert(base_pos, 4);
    // 項番14b: オッズ (ブロック内位置5, 6バイト)
    odds_entry["odds"] = record.extractAndConvert(base_pos + 4, 6);
    // 項番14c: 人気順 (ブロック内位置11, 3バイト)
    odds_entry["popularity_rank"] = record.extractAndConvert(base_pos + 10, 3);
    exacta_odds_array.push_back(odds_entry);
  }
  record.structured_data["exacta_odds"] = exacta_odds_array;
  // 項番15: 馬単票数合計（位置:4019, バイト:11）
  record.structured_data["exacta_total_votes"] = record.extractAndConvert(4018, 11);
}
