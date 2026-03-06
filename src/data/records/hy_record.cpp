#include "data/record_parser.h"
#include "json.hpp"

void parseHYFields(ParsedRecord& record) {
  // HY（馬名の意味由来）レコード
  // レコード長: 123バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 血統登録番号 (位置: 12, サイズ: 10)
  record.structured_data["pedigree_reg_num"] = record.extractAndConvert(11, 10);
  // 項番5: 馬名 (位置: 22, サイズ: 36)
  record.structured_data["horse_name"] = record.extractAndConvert(21, 36);
  // 項番6: 馬名の意味由来 (位置: 58, サイズ: 64)
  record.structured_data["horse_name_meaning"] = record.extractAndConvert(57, 64);
}
