#include "data/record_parser.h"
#include "json.hpp"

void parseYSFields(ParsedRecord& record) {
  // YSレコード（開催スケジュール）
  // レコード長: 382バイト

  // 項番2: データ区分 (位置:3, バイト:1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置:4, バイト:8) - yyyymmdd
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 開催年 (位置:12, バイト:4) - キー項目, yyyy
  record.structured_data["meet_year"] = record.extractAndConvert(11, 4);
  // 項番5: 開催月日 (位置:16, バイト:4) - キー項目, mmdd
  record.structured_data["meet_date"] = record.extractAndConvert(15, 4);
  // 項番6: 競馬場コード (位置:20, バイト:2) - キー項目, コード表 2001.競馬場コード参照
  record.structured_data["racecourse_code"] = record.extractAndConvert(19, 2);
  // 項番7: 開催回[第N回] (位置:22, バイト:2) - キー項目
  record.structured_data["meet_round"] = record.extractAndConvert(21, 2);
  // 項番8: 開催日目[N日目] (位置:24, バイト:2) - キー項目
  record.structured_data["meet_day"] = record.extractAndConvert(23, 2);
  // 項番9: 曜日コード (位置:26, バイト:1) - コード表 2002.曜日コード参照
  record.structured_data["weekday_code"] = record.extractAndConvert(25, 1);
  // 項番10: <重賞案内> (位置:27, バイト:354, 118バイト * 3ブロック)
  nlohmann::json featured_races_array = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 26 + (i * 118);  // 0ベース位置
    nlohmann::json featured_race;
    featured_race["special_race_number"] = record.extractAndConvert(base_pos + 0, 4);
    featured_race["race_name_main"] = record.extractAndConvert(base_pos + 4, 60);
    featured_race["race_short_name_10"] = record.extractAndConvert(base_pos + 64, 20);
    featured_race["race_short_name_6"] = record.extractAndConvert(base_pos + 84, 12);
    featured_race["race_short_name_3"] = record.extractAndConvert(base_pos + 96, 6);
    featured_race["graded_race_round_number"] = record.extractAndConvert(base_pos + 102, 3);
    featured_race["grade_code"] = record.extractAndConvert(base_pos + 105, 1);
    featured_race["race_type_code"] = record.extractAndConvert(base_pos + 106, 2);
    featured_race["race_symbol_code"] = record.extractAndConvert(base_pos + 108, 3);
    featured_race["weight_type_code"] = record.extractAndConvert(base_pos + 111, 1);
    featured_race["distance"] = record.extractAndConvert(base_pos + 112, 4);
    featured_race["track_code"] = record.extractAndConvert(base_pos + 116, 2);
    featured_races_array.push_back(featured_race);
  }
  record.structured_data["graded_race_guide"] = featured_races_array;
}
