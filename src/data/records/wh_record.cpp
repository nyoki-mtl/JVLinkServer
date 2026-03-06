#include "data/record_parser.h"
#include "json.hpp"

void parseWHFields(ParsedRecord& record) {
  // WH（馬体重）レコード
  // レコード長: 847バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 開催年 (位置: 12, サイズ: 4)
  record.structured_data["meet_year"] = record.extractAndConvert(11, 4);
  // 項番5: 開催月日 (位置: 16, サイズ: 4)
  record.structured_data["meet_date"] = record.extractAndConvert(15, 4);
  // 項番6: 競馬場コード (位置: 20, サイズ: 2)
  record.structured_data["racecourse_code"] = record.extractAndConvert(19, 2);
  // 項番7: 開催回[第N回] (位置: 22, サイズ: 2)
  record.structured_data["meet_round"] = record.extractAndConvert(21, 2);
  // 項番8: 開催日目[N日目] (位置: 24, サイズ: 2)
  record.structured_data["meet_day"] = record.extractAndConvert(23, 2);
  // 項番9: レース番号 (位置: 26, サイズ: 2)
  record.structured_data["race_number"] = record.extractAndConvert(25, 2);
  // 項番10: 発表月日時分 (位置: 28, サイズ: 8)
  record.structured_data["announcement_datetime"] = record.extractAndConvert(27, 8);
  // 項番11: 馬体重情報 (位置: 36, サイズ: 45, 繰り返し: 18)
  nlohmann::json horse_weight_data_array = nlohmann::json::array();
  for (size_t i = 0; i < 18; i++) {
    size_t base_pos = 35 + i * 45;
    nlohmann::json horse_weight_data;
    // 馬番: (位置: 1, サイズ: 2)
    horse_weight_data["horse_number"] = record.extractAndConvert(base_pos, 2);
    // 馬名: (位置: 3, サイズ: 36)
    horse_weight_data["horse_name"] = record.extractAndConvert(base_pos + 2, 36);
    // 馬体重: (位置: 39, サイズ: 3)
    horse_weight_data["horse_weight"] = record.extractAndConvert(base_pos + 38, 3);
    // 増減符号: (位置: 42, サイズ: 1)
    horse_weight_data["weight_change_sign"] = record.extractAndConvert(base_pos + 41, 1);
    // 増減差: (位置: 43, サイズ: 3)
    horse_weight_data["weight_change_diff"] = record.extractAndConvert(base_pos + 42, 3);
    horse_weight_data_array.push_back(horse_weight_data);
  }
  record.structured_data["horse_weight_infos"] = horse_weight_data_array;
}
