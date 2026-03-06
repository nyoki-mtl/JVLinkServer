#include "data/record_parser.h"
#include "json.hpp"

void parseHCFields(ParsedRecord& record) {
  // HCレコード（坂路調教）
  // レコード長: 60バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: トレセン区分 (位置: 12, サイズ: 1)
  record.structured_data["training_center_code"] = record.extractAndConvert(11, 1);
  // 項番5: 調教年月日 (位置: 13, サイズ: 8)
  record.structured_data["training_date"] = record.extractAndConvert(12, 8);
  // 項番6: 調教時刻 (位置: 21, サイズ: 4)
  record.structured_data["training_time"] = record.extractAndConvert(20, 4);
  // 項番7: 血統登録番号 (位置: 25, サイズ: 10)
  record.structured_data["pedigree_reg_num"] = record.extractAndConvert(24, 10);
  // 項番8: 4ハロンタイム合計(800M～0M) (位置: 35, サイズ: 4)
  record.structured_data["total_time_4f"] = record.extractAndConvert(34, 4);
  // 項番9: ラップタイム(800M～600M) (位置: 39, サイズ: 3)
  record.structured_data["lap_time_800_600"] = record.extractAndConvert(38, 3);
  // 項番10: 3ハロンタイム合計(600M～0M) (位置: 42, サイズ: 4)
  record.structured_data["total_time_3f"] = record.extractAndConvert(41, 4);
  // 項番11: ラップタイム(600M～400M) (位置: 46, サイズ: 3)
  record.structured_data["lap_time_600_400"] = record.extractAndConvert(45, 3);
  // 項番12: 2ハロンタイム合計(400M～0M) (位置: 49, サイズ: 4)
  record.structured_data["total_time_2f"] = record.extractAndConvert(48, 4);
  // 項番13: ラップタイム(400M～200M) (位置: 53, サイズ: 3)
  record.structured_data["lap_time_400_200"] = record.extractAndConvert(52, 3);
  // 項番14: ラップタイム(200M～0M) (位置: 56, サイズ: 3)
  record.structured_data["lap_time_200_0"] = record.extractAndConvert(55, 3);
}
