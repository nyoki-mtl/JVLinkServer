#include "data/record_parser.h"
#include "json.hpp"

void parseSEFields(ParsedRecord& record) {
  // SEレコード（馬毎レース情報）の完全実装
  // レコード長: 555バイト

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
  // 項番10: 枠番 (位置28, 1バイト)
  record.structured_data["bracket_number"] = record.extractAndConvert(27, 1);
  // 項番11: 馬番 (位置29, 2バイト)
  record.structured_data["horse_number"] = record.extractAndConvert(28, 2);
  // 項番12: 血統登録番号 (位置31, 10バイト)
  record.structured_data["pedigree_reg_num"] = record.extractAndConvert(30, 10);
  // 項番13: 馬名 (位置41, 36バイト)
  record.structured_data["horse_name"] = record.extractAndConvert(40, 36);
  // 項番14: 馬記号コード (位置77, 2バイト)
  record.structured_data["horse_symbol_code"] = record.extractAndConvert(76, 2);
  // 項番15: 性別コード (位置79, 1バイト)
  record.structured_data["horse_sex_code"] = record.extractAndConvert(78, 1);
  // 項番16: 品種コード (位置80, 1バイト)
  record.structured_data["breed_code"] = record.extractAndConvert(79, 1);
  // 項番17: 毛色コード (位置81, 2バイト)
  record.structured_data["coat_color_code"] = record.extractAndConvert(80, 2);
  // 項番18: 馬齢 (位置83, 2バイト)
  record.structured_data["horse_age"] = record.extractAndConvert(82, 2);
  // 項番19: 東西所属コード (位置85, 1バイト)
  record.structured_data["east_west_affiliation_code"] = record.extractAndConvert(84, 1);
  // 項番20: 調教師コード (位置86, 5バイト)
  record.structured_data["trainer_code"] = record.extractAndConvert(85, 5);
  // 項番21: 調教師名略称 (位置91, 8バイト)
  record.structured_data["trainer_short_name"] = record.extractAndConvert(90, 8);
  // 項番22: 馬主コード (位置99, 6バイト)
  record.structured_data["owner_code"] = record.extractAndConvert(98, 6);
  // 項番23: 馬主名(法人格無) (位置105, 64バイト)
  record.structured_data["owner_name_individual"] = record.extractAndConvert(104, 64);
  // 項番24: 服色標示 (位置169, 60バイト)
  record.structured_data["silk_colors"] = record.extractAndConvert(168, 60);
  // 項番25: 予備 (位置229, 60バイト) - スキップ
  // 項番26: 負担重量 (位置289, 3バイト)
  record.structured_data["carrying_weight"] = record.extractAndConvert(288, 3);
  // 項番27: 変更前負担重量 (位置292, 3バイト)
  record.structured_data["before_carrying_weight"] = record.extractAndConvert(291, 3);
  // 項番28: ブリンカー使用区分 (位置295, 1バイト)
  record.structured_data["blinker_usage_code"] = record.extractAndConvert(294, 1);
  // 項番29: 予備 (位置296, 1バイト) - スキップ
  // 項番30: 騎手コード (位置297, 5バイト)
  record.structured_data["jockey_code"] = record.extractAndConvert(296, 5);
  // 項番31: 変更前騎手コード (位置302, 5バイト)
  record.structured_data["before_jockey_code"] = record.extractAndConvert(301, 5);
  // 項番32: 騎手名略称 (位置307, 8バイト)
  record.structured_data["jockey_short_name"] = record.extractAndConvert(306, 8);
  // 項番33: 変更前騎手名略称 (位置315, 8バイト)
  record.structured_data["before_jockey_short_name"] = record.extractAndConvert(314, 8);
  // 項番34: 騎手見習コード (位置323, 1バイト)
  record.structured_data["jockey_apprentice_code"] = record.extractAndConvert(322, 1);
  // 項番35: 変更前騎手見習コード (位置324, 1バイト)
  record.structured_data["before_jockey_apprentice_code"] = record.extractAndConvert(323, 1);
  // 項番36: 馬体重 (位置325, 3バイト)
  record.structured_data["horse_weight"] = record.extractAndConvert(324, 3);
  // 項番37: 増減符号 (位置328, 1バイト)
  record.structured_data["weight_change_sign"] = record.extractAndConvert(327, 1);
  // 項番38: 増減差 (位置329, 3バイト)
  record.structured_data["weight_change_diff"] = record.extractAndConvert(328, 3);
  // 項番39: 異常区分コード (位置332, 1バイト)
  record.structured_data["abnormality_code"] = record.extractAndConvert(331, 1);
  // 項番40: 入線順位 (位置333, 2バイト)
  record.structured_data["finish_order"] = record.extractAndConvert(332, 2);
  // 項番41: 確定着順 (位置335, 2バイト)
  record.structured_data["confirmed_placing"] = record.extractAndConvert(334, 2);
  // 項番42: 同着区分 (位置337, 1バイト)
  record.structured_data["dead_heat_code"] = record.extractAndConvert(336, 1);
  // 項番43: 同着頭数 (位置338, 1バイト)
  record.structured_data["dead_heat_count"] = record.extractAndConvert(337, 1);
  // 項番44: 走破タイム (位置339, 4バイト)
  record.structured_data["finish_time"] = record.extractAndConvert(338, 4);
  // 項番45: 着差コード (位置343, 3バイト)
  record.structured_data["margin_code"] = record.extractAndConvert(342, 3);
  // 項番46: ＋着差コード (位置346, 3バイト)
  record.structured_data["margin_code_plus"] = record.extractAndConvert(345, 3);
  // 項番47: ＋＋着差コード (位置349, 3バイト)
  record.structured_data["margin_code_plus_plus"] = record.extractAndConvert(348, 3);
  // 項番48: 1コーナーでの順位 (位置352, 2バイト)
  record.structured_data["corner1_position"] = record.extractAndConvert(351, 2);
  // 項番49: 2コーナーでの順位 (位置354, 2バイト)
  record.structured_data["corner2_position"] = record.extractAndConvert(353, 2);
  // 項番50: 3コーナーでの順位 (位置356, 2バイト)
  record.structured_data["corner3_position"] = record.extractAndConvert(355, 2);
  // 項番51: 4コーナーでの順位 (位置358, 2バイト)
  record.structured_data["corner4_position"] = record.extractAndConvert(357, 2);
  // 項番52: 単勝オッズ (位置360, 4バイト)
  record.structured_data["win_odds"] = record.extractAndConvert(359, 4);
  // 項番53: 単勝人気順 (位置364, 2バイト)
  record.structured_data["win_popularity_rank"] = record.extractAndConvert(363, 2);
  // 項番54: 獲得本賞金 (位置366, 8バイト)
  record.structured_data["earned_purse_money"] = record.extractAndConvert(365, 8);
  // 項番55: 獲得付加賞金 (位置374, 8バイト)
  record.structured_data["earned_added_money"] = record.extractAndConvert(373, 8);
  // 項番56: 予備 (位置382, 3バイト) - スキップ
  // 項番57: 予備 (位置385, 3バイト) - スキップ
  // 項番58: 後4ハロンタイム (位置388, 3バイト)
  record.structured_data["last_4f_time"] = record.extractAndConvert(387, 3);
  // 項番59: 後3ハロンタイム (位置391, 3バイト)
  record.structured_data["last_3f_time"] = record.extractAndConvert(390, 3);
  // 項番60: 1着馬(相手馬)情報 (位置394, 138バイト (46バイト×3回))
  nlohmann::json opponent_horses_array = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 393 + i * 46;
    nlohmann::json opponent_horse_obj;
    opponent_horse_obj["pedigree_reg_num"] = record.extractAndConvert(base_pos + 0, 10);
    opponent_horse_obj["horse_name"] = record.extractAndConvert(base_pos + 10, 36);
    opponent_horses_array.push_back(opponent_horse_obj);
  }
  record.structured_data["opponent_horses"] = opponent_horses_array;
  // 項番61: タイム差 (位置532, 4バイト)
  record.structured_data["time_diff"] = record.extractAndConvert(531, 4);
  // 項番62: レコード更新区分 (位置536, 1バイト)
  record.structured_data["record_update_code"] = record.extractAndConvert(535, 1);
  // 項番63: マイニング区分 (位置537, 1バイト)
  record.structured_data["mining_code"] = record.extractAndConvert(536, 1);
  // 項番64: マイニング予想走破タイム (位置538, 5バイト)
  record.structured_data["mining_pred_finish_time"] = record.extractAndConvert(537, 5);
  // 項番65: マイニング予想誤差(信頼度)＋ (位置543, 4バイト)
  record.structured_data["mining_pred_err_margin_plus"] = record.extractAndConvert(542, 4);
  // 項番66: マイニング予想誤差(信頼度)－ (位置547, 4バイト)
  record.structured_data["mining_pred_err_margin_minus"] = record.extractAndConvert(546, 4);
  // 項番67: マイニング予想順位 (位置551, 2バイト)
  record.structured_data["mining_pred_rank"] = record.extractAndConvert(550, 2);
  // 項番68: 今回レース脚質判定 (位置553, 1バイト)
  record.structured_data["current_race_running_style_judgement"] = record.extractAndConvert(552, 1);
}
