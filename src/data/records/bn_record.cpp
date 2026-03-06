#include "data/record_parser.h"
#include "json.hpp"

void parseBNFields(ParsedRecord& record) {
  // BNレコード（馬主マスタ）
  // レコード長: 477バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 馬主コード (位置: 12, サイズ: 6)
  record.structured_data["owner_code"] = record.extractAndConvert(11, 6);
  // 項番5: 馬主名(法人格有) (位置: 18, サイズ: 64)
  record.structured_data["owner_name_with_corp"] = record.extractAndConvert(17, 64);
  // 項番6: 馬主名(法人格無) (位置: 82, サイズ: 64)
  record.structured_data["owner_name"] = record.extractAndConvert(81, 64);
  // 項番7: 馬主名半角カナ (位置: 146, サイズ: 50)
  record.structured_data["owner_name_kana"] = record.extractAndConvert(145, 50);
  // 項番8: 馬主名欧字 (位置: 196, サイズ: 100)
  record.structured_data["owner_name_english"] = record.extractAndConvert(195, 100);
  // 項番9: 服色標示 (位置: 296, サイズ: 60)
  record.structured_data["silk_colors_code"] = record.extractAndConvert(295, 60);
  // 項番10: 本年・累計成績情報 (位置: 356, サイズ: 60, 繰り返し: 2)
  nlohmann::json performance_stats_array = nlohmann::json::array();
  for (int i = 0; i < 2; i++) {
    size_t base_pos = 355 + i * 60;
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
