#include "data/record_parser.h"
#include "json.hpp"

void parseO2Fields(ParsedRecord& record) {
  // O2レコード（オッズ2：馬連）の解析
  // レコード長: 2042バイト

  // 項番2: データ区分 (位置3, 1バイト)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置4, 8バイト)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 開催年 (位置12, 4バイト)
  record.structured_data["meet_year"] = record.extractAndConvert(11, 4);
  // 項番5: 開催月日 (位置16, 4バイト)
  record.structured_data["meet_date"] = record.extractAndConvert(15, 4);
  // 項番6: 競馬場コード (位置20, 2バイト)
  record.structured_data["racecourse_code"] = record.extractAndConvert(19, 2);
  // 項番7: 開催回 (位置22, 2バイト)
  record.structured_data["meet_round"] = record.extractAndConvert(21, 2);
  // 項番8: 開催日目 (位置24, 2バイト)
  record.structured_data["meet_day"] = record.extractAndConvert(23, 2);
  // 項番9: レース番号 (位置26, 2バイト)
  record.structured_data["race_number"] = record.extractAndConvert(25, 2);
  // 項番10: 発表月日時分 (位置28, 8バイト)
  record.structured_data["announcement_datetime"] = record.extractAndConvert(27, 8);
  // 項番11: 登録頭数 (位置36, 2バイト)
  record.structured_data["num_entries"] = record.extractAndConvert(35, 2);
  // 項番12: 出走頭数 (位置38, 2バイト)
  record.structured_data["num_starters"] = record.extractAndConvert(37, 2);
  // 項番13: 発売フラグ 馬連 (位置40, 1バイト)
  record.structured_data["quinella_sales_flag"] = record.extractAndConvert(39, 1);
  // 項番14: 馬連オッズ (位置41からの153組 × 13バイト = 1989バイト)
  nlohmann::json quinella_odds_list = nlohmann::json::array();
  for (int i = 0; i < 153; i++) {
    size_t base_pos = 40 + (i * 13);
    nlohmann::json odds_obj;
    odds_obj["combination"] = record.extractAndConvert(base_pos + 0, 4);
    odds_obj["odds"] = record.extractAndConvert(base_pos + 4, 6);
    odds_obj["popularity_rank"] = record.extractAndConvert(base_pos + 10, 3);
    quinella_odds_list.push_back(odds_obj);
  }
  record.structured_data["quinella_odds"] = quinella_odds_list;
  // 項番15: 馬連票数合計 (位置2030, 11バイト)
  record.structured_data["quinella_total_votes"] = record.extractAndConvert(2029, 11);
}
