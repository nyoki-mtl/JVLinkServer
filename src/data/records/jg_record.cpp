#include "data/record_parser.h"
#include "json.hpp"

void parseJGFields(ParsedRecord& record) {
  // JG（競走馬除外情報）レコード
  // レコード長: 80バイト

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
  // 項番7: 開催回 (位置: 22, サイズ: 2)
  record.structured_data["meet_round"] = record.extractAndConvert(21, 2);
  // 項番8: 開催日目 (位置: 24, サイズ: 2)
  record.structured_data["meet_day"] = record.extractAndConvert(23, 2);
  // 項番9: レース番号 (位置: 26, サイズ: 2)
  record.structured_data["race_number"] = record.extractAndConvert(25, 2);
  // 項番10: 血統登録番号 (位置: 28, サイズ: 10)
  record.structured_data["pedigree_reg_num"] = record.extractAndConvert(27, 10);
  // 項番11: 馬名 (位置: 38, サイズ: 36)
  record.structured_data["horse_name"] = record.extractAndConvert(37, 36);
  // 項番12: 出馬投票受付順番 (位置: 74, サイズ: 3)
  record.structured_data["entry_order"] = record.extractAndConvert(73, 3);
  // 項番13: 出走区分 (位置: 77, サイズ: 1)
  record.structured_data["entry_code"] = record.extractAndConvert(76, 1);
  // 項番14: 除外状態区分 (位置: 78, サイズ: 1)
  record.structured_data["exclusion_code"] = record.extractAndConvert(77, 1);
}
