#include "data/record_parser.h"
#include "json.hpp"

void parseCKFields(ParsedRecord& record) {
  // CKレコード（出走別着度数）の解析
  // レコード長: 6870バイト

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
  // 項番10: 血統登録番号 (位置28, 10バイト)
  record.structured_data["pedigree_reg_num"] = record.extractAndConvert(27, 10);
  // 項番11: 馬名 (位置38, 36バイト)
  record.structured_data["horse_name"] = record.extractAndConvert(37, 36);
  // 項番12: 平地本賞金累計 (位置74, 9バイト)
  record.structured_data["flat_purse_total"] = record.extractAndConvert(73, 9);
  // 項番13: 障害本賞金累計 (位置83, 9バイト)
  record.structured_data["obstacle_purse_total"] = record.extractAndConvert(82, 9);
  // 項番14: 平地付加賞金累計 (位置92, 9バイト)
  record.structured_data["flat_added_money_total"] = record.extractAndConvert(91, 9);
  // 項番15: 障害付加賞金累計 (位置101, 9バイト)
  record.structured_data["obstacle_added_money_total"] = record.extractAndConvert(100, 9);
  // 項番16: 平地収得賞金累計 (位置110, 9バイト)
  record.structured_data["flat_earned_money_total"] = record.extractAndConvert(109, 9);
  // 項番17: 障害収得賞金累計 (位置119, 9バイト)
  record.structured_data["obstacle_earned_money_total"] = record.extractAndConvert(118, 9);
  // 項番18: 総合着回数(中央+地方+海外) (位置128, 18バイト(3バイト×6))
  record.structured_data["total_placing_counts"] = record.extractAndConvertArray(127, 3, 6);
  // 項番19: 中央合計着回数 (位置146, 18バイト(3バイト×6))
  record.structured_data["jra_total_placing_counts"] = record.extractAndConvertArray(145, 3, 6);
  // 項番20: 芝直・着回数 (位置164, 18バイト(3バイト×6))
  record.structured_data["turf_straight_placing_counts"] = record.extractAndConvertArray(163, 3, 6);
  // 項番21: 芝右・着回数 (位置182, 18バイト(3バイト×6))
  record.structured_data["turf_right_placing_counts"] = record.extractAndConvertArray(181, 3, 6);
  // 項番22: 芝左・着回数 (位置200, 18バイト(3バイト×6))
  record.structured_data["turf_left_placing_counts"] = record.extractAndConvertArray(199, 3, 6);
  // 項番23: ダ直・着回数 (位置218, 18バイト(3バイト×6))
  record.structured_data["dirt_straight_placing_counts"] = record.extractAndConvertArray(217, 3, 6);
  // 項番24: ダ右・着回数 (位置236, 18バイト(3バイト×6))
  record.structured_data["dirt_right_placing_counts"] = record.extractAndConvertArray(235, 3, 6);
  // 項番25: ダ左・着回数 (位置254, 18バイト(3バイト×6))
  record.structured_data["dirt_left_placing_counts"] = record.extractAndConvertArray(253, 3, 6);
  // 項番26: 障害・着回数 (位置272, 18バイト(3バイト×6))
  record.structured_data["obstacle_placing_counts"] = record.extractAndConvertArray(271, 3, 6);
  // 項番27: 芝良・着回数 (位置290, 18バイト(3バイト×6))
  record.structured_data["turf_good_placing_counts"] = record.extractAndConvertArray(289, 3, 6);
  // 項番28: 芝稍・着回数 (位置308, 18バイト(3バイト×6))
  record.structured_data["turf_yielding_placing_counts"] = record.extractAndConvertArray(307, 3, 6);
  // 項番29: 芝重・着回数 (位置326, 18バイト(3バイト×6))
  record.structured_data["turf_heavy_placing_counts"] = record.extractAndConvertArray(325, 3, 6);
  // 項番30: 芝不・着回数 (位置344, 18バイト(3バイト×6))
  record.structured_data["turf_soft_placing_counts"] = record.extractAndConvertArray(343, 3, 6);
  // 項番31: ダ良・着回数 (位置362, 18バイト(3バイト×6))
  record.structured_data["dirt_good_placing_counts"] = record.extractAndConvertArray(361, 3, 6);
  // 項番32: ダ稍・着回数 (位置380, 18バイト(3バイト×6))
  record.structured_data["dirt_yielding_placing_counts"] = record.extractAndConvertArray(379, 3, 6);
  // 項番33: ダ重・着回数 (位置398, 18バイト(3バイト×6))
  record.structured_data["dirt_heavy_placing_counts"] = record.extractAndConvertArray(397, 3, 6);
  // 項番34: ダ不・着回数 (位置416, 18バイト(3バイト×6))
  record.structured_data["dirt_soft_placing_counts"] = record.extractAndConvertArray(415, 3, 6);
  // 項番35: 障良・着回数 (位置434, 18バイト(3バイト×6))
  record.structured_data["obstacle_good_placing_counts"] = record.extractAndConvertArray(433, 3, 6);
  // 項番36: 障稍・着回数 (位置452, 18バイト(3バイト×6))
  record.structured_data["obstacle_yielding_placing_counts"] = record.extractAndConvertArray(451, 3, 6);
  // 項番37: 障重・着回数 (位置470, 18バイト(3バイト×6))
  record.structured_data["obstacle_heavy_placing_counts"] = record.extractAndConvertArray(469, 3, 6);
  // 項番38: 障不・着回数 (位置488, 18バイト(3バイト×6))
  record.structured_data["obstacle_soft_placing_counts"] = record.extractAndConvertArray(487, 3, 6);
  // 項番39: 芝1200以下・着回数 (位置506, 18バイト(3バイト×6))
  record.structured_data["turf_dist_1200_placing_counts"] = record.extractAndConvertArray(505, 3, 6);
  // 項番40: 芝1201-1400・着回数 (位置524, 18バイト(3バイト×6))
  record.structured_data["turf_dist_1201_1400_placing_counts"] = record.extractAndConvertArray(523, 3, 6);
  // 項番41: 芝1401-1600・着回数 (位置542, 18バイト(3バイト×6))
  record.structured_data["turf_dist_1401_1600_placing_counts"] = record.extractAndConvertArray(541, 3, 6);
  // 項番42: 芝1601-1800・着回数 (位置560, 18バイト(3バイト×6))
  record.structured_data["turf_dist_1601_1800_placing_counts"] = record.extractAndConvertArray(559, 3, 6);
  // 項番43: 芝1801-2000・着回数 (位置578, 18バイト(3バイト×6))
  record.structured_data["turf_dist_1801_2000_placing_counts"] = record.extractAndConvertArray(577, 3, 6);
  // 項番44: 芝2001-2200・着回数 (位置596, 18バイト(3バイト×6))
  record.structured_data["turf_dist_2001_2200_placing_counts"] = record.extractAndConvertArray(595, 3, 6);
  // 項番45: 芝2201-2400・着回数 (位置614, 18バイト(3バイト×6))
  record.structured_data["turf_dist_2201_2400_placing_counts"] = record.extractAndConvertArray(613, 3, 6);
  // 項番46: 芝2401-2800・着回数 (位置632, 18バイト(3バイト×6))
  record.structured_data["turf_dist_2401_2800_placing_counts"] = record.extractAndConvertArray(631, 3, 6);
  // 項番47: 芝2801以上・着回数 (位置650, 18バイト(3バイト×6))
  record.structured_data["turf_dist_2801_placing_counts"] = record.extractAndConvertArray(649, 3, 6);
  // 項番48: ダ1200以下・着回数 (位置668, 18バイト(3バイト×6))
  record.structured_data["dirt_dist_1200_placing_counts"] = record.extractAndConvertArray(667, 3, 6);
  // 項番49: ダ1201-1400・着回数 (位置686, 18バイト(3バイト×6))
  record.structured_data["dirt_dist_1201_1400_placing_counts"] = record.extractAndConvertArray(685, 3, 6);
  // 項番50: ダ1401-1600・着回数 (位置704, 18バイト(3バイト×6))
  record.structured_data["dirt_dist_1401_1600_placing_counts"] = record.extractAndConvertArray(703, 3, 6);
  // 項番51: ダ1601-1800・着回数 (位置722, 18バイト(3バイト×6))
  record.structured_data["dirt_dist_1601_1800_placing_counts"] = record.extractAndConvertArray(721, 3, 6);
  // 項番52: ダ1801-2000・着回数 (位置740, 18バイト(3バイト×6))
  record.structured_data["dirt_dist_1801_2000_placing_counts"] = record.extractAndConvertArray(739, 3, 6);
  // 項番53: ダ2001-2200・着回数 (位置758, 18バイト(3バイト×6))
  record.structured_data["dirt_dist_2001_2200_placing_counts"] = record.extractAndConvertArray(757, 3, 6);
  // 項番54: ダ2201-2400・着回数 (位置776, 18バイト(3バイト×6))
  record.structured_data["dirt_dist_2201_2400_placing_counts"] = record.extractAndConvertArray(775, 3, 6);
  // 項番55: ダ2401-2800・着回数 (位置794, 18バイト(3バイト×6))
  record.structured_data["dirt_dist_2401_2800_placing_counts"] = record.extractAndConvertArray(793, 3, 6);
  // 項番56: ダ2801以上・着回数 (位置812, 18バイト(3バイト×6))
  record.structured_data["dirt_dist_2801_placing_counts"] = record.extractAndConvertArray(811, 3, 6);
  // 項番57: 札幌芝・着回数 (位置830, 18バイト(3バイト×6))
  record.structured_data["sapporo_turf_placing_counts"] = record.extractAndConvertArray(829, 3, 6);
  // 項番58: 函館芝・着回数 (位置848, 18バイト(3バイト×6))
  record.structured_data["hakodate_turf_placing_counts"] = record.extractAndConvertArray(847, 3, 6);
  // 項番59: 福島芝・着回数 (位置866, 18バイト(3バイト×6))
  record.structured_data["fukushima_turf_placing_counts"] = record.extractAndConvertArray(865, 3, 6);
  // 項番60: 新潟芝・着回数 (位置884, 18バイト(3バイト×6))
  record.structured_data["niigata_turf_placing_counts"] = record.extractAndConvertArray(883, 3, 6);
  // 項番61: 東京芝・着回数 (位置902, 18バイト(3バイト×6))
  record.structured_data["tokyo_turf_placing_counts"] = record.extractAndConvertArray(901, 3, 6);
  // 項番62: 中山芝・着回数 (位置920, 18バイト(3バイト×6))
  record.structured_data["nakayama_turf_placing_counts"] = record.extractAndConvertArray(919, 3, 6);
  // 項番63: 中京芝・着回数 (位置938, 18バイト(3バイト×6))
  record.structured_data["chukyo_turf_placing_counts"] = record.extractAndConvertArray(937, 3, 6);
  // 項番64: 京都芝・着回数 (位置956, 18バイト(3バイト×6))
  record.structured_data["kyoto_turf_placing_counts"] = record.extractAndConvertArray(955, 3, 6);
  // 項番65: 阪神芝・着回数 (位置974, 18バイト(3バイト×6))
  record.structured_data["hanshin_turf_placing_counts"] = record.extractAndConvertArray(973, 3, 6);
  // 項番66: 小倉芝・着回数 (位置992, 18バイト(3バイト×6))
  record.structured_data["kokura_turf_placing_counts"] = record.extractAndConvertArray(991, 3, 6);
  // 項番67: 札幌ダ・着回数 (位置1010, 18バイト(3バイト×6))
  record.structured_data["sapporo_dirt_placing_counts"] = record.extractAndConvertArray(1009, 3, 6);
  // 項番68: 函館ダ・着回数 (位置1028, 18バイト(3バイト×6))
  record.structured_data["hakodate_dirt_placing_counts"] = record.extractAndConvertArray(1027, 3, 6);
  // 項番69: 福島ダ・着回数 (位置1046, 18バイト(3バイト×6))
  record.structured_data["fukushima_dirt_placing_counts"] = record.extractAndConvertArray(1045, 3, 6);
  // 項番70: 新潟ダ・着回数 (位置1064, 18バイト(3バイト×6))
  record.structured_data["niigata_dirt_placing_counts"] = record.extractAndConvertArray(1063, 3, 6);
  // 項番71: 東京ダ・着回数 (位置1082, 18バイト(3バイト×6))
  record.structured_data["tokyo_dirt_placing_counts"] = record.extractAndConvertArray(1081, 3, 6);
  // 項番72: 中山ダ・着回数 (位置1100, 18バイト(3バイト×6))
  record.structured_data["nakayama_dirt_placing_counts"] = record.extractAndConvertArray(1099, 3, 6);
  // 項番73: 中京ダ・着回数 (位置1118, 18バイト(3バイト×6))
  record.structured_data["chukyo_dirt_placing_counts"] = record.extractAndConvertArray(1117, 3, 6);
  // 項番74: 京都ダ・着回数 (位置1136, 18バイト(3バイト×6))
  record.structured_data["kyoto_dirt_placing_counts"] = record.extractAndConvertArray(1135, 3, 6);
  // 項番75: 阪神ダ・着回数 (位置1154, 18バイト(3バイト×6))
  record.structured_data["hanshin_dirt_placing_counts"] = record.extractAndConvertArray(1153, 3, 6);
  // 項番76: 小倉ダ・着回数 (位置1172, 18バイト(3バイト×6))
  record.structured_data["kokura_dirt_placing_counts"] = record.extractAndConvertArray(1171, 3, 6);
  // 項番77: 札幌障・着回数 (位置1190, 18バイト(3バイト×6))
  record.structured_data["sapporo_obstacle_placing_counts"] = record.extractAndConvertArray(1189, 3, 6);
  // 項番78: 函館障・着回数 (位置1208, 18バイト(3バイト×6))
  record.structured_data["hakodate_obstacle_placing_counts"] = record.extractAndConvertArray(1207, 3, 6);
  // 項番79: 福島障・着回数 (位置1226, 18バイト(3バイト×6))
  record.structured_data["fukushima_obstacle_placing_counts"] = record.extractAndConvertArray(1225, 3, 6);
  // 項番80: 新潟障・着回数 (位置1244, 18バイト(3バイト×6))
  record.structured_data["niigata_obstacle_placing_counts"] = record.extractAndConvertArray(1243, 3, 6);
  // 項番81: 東京障・着回数 (位置1262, 18バイト(3バイト×6))
  record.structured_data["tokyo_obstacle_placing_counts"] = record.extractAndConvertArray(1261, 3, 6);
  // 項番82: 中山障・着回数 (位置1280, 18バイト(3バイト×6))
  record.structured_data["nakayama_obstacle_placing_counts"] = record.extractAndConvertArray(1279, 3, 6);
  // 項番83: 中京障・着回数 (位置1298, 18バイト(3バイト×6))
  record.structured_data["chukyo_obstacle_placing_counts"] = record.extractAndConvertArray(1297, 3, 6);
  // 項番84: 京都障・着回数 (位置1316, 18バイト(3バイト×6))
  record.structured_data["kyoto_obstacle_placing_counts"] = record.extractAndConvertArray(1315, 3, 6);
  // 項番85: 阪神障・着回数 (位置1334, 18バイト(3バイト×6))
  record.structured_data["hanshin_obstacle_placing_counts"] = record.extractAndConvertArray(1333, 3, 6);
  // 項番86: 小倉障・着回数 (位置1352, 18バイト(3バイト×6))
  record.structured_data["kokura_obstacle_placing_counts"] = record.extractAndConvertArray(1351, 3, 6);
  // 項番87: 脚質傾向 (位置1370, 12バイト(3バイト×4))
  record.structured_data["running_style_counts"] = record.extractAndConvertArray(1369, 3, 4);
  // 項番88: 登録レース数 (位置1382, 3バイト)
  record.structured_data["registered_race_count"] = record.extractAndConvert(1381, 3);
  // 項番89: 騎手コード (位置1385, 5バイト)
  record.structured_data["jockey_code"] = record.extractAndConvert(1384, 5);
  // 項番90: 騎手名 (位置1390, 34バイト)
  record.structured_data["jockey_name"] = record.extractAndConvert(1389, 34);
  // 項番91: 騎手成績情報
  {
    nlohmann::json jockey_stats = nlohmann::json::array();
    const int base_offset = 1423;
    const int block_size = 1220;
    for (int i = 0; i < 2; ++i) {
      nlohmann::json stats;
      int block_start_offset = base_offset + i * block_size;
      // 項番91a: 設定年 (位置1424, 4バイト)
      stats["year"] = record.extractAndConvert(block_start_offset + 0, 4);
      // 項番91b: 平地本賞金合計 (位置1428, 10バイト)
      stats["flat_prize_money"] = record.extractAndConvert(block_start_offset + 4, 10);
      // 項番91c: 障害本賞金合計 (位置1438, 10バイト)
      stats["obstacle_prize_money"] = record.extractAndConvert(block_start_offset + 14, 10);
      // 項番91d: 平地付加賞金合計 (位置1448, 10バイト)
      stats["flat_added_money"] = record.extractAndConvert(block_start_offset + 24, 10);
      // 項番91e: 障害付加賞金合計 (位置1458, 10バイト)
      stats["obstacle_added_money"] = record.extractAndConvert(block_start_offset + 34, 10);
      // 項番91f: 芝着回数 (位置1468, 30バイト(5バイト×6))
      stats["turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 44, 5, 6);
      // 項番91g: ダート着回数 (位置1498, 30バイト(5バイト×6))
      stats["dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 74, 5, 6);
      // 項番91h: 障害着回数 (位置1528, 24バイト(4バイト×6))
      stats["obstacle_placing_counts"] = record.extractAndConvertArray(block_start_offset + 104, 4, 6);
      // 項番91i: 芝1200以下・着回数 (位置1552, 24バイト(4バイト×6))
      stats["turf_dist_1200_placing_counts"] = record.extractAndConvertArray(block_start_offset + 128, 4, 6);
      // 項番91j: 芝1201-1400・着回数 (位置1576, 24バイト(4バイト×6))
      stats["turf_dist_1201_1400_placing_counts"] = record.extractAndConvertArray(block_start_offset + 152, 4, 6);
      // 項番91k: 芝1401-1600・着回数 (位置1600, 24バイト(4バイト×6))
      stats["turf_dist_1401_1600_placing_counts"] = record.extractAndConvertArray(block_start_offset + 176, 4, 6);
      // 項番91l: 芝1601-1800・着回数 (位置1624, 24バイト(4バイト×6))
      stats["turf_dist_1601_1800_placing_counts"] = record.extractAndConvertArray(block_start_offset + 200, 4, 6);
      // 項番91m: 芝1801-2000・着回数 (位置1648, 24バイト(4バイト×6))
      stats["turf_dist_1801_2000_placing_counts"] = record.extractAndConvertArray(block_start_offset + 224, 4, 6);
      // 項番91n: 芝2001-2200・着回数 (位置1672, 24バイト(4バイト×6))
      stats["turf_dist_2001_2200_placing_counts"] = record.extractAndConvertArray(block_start_offset + 248, 4, 6);
      // 項番91o: 芝2201-2400・着回数 (位置1696, 24バイト(4バイト×6))
      stats["turf_dist_2201_2400_placing_counts"] = record.extractAndConvertArray(block_start_offset + 272, 4, 6);
      // 項番91p: 芝2401-2800・着回数 (位置1720, 24バイト(4バイト×6))
      stats["turf_dist_2401_2800_placing_counts"] = record.extractAndConvertArray(block_start_offset + 296, 4, 6);
      // 項番91q: 芝2801以上・着回数 (位置1744, 24バイト(4バイト×6))
      stats["turf_dist_2801_placing_counts"] = record.extractAndConvertArray(block_start_offset + 320, 4, 6);
      // 項番91r: ダ1200以下・着回数 (位置1768, 24バイト(4バイト×6))
      stats["dirt_dist_1200_placing_counts"] = record.extractAndConvertArray(block_start_offset + 344, 4, 6);
      // 項番91s: ダ1201-1400・着回数 (位置1792, 24バイト(4バイト×6))
      stats["dirt_dist_1201_1400_placing_counts"] = record.extractAndConvertArray(block_start_offset + 368, 4, 6);
      // 項番91t: ダ1401-1600・着回数 (位置1816, 24バイト(4バイト×6))
      stats["dirt_dist_1401_1600_placing_counts"] = record.extractAndConvertArray(block_start_offset + 392, 4, 6);
      // 項番91u: ダ1601-1800・着回数 (位置1840, 24バイト(4バイト×6))
      stats["dirt_dist_1601_1800_placing_counts"] = record.extractAndConvertArray(block_start_offset + 416, 4, 6);
      // 項番91v: ダ1801-2000・着回数 (位置1864, 24バイト(4バイト×6))
      stats["dirt_dist_1801_2000_placing_counts"] = record.extractAndConvertArray(block_start_offset + 440, 4, 6);
      // 項番91w: ダ2001-2200・着回数 (位置1888, 24バイト(4バイト×6))
      stats["dirt_dist_2001_2200_placing_counts"] = record.extractAndConvertArray(block_start_offset + 464, 4, 6);
      // 項番91x: ダ2201-2400・着回数 (位置1912, 24バイト(4バイト×6))
      stats["dirt_dist_2201_2400_placing_counts"] = record.extractAndConvertArray(block_start_offset + 488, 4, 6);
      // 項番91y: ダ2401-2800・着回数 (位置1936, 24バイト(4バイト×6))
      stats["dirt_dist_2401_2800_placing_counts"] = record.extractAndConvertArray(block_start_offset + 512, 4, 6);
      // 項番91z: ダ2801以上・着回数 (位置1960, 24バイト(4バイト×6))
      stats["dirt_dist_2801_placing_counts"] = record.extractAndConvertArray(block_start_offset + 536, 4, 6);
      // 項番91aa: 札幌芝・着回数 (位置1984, 24バイト(4バイト×6))
      stats["sapporo_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 560, 4, 6);
      // 項番91ab: 函館芝・着回数 (位置2008, 24バイト(4バイト×6))
      stats["hakodate_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 584, 4, 6);
      // 項番91ac: 福島芝・着回数 (位置2032, 24バイト(4バイト×6))
      stats["fukushima_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 608, 4, 6);
      // 項番91ad: 新潟芝・着回数 (位置2056, 24バイト(4バイト×6))
      stats["niigata_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 632, 4, 6);
      // 項番91ae: 東京芝・着回数 (位置2080, 24バイト(4バイト×6))
      stats["tokyo_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 656, 4, 6);
      // 項番91af: 中山芝・着回数 (位置2104, 24バイト(4バイト×6))
      stats["nakayama_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 680, 4, 6);
      // 項番91ag: 中京芝・着回数 (位置2128, 24バイト(4バイト×6))
      stats["chukyo_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 704, 4, 6);
      // 項番91ah: 京都芝・着回数 (位置2152, 24バイト(4バイト×6))
      stats["kyoto_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 728, 4, 6);
      // 項番91ai: 阪神芝・着回数 (位置2176, 24バイト(4バイト×6))
      stats["hanshin_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 752, 4, 6);
      // 項番91aj: 小倉芝・着回数 (位置2200, 24バイト(4バイト×6))
      stats["kokura_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 776, 4, 6);
      // 項番91ak: 札幌ダ・着回数 (位置2224, 24バイト(4バイト×6))
      stats["sapporo_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 800, 4, 6);
      // 項番91al: 函館ダ・着回数 (位置2248, 24バイト(4バイト×6))
      stats["hakodate_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 824, 4, 6);
      // 項番91am: 福島ダ・着回数 (位置2272, 24バイト(4バイト×6))
      stats["fukushima_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 848, 4, 6);
      // 項番91an: 新潟ダ・着回数 (位置2296, 24バイト(4バイト×6))
      stats["niigata_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 872, 4, 6);
      // 項番91ao: 東京ダ・着回数 (位置2320, 24バイト(4バイト×6))
      stats["tokyo_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 896, 4, 6);
      // 項番91ap: 中山ダ・着回数 (位置2344, 24バイト(4バイト×6))
      stats["nakayama_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 920, 4, 6);
      // 項番91aq: 中京ダ・着回数 (位置2368, 24バイト(4バイト×6))
      stats["chukyo_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 944, 4, 6);
      // 項番91ar: 京都ダ・着回数 (位置2392, 24バイト(4バイト×6))
      stats["kyoto_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 968, 4, 6);
      // 項番91as: 阪神ダ・着回数 (位置2416, 24バイト(4バイト×6))
      stats["hanshin_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 992, 4, 6);
      // 項番91at: 小倉ダ・着回数 (位置2440, 24バイト(4バイト×6))
      stats["kokura_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 1016, 4, 6);
      // 項番91au: 札幌障・着回数 (位置2464, 18バイト(3バイト×6))
      stats["sapporo_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1040, 3, 6);
      // 項番91av: 函館障・着回数 (位置2482, 18バイト(3バイト×6))
      stats["hakodate_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1058, 3, 6);
      // 項番91aw: 福島障・着回数 (位置2500, 18バイト(3バイト×6))
      stats["fukushima_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1076, 3, 6);
      // 項番91ax: 新潟障・着回数 (位置2518, 18バイト(3バイト×6))
      stats["niigata_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1094, 3, 6);
      // 項番91ay: 東京障・着回数 (位置2536, 18バイト(3バイト×6))
      stats["tokyo_obstacle_placing_counts"] = record.extractAndConvertArray(block_start_offset + 1112, 3, 6);
      // 項番91az: 中山障・着回数 (位置2554, 18バイト(3バイト×6))
      stats["nakayama_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1130, 3, 6);
      // 項番91ba: 中京障・着回数 (位置2572, 18バイト(3バイト×6))
      stats["chukyo_obstacle_placing_counts"] = record.extractAndConvertArray(block_start_offset + 1148, 3, 6);
      // 項番91bb: 京都障・着回数 (位置2590, 18バイト(3バイト×6))
      stats["kyoto_obstacle_placing_counts"] = record.extractAndConvertArray(block_start_offset + 1166, 3, 6);
      // 項番91bc: 阪神障・着回数 (位置2608, 18バイト(3バイト×6))
      stats["hanshin_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1184, 3, 6);
      // 項番91bd: 小倉障・着回数 (位置2626, 18バイト(3バイト×6))
      stats["kokura_obstacle_placing_counts"] = record.extractAndConvertArray(block_start_offset + 1202, 3, 6);
      jockey_stats.push_back(stats);
    }
    record.structured_data["jockey_performance_stats"] = jockey_stats;
  }
  // 項番92: 調教師コード (位置3864, 5バイト)
  record.structured_data["trainer_code"] = record.extractAndConvert(3863, 5);
  // 項番93: 調教師名 (位置3869, 34バイト)
  record.structured_data["trainer_name"] = record.extractAndConvert(3868, 34);
  // 項番94: 調教師成績情報
  {
    nlohmann::json trainer_stats = nlohmann::json::array();
    const int base_offset = 3902;
    const int block_size = 1220;
    for (int i = 0; i < 2; ++i) {
      nlohmann::json stats;
      int block_start_offset = base_offset + i * block_size;
      // 項番94a: 設定年 (位置3903, 4バイト)
      stats["year"] = record.extractAndConvert(block_start_offset + 0, 4);
      // 項番94b: 平地本賞金合計 (位置3907, 10バイト)
      stats["flat_prize_money"] = record.extractAndConvert(block_start_offset + 4, 10);
      // 項番94c: 障害本賞金合計 (位置3917, 10バイト)
      stats["obstacle_prize_money"] = record.extractAndConvert(block_start_offset + 14, 10);
      // 項番94d: 平地付加賞金合計 (位置3927, 10バイト)
      stats["flat_added_money"] = record.extractAndConvert(block_start_offset + 24, 10);
      // 項番94e: 障害付加賞金合計 (位置3937, 10バイト)
      stats["obstacle_added_money"] = record.extractAndConvert(block_start_offset + 34, 10);
      // 項番94f: 芝着回数 (位置3947, 30バイト(5バイト×6))
      stats["turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 44, 5, 6);
      // 項番94g: ダート着回数 (位置3977, 30バイト(5バイト×6))
      stats["dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 74, 5, 6);
      // 項番94h: 障害着回数 (位置4007, 24バイト(4バイト×6))
      stats["obstacle_placing_counts"] = record.extractAndConvertArray(block_start_offset + 104, 4, 6);
      // 項番94i: 芝1200以下・着回数 (位置4031, 24バイト(4バイト×6))
      stats["turf_dist_1200_placing_counts"] = record.extractAndConvertArray(block_start_offset + 128, 4, 6);
      // 項番94j: 芝1201-1400・着回数 (位置4055, 24バイト(4バイト×6))
      stats["turf_dist_1201_1400_placing_counts"] = record.extractAndConvertArray(block_start_offset + 152, 4, 6);
      // 項番94k: 芝1401-1600・着回数 (位置4079, 24バイト(4バイト×6))
      stats["turf_dist_1401_1600_placing_counts"] = record.extractAndConvertArray(block_start_offset + 176, 4, 6);
      // 項番94l: 芝1601-1800・着回数 (位置4103, 24バイト(4バイト×6))
      stats["turf_dist_1601_1800_placing_counts"] = record.extractAndConvertArray(block_start_offset + 200, 4, 6);
      // 項番94m: 芝1801-2000・着回数 (位置4127, 24バイト(4バイト×6))
      stats["turf_dist_1801_2000_placing_counts"] = record.extractAndConvertArray(block_start_offset + 224, 4, 6);
      // 項番94n: 芝2001-2200・着回数 (位置4151, 24バイト(4バイト×6))
      stats["turf_dist_2001_2200_placing_counts"] = record.extractAndConvertArray(block_start_offset + 248, 4, 6);
      // 項番94o: 芝2201-2400・着回数 (位置4175, 24バイト(4バイト×6))
      stats["turf_dist_2201_2400_placing_counts"] = record.extractAndConvertArray(block_start_offset + 272, 4, 6);
      // 項番94p: 芝2401-2800・着回数 (位置4199, 24バイト(4バイト×6))
      stats["turf_dist_2401_2800_placing_counts"] = record.extractAndConvertArray(block_start_offset + 296, 4, 6);
      // 項番94q: 芝2801以上・着回数 (位置4223, 24バイト(4バイト×6))
      stats["turf_dist_2801_placing_counts"] = record.extractAndConvertArray(block_start_offset + 320, 4, 6);
      // 項番94r: ダ1200以下・着回数 (位置4247, 24バイト(4バイト×6))
      stats["dirt_dist_1200_placing_counts"] = record.extractAndConvertArray(block_start_offset + 344, 4, 6);
      // 項番94s: ダ1201-1400・着回数 (位置4271, 24バイト(4バイト×6))
      stats["dirt_dist_1201_1400_placing_counts"] = record.extractAndConvertArray(block_start_offset + 368, 4, 6);
      // 項番94t: ダ1401-1600・着回数 (位置4295, 24バイト(4バイト×6))
      stats["dirt_dist_1401_1600_placing_counts"] = record.extractAndConvertArray(block_start_offset + 392, 4, 6);
      // 項番94u: ダ1601-1800・着回数 (位置4319, 24バイト(4バイト×6))
      stats["dirt_dist_1601_1800_placing_counts"] = record.extractAndConvertArray(block_start_offset + 416, 4, 6);
      // 項番94v: ダ1801-2000・着回数 (位置4343, 24バイト(4バイト×6))
      stats["dirt_dist_1801_2000_placing_counts"] = record.extractAndConvertArray(block_start_offset + 440, 4, 6);
      // 項番94w: ダ2001-2200・着回数 (位置4367, 24バイト(4バイト×6))
      stats["dirt_dist_2001_2200_placing_counts"] = record.extractAndConvertArray(block_start_offset + 464, 4, 6);
      // 項番94x: ダ2201-2400・着回数 (位置4391, 24バイト(4バイト×6))
      stats["dirt_dist_2201_2400_placing_counts"] = record.extractAndConvertArray(block_start_offset + 488, 4, 6);
      // 項番94y: ダ2401-2800・着回数 (位置4415, 24バイト(4バイト×6))
      stats["dirt_dist_2401_2800_placing_counts"] = record.extractAndConvertArray(block_start_offset + 512, 4, 6);
      // 項番94z: ダ2801以上・着回数 (位置4439, 24バイト(4バイト×6))
      stats["dirt_dist_2801_placing_counts"] = record.extractAndConvertArray(block_start_offset + 536, 4, 6);
      // 項番94aa: 札幌芝・着回数 (位置4463, 24バイト(4バイト×6))
      stats["sapporo_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 560, 4, 6);
      // 項番94ab: 函館芝・着回数 (位置4487, 24バイト(4バイト×6))
      stats["hakodate_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 584, 4, 6);
      // 項番94ac: 福島芝・着回数 (位置4511, 24バイト(4バイト×6))
      stats["fukushima_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 608, 4, 6);
      // 項番94ad: 新潟芝・着回数 (位置4535, 24バイト(4バイト×6))
      stats["niigata_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 632, 4, 6);
      // 項番94ae: 東京芝・着回数 (位置4559, 24バイト(4バイト×6))
      stats["tokyo_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 656, 4, 6);
      // 項番94af: 中山芝・着回数 (位置4583, 24バイト(4バイト×6))
      stats["nakayama_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 680, 4, 6);
      // 項番94ag: 中京芝・着回数 (位置4607, 24バイト(4バイト×6))
      stats["chukyo_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 704, 4, 6);
      // 項番94ah: 京都芝・着回数 (位置4631, 24バイト(4バイト×6))
      stats["kyoto_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 728, 4, 6);
      // 項番94ai: 阪神芝・着回数 (位置4655, 24バイト(4バイト×6))
      stats["hanshin_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 752, 4, 6);
      // 項番94aj: 小倉芝・着回数 (位置4679, 24バイト(4バイト×6))
      stats["kokura_turf_placing_counts"] = record.extractAndConvertArray(block_start_offset + 776, 4, 6);
      // 項番94ak: 札幌ダ・着回数 (位置4703, 24バイト(4バイト×6))
      stats["sapporo_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 800, 4, 6);
      // 項番94al: 函館ダ・着回数 (位置4727, 24バイト(4バイト×6))
      stats["hakodate_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 824, 4, 6);
      // 項番94am: 福島ダ・着回数 (位置4751, 24バイト(4バイト×6))
      stats["fukushima_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 848, 4, 6);
      // 項番94an: 新潟ダ・着回数 (位置4775, 24バイト(4バイト×6))
      stats["niigata_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 872, 4, 6);
      // 項番94ao: 東京ダ・着回数 (位置4799, 24バイト(4バイト×6))
      stats["tokyo_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 896, 4, 6);
      // 項番94ap: 中山ダ・着回数 (位置4823, 24バイト(4バイト×6))
      stats["nakayama_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 920, 4, 6);
      // 項番94aq: 中京ダ・着回数 (位置4847, 24バイト(4バイト×6))
      stats["chukyo_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 944, 4, 6);
      // 項番94ar: 京都ダ・着回数 (位置4871, 24バイト(4バイト×6))
      stats["kyoto_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 968, 4, 6);
      // 項番94as: 阪神ダ・着回数 (位置4895, 24バイト(4バイト×6))
      stats["hanshin_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 992, 4, 6);
      // 項番94at: 小倉ダ・着回数 (位置4919, 24バイト(4バイト×6))
      stats["kokura_dirt_placing_counts"] = record.extractAndConvertArray(block_start_offset + 1016, 4, 6);
      // 項番94au: 札幌障・着回数 (位置4943, 18バイト(3バイト×6))
      stats["sapporo_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1040, 3, 6);
      // 項番94av: 函館障・着回数 (位置4961, 18バイト(3バイト×6))
      stats["hakodate_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1058, 3, 6);
      // 項番94aw: 福島障・着回数 (位置4979, 18バイト(3バイト×6))
      stats["fukushima_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1076, 3, 6);
      // 項番94ax: 新潟障・着回数 (位置4997, 18バイト(3バイト×6))
      stats["niigata_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1094, 3, 6);
      // 項番94ay: 東京障・着回数 (位置5015, 18バイト(3バイト×6))
      stats["tokyo_obstacle_placing_counts"] = record.extractAndConvertArray(block_start_offset + 1112, 3, 6);
      // 項番94az: 中山障・着回数 (位置5033, 18バイト(3バイト×6))
      stats["nakayama_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1130, 3, 6);
      // 項番94ba: 中京障・着回数 (位置5051, 18バイト(3バイト×6))
      stats["chukyo_obstacle_placing_counts"] = record.extractAndConvertArray(block_start_offset + 1148, 3, 6);
      // 項番94bb: 京都障・着回数 (位置5069, 18バイト(3バイト×6))
      stats["kyoto_obstacle_placing_counts"] = record.extractAndConvertArray(block_start_offset + 1166, 3, 6);
      // 項番94bc: 阪神障・着回数 (位置5087, 18バイト(3バイト×6))
      stats["hanshin_obstacle_placing_counts"] =
          record.extractAndConvertArray(block_start_offset + 1184, 3, 6);
      // 項番94bd: 小倉障・着回数 (位置5105, 18バイト(3バイト×6))
      stats["kokura_obstacle_placing_counts"] = record.extractAndConvertArray(block_start_offset + 1202, 3, 6);
      trainer_stats.push_back(stats);
    }
    record.structured_data["trainer_performance_stats"] = trainer_stats;
  }
  // 項番95: 馬主コード (位置6343, 6バイト)
  record.structured_data["owner_code"] = record.extractAndConvert(6342, 6);
  // 項番96: 馬主名(法人格有) (位置6349, 64バイト)
  record.structured_data["owner_name_with_corp"] = record.extractAndConvert(6348, 64);
  // 項番97: 馬主名(法人格無) (位置6413, 64バイト)
  record.structured_data["owner_name_individual"] = record.extractAndConvert(6412, 64);
  // 項番98: 馬主成績情報
  {
    nlohmann::json owner_stats = nlohmann::json::array();
    const int base_offset = 6476;
    const int block_size = 60;
    for (int i = 0; i < 2; ++i) {
      nlohmann::json stats;
      int current_offset = base_offset + i * block_size;
      // 項番98a: 設定年 (位置6477, 4バイト)
      stats["year"] = record.extractAndConvert(current_offset + 0, 4);
      // 項番98b: 本賞金合計 (位置6481, 10バイト)
      stats["prize_money"] = record.extractAndConvert(current_offset + 4, 10);
      // 項番98c: 付加賞金合計 (位置6491, 10バイト)
      stats["added_money"] = record.extractAndConvert(current_offset + 14, 10);
      // 項番98d: 着回数 (位置6501, 36バイト(6バイト×6))
      stats["placing_counts"] = record.extractAndConvertArray(current_offset + 24, 6, 6);
      owner_stats.push_back(stats);
    }
    record.structured_data["owner_performance_stats"] = owner_stats;
  }
  // 項番99: 生産者コード (位置6597, 8バイト)
  record.structured_data["breeder_code"] = record.extractAndConvert(6596, 8);
  // 項番100: 生産者名(法人格有) (位置6605, 72バイト)
  record.structured_data["breeder_name_with_corp"] = record.extractAndConvert(6604, 72);
  // 項番101: 生産者名(法人格無) (位置6677, 72バイト)
  record.structured_data["breeder_name_individual"] = record.extractAndConvert(6676, 72);
  // 項番102: 生産者成績情報
  {
    nlohmann::json breeder_stats = nlohmann::json::array();
    const int base_offset = 6748;
    const int block_size = 60;
    for (int i = 0; i < 2; ++i) {
      nlohmann::json stats;
      int current_offset = base_offset + i * block_size;
      // 項番102a: 設定年 (位置6749, 4バイト)
      stats["year"] = record.extractAndConvert(current_offset + 0, 4);
      // 項番102b: 本賞金合計 (位置6753, 10バイト)
      stats["prize_money"] = record.extractAndConvert(current_offset + 4, 10);
      // 項番102c: 付加賞金合計 (位置6763, 10バイト)
      stats["added_money"] = record.extractAndConvert(current_offset + 14, 10);
      // 項番102d: 着回数 (位置6773, 36バイト(6バイト×6))
      stats["placing_counts"] = record.extractAndConvertArray(current_offset + 24, 6, 6);
      breeder_stats.push_back(stats);
    }
    record.structured_data["breeder_performance_stats"] = breeder_stats;
  }
}
