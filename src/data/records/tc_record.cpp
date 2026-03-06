#include "data/record_parser.h"
#include "json.hpp"

void parseTCFields(ParsedRecord& record) {
  // TC (発走時刻変更) レコード
  // レコード長: 45バイト

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
  // 項番11: 変更後 発走時刻 (位置: 36, サイズ: 4)
  record.structured_data["after_post_time"] = record.extractAndConvert(35, 4);
  // 項番12: 変更前 発走時刻 (位置: 40, サイズ: 4)
  record.structured_data["before_post_time"] = record.extractAndConvert(39, 4);
}
