#include "data/record_parser.h"
#include "json.hpp"

void parseWFFields(ParsedRecord& record) {
  // WFレコード（重勝式WIN5）
  // レコード長: 7215バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 開催年 (位置: 12, サイズ: 4)
  record.structured_data["meet_year"] = record.extractAndConvert(11, 4);
  // 項番5: 開催月日 (位置: 16, サイズ: 4)
  record.structured_data["meet_date"] = record.extractAndConvert(15, 4);
  // 項番6: 予備 (位置: 20, サイズ: 2) - スキップ
  // 項番7: 重勝式対象レース情報 (位置: 22, サイズ: 8, 繰り返し: 5)
  nlohmann::json target_races_list = nlohmann::json::array();
  for (int i = 0; i < 5; i++) {
    size_t base_pos = 21 + (i * 8);
    nlohmann::json target_race;
    // 7a: 競馬場コード (オフセット: 0, サイズ: 2)
    target_race["racecourse_code"] = record.extractAndConvert(base_pos + 0, 2);
    // 7b: 開催回 (オフセット: 2, サイズ: 2)
    target_race["meet_round"] = record.extractAndConvert(base_pos + 2, 2);
    // 7c: 開催日目 (オフセット: 4, サイズ: 2)
    target_race["meet_day"] = record.extractAndConvert(base_pos + 4, 2);
    // 7d: レース番号 (オフセット: 6, サイズ: 2)
    target_race["race_number"] = record.extractAndConvert(base_pos + 6, 2);
    target_races_list.push_back(target_race);
  }
  record.structured_data["target_races"] = target_races_list;

  // 項番8: 予備 (位置: 62, サイズ: 6) - スキップ
  // 項番9: 重勝式発売票数 (位置: 68, サイズ: 11)
  record.structured_data["total_tickets_sold"] = record.extractAndConvert(67, 11);
  // 項番10: 有効票数情報 (位置: 79, サイズ: 11, 繰り返し: 5)
  nlohmann::json valid_votes_list = nlohmann::json::array();
  for (int i = 0; i < 5; i++) {
    size_t base_pos = 78 + (i * 11);
    // 10a: 有効票数 (オフセット: 0, サイズ: 11)
    valid_votes_list.push_back(record.extractAndConvert(base_pos + 0, 11));
  }
  record.structured_data["valid_ticket_counts"] = valid_votes_list;
  // 項番11: 返還フラグ (位置: 134, サイズ: 1)
  record.structured_data["refund_flag"] = record.extractAndConvert(133, 1);
  // 項番12: 不成立フラグ (位置: 135, サイズ: 1)
  record.structured_data["void_flag"] = record.extractAndConvert(134, 1);
  // 項番13: 的中無フラグ (位置: 136, サイズ: 1)
  record.structured_data["no_winner_flag"] = record.extractAndConvert(135, 1);
  // 項番14: キャリーオーバー金額初期 (位置: 137, サイズ: 15)
  record.structured_data["carryover_initial"] = record.extractAndConvert(136, 15);
  // 項番15: キャリーオーバー金額残高 (位置: 152, サイズ: 15)
  record.structured_data["carryover_remaining"] = record.extractAndConvert(151, 15);
  // 項番16: 重勝式払戻情報 (位置: 167, サイズ: 29, 繰り返し: 243)
  nlohmann::json payout_info_list = nlohmann::json::array();
  for (int i = 0; i < 243; i++) {
    size_t base_pos = 166 + (i * 29);
    nlohmann::json payout_info;
    payout_info["combination"] = record.extractAndConvert(base_pos + 0, 10);
    payout_info["payout"] = record.extractAndConvert(base_pos + 10, 9);
    payout_info["winning_tickets"] = record.extractAndConvert(base_pos + 19, 10);
    payout_info_list.push_back(payout_info);
  }
  record.structured_data["payout_info"] = payout_info_list;
}
