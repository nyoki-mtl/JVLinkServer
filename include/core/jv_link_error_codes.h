#pragma once

/**
 * JV-Link API Return/Error Codes
 *
 * Important:
 * - JV-Linkの戻り値はメソッドごとに意味が異なる場合があります。
 *   例: -1 は JVOpen では「該当データなし」を、JVRead/JVGets では「ファイル切替中」を意味します。
 * - 0 は JVRead/JVGets では「全ファイル読み込み終了(EOF)」を意味しますが、一般には成功を表します。
 *
 * このヘッダでは、コンテキスト毎の判定ヘルパーを用意し、重複値の意味を明確化します。
 */

namespace jvlink {
namespace error {

// Success
constexpr long JV_SUCCESS = 0;

// Common codes (method-specific semantics)
constexpr long JV_ERROR_NO_DATA = -1;        // JVOpen: 該当データなし
constexpr long JV_ERROR_FILE_SWITCHING = -1; // JVRead/JVGets: ファイル切替中
constexpr long JV_ERROR_INVALID_REQUEST = -2;       // 不正なリクエスト
constexpr long JV_ERROR_DOWNLOAD_IN_PROGRESS = -3;  // ダウンロード中（JVRead/JVGets）

// JVInit errors (-101 to -103)
constexpr long JV_ERROR_INIT_SID_EMPTY = -101;     // sidが設定されていない
constexpr long JV_ERROR_INIT_SID_TOO_LONG = -102;  // sidが64バイトを超えている
constexpr long JV_ERROR_INIT_SID_INVALID = -103;   // sidが不正（先頭がスペース）

// General parameter error (-100)
constexpr long JV_ERROR_PARAM_GENERAL = -100;  // パラメータ不正（汎用）/レジストリ保存失敗

// Parameter errors (-111 to -118)
constexpr long JV_ERROR_PARAM_DATASPEC_INVALID = -111;   // dataspecが不正
constexpr long JV_ERROR_PARAM_INVALID = -112;            // その他のパラメータが不正
constexpr long JV_ERROR_PARAM_FROMTIME_END = -113;       // fromtime（終了時刻）が不正
constexpr long JV_ERROR_PARAM_KEY_INVALID = -114;        // keyが不正
constexpr long JV_ERROR_PARAM_OPTION_INVALID = -115;     // optionが不正（範囲外）
constexpr long JV_ERROR_PARAM_DATASPEC_COUNT = -116;     // dataspecの指定数が不正
constexpr long JV_ERROR_PARAM_FILEPATH_INVALID = -118;   // filepathパラメータが不正

// State errors (-201 to -211)
constexpr long JV_ERROR_NOT_INITIALIZED = -201;    // JVInitが行われていない
constexpr long JV_ERROR_ALREADY_OPEN = -202;       // 前回のJVOpenが継続中（JVCloseが必要）
constexpr long JV_ERROR_NOT_OPEN = -203;           // JVOpenが行われていない
constexpr long JV_ERROR_REGISTRY_INVALID = -211;   // レジストリの内容が不正

// Authentication errors (-301 to -305)
constexpr long JV_ERROR_AUTH_FAILED = -301;          // 認証エラー
constexpr long JV_ERROR_AUTH_EXPIRED = -302;         // サービスキーの有効期限切れ
constexpr long JV_ERROR_AUTH_NOT_SET = -303;         // サービスキーが設定されていない（空値）
constexpr long JV_ERROR_AUTH_VIEWER = -304;          // Racing Viewer認証エラー
constexpr long JV_ERROR_AUTH_TOS_NOT_AGREED = -305;  // 利用規約に同意していない

// File errors (-401 to -403)
constexpr long JV_ERROR_INTERNAL = -401;               // JV-Link内部エラー
constexpr long JV_ERROR_FILE_CORRUPTED_HEADER = -402;  // ダウンロードファイルのヘッダー情報が異常（破損）
constexpr long JV_ERROR_FILE_CORRUPTED_RACING = -403;  // ダウンロードファイルのレーシング情報が異常（破損）

// Server communication errors (-411 to -431)
constexpr long JV_ERROR_SERVER_HTTP_404 = -411;           // サーバーエラー（HTTP 404）
constexpr long JV_ERROR_SERVER_HTTP_403 = -412;           // サーバーエラー（HTTP 403）
constexpr long JV_ERROR_SERVER_HTTP_OTHER = -413;         // サーバーエラー（その他HTTPステータス）
constexpr long JV_ERROR_SERVER_INVALID_RESPONSE = -421;   // サーバーレスポンスが不正
constexpr long JV_ERROR_SERVER_APP_ERROR = -431;          // サーバーアプリ内部エラー

// Other errors (-501 to -504)
constexpr long JV_ERROR_SETUP_INVALID_STARTKIT = -501;  // セットアップ処理でスタートキットが無効
constexpr long JV_ERROR_DOWNLOAD_FAILED = -502;         // ダウンロード失敗（通信/ディスクエラー等）
constexpr long JV_ERROR_FILE_NOT_FOUND = -503;          // ファイルが見つからない
constexpr long JV_ERROR_SERVER_MAINTENANCE = -504;      // サーバーメンテナンス中

// Context-specific helpers
// JVRead/JVGets
inline bool isJVGetsEOF(long code) { return code == JV_SUCCESS; }               // 0
inline bool isJVGetsFileSwitching(long code) { return code == JV_ERROR_FILE_SWITCHING; } // -1
inline bool isJVGetsDownloadInProgress(long code) { return code == JV_ERROR_DOWNLOAD_IN_PROGRESS; } // -3

// Convert error code to human-readable message
inline std::string getErrorMessage(long errorCode) {
  switch (errorCode) {
    case JV_SUCCESS:
      return "Success";
    case JV_ERROR_NO_DATA:
      return "No data available";
    case JV_ERROR_INVALID_REQUEST:
      return "Invalid request";
    case JV_ERROR_DOWNLOAD_IN_PROGRESS:
      return "Download in progress";

    // JVInit errors
    case JV_ERROR_INIT_SID_EMPTY:
      return "Software ID (SID) is not set";
    case JV_ERROR_INIT_SID_TOO_LONG:
      return "Software ID (SID) exceeds 64 bytes";
    case JV_ERROR_INIT_SID_INVALID:
      return "Software ID (SID) is invalid (starts with space)";

    // General parameter error
    case JV_ERROR_PARAM_GENERAL:
      return "Invalid parameter or registry save failed";

    // Parameter errors
    case JV_ERROR_PARAM_DATASPEC_INVALID:
      return "Invalid dataspec parameter";
    case JV_ERROR_PARAM_INVALID:
      return "Invalid parameter";
    case JV_ERROR_PARAM_FROMTIME_END:
      return "Invalid fromtime end time";
    case JV_ERROR_PARAM_KEY_INVALID:
      return "Invalid key parameter";
    case JV_ERROR_PARAM_OPTION_INVALID:
      return "Invalid option parameter (out of range)";
    case JV_ERROR_PARAM_DATASPEC_COUNT:
      return "Invalid number of dataspec specifications";
    case JV_ERROR_PARAM_FILEPATH_INVALID:
      return "Invalid filepath parameter";

    // State errors
    case JV_ERROR_NOT_INITIALIZED:
      return "JVInit has not been called";
    case JV_ERROR_ALREADY_OPEN:
      return "Previous JVOpen is still active (JVClose required)";
    case JV_ERROR_NOT_OPEN:
      return "JVOpen has not been called";
    case JV_ERROR_REGISTRY_INVALID:
      return "Invalid registry contents";

    // Authentication errors
    case JV_ERROR_AUTH_FAILED:
      return "Authentication failed";
    case JV_ERROR_AUTH_EXPIRED:
      return "Service key has expired";
    case JV_ERROR_AUTH_NOT_SET:
      return "Service key is not set";
    case JV_ERROR_AUTH_VIEWER:
      return "Racing Viewer authorization error";
    case JV_ERROR_AUTH_TOS_NOT_AGREED:
      return "Terms of service not agreed to";

    // File errors
    case JV_ERROR_INTERNAL:
      return "JV-Link internal error";
    case JV_ERROR_FILE_CORRUPTED_HEADER:
      return "Download file header is corrupted";
    case JV_ERROR_FILE_CORRUPTED_RACING:
      return "Download file racing information is corrupted";

    // Server communication errors
    case JV_ERROR_SERVER_HTTP_404:
      return "Server error (HTTP 404)";
    case JV_ERROR_SERVER_HTTP_403:
      return "Server error (HTTP 403)";
    case JV_ERROR_SERVER_HTTP_OTHER:
      return "Server error (other HTTP status)";
    case JV_ERROR_SERVER_INVALID_RESPONSE:
      return "Server response is invalid";
    case JV_ERROR_SERVER_APP_ERROR:
      return "Server application internal error";

    // Other errors
    case JV_ERROR_SETUP_INVALID_STARTKIT:
      return "Invalid start kit for setup";
    case JV_ERROR_DOWNLOAD_FAILED:
      return "Download failed (communication or disk error)";
    case JV_ERROR_FILE_NOT_FOUND:
      return "File not found";
    case JV_ERROR_SERVER_MAINTENANCE:
      return "Server is under maintenance";

    default:
      return "Unknown error code: " + std::to_string(errorCode);
  }
}

}  // namespace error
}  // namespace jvlink
