#include "data/record_parser.h"
#include "json.hpp"

void parseCHFields(ParsedRecord& record) {
  // CHレコード（調教師マスタ）の解析
  // レコード長: 3862バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 調教師コード (位置: 12, サイズ: 5)
  record.structured_data["trainer_code"] = record.extractAndConvert(11, 5);
  // 項番5: 調教師抹消区分 (位置: 17, サイズ: 1)
  record.structured_data["deregistration_flag"] = record.extractAndConvert(16, 1);
  // 項番6: 調教師免許交付年月日 (位置: 18, サイズ: 8)
  record.structured_data["license_issue_date"] = record.extractAndConvert(17, 8);
  // 項番7: 調教師免許抹消年月日 (位置: 26, サイズ: 8)
  record.structured_data["license_revoked_date"] = record.extractAndConvert(25, 8);
  // 項番8: 生年月日 (位置: 34, サイズ: 8)
  record.structured_data["birth_date"] = record.extractAndConvert(33, 8);
  // 項番9: 調教師名 (位置: 42, サイズ: 34)
  record.structured_data["trainer_name"] = record.extractAndConvert(41, 34);
  // 項番10: 調教師名半角カナ (位置: 76, サイズ: 30)
  record.structured_data["trainer_name_kana"] = record.extractAndConvert(75, 30);
  // 項番11: 調教師名略称 (位置: 106, サイズ: 8)
  record.structured_data["trainer_name_short"] = record.extractAndConvert(105, 8);
  // 項番12: 調教師名欧字 (位置: 114, サイズ: 80)
  record.structured_data["trainer_name_english"] = record.extractAndConvert(113, 80);
  // 項番13: 性別区分 (位置: 194, サイズ: 1)
  record.structured_data["sex_code"] = record.extractAndConvert(193, 1);
  // 項番14: 調教師東西所属コード (位置: 195, サイズ: 1)
  record.structured_data["affiliation_code"] = record.extractAndConvert(194, 1);
  // 項番15: 招待地域名 (位置: 196, サイズ: 20)
  record.structured_data["invitation_area_name"] = record.extractAndConvert(195, 20);
  // 項番16: 最近重賞勝利情報 (位置: 216, サイズ: 163, 繰り返し: 3)
  nlohmann::json recent_graded_wins_array = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 215 + i * 163;
    nlohmann::json win_info;
    win_info["race_key"] = record.extractAndConvert(base_pos, 16);
    win_info["race_name_main"] = record.extractAndConvert(base_pos + 16, 60);
    win_info["race_short_name_10"] = record.extractAndConvert(base_pos + 76, 20);
    win_info["race_short_name_6"] = record.extractAndConvert(base_pos + 96, 12);
    win_info["race_short_name_3"] = record.extractAndConvert(base_pos + 108, 6);
    win_info["grade_code"] = record.extractAndConvert(base_pos + 114, 1);
    win_info["num_starters"] = record.extractAndConvert(base_pos + 115, 2);
    win_info["pedigree_reg_num"] = record.extractAndConvert(base_pos + 117, 10);
    win_info["horse_name"] = record.extractAndConvert(base_pos + 127, 36);
    recent_graded_wins_array.push_back(win_info);
  }
  record.structured_data["recent_graded_wins"] = recent_graded_wins_array;
  // 項番17: 本年・前年・累計成績情報 (位置: 705, サイズ: 1052, 繰り返し: 3)
  nlohmann::json performance_stats_array = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 704 + i * 1052;
    nlohmann::json performance_stat;
    // 17a: 設定年 (オフセット: 0, サイズ: 4)
    performance_stat["year"] = record.extractAndConvert(base_pos, 4);
    // 17b: 平地本賞金合計 (オフセット: 4, サイズ: 10)
    performance_stat["flat_prize_money"] = record.extractAndConvert(base_pos + 4, 10);
    // 17c: 障害本賞金合計 (オフセット: 14, サイズ: 10)
    performance_stat["steeplechase_prize_money"] = record.extractAndConvert(base_pos + 14, 10);
    // 17d: 平地付加賞金合計 (オフセット: 24, サイズ: 10)
    performance_stat["flat_added_money"] = record.extractAndConvert(base_pos + 24, 10);
    // 17e: 障害付加賞金合計 (オフセット: 34, サイズ: 10)
    performance_stat["steeplechase_added_money"] = record.extractAndConvert(base_pos + 34, 10);
    // 17f: 平地着回数 (オフセット: 44, サイズ: 6, 繰り返し: 6)
    performance_stat["flat_placing_counts"] = record.extractAndConvertArray(base_pos + 44, 6, 6);
    // 17g: 障害着回数 (オフセット: 80, サイズ: 6, 繰り返し: 6)
    performance_stat["steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 80, 6, 6);
    // 17h: 札幌平地着回数 (オフセット: 116)
    performance_stat["sapporo_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 116, 6, 6);
    // 17i: 札幌障害着回数 (オフセット: 152)
    performance_stat["sapporo_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 152, 6, 6);
    // 17j: 函館平地着回数 (オフセット: 188)
    performance_stat["hakodate_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 188, 6, 6);
    // 17k: 函館障害着回数 (オフセット: 224)
    performance_stat["hakodate_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 224, 6, 6);
    // 17l: 福島平地着回数 (オフセット: 260)
    performance_stat["fukushima_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 260, 6, 6);
    // 17m: 福島障害着回数 (オフセット: 296)
    performance_stat["fukushima_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 296, 6, 6);
    // 17n: 新潟平地着回数 (オフセット: 332)
    performance_stat["niigata_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 332, 6, 6);
    // 17o: 新潟障害着回数 (オフセット: 368)
    performance_stat["niigata_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 368, 6, 6);
    // 17p: 東京平地着回数 (オフセット: 404)
    performance_stat["tokyo_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 404, 6, 6);
    // 17q: 東京障害着回数 (オフセット: 440)
    performance_stat["tokyo_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 440, 6, 6);
    // 17r: 中山平地着回数 (オフセット: 476)
    performance_stat["nakayama_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 476, 6, 6);
    // 17s: 中山障害着回数 (オフセット: 512)
    performance_stat["nakayama_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 512, 6, 6);
    // 17t: 中京平地着回数 (オフセット: 548)
    performance_stat["chukyo_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 548, 6, 6);
    // 17u: 中京障害着回数 (オフセット: 584)
    performance_stat["chukyo_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 584, 6, 6);
    // 17v: 京都平地着回数 (オフセット: 620)
    performance_stat["kyoto_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 620, 6, 6);
    // 17w: 京都障害着回数 (オフセット: 656)
    performance_stat["kyoto_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 656, 6, 6);
    // 17x: 阪神平地着回数 (オフセット: 692)
    performance_stat["hanshin_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 692, 6, 6);
    // 17y: 阪神障害着回数 (オフセット: 728)
    performance_stat["hanshin_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 728, 6, 6);
    // 17z: 小倉平地着回数 (オフセット: 764)
    performance_stat["kokura_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 764, 6, 6);
    // 17aa: 小倉障害着回数 (オフセット: 800)
    performance_stat["kokura_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 800, 6, 6);
    // 17ab: 芝1600M以下着回数 (オフセット: 836)
    performance_stat["turf_class_d_placing_counts"] = record.extractAndConvertArray(base_pos + 836, 6, 6);
    // 17ac: 芝1601-2200M着回数 (オフセット: 872)
    performance_stat["turf_class_e_placing_counts"] = record.extractAndConvertArray(base_pos + 872, 6, 6);
    // 17ad: 芝2201M以上着回数 (オフセット: 908)
    performance_stat["turf_gt2200_placing_counts"] = record.extractAndConvertArray(base_pos + 908, 6, 6);
    // 17ae: ダート1600M以下着回数 (オフセット: 944)
    performance_stat["dirt_class_d_placing_counts"] = record.extractAndConvertArray(base_pos + 944, 6, 6);
    // 17af: ダート1601-2200M着回数 (オフセット: 980)
    performance_stat["dirt_class_e_placing_counts"] = record.extractAndConvertArray(base_pos + 980, 6, 6);
    // 17ag: ダート2201M以上着回数 (オフセット: 1016)
    performance_stat["dirt_gt2200_placing_counts"] = record.extractAndConvertArray(base_pos + 1016, 6, 6);
    performance_stats_array.push_back(performance_stat);
  }
  record.structured_data["performance_stats"] = performance_stats_array;
}
