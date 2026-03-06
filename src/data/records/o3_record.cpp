#include "data/record_parser.h"
#include "json.hpp"

void parseO3Fields(ParsedRecord& record) {
  // O3レコード（オッズ3：ワイド）の解析
  // レコード長: 2654バイト

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
  // 項番13: 発売フラグ ワイド (位置40, 1バイト)
  record.structured_data["wide_sales_flag"] = record.extractAndConvert(39, 1);
  // 項番14: ワイドオッズ (位置41からの153組 × 17バイト = 2601バイト)
  nlohmann::json wide_odds_list = nlohmann::json::array();
  for (int i = 0; i < 153; i++) {
    size_t base_pos = 40 + (i * 17);
    nlohmann::json odds_entry;
    // 項番14a: 組番 (ブロック内位置1, 4バイト)
    odds_entry["combination"] = record.extractAndConvert(base_pos, 4);
    // 項番14b: 最低オッズ (ブロック内位置5, 5バイト)
    odds_entry["min_odds"] = record.extractAndConvert(base_pos + 4, 5);
    // 項番14c: 最高オッズ (ブロック内位置10, 5バイト)
    odds_entry["max_odds"] = record.extractAndConvert(base_pos + 9, 5);
    // 項番14d: 人気順 (ブロック内位置15, 3バイト)
    odds_entry["popularity_rank"] = record.extractAndConvert(base_pos + 14, 3);
    wide_odds_list.push_back(odds_entry);
  }
  record.structured_data["wide_odds"] = wide_odds_list;
  // 項番15: ワイド票数合計 (位置2642, 11バイト)
  record.structured_data["wide_total_votes"] = record.extractAndConvert(2641, 11);
}
