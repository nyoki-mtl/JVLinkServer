#include "data/record_parser.h"
#include "json.hpp"

void parseHNFields(ParsedRecord& record) {
  // HNレコード（繁殖馬マスタ）
  // レコード長: 251バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 繁殖登録番号 (位置: 12, サイズ: 10)
  record.structured_data["breeding_reg_num"] = record.extractAndConvert(11, 10);
  // 項番5: 予備 (位置: 22, サイズ: 8) - スキップ
  // 項番6: 血統登録番号 (位置: 30, サイズ: 10)
  record.structured_data["pedigree_reg_num"] = record.extractAndConvert(29, 10);
  // 項番7: 予備 (位置: 40, サイズ: 1) - スキップ
  // 項番8: 馬名 (位置: 41, サイズ: 36)
  record.structured_data["horse_name"] = record.extractAndConvert(40, 36);
  // 項番9: 馬名半角カナ (位置: 77, サイズ: 40)
  record.structured_data["horse_name_kana"] = record.extractAndConvert(76, 40);
  // 項番10: 馬名欧字 (位置: 117, サイズ: 80)
  record.structured_data["horse_name_english"] = record.extractAndConvert(116, 80);
  // 項番11: 生年 (位置: 197, サイズ: 4)
  record.structured_data["birth_year"] = record.extractAndConvert(196, 4);
  // 項番12: 性別コード (位置: 201, サイズ: 1)
  record.structured_data["sex_code"] = record.extractAndConvert(200, 1);
  // 項番13: 品種コード (位置: 202, サイズ: 1)
  record.structured_data["breed_code"] = record.extractAndConvert(201, 1);
  // 項番14: 毛色コード (位置: 203, サイズ: 2)
  record.structured_data["coat_color_code"] = record.extractAndConvert(202, 2);
  // 項番15: 繁殖馬持込区分 (位置: 205, サイズ: 1)
  record.structured_data["import_code"] = record.extractAndConvert(204, 1);
  // 項番16: 輸入年 (位置: 206, サイズ: 4)
  record.structured_data["import_year"] = record.extractAndConvert(205, 4);
  // 項番17: 産地名 (位置: 210, サイズ: 20)
  record.structured_data["birthplace_name"] = record.extractAndConvert(209, 20);
  // 項番18: 父馬繁殖登録番号 (位置: 230, サイズ: 10)
  record.structured_data["sire_breeding_reg_num"] = record.extractAndConvert(229, 10);
  // 項番19: 母馬繁殖登録番号 (位置: 240, サイズ: 10)
  record.structured_data["dam_breeding_reg_num"] = record.extractAndConvert(239, 10);
}
