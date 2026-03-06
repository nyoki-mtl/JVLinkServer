#include <tuple>

#include "data/record_parser.h"
#include "json.hpp"

void parseWCFields(ParsedRecord& record) {
  // WC（ウッドチップ調教）レコード
  // レコード長: 105バイト

  // 項番1-10: 基本情報
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  record.structured_data["training_center_code"] = record.extractAndConvert(11, 1);
  record.structured_data["training_date"] = record.extractAndConvert(12, 8);
  record.structured_data["training_time"] = record.extractAndConvert(20, 4);
  // 項番8: 血統登録番号 (位置: 25, サイズ: 10)
  record.structured_data["pedigree_reg_num"] = record.extractAndConvert(24, 10);
  record.structured_data["course"] = record.extractAndConvert(34, 1);
  record.structured_data["track_direction"] = record.extractAndConvert(35, 1);
  // 項番10: 予備 (位置37, 1バイト) - スキップ

  // 項番11-30: ウッドチップタイム情報
  record.structured_data["total_time_10f"] = record.extractAndConvert(37, 4);
  record.structured_data["lap_time_2000_1800"] = record.extractAndConvert(41, 3);
  record.structured_data["total_time_9f"] = record.extractAndConvert(44, 4);
  record.structured_data["lap_time_1800_1600"] = record.extractAndConvert(48, 3);
  record.structured_data["total_time_8f"] = record.extractAndConvert(51, 4);
  record.structured_data["lap_time_1600_1400"] = record.extractAndConvert(55, 3);
  record.structured_data["total_time_7f"] = record.extractAndConvert(58, 4);
  record.structured_data["lap_time_1400_1200"] = record.extractAndConvert(62, 3);
  record.structured_data["total_time_6f"] = record.extractAndConvert(65, 4);
  record.structured_data["lap_time_1200_1000"] = record.extractAndConvert(69, 3);
  record.structured_data["total_time_5f"] = record.extractAndConvert(72, 4);
  record.structured_data["lap_time_1000_800"] = record.extractAndConvert(76, 3);
  record.structured_data["total_time_4f"] = record.extractAndConvert(79, 4);
  record.structured_data["lap_time_800_600"] = record.extractAndConvert(83, 3);
  record.structured_data["total_time_3f"] = record.extractAndConvert(86, 4);
  record.structured_data["lap_time_600_400"] = record.extractAndConvert(90, 3);
  record.structured_data["total_time_2f"] = record.extractAndConvert(93, 4);
  record.structured_data["lap_time_400_200"] = record.extractAndConvert(97, 3);
  record.structured_data["lap_time_200_0"] = record.extractAndConvert(100, 3);
}
