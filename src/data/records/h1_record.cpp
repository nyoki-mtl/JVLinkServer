#include "data/record_parser.h"
#include "json.hpp"

void parseH1Fields(ParsedRecord& record) {
  // H1（票数全賭式）レコードの解析
  // レコード長: 28955バイト

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
  // 項番12: 発売フラグ 単勝
  record.structured_data["win_sales_flag"] = record.extractAndConvert(31, 1);
  // 項番13: 発売フラグ 複勝
  record.structured_data["place_sales_flag"] = record.extractAndConvert(32, 1);
  // 項番14: 発売フラグ 枠連
  record.structured_data["bracket_quinella_sales_flag"] = record.extractAndConvert(33, 1);
  // 項番15: 発売フラグ 馬連
  record.structured_data["quinella_sales_flag"] = record.extractAndConvert(34, 1);
  // 項番16: 発売フラグ ワイド
  record.structured_data["wide_sales_flag"] = record.extractAndConvert(35, 1);
  // 項番17: 発売フラグ 馬単
  record.structured_data["exacta_sales_flag"] = record.extractAndConvert(36, 1);
  // 項番18: 発売フラグ 3連複
  record.structured_data["trio_sales_flag"] = record.extractAndConvert(37, 1);
  // 項番19: 複勝着払キー (位置39, 1バイト)
  record.structured_data["place_payout_key"] = record.extractAndConvert(38, 1);
  // 項番20: 返還馬番情報(馬番01～28) (位置40, 28バイト)
  record.structured_data["refund_horse_numbers"] = record.extractAndConvert(39, 28);
  // 項番21: 返還枠番情報(枠番1～8) (位置68, 8バイト)
  record.structured_data["refund_bracket_numbers"] = record.extractAndConvert(67, 8);
  // 項番22: 返還同枠情報(枠番1～8) (位置76, 8バイト)
  record.structured_data["refund_same_bracket"] = record.extractAndConvert(75, 8);
  // 項番23: 単勝票数 (位置84, 420バイト(15バイト×28))
  nlohmann::json win_voting_list = nlohmann::json::array();
  for (int i = 0; i < 28; i++) {
    size_t base_pos = 83 + (i * 15);
    nlohmann::json vote_obj;
    vote_obj["horse_number"] = record.extractAndConvert(base_pos + 0, 2);
    vote_obj["votes"] = record.extractAndConvert(base_pos + 2, 11);
    vote_obj["popularity_rank"] = record.extractAndConvert(base_pos + 13, 2);
    win_voting_list.push_back(vote_obj);
  }
  record.structured_data["win_votes"] = win_voting_list;
  // 項番24: 複勝票数 (位置504, 420バイト(15バイト×28))
  nlohmann::json place_voting_list = nlohmann::json::array();
  for (int i = 0; i < 28; i++) {
    size_t base_pos = 503 + (i * 15);
    nlohmann::json vote_obj;
    vote_obj["horse_number"] = record.extractAndConvert(base_pos + 0, 2);
    vote_obj["votes"] = record.extractAndConvert(base_pos + 2, 11);
    vote_obj["popularity_rank"] = record.extractAndConvert(base_pos + 13, 2);
    place_voting_list.push_back(vote_obj);
  }
  record.structured_data["place_votes"] = place_voting_list;
  // 項番25: 枠連票数 (位置924, 540バイト(15バイト×36))
  nlohmann::json bracket_quinella_voting_list = nlohmann::json::array();
  for (int i = 0; i < 36; i++) {
    size_t base_pos = 923 + (i * 15);
    nlohmann::json vote_obj;
    vote_obj["combination"] = record.extractAndConvert(base_pos + 0, 2);
    vote_obj["votes"] = record.extractAndConvert(base_pos + 2, 11);
    vote_obj["popularity_rank"] = record.extractAndConvert(base_pos + 13, 2);
    bracket_quinella_voting_list.push_back(vote_obj);
  }
  record.structured_data["bracket_quinella_votes"] = bracket_quinella_voting_list;
  // 項番26: 馬連票数 (位置1464, 2754バイト(18バイト×153))
  nlohmann::json quinella_voting_list = nlohmann::json::array();
  for (int i = 0; i < 153; i++) {
    size_t base_pos = 1463 + (i * 18);
    nlohmann::json vote_obj;
    vote_obj["combination"] = record.extractAndConvert(base_pos + 0, 4);
    vote_obj["votes"] = record.extractAndConvert(base_pos + 4, 11);
    vote_obj["popularity_rank"] = record.extractAndConvert(base_pos + 15, 3);
    quinella_voting_list.push_back(vote_obj);
  }
  record.structured_data["quinella_votes"] = quinella_voting_list;
  // 項番27: ワイド票数 (位置4218, 2754バイト(18バイト×153))
  nlohmann::json wide_voting_list = nlohmann::json::array();
  for (int i = 0; i < 153; i++) {
    size_t base_pos = 4217 + (i * 18);
    nlohmann::json vote_obj;
    vote_obj["combination"] = record.extractAndConvert(base_pos + 0, 4);
    vote_obj["votes"] = record.extractAndConvert(base_pos + 4, 11);
    vote_obj["popularity_rank"] = record.extractAndConvert(base_pos + 15, 3);
    wide_voting_list.push_back(vote_obj);
  }
  record.structured_data["wide_votes"] = wide_voting_list;
  // 項番28: 馬単票数 (位置6972, 5508バイト(18バイト×306))
  nlohmann::json exacta_voting_list = nlohmann::json::array();
  for (int i = 0; i < 306; i++) {
    size_t base_pos = 6971 + (i * 18);
    nlohmann::json vote_obj;
    vote_obj["combination"] = record.extractAndConvert(base_pos + 0, 4);
    vote_obj["votes"] = record.extractAndConvert(base_pos + 4, 11);
    vote_obj["popularity_rank"] = record.extractAndConvert(base_pos + 15, 3);
    exacta_voting_list.push_back(vote_obj);
  }
  record.structured_data["exacta_votes"] = exacta_voting_list;
  // 項番29: 3連複票数 (位置12480, 16320バイト(20バイト×816))
  nlohmann::json trio_voting_list = nlohmann::json::array();
  for (int i = 0; i < 816; i++) {
    size_t base_pos = 12479 + (i * 20);
    nlohmann::json vote_obj;
    vote_obj["combination"] = record.extractAndConvert(base_pos + 0, 6);
    vote_obj["votes"] = record.extractAndConvert(base_pos + 6, 11);
    vote_obj["popularity_rank"] = record.extractAndConvert(base_pos + 17, 3);
    trio_voting_list.push_back(vote_obj);
  }
  record.structured_data["trio_votes"] = trio_voting_list;
  // 項番30: 単勝票数合計 (位置28800, 11バイト)
  record.structured_data["win_total_votes"] = record.extractAndConvert(28799, 11);
  // 項番31: 複勝票数合計 (位置28811, 11バイト)
  record.structured_data["place_total_votes"] = record.extractAndConvert(28810, 11);
  // 項番32: 枠連票数合計 (位置28822, 11バイト)
  record.structured_data["bracket_quinella_total_votes"] = record.extractAndConvert(28821, 11);
  // 項番33: 馬連票数合計 (位置28833, 11バイト)
  record.structured_data["quinella_total_votes"] = record.extractAndConvert(28832, 11);
  // 項番34: ワイド票数合計 (位置28844, 11バイト)
  record.structured_data["wide_total_votes"] = record.extractAndConvert(28843, 11);
  // 項番35: 馬単票数合計 (位置28855, 11バイト)
  record.structured_data["exacta_total_votes"] = record.extractAndConvert(28854, 11);
  // 項番36: 3連複票数合計 (位置28866, 11バイト)
  record.structured_data["trio_total_votes"] = record.extractAndConvert(28865, 11);
  // 項番37: 単勝返還票数合計 (位置28877, 11バイト)
  record.structured_data["win_refund_votes"] = record.extractAndConvert(28876, 11);
  // 項番38: 複勝返還票数合計 (位置28888, 11バイト)
  record.structured_data["place_refund_votes"] = record.extractAndConvert(28887, 11);
  // 項番39: 枠連返還票数合計 (位置28899, 11バイト)
  record.structured_data["bracket_quinella_refund_votes"] = record.extractAndConvert(28898, 11);
  // 項番40: 馬連返還票数合計 (位置28910, 11バイト)
  record.structured_data["quinella_refund_votes"] = record.extractAndConvert(28909, 11);
  // 項番41: ワイド返還票数合計 (位置28921, 11バイト)
  record.structured_data["wide_refund_votes"] = record.extractAndConvert(28920, 11);
  // 項番42: 馬単返還票数合計 (位置28932, 11バイト)
  record.structured_data["exacta_refund_votes"] = record.extractAndConvert(28931, 11);
  // 項番43: 3連複返還票数合計 (位置28943, 11バイト)
  record.structured_data["trio_refund_votes"] = record.extractAndConvert(28942, 11);
}
