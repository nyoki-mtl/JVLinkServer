#include "data/record_parser.h"
#include "json.hpp"

void parseRAFields(ParsedRecord& record) {
  // RAレコード（レース詳細）解析
  // レコード長: 1272バイト

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
  // 項番10: 曜日コード (位置28, 1バイト)
  record.structured_data["weekday_code"] = record.extractAndConvert(27, 1);
  // 項番11: 特別競走番号 (位置29, 4バイト)
  record.structured_data["special_race_number"] = record.extractAndConvert(28, 4);
  // 項番12: 競走名本題 (位置33, 60バイト) 全角30文字
  record.structured_data["race_name_main"] = record.extractAndConvert(32, 60);
  // 項番13: 競走名副題 (位置93, 60バイト) 全角30文字
  record.structured_data["race_name_subtitle"] = record.extractAndConvert(92, 60);
  // 項番14: 競走名カッコ内 (位置153, 60バイト) 全角30文字
  record.structured_data["race_name_parentheses"] = record.extractAndConvert(152, 60);
  // 項番15: 競走名本題欧字 (位置213, 120バイト) 半角120文字
  record.structured_data["race_name_main_english"] = record.extractAndConvert(212, 120);
  // 項番16: 競走名副題欧字 (位置333, 120バイト) 半角120文字
  record.structured_data["race_name_subtitle_english"] = record.extractAndConvert(332, 120);
  // 項番17: 競走名カッコ内欧字 (位置453, 120バイト) 半角120文字
  record.structured_data["race_name_parentheses_english"] = record.extractAndConvert(452, 120);
  // 項番18: 競走名略称10文字 (位置573, 20バイト) 全角10文字
  record.structured_data["race_short_name_10"] = record.extractAndConvert(572, 20);
  // 項番19: 競走名略称6文字 (位置593, 12バイト) 全角6文字
  record.structured_data["race_short_name_6"] = record.extractAndConvert(592, 12);
  // 項番20: 競走名略称3文字 (位置605, 6バイト) 全角3文字
  record.structured_data["race_short_name_3"] = record.extractAndConvert(604, 6);
  // 項番21: 競走名区分 (位置611, 1バイト)
  record.structured_data["race_name_code"] = record.extractAndConvert(610, 1);
  // 項番22: 重賞回次 (位置612, 3バイト)
  record.structured_data["graded_race_round_number"] = record.extractAndConvert(611, 3);
  // 項番23: グレードコード (位置615, 1バイト)
  record.structured_data["grade_code"] = record.extractAndConvert(614, 1);
  // 項番24: 変更前グレードコード (位置616, 1バイト)
  record.structured_data["before_grade_code"] = record.extractAndConvert(615, 1);
  // 項番25: 競走種別コード (位置617, 2バイト)
  record.structured_data["race_type_code"] = record.extractAndConvert(616, 2);
  // 項番26: 競走記号コード (位置619, 3バイト) <コード表 2006. 競走記号コード>参照
  record.structured_data["race_symbol_code"] = record.extractAndConvert(618, 3);
  // 項番27: 重量種別コード (位置622, 1バイト) <コード表 2008. 重量種別コード>参照
  record.structured_data["weight_type_code"] = record.extractAndConvert(621, 1);
  // 項番28: 競走条件コード 2歳条件 (位置623, 3バイト) <コード表 2007. 競争条件コード>参照
  record.structured_data["race_cond_code_2yo"] = record.extractAndConvert(622, 3);
  // 項番29: 競走条件コード 3歳条件 (位置626, 3バイト) <コード表 2007. 競争条件コード>参照
  record.structured_data["race_cond_code_3yo"] = record.extractAndConvert(625, 3);
  // 項番30: 競走条件コード 4歳条件 (位置629, 3バイト) <コード表 2007. 競争条件コード>参照
  record.structured_data["race_cond_code_4yo"] = record.extractAndConvert(628, 3);
  // 項番31: 競走条件コード 5歳以上条件 (位置632, 3バイト) <コード表 2007. 競争条件コード>参照
  record.structured_data["race_cond_code_5yo_up"] = record.extractAndConvert(631, 3);
  // 項番32: 競走条件コード 最若年条件 (位置635, 3バイト) <コード表 2007. 競争条件コード>参照
  record.structured_data["race_cond_code_youngest"] = record.extractAndConvert(634, 3);
  // 項番33: 競走条件名称 (位置638, 60バイト) 全角30文字
  record.structured_data["race_condition_name"] = record.extractAndConvert(637, 60);
  // 項番34: 距離 (位置698, 4バイト) 単位:メートル
  record.structured_data["distance"] = record.extractAndConvert(697, 4);
  // 項番35: 変更前距離 (位置702, 4バイト) 単位:メートル
  record.structured_data["before_distance"] = record.extractAndConvert(701, 4);
  // 項番36: トラックコード (位置706, 2バイト) <コード表 2009. トラックコード>参照
  record.structured_data["track_code"] = record.extractAndConvert(705, 2);
  // 項番37: 変更前トラックコード (位置708, 2バイト) <コード表 2009. トラックコード>参照
  record.structured_data["before_track_code"] = record.extractAndConvert(707, 2);
  // 項番38: コース区分 (位置710, 2バイト) 半角2文字 "A "~"E "
  record.structured_data["course_code"] = record.extractAndConvert(709, 2);
  // 項番39: 変更前コース区分 (位置712, 2バイト) 半角2文字
  record.structured_data["before_course_code"] = record.extractAndConvert(711, 2);
  // 項番40: 本賞金 (位置714, 56バイト = 8バイト×7) 単位:100円
  record.structured_data["purse_money"] = record.extractAndConvertArray(713, 8, 7);
  // 項番41: 変更前本賞金 (位置770, 40バイト = 8バイト×5) 単位:100円
  record.structured_data["before_purse_money"] = record.extractAndConvertArray(769, 8, 5);
  // 項番42: 付加賞金 (位置810, 40バイト = 8バイト×5) 単位:100円
  record.structured_data["added_money"] = record.extractAndConvertArray(809, 8, 5);
  // 項番43: 変更前付加賞金 (位置850, 24バイト = 8バイト×3) 単位:100円
  record.structured_data["before_added_money"] = record.extractAndConvertArray(849, 8, 3);
  // 項番44: 発走時刻 (位置874, 4バイト) HHMM形式
  record.structured_data["post_time"] = record.extractAndConvert(873, 4);
  // 項番45: 変更前発走時刻 (位置878, 4バイト) HHMM形式
  record.structured_data["before_post_time"] = record.extractAndConvert(877, 4);
  // 項番46: 登録頭数 (位置882, 2バイト)
  record.structured_data["num_entries"] = record.extractAndConvert(881, 2);
  // 項番47: 出走頭数 (位置884, 2バイト)
  record.structured_data["num_starters"] = record.extractAndConvert(883, 2);
  // 項番48: 入線頭数 (位置886, 2バイト)
  record.structured_data["num_finishers"] = record.extractAndConvert(885, 2);
  // 項番49: 天候コード (位置888, 1バイト)
  record.structured_data["weather_code"] = record.extractAndConvert(887, 1);
  // 項番50: 芝馬場状態コード (位置889, 1バイト)
  record.structured_data["turf_track_condition_code"] = record.extractAndConvert(888, 1);
  // 項番51: ダート馬場状態コード (位置890, 1バイト)
  record.structured_data["dirt_track_condition_code"] = record.extractAndConvert(889, 1);
  // 項番52: ラップタイム (位置891, 75バイト = 3バイト×25) 単位:0.1秒 SS.S形式
  record.structured_data["lap_times"] = record.extractAndConvertArray(890, 3, 25);
  // 項番53: 障害マイルタイム (位置966, 4バイト) 単位:0.1秒 MSS.S形式
  record.structured_data["mile_time"] = record.extractAndConvert(965, 4);
  // 項番54: 前3ハロン (位置970, 3バイト) 単位:0.1秒 SS.S形式
  record.structured_data["first_3f_time"] = record.extractAndConvert(969, 3);
  // 項番55: 前4ハロン (位置973, 3バイト) 単位:0.1秒 SS.S形式
  record.structured_data["first_4f_time"] = record.extractAndConvert(972, 3);
  // 項番56: 後3ハロン (位置976, 3バイト) 単位:0.1秒 SS.S形式
  record.structured_data["last_3f_time"] = record.extractAndConvert(975, 3);
  // 項番57: 後4ハロン (位置979, 3バイト) 単位:0.1秒 SS.S形式
  record.structured_data["last_4f_time"] = record.extractAndConvert(978, 3);
  // 項番58: コーナー通過順位 (位置982, 288バイト = 72バイト×4)
  nlohmann::json corners_array = nlohmann::json::array();
  for (int i = 0; i < 4; i++) {
    size_t base_pos = 981 + (i * 72);
    nlohmann::json corner_obj;
    // 項番58a: コーナー番号 (1バイト)
    corner_obj["corner"] = record.extractAndConvert(base_pos + 0, 1);
    // 項番58b: 周回数 (1バイト)
    corner_obj["lap_count"] = record.extractAndConvert(base_pos + 1, 1);
    // 項番58c: 通過順位 (70バイト) 半角70文字
    corner_obj["passing_order"] = record.extractAndConvert(base_pos + 2, 70);
    corners_array.push_back(corner_obj);
  }
  record.structured_data["corner_passing_order"] = corners_array;
  // 項番59: レコード更新区分 (位置1270, 1バイト)
  record.structured_data["record_update_code"] = record.extractAndConvert(1269, 1);
}
