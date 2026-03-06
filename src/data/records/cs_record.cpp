#include "data/record_parser.h"
#include "json.hpp"

void parseCSFields(ParsedRecord& record) {
  // CSレコード（コース情報）
  // レコード長: 6829バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 競馬場コード (位置: 12, サイズ: 2)
  record.structured_data["racecourse_code"] = record.extractAndConvert(11, 2);
  // 項番5: 距離 (位置: 14, サイズ: 4)
  record.structured_data["distance"] = record.extractAndConvert(13, 4);
  // 項番6: トラックコード (位置: 18, サイズ: 2)
  record.structured_data["track_code"] = record.extractAndConvert(17, 2);
  // 項番7: コース改修年月日 (位置: 20, サイズ: 8)
  record.structured_data["course_revision_date"] = record.extractAndConvert(19, 8);
  // 項番8: コース説明 (位置: 28, サイズ: 6800)
  record.structured_data["course_description"] = record.extractAndConvert(27, 6800);
}
