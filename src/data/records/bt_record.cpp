#include "data/record_parser.h"
#include "json.hpp"

void parseBTFields(ParsedRecord& record) {
  // BTレコード（系統情報）
  // レコード長: 6889バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 繁殖登録番号 (位置: 12, サイズ: 10)
  record.structured_data["breeding_reg_num"] = record.extractAndConvert(11, 10);
  // 項番5: 系統ID (位置: 22, サイズ: 30)
  record.structured_data["lineage_id"] = record.extractAndConvert(21, 30);
  // 項番6: 系統名 (位置: 52, サイズ: 36)
  record.structured_data["lineage_name"] = record.extractAndConvert(51, 36);
  // 項番7: 系統説明 (位置: 88, サイズ: 6800)
  record.structured_data["lineage_description"] = record.extractAndConvert(87, 6800);
}
