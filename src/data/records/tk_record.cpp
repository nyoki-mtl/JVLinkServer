#include "data/record_parser.h"
#include "json.hpp"
#include "spdlog/spdlog.h"

void parseTKFields(ParsedRecord& record) {
  // TK（特別登録馬）レコードの解析
  // レコード長: 21657バイト

  // 項番2: データ区分 (位置3, 1バイト)
  record.structured_data["data_code"] = record.extractAndConvert(2, 1);
  // 項番3: データ作成年月日 (位置4, 8バイト)
  record.structured_data["data_creation_date"] = record.extractAndConvert(3, 8);
  // 項番4: 開催年 (位置12, 4バイト) - キー項目
  record.structured_data["meet_year"] = record.extractAndConvert(11, 4);
  // 項番5: 開催月日 (位置16, 4バイト) - キー項目
  record.structured_data["meet_date"] = record.extractAndConvert(15, 4);
  // 項番6: 競馬場コード (位置20, 2バイト) - キー項目
  record.structured_data["racecourse_code"] = record.extractAndConvert(19, 2);
  // 項番7: 開催回[第N回] (位置22, 2バイト) - キー項目
  record.structured_data["meet_round"] = record.extractAndConvert(21, 2);
  // 項番8: 開催日目[N日目] (位置24, 2バイト) - キー項目
  record.structured_data["meet_day"] = record.extractAndConvert(23, 2);
  // 項番9: レース番号 (位置26, 2バイト) - キー項目
  record.structured_data["race_number"] = record.extractAndConvert(25, 2);
  // 項番10: 曜日コード (位置28, 1バイト)
  record.structured_data["weekday_code"] = record.extractAndConvert(27, 1);
  // 項番11: 特別競走番号 (位置29, 4バイト)
  record.structured_data["special_race_number"] = record.extractAndConvert(28, 4);
  // 項番12: 競走名本題 (位置33, 60バイト) 全角30文字 レース名の本題
  record.structured_data["race_name_main"] = record.extractAndConvert(32, 60);
  // 項番13: 競走名副題 (位置93, 60バイト) 全角30文字 レース名の副題
  record.structured_data["race_name_subtitle"] = record.extractAndConvert(92, 60);
  // 項番14: 競走名カッコ内 (位置153, 60バイト) 全角30文字 レースの条件やトライアル対象レース名、レース名通称など
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
  // 項番21: 競走名区分 (位置611, 1バイト) 重賞回次(第N回)を本題・副題・カッコ内のうちどれに設定すべきかを示す（0:初期値
  // 1:本題 2:副題 3:カッコ内）重賞のみ設定
  record.structured_data["race_name_code"] = record.extractAndConvert(610, 1);
  // 項番22: 重賞回次[第N回] (位置612, 3バイト) そのレースの重賞としての通算回数
  record.structured_data["graded_race_round_number"] = record.extractAndConvert(611, 3);
  // 項番23: グレードコード (位置615, 1バイト) <コード表 2003.グレードコード>参照
  record.structured_data["grade_code"] = record.extractAndConvert(614, 1);
  // 項番24: 競走種別コード (位置616, 2バイト) <コード表 2005.競走種別コード>参照
  record.structured_data["race_type_code"] = record.extractAndConvert(615, 2);
  // 項番25: 競走記号コード (位置618, 3バイト) <コード表 2006.競走記号コード>参照
  record.structured_data["race_symbol_code"] = record.extractAndConvert(617, 3);
  // 項番26: 重量種別コード (位置621, 1バイト) <コード表 2008.重量種別コード>参照
  record.structured_data["weight_type_code"] = record.extractAndConvert(620, 1);
  // 項番27: 競走条件コード 2歳条件 (位置622, 3バイト) 2歳馬の競走条件 <コード表 2007.競争条件コード>参照
  record.structured_data["race_cond_code_2yo"] = record.extractAndConvert(621, 3);
  // 項番28: 競走条件コード 3歳条件 (位置625, 3バイト) 3歳馬の競走条件 <コード表 2007.競争条件コード>参照
  record.structured_data["race_cond_code_3yo"] = record.extractAndConvert(624, 3);
  // 項番29: 競走条件コード 4歳条件 (位置628, 3バイト) 4歳馬の競走条件 <コード表 2007.競争条件コード>参照
  record.structured_data["race_cond_code_4yo"] = record.extractAndConvert(627, 3);
  // 項番30: 競走条件コード 5歳以上条件 (位置631, 3バイト) 5歳以上馬の競走条件 <コード表 2007.競争条件コード>参照
  record.structured_data["race_cond_code_5yo_up"] = record.extractAndConvert(630, 3);
  // 項番31: 競走条件コード 最若年条件 (位置634, 3バイト) 出走可能な最も馬齢が若い馬に対する条件 <コード表
  // 2007.競争条件コード>参照
  record.structured_data["race_cond_code_youngest"] = record.extractAndConvert(633, 3);
  // 項番32: 距離 (位置637, 4バイト) 単位:メートル
  record.structured_data["distance"] = record.extractAndConvert(636, 4);
  // 項番33: トラックコード (位置641, 2バイト) <コード表 2009.トラックコード>参照
  record.structured_data["track_code"] = record.extractAndConvert(640, 2);
  // 項番34: コース区分 (位置643, 2バイト) 半角2文字 使用するコースを設定 "A "~"E "を設定
  // 尚、2002年以前の東京競馬場は"A1"、"A2"も存在
  record.structured_data["course_code"] = record.extractAndConvert(642, 2);
  // 項番35: ハンデ発表日 (位置645, 8バイト) ハンディキャップレースにおいてハンデが発表された日 西暦4桁+月日各2桁
  // yyyymmdd形式
  record.structured_data["handicap_announcement_date"] = record.extractAndConvert(644, 8);
  // 項番36: 登録頭数 (位置653, 3バイト) 特別登録頭数
  record.structured_data["num_entries"] = record.extractAndConvert(652, 3);
  // 項番37: 登録馬毎情報 (位置656から, 300頭×70バイト=21000バイト)
  nlohmann::json horses_array = nlohmann::json::array();
  for (int i = 0; i < 300; i++) {
    size_t base_pos = 655 + i * 70;
    // 連番をチェックし、空ならスキップ
    std::string entry_number = record.extractAndConvert(base_pos + 0, 3);
    if (entry_number == "   ") {
      continue;
    }
    nlohmann::json horse_obj;
    // 項番37a: 連番 (ブロック内位置:1, 3バイト) 連番1~300
    horse_obj["serial_number"] = record.extractAndConvert(base_pos + 0, 3);
    // 項番37b: 血統登録番号 (ブロック内位置:4, 10バイト) 生年(西暦)4桁＋品種1桁<コード表 2201.品種コード>参照＋数字5桁
    horse_obj["pedigree_reg_num"] = record.extractAndConvert(base_pos + 3, 10);
    // 項番37c: 馬名 (ブロック内位置:14, 36バイト) 全角18文字
    horse_obj["horse_name"] = record.extractAndConvert(base_pos + 13, 36);
    // 項番37d: 馬記号コード (ブロック内位置:50, 2バイト) <コード表 2204.馬記号コード>参照
    horse_obj["horse_symbol_code"] = record.extractAndConvert(base_pos + 49, 2);
    // 項番37e: 性別コード (ブロック内位置:52, 1バイト) <コード表 2202.性別コード>参照
    // 初招待となる競走馬については初期値の場合有り
    horse_obj["sex_code"] = record.extractAndConvert(base_pos + 51, 1);
    // 項番37f: 調教師東西所属コード (ブロック内位置:53, 1バイト) <コード表 2301.東西所属コード>参照
    // 初招待となる競走馬については初期値の場合有り
    horse_obj["trainer_affiliation_code"] = record.extractAndConvert(base_pos + 52, 1);
    // 項番37g: 調教師コード (ブロック内位置:54, 5バイト) 調教師マスタへリンク
    // 初招待となる競走馬については初期値の場合有り
    horse_obj["trainer_code"] = record.extractAndConvert(base_pos + 53, 5);
    // 項番37h: 調教師名略称 (ブロック内位置:59, 8バイト) 全角4文字 初招待となる競走馬については初期値の場合有り
    horse_obj["trainer_short_name"] = record.extractAndConvert(base_pos + 58, 8);
    // 項番37i: 負担重量 (ブロック内位置:67, 3バイト) 単位:0.1kg ハンディキャップレースについては月曜以降に設定
    horse_obj["impost_weight"] = record.extractAndConvert(base_pos + 66, 3);
    // 項番37j: 交流区分 (ブロック内位置:70, 1バイト) 中央交流登録馬の場合に設定 0:初期値 1:地方馬 2:外国馬
    horse_obj["exchange_code"] = record.extractAndConvert(base_pos + 69, 1);
    horses_array.push_back(horse_obj);
  }
  // entry_count と horses_array の要素数の整合性を検証
  std::string num_entries_str = record.structured_data["num_entries"].get<std::string>();
  int declared_count = 0;
  try {
    declared_count = std::stoi(num_entries_str);
  } catch (...) {
    // パース失敗は無視（num_entries が空白等の場合）
  }
  if (declared_count > 0 && static_cast<int>(horses_array.size()) != declared_count) {
    spdlog::warn("TK record: num_entries ({}) != parsed horse count ({})", declared_count, horses_array.size());
  }
  record.structured_data["entry_horses"] = horses_array;
}
