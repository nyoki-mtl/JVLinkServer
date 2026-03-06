#include "data/record_parser.h"
#include "json.hpp"

void parseUMFields(ParsedRecord& record) {
  // UM (競走馬マスタ) レコードの解析
  // レコード長: 1,609バイト

  // 項番2: データ区分 (位置3, 1バイト)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置4, 8バイト)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 血統登録番号 (位置12, 10バイト)
  record.structured_data["pedigree_reg_num"] = record.extractAndConvert(11, 10);
  // 項番5: 競走馬抹消区分 (位置22, 1バイト)
  record.structured_data["deregistration_flag"] = record.extractAndConvert(21, 1);
  // 項番6: 競走馬登録年月日 (位置23, 8バイト)
  record.structured_data["registration_date"] = record.extractAndConvert(22, 8);
  // 項番7: 競走馬抹消年月日 (位置31, 8バイト)
  record.structured_data["deregistration_date"] = record.extractAndConvert(30, 8);
  // 項番8: 生年月日 (位置39, 8バイト)
  record.structured_data["birth_date"] = record.extractAndConvert(38, 8);
  // 項番9: 馬名 (位置47, 36バイト)
  record.structured_data["horse_name"] = record.extractAndConvert(46, 36);
  // 項番10: 馬名半角カナ (位置83, 36バイト)
  record.structured_data["horse_name_kana"] = record.extractAndConvert(82, 36);
  // 項番11: 馬名欧字 (位置119, 60バイト)
  record.structured_data["horse_name_english"] = record.extractAndConvert(118, 60);
  // 項番12: JRA施設在きゅうフラグ (位置179, 1バイト)
  record.structured_data["jra_facility_flag"] = record.extractAndConvert(178, 1);
  // 項番13: 予備 (位置180, 19バイト) - スキップ
  // 項番14: 馬記号コード (位置199, 2バイト)
  record.structured_data["horse_symbol_code"] = record.extractAndConvert(198, 2);
  // 項番15: 性別コード (位置201, 1バイト)
  record.structured_data["sex_code"] = record.extractAndConvert(200, 1);
  // 項番16: 品種コード (位置202, 1バイト)
  record.structured_data["breed_code"] = record.extractAndConvert(201, 1);
  // 項番17: 毛色コード (位置203, 2バイト)
  record.structured_data["coat_color_code"] = record.extractAndConvert(202, 2);
  // 項番18: 3代血統情報 (位置205, 644バイト)
  nlohmann::json bloodline_info_array = nlohmann::json::array();
  for (int i = 0; i < 14; i++) {
    size_t base_pos = 204 + (i * 46);
    nlohmann::json bloodline_entry;
    // 項番18a: 繁殖登録番号 (ブロック内位置1, 10バイト)
    bloodline_entry["breeding_reg_num"] = record.extractAndConvert(base_pos, 10);
    // 項番18b: 馬名 (ブロック内位置11, 36バイト)
    bloodline_entry["horse_name"] = record.extractAndConvert(base_pos + 10, 36);
    bloodline_info_array.push_back(bloodline_entry);
  }
  record.structured_data["pedigree_3gen"] = bloodline_info_array;
  // 項番19: 東西所属コード (位置849, 1バイト)
  record.structured_data["affiliation_code"] = record.extractAndConvert(848, 1);
  // 項番20: 調教師コード (位置850, 5バイト)
  record.structured_data["trainer_code"] = record.extractAndConvert(849, 5);
  // 項番21: 調教師名略称 (位置855, 8バイト)
  record.structured_data["trainer_name_short"] = record.extractAndConvert(854, 8);
  // 項番22: 招待地域名 (位置863, 20バイト)
  record.structured_data["invitation_area_name"] = record.extractAndConvert(862, 20);
  // 項番23: 生産者コード (位置883, 8バイト)
  record.structured_data["breeder_code"] = record.extractAndConvert(882, 8);
  // 項番24: 生産者名(法人格無) (位置891, 72バイト)
  record.structured_data["breeder_name"] = record.extractAndConvert(890, 72);
  // 項番25: 産地名 (位置963, 20バイト)
  record.structured_data["birthplace_name"] = record.extractAndConvert(962, 20);
  // 項番26: 馬主コード (位置983, 6バイト)
  record.structured_data["owner_code"] = record.extractAndConvert(982, 6);
  // 項番27: 馬主名(法人格無) (位置989, 64バイト)
  record.structured_data["owner_name"] = record.extractAndConvert(988, 64);
  // 項番28: 平地本賞金累計 (位置1053, 9バイト)
  record.structured_data["flat_prize_money_total"] = record.extractAndConvert(1052, 9);
  // 項番29: 障害本賞金累計 (位置1062, 9バイト)
  record.structured_data["steeplechase_prize_money_total"] = record.extractAndConvert(1061, 9);
  // 項番30: 平地付加賞金累計 (位置1071, 9バイト)
  record.structured_data["flat_added_money_total"] = record.extractAndConvert(1070, 9);
  // 項番31: 障害付加賞金累計 (位置1080, 9バイト)
  record.structured_data["steeplechase_added_money_total"] = record.extractAndConvert(1079, 9);
  // 項番32: 平地収得賞金累計 (位置1089, 9バイト)
  record.structured_data["flat_earnings_total"] = record.extractAndConvert(1088, 9);
  // 項番33: 障害収得賞金累計 (位置1098, 9バイト)
  record.structured_data["steeplechase_earnings_total"] = record.extractAndConvert(1097, 9);
  // 項番34: 総合着回数 (位置1107, 18バイト)
  record.structured_data["overall_placing_counts"] = record.extractAndConvertArray(1106, 3, 6);
  // 項番35: 中央合計着回数 (位置1125, 18バイト)
  record.structured_data["central_placing_counts"] = record.extractAndConvertArray(1124, 3, 6);
  // 項番36: 芝直線着回数 (位置1143, 18バイト)
  record.structured_data["turf_straight_placing_counts"] = record.extractAndConvertArray(1142, 3, 6);
  // 項番37: 芝右回り着回数 (位置1161, 18バイト)
  record.structured_data["turf_right_placing_counts"] = record.extractAndConvertArray(1160, 3, 6);
  // 項番38: 芝左回り着回数 (位置1179, 18バイト)
  record.structured_data["turf_left_placing_counts"] = record.extractAndConvertArray(1178, 3, 6);
  // 項番39: ダート直線着回数 (位置1197, 18バイト)
  record.structured_data["dirt_straight_placing_counts"] = record.extractAndConvertArray(1196, 3, 6);
  // 項番40: ダート右回り着回数 (位置1215, 18バイト)
  record.structured_data["dirt_right_placing_counts"] = record.extractAndConvertArray(1214, 3, 6);
  // 項番41: ダート左回り着回数 (位置1233, 18バイト)
  record.structured_data["dirt_left_placing_counts"] = record.extractAndConvertArray(1232, 3, 6);
  // 項番42: 障害着回数 (位置1251, 18バイト)
  record.structured_data["steeplechase_placing_counts"] = record.extractAndConvertArray(1250, 3, 6);
  // 項番43: 芝良着回数 (位置1269, 18バイト)
  record.structured_data["turf_good_placing_counts"] = record.extractAndConvertArray(1268, 3, 6);
  // 項番44: 芝稍重着回数 (位置1287, 18バイト)
  record.structured_data["turf_slightly_heavy_placing_counts"] = record.extractAndConvertArray(1286, 3, 6);
  // 項番45: 芝重着回数 (位置1305, 18バイト)
  record.structured_data["turf_heavy_placing_counts"] = record.extractAndConvertArray(1304, 3, 6);
  // 項番46: 芝不良着回数 (位置1323, 18バイト)
  record.structured_data["turf_bad_placing_counts"] = record.extractAndConvertArray(1322, 3, 6);
  // 項番47: ダート良着回数 (位置1341, 18バイト)
  record.structured_data["dirt_good_placing_counts"] = record.extractAndConvertArray(1340, 3, 6);
  // 項番48: ダート稍重着回数 (位置1359, 18バイト)
  record.structured_data["dirt_slightly_heavy_placing_counts"] = record.extractAndConvertArray(1358, 3, 6);
  // 項番49: ダート重着回数 (位置1377, 18バイト)
  record.structured_data["dirt_heavy_placing_counts"] = record.extractAndConvertArray(1376, 3, 6);
  // 項番50: ダート不良着回数 (位置1395, 18バイト)
  record.structured_data["dirt_bad_placing_counts"] = record.extractAndConvertArray(1394, 3, 6);
  // 項番51: 障害良着回数 (位置1413, 18バイト)
  record.structured_data["steeplechase_good_placing_counts"] = record.extractAndConvertArray(1412, 3, 6);
  // 項番52: 障害稍重着回数 (位置1431, 18バイト)
  record.structured_data["steeplechase_slightly_heavy_placing_counts"] = record.extractAndConvertArray(1430, 3, 6);
  // 項番53: 障害重着回数 (位置1449, 18バイト)
  record.structured_data["steeplechase_heavy_placing_counts"] = record.extractAndConvertArray(1448, 3, 6);
  // 項番54: 障害不良着回数 (位置1467, 18バイト)
  record.structured_data["steeplechase_bad_placing_counts"] = record.extractAndConvertArray(1466, 3, 6);
  // 項番55: 芝1600m以下着回数 (位置1485, 18バイト)
  record.structured_data["turf_short_placing_counts"] = record.extractAndConvertArray(1484, 3, 6);
  // 項番56: 芝2200m以下着回数 (位置1503, 18バイト)
  record.structured_data["turf_mid_placing_counts"] = record.extractAndConvertArray(1502, 3, 6);
  // 項番57: 芝2200m超着回数 (位置1521, 18バイト)
  record.structured_data["turf_long_placing_counts"] = record.extractAndConvertArray(1520, 3, 6);
  // 項番58: ダート1600m以下着回数 (位置1539, 18バイト)
  record.structured_data["dirt_short_placing_counts"] = record.extractAndConvertArray(1538, 3, 6);
  // 項番59: ダート2200m以下着回数 (位置1557, 18バイト)
  record.structured_data["dirt_mid_placing_counts"] = record.extractAndConvertArray(1556, 3, 6);
  // 項番60: ダート2200m超着回数 (位置1575, 18バイト)
  record.structured_data["dirt_long_placing_counts"] = record.extractAndConvertArray(1574, 3, 6);
  // 項番61: 脚質傾向 (位置1593, 12バイト)
  record.structured_data["running_style_counts"] = record.extractAndConvertArray(1592, 3, 4);
  // 項番62: 登録レース数 (位置1605, 3バイト)
  record.structured_data["registered_race_count"] = record.extractAndConvert(1604, 3);
}
