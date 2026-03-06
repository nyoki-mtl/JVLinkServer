#include "data/record_parser.h"
#include "json.hpp"

void parseTMFields(ParsedRecord& record) {
  // TMレコード（対戦型データマイニング予想）
  // レコード長: 141バイト

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
  // 項番10: データ作成時分 (位置: 28, サイズ: 4)
  record.structured_data["data_creation_time"] = record.extractAndConvert(27, 4);

  // 項番11: マイニング予想データ (位置: 32, サイズ: 6, 繰り返し: 18)
  nlohmann::json mining_forecast_array = nlohmann::json::array();
  for (int i = 0; i < 18; i++) {
    size_t base_pos = 31 + (i * 6);
    nlohmann::json mining_forecast;
    mining_forecast["horse_number"] = record.extractAndConvert(base_pos + 0, 2);
    mining_forecast["prediction_score"] = record.extractAndConvert(base_pos + 2, 4);
    mining_forecast_array.push_back(mining_forecast);
  }
  record.structured_data["mining_predictions"] = mining_forecast_array;
}
