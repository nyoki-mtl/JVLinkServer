#include "data/record_parser.h"
#include "json.hpp"

void parseHRFields(ParsedRecord& record) {
  // HR（払戻）レコードの解析
  // レコード長: 719バイト

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
  // 項番12: 不成立フラグ 単勝 (位置32, 1バイト)
  record.structured_data["win_cancelled_flag"] = record.extractAndConvert(31, 1);
  // 項番13: 不成立フラグ 複勝 (位置33, 1バイト)
  record.structured_data["place_cancelled_flag"] = record.extractAndConvert(32, 1);
  // 項番14: 不成立フラグ 枠連 (位置34, 1バイト)
  record.structured_data["bracket_quinella_cancelled_flag"] = record.extractAndConvert(33, 1);
  // 項番15: 不成立フラグ 馬連 (位置35, 1バイト)
  record.structured_data["quinella_cancelled_flag"] = record.extractAndConvert(34, 1);
  // 項番16: 不成立フラグ ワイド (位置36, 1バイト)
  record.structured_data["wide_cancelled_flag"] = record.extractAndConvert(35, 1);
  // 項番17: 予備 (位置37, 1バイト) - スキップ
  // 項番18: 不成立フラグ 馬単 (位置38, 1バイト)
  record.structured_data["exacta_cancelled_flag"] = record.extractAndConvert(37, 1);
  // 項番19: 不成立フラグ 3連複 (位置39, 1バイト)
  record.structured_data["trio_cancelled_flag"] = record.extractAndConvert(38, 1);
  // 項番20: 不成立フラグ 3連単 (位置40, 1バイト)
  record.structured_data["trifecta_cancelled_flag"] = record.extractAndConvert(39, 1);
  // 項番21: 特払フラグ 単勝 (位置41, 1バイト)
  record.structured_data["win_special_payout_flag"] = record.extractAndConvert(40, 1);
  // 項番22: 特払フラグ 複勝 (位置42, 1バイト)
  record.structured_data["place_special_payout_flag"] = record.extractAndConvert(41, 1);
  // 項番23: 特払フラグ 枠連 (位置43, 1バイト)
  record.structured_data["bracket_quinella_special_payout_flag"] = record.extractAndConvert(42, 1);
  // 項番24: 特払フラグ 馬連 (位置44, 1バイト)
  record.structured_data["quinella_special_payout_flag"] = record.extractAndConvert(43, 1);
  // 項番25: 特払フラグ ワイド (位置45, 1バイト)
  record.structured_data["wide_special_payout_flag"] = record.extractAndConvert(44, 1);
  // 項番26: 予備 (位置46, 1バイト) - スキップ
  // 項番27: 特払フラグ 馬単 (位置47, 1バイト)
  record.structured_data["exacta_special_payout_flag"] = record.extractAndConvert(46, 1);
  // 項番28: 特払フラグ 3連複 (位置48, 1バイト)
  record.structured_data["trio_special_payout_flag"] = record.extractAndConvert(47, 1);
  // 項番29: 特払フラグ 3連単 (位置49, 1バイト)
  record.structured_data["trifecta_special_payout_flag"] = record.extractAndConvert(48, 1);
  // 項番30: 返還フラグ 単勝 (位置50, 1バイト)
  record.structured_data["win_refund_flag"] = record.extractAndConvert(49, 1);
  // 項番31: 返還フラグ 複勝 (位置51, 1バイト)
  record.structured_data["place_refund_flag"] = record.extractAndConvert(50, 1);
  // 項番32: 返還フラグ 枠連 (位置52, 1バイト)
  record.structured_data["bracket_quinella_refund_flag"] = record.extractAndConvert(51, 1);
  // 項番33: 返還フラグ 馬連 (位置53, 1バイト)
  record.structured_data["quinella_refund_flag"] = record.extractAndConvert(52, 1);
  // 項番34: 返還フラグ ワイド (位置54, 1バイト)
  record.structured_data["wide_refund_flag"] = record.extractAndConvert(53, 1);
  // 項番35: 予備 (位置55, 1バイト) - スキップ
  // 項番36: 返還フラグ 馬単 (位置56, 1バイト)
  record.structured_data["exacta_refund_flag"] = record.extractAndConvert(55, 1);
  // 項番37: 返還フラグ 3連複 (位置57, 1バイト)
  record.structured_data["trio_refund_flag"] = record.extractAndConvert(56, 1);
  // 項番38: 返還フラグ 3連単 (位置58, 1バイト)
  record.structured_data["trifecta_refund_flag"] = record.extractAndConvert(57, 1);
  // 項番39: 返還馬番情報 (位置59, 28バイト)
  record.structured_data["refund_horse_number_info_28"] = record.extractAndConvert(58, 28);
  // 項番40: 返還枠番情報 (位置87, 8バイト)
  record.structured_data["refund_bracket_info"] = record.extractAndConvert(86, 8);
  // 項番41: 返還同枠情報 (位置95, 8バイト)
  record.structured_data["refund_same_bracket_info"] = record.extractAndConvert(94, 8);
  // 項番42: 単勝払戻 (位置103, 39バイト(13バイト×3))
  nlohmann::json tansho_payback_list = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 102 + (i * 13);
    nlohmann::json payback_obj;
    payback_obj["number"] = record.extractAndConvert(base_pos + 0, 2);
    payback_obj["payout"] = record.extractAndConvert(base_pos + 2, 9);
    payback_obj["popularity_rank"] = record.extractAndConvert(base_pos + 11, 2);
    tansho_payback_list.push_back(payback_obj);
  }
  record.structured_data["win_payback"] = tansho_payback_list;
  // 項番43: 複勝払戻 (位置142, 65バイト(13バイト×5))
  nlohmann::json fukusho_payback_list = nlohmann::json::array();
  for (int i = 0; i < 5; i++) {
    size_t base_pos = 141 + (i * 13);
    nlohmann::json payback_obj;
    payback_obj["number"] = record.extractAndConvert(base_pos + 0, 2);
    payback_obj["payout"] = record.extractAndConvert(base_pos + 2, 9);
    payback_obj["popularity_rank"] = record.extractAndConvert(base_pos + 11, 2);
    fukusho_payback_list.push_back(payback_obj);
  }
  record.structured_data["place_payback"] = fukusho_payback_list;
  // 項番44: 枠連払戻 (位置207, 39バイト(13バイト×3))
  nlohmann::json wakuren_payback_list = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 206 + (i * 13);
    nlohmann::json payback_obj;
    payback_obj["number"] = record.extractAndConvert(base_pos + 0, 2);
    payback_obj["payout"] = record.extractAndConvert(base_pos + 2, 9);
    payback_obj["popularity_rank"] = record.extractAndConvert(base_pos + 11, 2);
    wakuren_payback_list.push_back(payback_obj);
  }
  record.structured_data["bracket_quinella_payback"] = wakuren_payback_list;
  // 項番45: 馬連払戻 (位置246, 48バイト(16バイト×3))
  nlohmann::json umaren_payback_list = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 245 + (i * 16);
    nlohmann::json payback_obj;
    payback_obj["number"] = record.extractAndConvert(base_pos + 0, 4);
    payback_obj["payout"] = record.extractAndConvert(base_pos + 4, 9);
    payback_obj["popularity_rank"] = record.extractAndConvert(base_pos + 13, 3);
    umaren_payback_list.push_back(payback_obj);
  }
  record.structured_data["quinella_payback"] = umaren_payback_list;
  // 項番46: ワイド払戻 (位置294, 112バイト(16バイト×7))
  nlohmann::json wide_payback_list = nlohmann::json::array();
  for (int i = 0; i < 7; i++) {
    size_t base_pos = 293 + (i * 16);
    nlohmann::json payback_obj;
    payback_obj["number"] = record.extractAndConvert(base_pos + 0, 4);
    payback_obj["payout"] = record.extractAndConvert(base_pos + 4, 9);
    payback_obj["popularity_rank"] = record.extractAndConvert(base_pos + 13, 3);
    wide_payback_list.push_back(payback_obj);
  }
  record.structured_data["wide_payback"] = wide_payback_list;
  // 項番47: 予備 (位置406, 48バイト(16バイト×3)) - スキップ
  // 項番48: 馬単払戻 (位置454, 96バイト(16バイト×6))
  nlohmann::json umatan_payback_list = nlohmann::json::array();
  for (int i = 0; i < 6; i++) {
    size_t base_pos = 453 + (i * 16);
    nlohmann::json payback_obj;
    payback_obj["number"] = record.extractAndConvert(base_pos + 0, 4);
    payback_obj["payout"] = record.extractAndConvert(base_pos + 4, 9);
    payback_obj["popularity_rank"] = record.extractAndConvert(base_pos + 13, 3);
    umatan_payback_list.push_back(payback_obj);
  }
  record.structured_data["exacta_payback"] = umatan_payback_list;
  // 項番49: 3連複払戻 (位置550, 54バイト(18バイト×3))
  nlohmann::json sanrenpuku_payback_list = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 549 + (i * 18);
    nlohmann::json payback_obj;
    payback_obj["number"] = record.extractAndConvert(base_pos + 0, 6);
    payback_obj["payout"] = record.extractAndConvert(base_pos + 6, 9);
    payback_obj["popularity_rank"] = record.extractAndConvert(base_pos + 15, 3);
    sanrenpuku_payback_list.push_back(payback_obj);
  }
  record.structured_data["trio_payback"] = sanrenpuku_payback_list;
  // 項番50: 3連単払戻 (位置604, 114バイト(19バイト×6))
  nlohmann::json sanrentan_payback_list = nlohmann::json::array();
  for (int i = 0; i < 6; i++) {
    size_t base_pos = 603 + (i * 19);
    nlohmann::json payback_obj;
    payback_obj["number"] = record.extractAndConvert(base_pos + 0, 6);
    payback_obj["payout"] = record.extractAndConvert(base_pos + 6, 9);
    payback_obj["popularity_rank"] = record.extractAndConvert(base_pos + 15, 4);
    sanrentan_payback_list.push_back(payback_obj);
  }
  record.structured_data["trifecta_payback"] = sanrentan_payback_list;
}
