#include "data/record_parser.h"
#include "json.hpp"

void parseSKFields(ParsedRecord& record) {
  // SKレコード（産駒マスタ）
  // レコード長: 208バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 血統登録番号 (位置: 12, サイズ: 10)
  record.structured_data["pedigree_reg_num"] = record.extractAndConvert(11, 10);
  // 項番5: 生年月日 (位置: 22, サイズ: 8)
  record.structured_data["birth_date"] = record.extractAndConvert(21, 8);
  // 項番6: 性別コード (位置: 30, サイズ: 1)
  record.structured_data["sex_code"] = record.extractAndConvert(29, 1);
  // 項番7: 品種コード (位置: 31, サイズ: 1)
  record.structured_data["breed_code"] = record.extractAndConvert(30, 1);
  // 項番8: 毛色コード (位置: 32, サイズ: 2)
  record.structured_data["coat_color_code"] = record.extractAndConvert(31, 2);
  // 項番9: 産駒持込区分 (位置: 34, サイズ: 1)
  record.structured_data["import_code"] = record.extractAndConvert(33, 1);
  // 項番10: 輸入年 (位置: 35, サイズ: 4)
  record.structured_data["import_year"] = record.extractAndConvert(34, 4);
  // 項番11: 生産者コード (位置: 39, サイズ: 8)
  record.structured_data["breeder_code"] = record.extractAndConvert(38, 8);
  // 項番12: 産地名 (位置: 47, サイズ: 20)
  record.structured_data["birthplace_name"] = record.extractAndConvert(46, 20);
  // 項番13: 3代血統繁殖登録番号 (位置: 67, サイズ: 10, 繰り返し: 14)
  // 父･母･父父･父母･母父･母母･父父父･父父母･父母父･父母母･母父父･母父母･母母父･母母母の順
  record.structured_data["three_gen_pedigree_breeding_reg_nums"] = record.extractAndConvertArray(66, 10, 14);
}
