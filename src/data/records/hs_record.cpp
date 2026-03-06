#include "data/record_parser.h"
#include "json.hpp"

void parseHSFields(ParsedRecord& record) {
  // HSレコード（競走馬市場取引価格）
  // レコード長: 200バイト

  // 項番2: データ区分 (位置: 3, サイズ: 1)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置: 4, サイズ: 8)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 血統登録番号 (位置: 12, サイズ: 10)
  record.structured_data["pedigree_reg_num"] = record.extractAndConvert(11, 10);
  // 項番5: 父馬 繁殖登録番号 (位置: 22, サイズ: 10)
  record.structured_data["sire_breeding_reg_num"] = record.extractAndConvert(21, 10);
  // 項番6: 母馬 繁殖登録番号 (位置: 32, サイズ: 10)
  record.structured_data["dam_breeding_reg_num"] = record.extractAndConvert(31, 10);
  // 項番7: 生年 (位置: 42, サイズ: 4)
  record.structured_data["birth_year"] = record.extractAndConvert(41, 4);
  // 項番8: 主催者・市場コード (位置: 46, サイズ: 6)
  record.structured_data["market_code"] = record.extractAndConvert(45, 6);
  // 項番9: 主催者名称 (位置: 52, サイズ: 40)
  record.structured_data["organizer_name"] = record.extractAndConvert(51, 40);
  // 項番10: 市場の名称 (位置: 92, サイズ: 80)
  record.structured_data["market_name"] = record.extractAndConvert(91, 80);
  // 項番11: 市場の開催期間(開始日) (位置: 172, サイズ: 8)
  record.structured_data["market_start_date"] = record.extractAndConvert(171, 8);
  // 項番12: 市場の開催期間(終了日) (位置: 180, サイズ: 8)
  record.structured_data["market_end_date"] = record.extractAndConvert(179, 8);
  // 項番13: 取引時の競走馬の年齢 (位置: 188, サイズ: 1)
  record.structured_data["horse_age_at_trade"] = record.extractAndConvert(187, 1);
  // 項番14: 取引価格 (位置: 189, サイズ: 10)
  record.structured_data["trade_price"] = record.extractAndConvert(188, 10);
}
