#include "data/record_parser.h"
#include "json.hpp"

void parseH6Fields(ParsedRecord& record) {
  // H6（三連単票数データ）レコードの解析
  // レコード長: 102890バイト

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
  // 項番10: 登録頭数 (位置28, 2バイト)
  record.structured_data["num_entries"] = record.extractAndConvert(27, 2);
  // 項番11: 出走頭数 (位置30, 2バイト)
  record.structured_data["num_starters"] = record.extractAndConvert(29, 2);
  // 項番12: 発売フラグ 3連単 (位置32, 1バイト)
  record.structured_data["trifecta_sales_flag"] = record.extractAndConvert(31, 1);
  // 項番13: 返還馬番情報(馬番01～18) (位置33, 18バイト)
  record.structured_data["refund_horse_numbers"] = record.extractAndConvert(32, 18);
  // 項番14: 三連単票数データ（位置51, 102816バイト（21バイト×4896））
  nlohmann::json trifecta_votes_per_combination = nlohmann::json::array();
  for (int i = 0; i < 4896; i++) {
    size_t base_pos = 50 + (i * 21);
    nlohmann::json vote_obj;
    vote_obj["combination"] = record.extractAndConvert(base_pos + 0, 6);
    vote_obj["votes"] = record.extractAndConvert(base_pos + 6, 11);
    vote_obj["popularity_rank"] = record.extractAndConvert(base_pos + 17, 4);
    trifecta_votes_per_combination.push_back(vote_obj);
  }
  record.structured_data["trifecta_votes"] = trifecta_votes_per_combination;
  // 項番15: 三連単票数合計 (位置102867, 11バイト)
  record.structured_data["trifecta_total_votes"] = record.extractAndConvert(102866, 11);
  // 項番16: 三連単返還票数合計 (位置102878, 11バイト)
  record.structured_data["trifecta_refund_votes"] = record.extractAndConvert(102877, 11);
}
