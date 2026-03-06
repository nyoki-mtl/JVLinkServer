#include "data/record_parser.h"
#include "json.hpp"

void parseWEFields(ParsedRecord& record) {
  // WE（天候馬場状態）レコード
  // レコード長: 42バイト

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
  // 項番9: 発表月日時分 (位置: 26, サイズ: 8)
  record.structured_data["announcement_datetime"] = record.extractAndConvert(25, 8);
  // 項番10: 変更識別 (位置: 34, サイズ: 1)
  record.structured_data["change_identifier"] = record.extractAndConvert(33, 1);
  // 項番11: 天候状態（現在） (位置: 35, サイズ: 1) <コード表 2003.天候コード>参照
  record.structured_data["weather_code"] = record.extractAndConvert(34, 1);
  // 項番12: 馬場状態・芝（現在） (位置: 36, サイズ: 1) <コード表 2010.馬場状態コード>参照
  record.structured_data["turf_track_condition_code"] = record.extractAndConvert(35, 1);
  // 項番13: 馬場状態・ダート（現在） (位置: 37, サイズ: 1) <コード表 2010.馬場状態コード>参照
  record.structured_data["dirt_track_condition_code"] = record.extractAndConvert(36, 1);
  // 項番14: 天候状態（変更前） (位置: 38, サイズ: 1) <コード表 2003.天候コード>参照
  record.structured_data["before_weather_code"] = record.extractAndConvert(37, 1);
  // 項番15: 馬場状態・芝（変更前） (位置: 39, サイズ: 1) <コード表 2010.馬場状態コード>参照
  record.structured_data["before_turf_track_condition_code"] = record.extractAndConvert(38, 1);
  // 項番16: 馬場状態・ダート（変更前） (位置: 40, サイズ: 1) <コード表 2010.馬場状態コード>参照
  record.structured_data["before_dirt_track_condition_code"] = record.extractAndConvert(39, 1);
}
