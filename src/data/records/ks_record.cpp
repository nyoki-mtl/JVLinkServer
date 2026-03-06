#include "data/record_parser.h"
#include "json.hpp"

void parseKSFields(ParsedRecord& record) {
  // KSレコード（騎手マスタ）の解析
  // レコード長: 4173バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 騎手コード (位置: 12, サイズ: 5)
  record.structured_data["jockey_code"] = record.extractAndConvert(11, 5);
  // 項番5: 騎手抹消区分 (位置: 17, サイズ: 1)
  record.structured_data["deregistration_flag"] = record.extractAndConvert(16, 1);
  // 項番6: 騎手免許交付年月日 (位置: 18, サイズ: 8)
  record.structured_data["license_issue_date"] = record.extractAndConvert(17, 8);
  // 項番7: 騎手免許抹消年月日 (位置: 26, サイズ: 8)
  record.structured_data["license_revoked_date"] = record.extractAndConvert(25, 8);
  // 項番8: 生年月日 (位置: 34, サイズ: 8)
  record.structured_data["birth_date"] = record.extractAndConvert(33, 8);
  // 項番9: 騎手名 (位置: 42, サイズ: 34)
  record.structured_data["jockey_name"] = record.extractAndConvert(41, 34);
  // 項番10: 予備 (位置: 76, サイズ: 34) - reserved, not output
  // 項番11: 騎手名半角カナ (位置: 110, サイズ: 30)
  record.structured_data["jockey_name_kana"] = record.extractAndConvert(109, 30);
  // 項番12: 騎手名略称 (位置: 140, サイズ: 8)
  record.structured_data["jockey_name_short"] = record.extractAndConvert(139, 8);
  // 項番13: 騎手名欧字 (位置: 148, サイズ: 80)
  record.structured_data["jockey_name_english"] = record.extractAndConvert(147, 80);
  // 項番14: 性別区分 (位置: 228, サイズ: 1)
  record.structured_data["sex_code"] = record.extractAndConvert(227, 1);
  // 項番15: 騎乗資格コード (位置: 229, サイズ: 1)
  record.structured_data["riding_qualification_code"] = record.extractAndConvert(228, 1);
  // 項番16: 騎手見習コード (位置: 230, サイズ: 1)
  record.structured_data["jockey_apprentice_code"] = record.extractAndConvert(229, 1);
  // 項番17: 騎手東西所属コード (位置: 231, サイズ: 1)
  record.structured_data["affiliation_code"] = record.extractAndConvert(230, 1);
  // 項番18: 招待地域名 (位置: 232, サイズ: 20)
  record.structured_data["invitation_area_name"] = record.extractAndConvert(231, 20);
  // 項番19: 所属調教師コード (位置: 252, サイズ: 5)
  record.structured_data["affiliated_trainer_code"] = record.extractAndConvert(251, 5);
  // 項番20: 所属調教師名略称 (位置: 257, サイズ: 8)
  record.structured_data["affiliated_trainer_name_short"] = record.extractAndConvert(256, 8);
  // 項番21: 初騎乗情報 (位置: 265, サイズ: 67, 繰り返し: 2)
  // 平地初騎乗・障害初騎乗の順
  nlohmann::json first_ride_info_array = nlohmann::json::array();
  for (int i = 0; i < 2; i++) {
    size_t base_pos = 264 + i * 67;
    std::string race_key = record.extractAndConvert(base_pos, 16);
    if (race_key.find_first_not_of(' ') == std::string::npos) {
      continue;
    }
    nlohmann::json entry;
    entry["race_key"] = race_key;
    entry["num_starters"] = record.extractAndConvert(base_pos + 16, 2);
    entry["pedigree_reg_num"] = record.extractAndConvert(base_pos + 18, 10);
    entry["horse_name"] = record.extractAndConvert(base_pos + 28, 36);
    entry["confirmed_placing"] = record.extractAndConvert(base_pos + 64, 2);
    entry["abnormality_code"] = record.extractAndConvert(base_pos + 66, 1);
    first_ride_info_array.push_back(entry);
  }
  record.structured_data["first_ride_info"] = first_ride_info_array;

  // 項番22: 初勝利情報 (位置: 399, サイズ: 64, 繰り返し: 2)
  // 平地初勝利・障害初勝利の順
  nlohmann::json first_win_info_array = nlohmann::json::array();
  for (int i = 0; i < 2; i++) {
    size_t base_pos = 398 + i * 64;
    std::string race_key = record.extractAndConvert(base_pos, 16);
    if (race_key.find_first_not_of(' ') == std::string::npos) {
      continue;
    }
    nlohmann::json entry;
    entry["race_key"] = race_key;
    entry["num_starters"] = record.extractAndConvert(base_pos + 16, 2);
    entry["pedigree_reg_num"] = record.extractAndConvert(base_pos + 18, 10);
    entry["horse_name"] = record.extractAndConvert(base_pos + 28, 36);
    first_win_info_array.push_back(entry);
  }
  record.structured_data["first_win_info"] = first_win_info_array;

  // 項番23: 最近重賞勝利情報 (位置: 527, サイズ: 163, 繰り返し: 3)
  nlohmann::json recent_grade_win_info_array = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 526 + i * 163;
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
    recent_grade_win_info_array.push_back(win_info);
  }
  record.structured_data["recent_graded_wins"] = recent_grade_win_info_array;
  // 項番24: 本年・前年・累計成績情報 (位置: 1016, サイズ: 1052, 繰り返し: 3)
  nlohmann::json yearly_performance_array = nlohmann::json::array();
  for (int i = 0; i < 3; i++) {
    size_t base_pos = 1015 + i * 1052;
    nlohmann::json yearly_performance;
    // 24a: 設定年 (オフセット: 0, サイズ: 4)
    yearly_performance["year"] = record.extractAndConvert(base_pos, 4);
    // 24b: 平地本賞金合計 (オフセット: 4, サイズ: 10)
    yearly_performance["flat_prize_money"] = record.extractAndConvert(base_pos + 4, 10);
    // 24c: 障害本賞金合計 (オフセット: 14, サイズ: 10)
    yearly_performance["steeplechase_prize_money"] = record.extractAndConvert(base_pos + 14, 10);
    // 24d: 平地付加賞金合計 (オフセット: 24, サイズ: 10)
    yearly_performance["flat_added_money"] = record.extractAndConvert(base_pos + 24, 10);
    // 24e: 障害付加賞金合計 (オフセット: 34, サイズ: 10)
    yearly_performance["steeplechase_added_money"] = record.extractAndConvert(base_pos + 34, 10);
    // 24f: 平地着回数 (オフセット: 44, サイズ: 6, 繰り返し: 6)
    yearly_performance["flat_placing_counts"] = record.extractAndConvertArray(base_pos + 44, 6, 6);
    // 24g: 障害着回数 (オフセット: 80, サイズ: 6, 繰り返し: 6)
    yearly_performance["steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 80, 6, 6);
    // 24h: 札幌平地着回数 (オフセット: 116, サイズ: 6, 繰り返し: 6)
    yearly_performance["sapporo_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 116, 6, 6);
    // 24i: 札幌障害着回数 (オフセット: 152, サイズ: 6, 繰り返し: 6)
    yearly_performance["sapporo_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 152, 6, 6);
    // 24j: 函館平地着回数 (オフセット: 188, サイズ: 6, 繰り返し: 6)
    yearly_performance["hakodate_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 188, 6, 6);
    // 24k: 函館障害着回数 (オフセット: 224, サイズ: 6, 繰り返し: 6)
    yearly_performance["hakodate_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 224, 6, 6);
    // 24l: 福島平地着回数 (オフセット: 260, サイズ: 6, 繰り返し: 6)
    yearly_performance["fukushima_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 260, 6, 6);
    // 24m: 福島障害着回数 (オフセット: 296, サイズ: 6, 繰り返し: 6)
    yearly_performance["fukushima_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 296, 6, 6);
    // 24n: 新潟平地着回数 (オフセット: 332, サイズ: 6, 繰り返し: 6)
    yearly_performance["niigata_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 332, 6, 6);
    // 24o: 新潟障害着回数 (オフセット: 368, サイズ: 6, 繰り返し: 6)
    yearly_performance["niigata_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 368, 6, 6);
    // 24p: 東京平地着回数 (オフセット: 404, サイズ: 6, 繰り返し: 6)
    yearly_performance["tokyo_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 404, 6, 6);
    // 24q: 東京障害着回数 (オフセット: 440, サイズ: 6, 繰り返し: 6)
    yearly_performance["tokyo_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 440, 6, 6);
    // 24r: 中山平地着回数 (オフセット: 476, サイズ: 6, 繰り返し: 6)
    yearly_performance["nakayama_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 476, 6, 6);
    // 24s: 中山障害着回数 (オフセット: 512, サイズ: 6, 繰り返し: 6)
    yearly_performance["nakayama_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 512, 6, 6);
    // 24t: 中京平地着回数 (オフセット: 548, サイズ: 6, 繰り返し: 6)
    yearly_performance["chukyo_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 548, 6, 6);
    // 24u: 中京障害着回数 (オフセット: 584, サイズ: 6, 繰り返し: 6)
    yearly_performance["chukyo_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 584, 6, 6);
    // 24v: 京都平地着回数 (オフセット: 620, サイズ: 6, 繰り返し: 6)
    yearly_performance["kyoto_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 620, 6, 6);
    // 24w: 京都障害着回数 (オフセット: 656, サイズ: 6, 繰り返し: 6)
    yearly_performance["kyoto_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 656, 6, 6);
    // 24x: 阪神平地着回数 (オフセット: 692, サイズ: 6, 繰り返し: 6)
    yearly_performance["hanshin_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 692, 6, 6);
    // 24y: 阪神障害着回数 (オフセット: 728, サイズ: 6, 繰り返し: 6)
    yearly_performance["hanshin_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 728, 6, 6);
    // 24z: 小倉平地着回数 (オフセット: 764, サイズ: 6, 繰り返し: 6)
    yearly_performance["kokura_flat_placing_counts"] = record.extractAndConvertArray(base_pos + 764, 6, 6);
    // 24aa: 小倉障害着回数 (オフセット: 800, サイズ: 6, 繰り返し: 6)
    yearly_performance["kokura_steeplechase_placing_counts"] = record.extractAndConvertArray(base_pos + 800, 6, 6);
    // 24ab: 芝1600M以下着回数 (オフセット: 836, サイズ: 6, 繰り返し: 6)
    yearly_performance["turf_class_d_placing_counts"] = record.extractAndConvertArray(base_pos + 836, 6, 6);
    // 24ac: 芝1601-2200M着回数 (オフセット: 872, サイズ: 6, 繰り返し: 6)
    yearly_performance["turf_class_e_placing_counts"] = record.extractAndConvertArray(base_pos + 872, 6, 6);
    // 24ad: 芝2201M以上着回数 (オフセット: 908, サイズ: 6, 繰り返し: 6)
    yearly_performance["turf_gt2200_placing_counts"] = record.extractAndConvertArray(base_pos + 908, 6, 6);
    // 24ae: ダート1600M以下着回数 (オフセット: 944, サイズ: 6, 繰り返し: 6)
    yearly_performance["dirt_class_d_placing_counts"] = record.extractAndConvertArray(base_pos + 944, 6, 6);
    // 24af: ダート1601-2200M着回数 (オフセット: 980, サイズ: 6, 繰り返し: 6)
    yearly_performance["dirt_class_e_placing_counts"] = record.extractAndConvertArray(base_pos + 980, 6, 6);
    // 24ag: ダート2201M以上着回数 (オフセット: 1016, サイズ: 6, 繰り返し: 6)
    yearly_performance["dirt_gt2200_placing_counts"] = record.extractAndConvertArray(base_pos + 1016, 6, 6);
    yearly_performance_array.push_back(yearly_performance);
  }
  record.structured_data["performance_stats"] = yearly_performance_array;
}
