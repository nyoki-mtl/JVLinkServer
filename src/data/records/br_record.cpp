#include "data/record_parser.h"
#include "json.hpp"

void parseBRFields(ParsedRecord& record) {
  // BRレコード（生産者マスタ）
  // レコード長: 545バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 生産者コード (位置: 12, サイズ: 8)
  record.structured_data["breeder_code"] = record.extractAndConvert(11, 8);
  // 項番5: 生産者名(法人格有) (位置: 20, サイズ: 72)
  record.structured_data["breeder_name_with_corp"] = record.extractAndConvert(19, 72);
  // 項番6: 生産者名(法人格無) (位置: 92, サイズ: 72)
  record.structured_data["breeder_name"] = record.extractAndConvert(91, 72);
  // 項番7: 生産者名半角カナ (位置: 164, サイズ: 72)
  record.structured_data["breeder_name_kana"] = record.extractAndConvert(163, 72);
  // 項番8: 生産者名欧字 (位置: 236, サイズ: 168)
  record.structured_data["breeder_name_english"] = record.extractAndConvert(235, 168);
  // 項番9: 生産者住所自治省名 (位置: 404, サイズ: 20)
  record.structured_data["address"] = record.extractAndConvert(403, 20);
  // 項番10: 本年・累計成績情報 (位置: 424, サイズ: 60, 繰り返し: 2)
  nlohmann::json performance_stats_array = nlohmann::json::array();
  for (int i = 0; i < 2; i++) {
    size_t base_pos = 423 + i * 60;
    nlohmann::json performance_stat;
    // 10a: 設定年 (オフセット: 0, サイズ: 4)
    performance_stat["year"] = record.extractAndConvert(base_pos, 4);
    // 10b: 本賞金合計 (オフセット: 4, サイズ: 10)
    performance_stat["prize_money"] = record.extractAndConvert(base_pos + 4, 10);
    // 10c: 付加賞金合計 (オフセット: 14, サイズ: 10)
    performance_stat["added_money"] = record.extractAndConvert(base_pos + 14, 10);
    // 10d: 着回数 (オフセット: 24, サイズ: 36)
    performance_stat["placing_counts"] = record.extractAndConvertArray(base_pos + 24, 6, 6);
    performance_stats_array.push_back(performance_stat);
  }
  record.structured_data["performance_stats"] = performance_stats_array;
}
