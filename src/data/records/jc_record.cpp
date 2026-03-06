#include "data/record_parser.h"
#include "json.hpp"

void parseJCFields(ParsedRecord& record) {
  // JC (騎手変更) レコード
  // レコード長: 161バイト

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
  // 項番9: レース番号 (位置: 26, サイズ: 2)
  record.structured_data["race_number"] = record.extractAndConvert(25, 2);
  // 項番10: 発表月日時分 (位置: 28, サイズ: 8)
  record.structured_data["announcement_datetime"] = record.extractAndConvert(27, 8);
  // 項番11: 馬番 (位置: 36, サイズ: 2)
  record.structured_data["horse_number"] = record.extractAndConvert(35, 2);
  // 項番12: 馬名 (位置: 38, サイズ: 36)
  record.structured_data["horse_name"] = record.extractAndConvert(37, 36);

  // 変更後騎手情報
  // 項番13: 変更後負担重量 (位置: 74, 3バイト) 単位:0.1kg
  record.structured_data["after_weight_carried"] = record.extractAndConvert(73, 3);
  // 項番14: 変更後騎手コード (位置: 77, 5バイト)
  record.structured_data["after_jockey_code"] = record.extractAndConvert(76, 5);
  // 項番15: 変更後騎手名 (位置: 82, 34バイト) 全角17文字
  record.structured_data["after_jockey_name"] = record.extractAndConvert(81, 34);
  // 項番16: 変更後騎手見習コード (位置: 116, 1バイト)
  record.structured_data["after_apprentice_code"] = record.extractAndConvert(115, 1);

  // 変更前騎手情報
  // 項番17: 変更前負担重量 (位置: 117, 3バイト) 単位:0.1kg
  record.structured_data["before_weight_carried"] = record.extractAndConvert(116, 3);
  // 項番18: 変更前騎手コード (位置: 120, 5バイト)
  record.structured_data["before_jockey_code"] = record.extractAndConvert(119, 5);
  // 項番19: 変更前騎手名 (位置: 125, 34バイト) 全角17文字
  record.structured_data["before_jockey_name"] = record.extractAndConvert(124, 34);
  // 項番20: 変更前騎手見習コード (位置: 159, 1バイト)
  record.structured_data["before_apprentice_code"] = record.extractAndConvert(158, 1);
}
