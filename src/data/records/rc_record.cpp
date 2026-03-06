#include "data/record_parser.h"
#include "json.hpp"

void parseRCFields(ParsedRecord& record) {
  // RCレコード（レコードマスタ）の完全実装
  // レコード長: 501バイト

  // 項番2: データ区分 (位置3, 1バイト)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置4, 8バイト)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: レコード識別区分 (位置12, 1バイト)
  record.structured_data["record_identification_code"] = record.extractAndConvert(11, 1);
  // 項番5: 開催年 (位置13, 4バイト)
  record.structured_data["meet_year"] = record.extractAndConvert(12, 4);
  // 項番6: 開催月日 (位置17, 4バイト)
  record.structured_data["meet_date"] = record.extractAndConvert(16, 4);
  // 項番7: 競馬場コード (位置21, 2バイト)
  record.structured_data["racecourse_code"] = record.extractAndConvert(20, 2);
  // 項番8: 開催回[第N回] (位置23, 2バイト)
  record.structured_data["meet_round"] = record.extractAndConvert(22, 2);
  // 項番9: 開催日目[N日目] (位置25, 2バイト)
  record.structured_data["meet_day"] = record.extractAndConvert(24, 2);
  // 項番10: レース番号 (位置27, 2バイト)
  record.structured_data["race_number"] = record.extractAndConvert(26, 2);
  // 項番11: 特別競走番号 (位置29, 4バイト)
  record.structured_data["special_race_number"] = record.extractAndConvert(28, 4);
  // 項番12: 競走名本題 (位置33, 60バイト)
  record.structured_data["race_name_main"] = record.extractAndConvert(32, 60);
  // 項番13: グレードコード (位置93, 1バイト)
  record.structured_data["grade_code"] = record.extractAndConvert(92, 1);
  // 項番14: 競走種別コード (位置94, 2バイト)
  record.structured_data["race_type_code"] = record.extractAndConvert(93, 2);
  // 項番15: 距離 (位置96, 4バイト)
  record.structured_data["distance"] = record.extractAndConvert(95, 4);
  // 項番16: トラックコード (位置100, 2バイト)
  record.structured_data["track_code"] = record.extractAndConvert(99, 2);
  // 項番17: レコード区分 (位置102, 1バイト)
  record.structured_data["record_type_code"] = record.extractAndConvert(101, 1);
  // 項番18: レコードタイム (位置103, 4バイト)
  record.structured_data["record_time"] = record.extractAndConvert(102, 4);
  // 項番19: 天候コード (位置107, 1バイト)
  record.structured_data["weather_code"] = record.extractAndConvert(106, 1);
  // 項番20: 芝馬場状態コード (位置108, 1バイト)
  record.structured_data["turf_track_condition_code"] = record.extractAndConvert(107, 1);
  // 項番21: ダート馬場状態コード (位置109, 1バイト)
  record.structured_data["dirt_track_condition_code"] = record.extractAndConvert(108, 1);
  // 項番22: レコード保持馬情報 (位置: 110, サイズ: 130, 繰り返し: 3)
  nlohmann::json record_horses_array = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 109 + i * 130;  // 各130バイト
    nlohmann::json record_horse;
    record_horse["pedigree_reg_num"] = record.extractAndConvert(base_pos + 0, 10);
    record_horse["horse_name"] = record.extractAndConvert(base_pos + 10, 36);
    record_horse["horse_symbol_code"] = record.extractAndConvert(base_pos + 46, 2);
    record_horse["sex_code"] = record.extractAndConvert(base_pos + 48, 1);
    record_horse["trainer_code"] = record.extractAndConvert(base_pos + 49, 5);
    record_horse["trainer_name"] = record.extractAndConvert(base_pos + 54, 34);
    record_horse["impost_weight"] = record.extractAndConvert(base_pos + 88, 3);
    record_horse["jockey_code"] = record.extractAndConvert(base_pos + 91, 5);
    record_horse["jockey_name"] = record.extractAndConvert(base_pos + 96, 34);
    record_horses_array.push_back(record_horse);
  }
  record.structured_data["record_holders"] = record_horses_array;
}
