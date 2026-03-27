#include "core/jv_link_wrapper.h"

#include <direct.h>
#include <spdlog/spdlog.h>
#include <sys/stat.h>

#include <algorithm>
#include <chrono>
#include <limits>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iostream>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <thread>
#include <vector>

// JV-Dataレコードの最大サイズ（改行文字とNULL終端文字を含む）
// JV-Link仕様で規定されている最大のレコードサイズに基づいています。
// 最大のレコードはWF（3連単）で、102,890バイトです。
// 安全マージン（約20%のオーバーヘッド）として120KB（122,880バイト）を確保します。
static const long JV_DATA_LARGEST_SIZE = 122880;

// ファイル名バッファサイズ
static const int JV_FILENAME_BUFFER_SIZE = 256;

// ダウンロード待機時間設定
static const int JV_DOWNLOAD_POLL_INTERVAL_MS = 100;       // ダウンロード状態ポーリング間隔
static const int JV_DOWNLOAD_BASE_TIMEOUT_ITERATIONS = 3000;    // 基本タイムアウト（5分）
static const int JV_DOWNLOAD_PER_FILE_ITERATIONS = 60;     // ファイル1件あたり追加猶予（6秒）
static const int JV_DOWNLOAD_PROGRESS_LOG_INTERVAL = 100;  // 進捗ログ出力間隔（10秒ごと）
static const long long JV_STREAM_PROGRESS_LOG_INTERVAL = 10000;  // ストリーム進捗ログ出力間隔
static const LCID JV_JAPANESE_LCID = MAKELCID(MAKELANGID(LANG_JAPANESE, SUBLANG_DEFAULT), SORT_DEFAULT);

// JV-Link COMコンポーネントのCLSID
// {2AB1774D-0C41-11D7-916F-0003479BEB3F}
const CLSID JVLinkWrapper::CLSID_JVLink = {0x2AB1774D, 0xC41, 0x11D7, {0x91, 0x6F, 0x0, 0x3, 0x47, 0x9B, 0xEB, 0x3F}};

JVLinkWrapper::JVLinkWrapper()
    : jvlink_dispatch_(nullptr),
      is_initialized_(false),
      m_pEventSink(nullptr),
      m_pConnectionPoint(nullptr),
      m_dwConnectionCookie(0) {
  m_comWorker = std::make_unique<ComThreadWorker>();
  if (!m_comWorker->start()) {
    throw std::runtime_error("Failed to start COM thread worker");
  }
}

JVLinkWrapper::~JVLinkWrapper() {
  if (m_comWorker) {
    // COMスレッドでクリーンアップを実行
    if (m_comWorker->isRunning()) {
      try {
        m_comWorker->invokeTask<bool>([this]() {
          disconnectEventSink();
          shutdownOnComThread();
          return true;
        });
      } catch (const std::exception& e) {
        spdlog::warn("Failed to run COM-thread cleanup in destructor: {}", e.what());
      } catch (...) {
        spdlog::warn("Failed to run COM-thread cleanup in destructor due to unknown exception");
      }
    }
    // COMスレッドを停止
    m_comWorker->stop();
  }
}

bool JVLinkWrapper::initialize(const std::string& sid) {
  // すでに初期化済み - 成功を返す
  if (is_initialized_) {
    spdlog::debug("JVLinkWrapper already initialized");
    return true;
  }

  spdlog::info("Initializing JVLinkWrapper with SID: {}", sid);

  // COMスレッドでJV-LinkのCOMインスタンスを作成
  bool createResult = m_comWorker->invokeTask<bool>([this]() { return createJVLinkInstance(); });

  if (!createResult) {
    spdlog::error("Failed to create JV-Link COM instance");
    return false;
  }

  // COMスレッドでJVInitを実行
  long initResult = m_comWorker->invokeTask<long>([this, &sid]() { return performJVInit(sid); });

  if (initResult != jvlink::error::JV_SUCCESS) {
    spdlog::error("JVInit failed for SID: {} - {}", sid, jvlink::error::getErrorMessage(initResult));
    try {
      m_comWorker->invokeTask<bool>([this]() {
        shutdownOnComThread();
        return true;
      });
    } catch (const std::exception& e) {
      spdlog::warn("Failed to cleanup after JVInit error: {}", e.what());
    } catch (...) {
      spdlog::warn("Failed to cleanup after JVInit error due to unknown exception");
    }
    return false;
  }

  // COMスレッドでJVCloseを呼び出す
  try {
    (void)m_comWorker->invokeTask<bool>([this]() { return performJVClose(); });
  } catch (const std::exception& e) {
    spdlog::error("Failed to run initial JVClose after JVInit: {}", e.what());
    return false;
  } catch (...) {
    spdlog::error("Failed to run initial JVClose after JVInit due to unknown exception");
    return false;
  }

  current_sid_ = sid;
  is_initialized_ = true;
  spdlog::info("JVLinkWrapper initialized successfully");

  // イベントハンドラーが設定されていれば、COMスレッドで接続を試みる
  if (m_eventHandler) {
    spdlog::info("Event handler is set, attempting to connect event sink after JVInit");
    bool connectResult = m_comWorker->invokeTask<bool>([this]() { return connectEventSink(); });
    if (!connectResult) {
      spdlog::warn("Failed to connect event sink after JVInit, will retry later");
    }
  }

  return true;
}

void JVLinkWrapper::shutdown() {
  if (!m_comWorker || !m_comWorker->isRunning() || m_comWorker->isInComThread()) {
    shutdownOnComThread();
    return;
  }

  m_comWorker->invokeTask<bool>([this]() {
    shutdownOnComThread();
    return true;
  });
}

void JVLinkWrapper::shutdownOnComThread() {
  if (jvlink_dispatch_) {
    spdlog::info("Shutting down JVLinkWrapper");
    jvlink_dispatch_->Release();
    jvlink_dispatch_ = nullptr;
  }
  is_initialized_ = false;
}

void JVLinkWrapper::queryStored(const std::string& dataspec, const std::string& fromdate, long option, int max_records,
                                const std::function<void(const std::string&)>& record_callback,
                                const std::function<void(const JVQueryResult&)>& meta_callback,
                                const std::vector<std::string>& filter_record_types,
                                const std::function<bool()>& cancel_requested) {
  // JVGetsを使用した実装（高性能、デフォルト）
  /**
   * @brief JVGetsを使用してJV-Linkから蓄積データをストリーミングします。
   *
   * @details
   * JVReadの代わりにJVGetsを使用することで、UNICODE変換を回避し
   * パフォーマンスを向上させます。処理フロー:
   * 1. JVOpenを呼び出して利用可能なデータを照会します。
   * 2. メタデータ（件数、タイムスタンプ）をmeta_callback経由で返します。
   * 3. 必要なダウンロードが完了するのを待ちます。
   * 4. record_callback経由でレコードをストリーミングします。
   * 5. JVCloseでクリーンアップします。
   */
  JVQueryResult result = {};
  auto should_cancel = [&cancel_requested]() { return cancel_requested && cancel_requested(); };

  // 初期化状態をチェック
  if (!is_initialized_) {
    result.error_message = "JVLinkWrapper not initialized";
    meta_callback(result);
    return;
  }

  // JVSessionGuardを使用して自動的にJVCloseを呼び出す
  JVSessionGuard session_guard(this);

  // JVOpenのパラメータを準備
  long read_count = 0, download_count = 0;
  std::string last_timestamp;
  std::string from_time_to_use = fromdate;

  // 必要に応じてYYYYMMDDをYYYYMMDDhhmmssに変換
  if (from_time_to_use.length() == 8) from_time_to_use += "000000";

  // JVOpen経由でデータを要求（COMスレッドで実行）
  long openResult = m_comWorker->invokeTask<long>(
      [this, &dataspec, &from_time_to_use, option, &read_count, &download_count, &last_timestamp]() {
        return performJVOpen(dataspec, from_time_to_use, option, read_count, download_count, last_timestamp);
      });

  spdlog::info(
      "queryStored JVOpen returned for dataspec: {}, option: {}, fromtime: {}, openResult: {}, read_count: {}, "
      "download_count: {}, last_timestamp: {}",
      dataspec, option, from_time_to_use, openResult, read_count, download_count, last_timestamp);

  if (should_cancel()) {
    spdlog::debug("queryStored cancellation requested after JVOpen for dataspec: {}", dataspec);
    throw JVOperationCanceledException("Stored stream canceled after JVOpen");
  }

  if (openResult < 0 && openResult != jvlink::error::JV_ERROR_NO_DATA) {
    result.error_code = openResult;
    result.error_message = "JV-Link API error: " + jvlink::error::getErrorMessage(openResult);
    spdlog::warn("queryStored invoking meta_callback with error for dataspec: {} (code: {})", dataspec, openResult);
    meta_callback(result);
    return;
  }

  // 必要に応じてダウンロード完了を待つ（COMスレッドで実行）
  if (download_count > 0) {
    long download_status_code = 0;
    bool downloadResult = m_comWorker->invokeTask<bool>(
        [this, download_count, &download_status_code]() { return waitForDownload(download_count, &download_status_code); });

    if (should_cancel()) {
      spdlog::debug("queryStored cancellation requested after download wait for dataspec: {}", dataspec);
      throw JVOperationCanceledException("Stored stream canceled during download wait");
    }

    if (!downloadResult) {
      result.error_code = static_cast<int>(
          (download_status_code < 0) ? download_status_code : jvlink::error::JV_ERROR_DOWNLOAD_FAILED);
      result.error_message = "JVStatus failed: " + jvlink::error::getErrorMessage(result.error_code);
      spdlog::warn("queryStored invoking meta_callback after JVStatus failure for dataspec: {} (status: {})", dataspec,
                   download_status_code);
      meta_callback(result);
      return;  // JVSessionGuardがJVCloseを呼ぶ
    }
  }

  // メタデータを設定し、コールバック経由で通知
  result.read_count = read_count;
  result.download_count = download_count;
  result.last_file_timestamp = last_timestamp;
  result.success = true;
  if (should_cancel()) {
    spdlog::debug("queryStored cancellation requested before success meta_callback for dataspec: {}", dataspec);
    throw JVOperationCanceledException("Stored stream canceled before meta callback");
  }
  spdlog::debug("queryStored invoking success meta_callback for dataspec: {}", dataspec);
  meta_callback(result);
  spdlog::debug("queryStored success meta_callback returned for dataspec: {}", dataspec);

  // レコードを読み込んでストリーミング
  long long total_streamed_records = 0;
  if (read_count > 0) {
    // max_records が正の場合のみ上限を適用。指定なし(<=0)はEOFまで全件読む。
    long long effective_max_records =
        (max_records > 0) ? static_cast<long long>(max_records) : (std::numeric_limits<long long>::max)();

    char filename[JV_FILENAME_BUFFER_SIZE] = {0};

    if (max_records > 0) {
      spdlog::debug("Starting data stream with JVGets - record_limit: {}, file_count(read_count): {}",
                    effective_max_records, read_count);
    } else {
      spdlog::debug("Starting data stream with JVGets - record_limit: unlimited, file_count(read_count): {}",
                    read_count);
    }

    long long actual_records = 0;
    int retry_count = 0;
    const int max_retries = 10000;  // 無限ループ防止のための最大リトライ回数

    while (actual_records < effective_max_records && retry_count < max_retries) {
      if (should_cancel()) {
        spdlog::debug("queryStored cancellation requested during JVGets loop for dataspec: {} after {} records",
                      dataspec, actual_records);
        throw JVOperationCanceledException("Stored stream canceled during JVGets loop");
      }

      BYTE* buffer = nullptr;
      long size = 0;
      long ret = m_comWorker->invokeTask<long>(
          [this, &buffer, &size, &filename]() { return jvGetsWithRetry(&buffer, &size, filename); });

      // unique_ptrで自動的にメモリ管理
      std::unique_ptr<BYTE[]> buffer_ptr(buffer);

      if (should_cancel()) {
        spdlog::debug("queryStored cancellation requested after JVGets for dataspec: {} (ret: {}, records: {})",
                      dataspec, ret, actual_records);
        throw JVOperationCanceledException("Stored stream canceled after JVGets call");
      }

      if (ret > 0 && buffer != nullptr) {
        // レコードの読み取りに成功
        retry_count = 0;  // 成功したらリトライカウントをリセット

        // レコード種別フィルタリングのチェック（最初の2文字で判定）
        if (!filter_record_types.empty() && size >= 2) {
          std::string record_type(reinterpret_cast<char*>(buffer), 2);
          bool should_skip = true;

          // フィルタリストに含まれているかチェック
          for (const auto& allowed_type : filter_record_types) {
            if (record_type == allowed_type) {
              should_skip = false;
              break;
            }
          }

          // このファイルのレコード種別が対象外の場合、JVSkipでファイル全体をスキップ
          if (should_skip) {
            spdlog::debug("Skipping file with record type '{}' using JVSkip", record_type);
            long skip_result = m_comWorker->invokeTask<long>([this]() { return performJVSkip(); });
            if (skip_result != 0) {
              spdlog::warn("JVSkip failed with code: {}", skip_result);
            }
            // スキップ後は次のファイルに進む（actual_recordsは増やさない）
            continue;
          }
        }

        actual_records++;
        spdlog::trace("Read record {}/{} with JVGets - size: {} bytes", static_cast<long long>(actual_records),
                      static_cast<long long>(effective_max_records), size);
        if (actual_records == 1) {
          spdlog::debug("queryStored first JVGets record ready for dataspec: {} (filename: {}, size: {})", dataspec,
                        filename, size);
        } else if (actual_records % JV_STREAM_PROGRESS_LOG_INTERVAL == 0) {
          spdlog::debug("queryStored JVGets progress for dataspec: {} - {} records read (current file: {})", dataspec,
                        static_cast<long long>(actual_records), filename);
        }

        // JVGetsから返されたデータをコールバックに渡す
        // データはShift_JISエンコーディングで、RecordParserが変換を行う
        record_callback(std::string(reinterpret_cast<char*>(buffer), size));
        if (should_cancel()) {
          spdlog::debug("queryStored cancellation requested after record callback for dataspec: {} (records: {})",
                        dataspec, actual_records);
          throw JVOperationCanceledException("Stored stream canceled after record callback");
        }
      } else if (ret > 0 && buffer == nullptr) {
        // JVGetsが成功を返したがデータがNULLの場合
        spdlog::error("jvGets returned success ({}) but buffer is NULL - retrying", ret);
        retry_count++;
        if (retry_count % JV_DOWNLOAD_PROGRESS_LOG_INTERVAL == 0) {
          spdlog::error("Excessive NULL buffer returns from jvGets - retry count: {}", retry_count);
        }
        // 待機時間を設けてCPU負荷を軽減
        std::this_thread::sleep_for(std::chrono::milliseconds(JV_DOWNLOAD_POLL_INTERVAL_MS));
      } else if (jvlink::error::isJVGetsEOF(ret)) {
        // EOF: 全てのファイルを読み取り完了 (0)
        spdlog::info("Data stream completed with JVGets - read {} records", static_cast<long long>(actual_records));
        break;
      } else if (jvlink::error::isJVGetsDownloadInProgress(ret)) {
        // ファイルダウンロード中（-3） - 待機して再試行
        retry_count++;
        if (retry_count % JV_DOWNLOAD_PROGRESS_LOG_INTERVAL == 0) {  // 10秒ごとにログ出力
          spdlog::debug("Waiting for file download... (retry count: {})", retry_count);
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(JV_DOWNLOAD_POLL_INTERVAL_MS));
      } else if (jvlink::error::isJVGetsFileSwitching(ret)) {
        // ファイル切り替え中（-1） - 通常の操作
        retry_count++;
        spdlog::trace("File switching - continuing (retry count: {})", retry_count);
        // ファイル切り替え時にはactual_recordsをインクリメントしない
      } else {
        // その他の負の値はエラー
        std::ostringstream oss;
        oss << "jvGets failed: " << jvlink::error::getErrorMessage(ret) << " (code: " << ret << ") after "
            << actual_records << " records";
        throw JVStreamReadException(static_cast<int>(ret), oss.str());
      }
    }

    if (retry_count >= max_retries) {
      std::ostringstream oss;
      oss << "jvGets retry limit exceeded (" << max_retries
          << ") while waiting for file switch/download completion";
      throw JVStreamReadException(static_cast<int>(jvlink::error::JV_ERROR_DOWNLOAD_FAILED), oss.str());
    }

    if (actual_records >= effective_max_records) {
      spdlog::info("Reached max_records limit: {}", static_cast<long long>(effective_max_records));
    }

    total_streamed_records = actual_records;
  }

  spdlog::info("queryStored finished for dataspec: {} (records_read={}, read_count={}, download_count={})", dataspec,
               total_streamed_records, read_count, download_count);

  // JVSessionGuardのデストラクタで自動的にJVCloseが呼ばれる
}

bool JVLinkWrapper::performJVClose() {
  /**
   * @brief JVCloseメソッドのシグネチャ: Long JVClose()
   *
   * @details
   * JV-Dataの読み取り処理を終了します。
   * - 開いているすべてのファイルを閉じます。
   * - 実行中のダウンロードスレッドを停止します。
   * - 保存パスから不要なファイルを削除します。
   *
   * @return 常に0（成功）を返します。
   *
   * @note JVOpen/JVRTOpenが実行されていなくても安全に呼び出せます。
   */
  if (!jvlink_dispatch_) {
    spdlog::trace("JVClose skipped - no JV-Link instance");
    return true;
  }

  VARIANT result;
  VariantInit(&result);
  HRESULT hr = invokeMethod(jvlink::dispid::JV_CLOSE, DISPATCH_METHOD, NULL, 0, &result);

  if (SUCCEEDED(hr)) {
    spdlog::debug("JVClose completed successfully");
  } else {
    spdlog::warn("JVClose failed with HRESULT: {:#x}", hr);
  }

  VariantClear(&result);
  return SUCCEEDED(hr);
}

long JVLinkWrapper::jvGetsWithRetry(BYTE** buff, long* size, char* filename) {
  /**
   * @brief JVGetsの自動リトライ版
   *
   * 破損ファイルエラー（-402, -403）が発生した場合、
   * 自動的にファイルを削除して再試行します。
   */
  if (!retry_config_.auto_retry_on_corruption) {
    // 自動リトライが無効の場合は通常のjvGetsを呼ぶ
    return jvGets(buff, size, filename);
  }

  long ret = 0;
  int total_attempts = std::max(1, retry_config_.max_retry_attempts);
  for (int attempt = 0; attempt < total_attempts; attempt++) {
    ret = jvGets(buff, size, filename);

    // 破損ファイルエラーの場合
    if (ret == jvlink::error::JV_ERROR_FILE_CORRUPTED_HEADER || ret == jvlink::error::JV_ERROR_FILE_CORRUPTED_RACING) {
      spdlog::warn("Corrupted file detected: {} ({}, attempt {}/{})", filename, jvlink::error::getErrorMessage(ret),
                   attempt + 1, total_attempts);

      if (attempt < total_attempts - 1) {
        // ファイル名を取得（NULL終端されているはず）
        std::string file_to_delete(filename);

        // ファイルを削除
        long delete_result = performJVFiledelete(file_to_delete);
        if (delete_result == jvlink::error::JV_SUCCESS) {
          spdlog::info("Successfully deleted corrupted file: {}", file_to_delete);
        } else {
          spdlog::error("Failed to delete corrupted file: {} ({})", file_to_delete,
                        jvlink::error::getErrorMessage(delete_result));
          // 削除に失敗しても続行を試みる
        }

        // リトライ前に少し待機
        std::this_thread::sleep_for(std::chrono::milliseconds(retry_config_.retry_delay_ms));

        // 前回のバッファがある場合は削除
        if (*buff != nullptr) {
          delete[] *buff;
          *buff = nullptr;
          *size = 0;
        }

        // 次の試行へ
        continue;
      }
    }

    // 他のエラーまたは成功時は即座に返す
    return ret;
  }

  // 最後の試行の結果を返す
  spdlog::error("Failed to read file after {} attempts: {}", total_attempts, filename);
  return ret;
}

long JVLinkWrapper::jvGets(BYTE** buff, long* size, char* filename) {
  /**
   * @brief JVGetsメソッドのシグネチャ: Long JVGets(Byte Array& buff, Long& size, String& filename)
   *
   * @details
   * JVReadと同様ですが、パフォーマンス向上のためバイト配列を直接返します。
   * UNICODE変換を避けることで処理速度が向上します。
   *
   * @return 戻り値：
   *   > 0: バッファに設定されたバイト数（読み取り成功）
   *   0: すべてのファイルを読み取り完了 (EOF)
   *   -1: ファイル切り替え中（データなし、読み取り継続）
   *   -3: ファイルダウンロード中（待機してリトライ）
   *   他: エラーコード（JVReadと同じ）
   */
  if (!jvlink_dispatch_) return -999;

  VARIANT result;
  VariantInit(&result);

  // 引数を準備
  DISPPARAMS dp = {NULL, NULL, 3, 0};
  VARIANT args[3];
  for (int i = 0; i < 3; i++) VariantInit(&args[i]);

  // バイト配列用のSAFEARRAYを準備
  SAFEARRAY* pSafeArray = NULL;
  _bstr_t bstrFilename;

  // sizeに初期値を設定（JVReadと同様にJV_DATA_LARGEST_SIZEを指定）
  *size = JV_DATA_LARGEST_SIZE;

  // COMディスパッチのために引数を逆順にする
  args[0].vt = VT_BSTR | VT_BYREF;
  args[0].pbstrVal = bstrFilename.GetAddress();  // filename (出力)
  args[1].vt = VT_I4 | VT_BYREF;
  args[1].plVal = size;  // size (入出力)
  args[2].vt = VT_BYREF | VT_ARRAY | VT_UI1;
  args[2].pparray = &pSafeArray;  // buff (出力) - バイト配列として

  // JVGetsを呼び出し
  HRESULT hr = invokeMethod(jvlink::dispid::JV_GETS, DISPATCH_METHOD, args, 3, &result);
  if (FAILED(hr)) {
    spdlog::error("JVGets failed: HRESULT={:#x}", hr);
    return -999;
  }

  long lResult = result.lVal;

  // 読み取りが成功した場合、返されたデータを処理
  if (lResult > 0 && pSafeArray != NULL) {
    // SAFEARRAYからデータを取得
    BYTE* pData = NULL;
    hr = SafeArrayAccessData(pSafeArray, (void**)&pData);
    if (SUCCEEDED(hr)) {
      // JVGetsの戻り値が実際のレコードサイズ
      long dataSize = lResult;

      // データをコピー
      *buff = new BYTE[dataSize];
      memcpy(*buff, pData, dataSize);

      // 実際のデータサイズを返す
      *size = dataSize;

      SafeArrayUnaccessData(pSafeArray);
    } else {
      spdlog::error("Failed to access SAFEARRAY data: HRESULT={:#x}", hr);
      *size = 0;
    }

    // ファイル名が利用可能な場合は抽出
    if (bstrFilename.length() > 0) {
      // ファイル名もShift_JISエンコーディング（932）
      int fnSize = WideCharToMultiByte(932, 0, bstrFilename, -1, NULL, 0, NULL, NULL);
      if (fnSize > 0 && fnSize <= JV_FILENAME_BUFFER_SIZE) {
        WideCharToMultiByte(932, 0, bstrFilename, -1, filename, fnSize, NULL, NULL);
      }
    }

    // SAFEARRAYを解放
    SafeArrayDestroy(pSafeArray);
  } else if (lResult > 0 && pSafeArray == NULL) {
    // データが返されたがSAFEARRAYがNULLの場合
    spdlog::warn("JVGets returned success but SAFEARRAY is NULL");
    *size = 0;
  } else {
    // その他の場合（エラーまたはEOF）
    *size = 0;
  }

  VariantClear(&result);
  return lResult;
}

long JVLinkWrapper::performJVSkip() {
  /**
   * @brief JVSkipメソッドのシグネチャ: void JVSkip()
   *
   * @details
   * 現在のファイル内の残りのレコードをスキップして、
   * 次のファイルの先頭に移動します。
   *
   * 使用方法：
   * - 蓄積系データは1つのファイルに1種類のレコードしか含まれない
   * - JVRead/JVGetsで読み出した最初のレコードが不要な種別の場合、
   *   JVSkipでそのファイルの残りを読み飛ばすことで処理時間を短縮
   * - 速報系データ（JVRTOpen）では1ファイルのみのため効果なし
   *
   * 例：
   * 1. JVRead/JVGetsでレコードを読む
   * 2. レコード種別（先頭2文字）を確認
   * 3. 不要な種別ならJVSkipで次のファイルへ
   *
   * @return 戻り値：
   *   0: 正常
   *   -201: JVInitが呼ばれていない
   *   -203: JVOpenが呼ばれていない
   */
  if (!jvlink_dispatch_) return -999;

  VARIANT result;
  VariantInit(&result);

  HRESULT hr = invokeMethod(jvlink::dispid::JV_SKIP, DISPATCH_METHOD, nullptr, 0, &result);
  if (FAILED(hr)) {
    spdlog::error("JVSkip invoke failed with HRESULT: {:#x}", hr);
    return -999;
  }

  long return_code = result.lVal;

  if (return_code == 0) {
    spdlog::debug("JVSkip executed successfully");
  } else {
    switch (return_code) {
      case -201:
        spdlog::error("JVSkip failed: JVInit not called");
        break;
      case -203:
        spdlog::error("JVSkip failed: JVOpen/JVRTOpen not called");
        break;
      default:
        spdlog::error("JVSkip failed with error code: {}", return_code);
    }
  }

  VariantClear(&result);
  return return_code;
}

long JVLinkWrapper::performJVFiledelete(const std::string& filename) {
  /**
   * @brief JVFiledeleteメソッドのシグネチャ: Long JVFiledelete(String filename)
   *
   * @details
   * JV-Linkの保存パスからダウンロード済みファイルを削除します。
   * JVRead/JVGetsでエラーが発生した場合、問題のあるファイルを削除して
   * JVOpenプロセスを再試行することでエラーを解決できます。
   *
   * 使用例：
   * 1. JVRead/JVGetsで-402または-403エラーが発生
   * 2. エラーとなったファイル名（JVReadから取得）を指定してJVFiledelete
   * 3. JVCloseしてからJVOpenを再実行
   *
   * @param filename 削除するファイルの名前（フルパスではなくファイル名のみ）
   * @return 戻り値：
   *   0: 正常（ファイル削除成功）
   *   -1: エラー（ファイルが見つからない、アクセス拒否など）
   *   -201: JVInitが呼ばれていない
   */
  if (!jvlink_dispatch_) return -999;

  spdlog::info("Deleting file: {}", filename);

  // 引数を準備
  VARIANT args[1];
  VariantInit(&args[0]);
  args[0].vt = VT_BSTR;
  args[0].bstrVal = convertUtf8ToBSTR(filename);

  VARIANT result;
  VariantInit(&result);

  // JVFiledeleteを呼び出し
  HRESULT hr = invokeMethod(jvlink::dispid::JV_FILE_DELETE, DISPATCH_METHOD, args, 1, &result);

  // BSTRのコピーをクリーンアップ
  SysFreeString(args[0].bstrVal);

  if (FAILED(hr)) {
    spdlog::error("JVFiledelete COM invocation failed with HRESULT: {:#x}", hr);
    return -999;
  }

  long return_code = result.lVal;

  // 結果をログに記録
  if (return_code == 0) {
    spdlog::info("JVFiledelete successful - deleted file: {}", filename);
  } else {
    switch (return_code) {
      case -1:
        spdlog::error("JVFiledelete failed: File not found or access denied - {}", filename);
        break;
      case -201:
        spdlog::error("JVFiledelete failed: JVInit not called");
        break;
      default:
        spdlog::error("JVFiledelete failed with error code: {} for file: {}", return_code, filename);
    }
  }

  VariantClear(&result);
  return return_code;
}

long JVLinkWrapper::deleteFile(const std::string& filename) {
  // 初期化状態をチェック
  if (!is_initialized_) {
    spdlog::error("JVLinkWrapper not initialized - cannot delete file");
    return -201;
  }

  // ファイル名が空でないことを確認
  if (filename.empty()) {
    spdlog::error("Filename is empty - cannot delete");
    return -1;
  }

  // COMスレッドで実行
  if (!m_comWorker || !m_comWorker->isRunning() || m_comWorker->isInComThread()) {
    return performJVFiledelete(filename);
  }
  return m_comWorker->invokeTask<long>([this, filename]() { return performJVFiledelete(filename); });
}

long JVLinkWrapper::fukuFile(const std::string& pattern, const std::string& filepath) {
  // 初期化状態をチェック
  if (!is_initialized_) {
    spdlog::error("JVLinkWrapper not initialized - cannot generate uniform image");
    return -201;
  }

  // パラメータの検証
  if (pattern.empty()) {
    spdlog::error("Pattern is empty - cannot generate uniform image");
    return -1;
  }

  if (filepath.empty()) {
    spdlog::error("Filepath is empty - cannot save uniform image");
    return -1;
  }

  // COMスレッドで実行
  if (!m_comWorker || !m_comWorker->isRunning() || m_comWorker->isInComThread()) {
    return performJVFukuFile(pattern, filepath);
  }
  return m_comWorker->invokeTask<long>([this, pattern, filepath]() { return performJVFukuFile(pattern, filepath); });
}

long JVLinkWrapper::fuku(const std::string& pattern, BYTE** buff, long* size) {
  // 初期化状態をチェック
  if (!is_initialized_) {
    spdlog::error("JVLinkWrapper not initialized - cannot generate uniform image");
    return -201;
  }

  // パラメータの検証
  if (pattern.empty()) {
    spdlog::error("Pattern is empty - cannot generate uniform image");
    return -1;
  }

  if (!buff || !size) {
    spdlog::error("Buffer or size pointer is null - cannot return uniform image");
    return -1;
  }

  // COMスレッドで実行
  if (!m_comWorker || !m_comWorker->isRunning() || m_comWorker->isInComThread()) {
    return performJVFuku(pattern, buff, size);
  }
  return m_comWorker->invokeTask<long>([this, pattern, buff, size]() { return performJVFuku(pattern, buff, size); });
}

long JVLinkWrapper::courseFile(const std::string& key, std::string& filepath, std::string& explanation) {
  // 初期化状態をチェック
  if (!is_initialized_) {
    spdlog::error("JVLinkWrapper not initialized - cannot retrieve course map");
    return -201;
  }

  // パラメータの検証
  if (key.empty()) {
    spdlog::error("Key is empty - cannot retrieve course map");
    return -114;
  }

  // COMスレッドで実行
  if (!m_comWorker || !m_comWorker->isRunning() || m_comWorker->isInComThread()) {
    return performJVCourseFile(key, filepath, explanation);
  }
  return m_comWorker->invokeTask<long>(
      [this, key, &filepath, &explanation]() { return performJVCourseFile(key, filepath, explanation); });
}

long JVLinkWrapper::courseFile2(const std::string& key, const std::string& filepath) {
  // 初期化状態をチェック
  if (!is_initialized_) {
    spdlog::error("JVLinkWrapper not initialized - cannot retrieve course map");
    return -201;
  }

  // パラメータの検証
  if (key.empty()) {
    spdlog::error("Key is empty - cannot retrieve course map");
    return -114;
  }

  if (filepath.empty()) {
    spdlog::error("Filepath is empty - cannot save course map");
    return jvlink::error::JV_ERROR_PARAM_FILEPATH_INVALID;
  }

  // COMスレッドで実行
  if (!m_comWorker || !m_comWorker->isRunning() || m_comWorker->isInComThread()) {
    return performJVCourseFile2(key, filepath);
  }
  return m_comWorker->invokeTask<long>([this, key, filepath]() { return performJVCourseFile2(key, filepath); });
}

bool JVLinkWrapper::createJVLinkInstance() {
  if (jvlink_dispatch_) {
    spdlog::debug("Releasing existing JV-Link instance");
    jvlink_dispatch_->Release();
    jvlink_dispatch_ = nullptr;
  }

  HRESULT hr = CoCreateInstance(CLSID_JVLink, NULL, CLSCTX_INPROC_SERVER, IID_IDispatch, (void**)&jvlink_dispatch_);

  if (SUCCEEDED(hr)) {
    spdlog::debug("JV-Link COM instance created successfully");
    return true;
  } else {
    spdlog::error("Failed to create JV-Link COM instance. HRESULT: {:#x}", hr);
    if (hr == REGDB_E_CLASSNOTREG) {
      spdlog::error("JV-Link is not registered. Please ensure JV-Link is properly installed.");
    }
    return false;
  }
}

long JVLinkWrapper::performJVInit(const std::string& sid) {
  /**
   * @brief JVInitメソッドのシグネチャ: Long JVInit(String sid)
   *
   * @details
   * JV-Linkを初期化し、最初に呼び出す必要があります。
   * レジストリからサービスキー、保存パス、その他の設定を読み込みます。
   *
   * @return 戻り値：
   *   0: 正常
   *   -101: sidが設定されていない
   *   -102: sidが64バイトを超えている
   *   -103: sidが無効（先頭がスペース）
   */
  VARIANT result;
  VariantInit(&result);

  // sidパラメータを準備
  VARIANT args[1];
  VariantInit(&args[0]);
  args[0].vt = VT_BSTR;
  args[0].bstrVal = convertUtf8ToBSTR(sid);

  // JVInitを呼び出し
  HRESULT hr = invokeMethod(jvlink::dispid::JV_INIT, DISPATCH_METHOD, args, 1, &result);
  SysFreeString(args[0].bstrVal);

  long return_code = 0;

  if (FAILED(hr)) {
    spdlog::error("JVInit COM invocation failed with HRESULT: {:#x}", hr);
    VariantClear(&result);
    return -1;  // COM呼び出しエラー
  }

  if (result.vt == VT_I4) {
    return_code = result.lVal;
    if (return_code != 0) {
      // エラーコードに応じたメッセージをログに記録
      switch (return_code) {
        case jvlink::error::JV_ERROR_INIT_SID_EMPTY:
          spdlog::error("JVInit failed: {}", jvlink::error::getErrorMessage(return_code));
          break;
        case jvlink::error::JV_ERROR_INIT_SID_TOO_LONG:
          spdlog::error("JVInit failed: {}", jvlink::error::getErrorMessage(return_code));
          break;
        case jvlink::error::JV_ERROR_INIT_SID_INVALID:
          spdlog::error("JVInit failed: {}", jvlink::error::getErrorMessage(return_code));
          break;
        default:
          spdlog::error("JVInit failed with error code: {}", return_code);
      }
    }
  } else {
    spdlog::error("JVInit returned unexpected variant type: {}", result.vt);
    return_code = -1;
  }

  VariantClear(&result);
  return return_code;
}

long JVLinkWrapper::performJVOpen(const std::string& dataspec, const std::string& fromdate, long option,
                                  long& read_count, long& download_count, std::string& last_timestamp) {
  /**
   * @brief JVOpenメソッドのシグネチャ: Long JVOpen(String dataspec, String fromtime, Long option, Long& readcount,
   * Long& downloadcount, String& lastfiletimestamp)
   *
   * @details
   * 蓄積データの取得を要求します。実行される手順：
   * 1. パラメータを検証します。
   * 2. 一致するファイルをサーバーに照会します。
   * 3. ローカルディスクに既存のファイルがあるか確認します。
   * 4. 見つからないファイルのためにダウンロードスレッドを開始します。
   *
   * @return 戻り値：
   *   0: 正常
   *   -1: 該当データなし（利用者が最新をダウンロード選択時）
   *   -2: 設定ダイアログがキャンセルされた
   *   -111〜-116: パラメータが不正
   *   -201: JVInitが呼ばれていない
   *   -202: 前のJVOpenがクローズされていない
   *   -301〜-303: 認証エラー
   *   -4xx: サーバーエラー
   *   -504: サーバーメンテナンス中
   */
  BSTR bstrLastTimestamp = NULL;

  // 引数配列を準備（COM呼び出しは逆順）
  VARIANT args[6];
  for (int i = 0; i < 6; i++) VariantInit(&args[i]);

  // 出力パラメータ（参照渡し）
  VARIANT varReadCount, varDownloadCount, varLastTimestamp;
  VariantInit(&varReadCount);
  varReadCount.vt = VT_I4 | VT_BYREF;
  varReadCount.plVal = &read_count;

  VariantInit(&varDownloadCount);
  varDownloadCount.vt = VT_I4 | VT_BYREF;
  varDownloadCount.plVal = &download_count;

  VariantInit(&varLastTimestamp);
  varLastTimestamp.vt = VT_BSTR | VT_BYREF;
  varLastTimestamp.pbstrVal = &bstrLastTimestamp;

  // COMディスパッチのために引数を逆順に設定
  args[0] = varLastTimestamp;  // lastfiletimestamp (出力)
  args[1] = varDownloadCount;  // downloadcount (出力)
  args[2] = varReadCount;      // readcount (出力)
  args[3].vt = VT_I4;
  args[3].lVal = option;  // option (1=通常, 2=週単位, 3=セットアップ, 4=セットアップ(ダイアログなし))
  args[4].vt = VT_BSTR;
  args[4].bstrVal = convertUtf8ToBSTR(fromdate);  // fromtime
  args[5].vt = VT_BSTR;
  args[5].bstrVal = convertUtf8ToBSTR(dataspec);  // dataspec

  // JVOpenを呼び出し
  VARIANT result;
  VariantInit(&result);
  HRESULT hr = invokeMethod(jvlink::dispid::JV_OPEN, DISPATCH_METHOD, args, 6, &result);

  // BSTRのコピーをクリーンアップ
  SysFreeString(args[4].bstrVal);
  SysFreeString(args[5].bstrVal);

  if (FAILED(hr)) {
    spdlog::error("JVOpen COM invocation failed with HRESULT: {:#x}", hr);
    VariantClear(&result);
    return -1;  // COM呼び出しエラー
  }

  long return_code = result.lVal;
  VariantClear(&result);

  // 利用可能な場合は最終ファイルタイムスタンプを抽出
  if (bstrLastTimestamp) {
    last_timestamp = convertBSTRToString(bstrLastTimestamp);
    SysFreeString(bstrLastTimestamp);
  }

  // 結果をログに記録
  spdlog::info(
      "JVOpen completed - dataspec: {}, option: {}, return: {}, read_count: {}, download_count: {}, last_timestamp: {}",
      dataspec, option, return_code, read_count, download_count, last_timestamp);

  // エラーコードに応じたメッセージをログに記録
  if (return_code != jvlink::error::JV_SUCCESS && return_code != jvlink::error::JV_ERROR_NO_DATA &&
      return_code != jvlink::error::JV_ERROR_INVALID_REQUEST) {
    std::string error_msg = jvlink::error::getErrorMessage(return_code);
    spdlog::error("JVOpen failed: {}", error_msg);
  } else if (return_code == jvlink::error::JV_ERROR_NO_DATA) {
    spdlog::info("JVOpen: No relevant data found");
  } else if (return_code == jvlink::error::JV_ERROR_INVALID_REQUEST) {
    spdlog::info("JVOpen: Setup dialog canceled by user");
  }

  return return_code;
}

bool JVLinkWrapper::waitForDownload(long download_count, long* last_status_code) {
  /**
   * @brief JVStatusをポーリングして、JV-Linkのダウンロードスレッドが完了するのを待ちます。
   *
   * @details
   * JVStatusの戻り値：
   *   >= 0: ダウンロードされたファイル数
   *   -201: JVInitが呼ばれていない
   *   -203: JVOpenが呼ばれていない
   *   -502: ダウンロード失敗（通信またはディスクエラー）
   *
   * @note
   * このタイムアウトは、個々のファイルではなく、バッチダウンロード操作全体に適用されます。
   * 大量のデータ（例：数年分の過去データや初回セットアップ）を要求する場合、5分では不十分な場合があります。
   */
  if (last_status_code) {
    *last_status_code = 0;
  }
  if (download_count <= 0) return true;

  long status_val = 0;
  // download_count に基づいてタイムアウトを動的に算出
  // 基本5分 + ファイル1件あたり6秒の追加猶予
  const int max_iterations = JV_DOWNLOAD_BASE_TIMEOUT_ITERATIONS
                             + download_count * JV_DOWNLOAD_PER_FILE_ITERATIONS;
  const int poll_interval_ms = JV_DOWNLOAD_POLL_INTERVAL_MS;
  spdlog::debug("Download timeout: {}s for {} files", max_iterations * poll_interval_ms / 1000, download_count);

  for (int i = 0; i < max_iterations; ++i) {
    VARIANT result;
    VariantInit(&result);

    // JVStatusを呼び出してダウンロードの進捗を取得
    if (FAILED(invokeMethod(jvlink::dispid::JV_STATUS, DISPATCH_METHOD, NULL, 0, &result)) || result.vt != VT_I4) {
      VariantClear(&result);
      if (last_status_code) {
        *last_status_code = jvlink::error::JV_ERROR_DOWNLOAD_FAILED;
      }
      return false;
    }

    status_val = result.lVal;
    VariantClear(&result);

    // ダウンロード完了をチェック
    if (status_val >= download_count) {
      spdlog::info("Download completed: {} files", status_val);
      if (last_status_code) {
        *last_status_code = status_val;
      }
      return true;
    }

    // 負の値はエラーを示す
    if (status_val < 0) {
      switch (status_val) {
        case -201:
          spdlog::error("JVStatus failed: JVInit not called");
          break;
        case -203:
          spdlog::error("JVStatus failed: JVOpen not called");
          break;
        case -502:
          spdlog::error("JVStatus failed: download failed (communication or disk error)");
          break;
        default:
          spdlog::error("JVStatus failed with error code: {}", status_val);
      }
      if (last_status_code) {
        *last_status_code = status_val;
      }
      return false;
    }

    // 定期的に進捗をログに記録（10秒ごと）
    if (i % JV_DOWNLOAD_PROGRESS_LOG_INTERVAL == 0 && i > 0) {
      spdlog::debug("Download progress: {}/{} files ({:.1f}%)", status_val, download_count,
                    (status_val * 100.0) / download_count);
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(poll_interval_ms));
  }

  // タイムアウトに達した - 警告をログに記録
  spdlog::warn("Download timeout reached after {} seconds. Downloaded {} of {} files",
               max_iterations * poll_interval_ms / 1000, status_val, download_count);
  if (last_status_code) {
    *last_status_code = jvlink::error::JV_ERROR_DOWNLOAD_FAILED;
  }
  return false;
}

HRESULT JVLinkWrapper::invokeMethod(DISPID dispId, WORD wFlags, VARIANT* pArgs, int cArgs, VARIANT* pResult) const {
  if (!jvlink_dispatch_) return E_POINTER;
  DISPPARAMS dp = {NULL, NULL, (UINT)cArgs, 0};
  if (cArgs > 0) dp.rgvarg = pArgs;
  return jvlink_dispatch_->Invoke(dispId, IID_NULL, JV_JAPANESE_LCID, wFlags, &dp, pResult, NULL, NULL);
}

BSTR JVLinkWrapper::convertUtf8ToBSTR(const std::string& value) const {
  if (value.empty()) {
    return SysAllocStringLen(L"", 0);
  }

  // HTTP/JSON 経由の入力は UTF-8 なので、そのまま UTF-16 BSTR に変換する。
  int wide_size = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, value.data(), static_cast<int>(value.size()),
                                      nullptr, 0);
  if (wide_size <= 0) {
    spdlog::warn("Failed to convert UTF-8 input to BSTR (length={})", value.size());
    return SysAllocStringLen(L"", 0);
  }

  std::wstring wide_value(wide_size, L'\0');
  if (MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, value.data(), static_cast<int>(value.size()),
                          wide_value.data(), wide_size) <= 0) {
    spdlog::warn("Failed to populate UTF-16 buffer from UTF-8 input (length={})", value.size());
    return SysAllocStringLen(L"", 0);
  }

  return SysAllocStringLen(wide_value.data(), static_cast<UINT>(wide_value.size()));
}

std::string JVLinkWrapper::convertBSTRToString(BSTR bstr) const {
  /**
   * @brief BSTR (COM文字列) をUTF-8文字列に変換します。
   *
   * @details
   * JV-Link の Automation 文字列は BSTR で受け取るため、UTF-16 から UTF-8 へ
   * 直接変換します。
   */
  if (!bstr) return "";
  UINT len = SysStringLen(bstr);
  if (len == 0) return "";

  int utf8_size = WideCharToMultiByte(CP_UTF8, 0, bstr, len, nullptr, 0, nullptr, nullptr);
  if (utf8_size <= 0) return "";

  std::string result(utf8_size, '\0');
  WideCharToMultiByte(CP_UTF8, 0, bstr, len, result.data(), utf8_size, nullptr, nullptr);
  return result;
}

void JVLinkWrapper::queryRealtime(const std::string& dataspec, const std::string& key,
                                  const std::function<void(const std::string&)>& record_callback,
                                  const std::function<void(const JVQueryResult&)>& meta_callback) {
  JVQueryResult result = {};

  // 初期化状態をチェック
  if (!is_initialized_) {
    result.error_message = "JVLinkWrapper not initialized";
    meta_callback(result);
    return;
  }

  // JVSessionGuardを使用して自動的にJVCloseを呼び出す
  JVSessionGuard session_guard(this);

  // リアルタイムデータストリームを開く（COMスレッドで実行）
  long rt_open_result = 0;
  if (!m_comWorker || !m_comWorker->isRunning() || m_comWorker->isInComThread()) {
    rt_open_result = performJVRTOpen(dataspec, key);
  } else {
    rt_open_result = m_comWorker->invokeTask<long>([this, dataspec, key]() { return performJVRTOpen(dataspec, key); });
  }
  if (rt_open_result == -1) {
    // -1は「データなし」を示す正常な戻り値
    result.success = true;
    result.read_count = 0;  // データがないことを示す
    meta_callback(result);
    // 空のストリームを返す（record_callbackは呼ばない）
    return;
  } else if (rt_open_result != 0) {
    // その他のエラーコード
    result.error_code = rt_open_result;
    result.error_message = "JV-Link API error: " + jvlink::error::getErrorMessage(rt_open_result);
    meta_callback(result);
    return;
  }

  // metaコールバック経由で成功を通知
  // リアルタイムデータにはJVOpenのような読み取り/ダウンロード件数はない
  result.success = true;
  meta_callback(result);

  // jvGetsはバッファを動的に割り当てるため、事前確保は不要
  char filename[256] = {0};

  int record_count = 0;
  spdlog::debug("Starting real-time data stream for dataspec: {}, key: {}", dataspec, key);

  // 完了するまでレコードを読み込んでストリーミング
  while (true) {
    BYTE* buffer = nullptr;
    long size = JV_DATA_LARGEST_SIZE;
    long ret =
        m_comWorker->invokeTask<long>([this, &buffer, &size, &filename]() { return jvGets(&buffer, &size, filename); });

    if (ret > 0) {
      // レコードの読み取りに成功 - コールバックで送信
      // 注意：ここで文字列のコピーを作成する理由：
      // 1. バッファは次のレコードのために再利用される
      // 2. コールバックは非同期でデータを処理する可能性がある
      record_count++;
      spdlog::trace("Read record #{} - size: {} bytes, file: {}", record_count, size, filename);
      record_callback(std::string(reinterpret_cast<char*>(buffer), size));

      // jvGetsによって割り当てられたメモリを解放
      delete[] buffer;
    } else if (jvlink::error::isJVGetsEOF(ret)) {
      // EOF: 全てのファイルを読み取り完了 (0)
      spdlog::info("Real-time data stream completed - total records: {}", record_count);
      break;
    } else if (jvlink::error::isJVGetsFileSwitching(ret)) {
      // ファイル切り替え中（-1） - 読み取りを継続
      spdlog::trace("File switching detected");
      continue;
    } else if (jvlink::error::isJVGetsDownloadInProgress(ret)) {
      // ファイルダウンロード中（-3） - 待機して再試行
      // これはリアルタイムデータでは起こらないはずだが、念のため処理する
      spdlog::debug("Unexpected download wait in real-time mode");
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
      continue;
    } else {
      // その他のエラーコードは問題を示す
      std::ostringstream oss;
      oss << "jvGets failed with error code: " << ret << " after " << record_count << " records";
      throw JVStreamReadException(static_cast<int>(ret), oss.str());
    }
  }

  // JVSessionGuardのデストラクタで自動的にJVCloseが呼ばれる
}

long JVLinkWrapper::performJVRTOpen(const std::string& dataspec, const std::string& key) {
  /**
   * @brief JVRTOpenメソッドのシグネチャ: Long JVRTOpen(String dataspec, String key)
   *
   * @details
   * リアルタイムデータの取得を要求します。
   * JVOpenとは異なり、データはダウンロードなしで直接取得されます。
   *
   * キーの形式はdataspecによって異なります：
   * - レース単位: "YYYYMMDDJJKKHHRR" または "YYYYMMDDJJRR"
   * - 開催日単位: "YYYYMMDD"
   * - 変更イベント単位: JVWatchEventからのパラメータ
   *
   * @return 戻り値：
   *   0: 正常
   *   -1: データなし
   *   -111: dataspecパラメータが不正
   *   -114: keyパラメータが不正
   *   -201: JVInitが呼ばれていない
   *   -202: 前のJVOpen/JVRTOpenがクローズされていない
   *   -301〜-303: 認証エラー
   *   -4xx: サーバーエラー
   *   -504: サーバーメンテナンス中
   */
  if (!jvlink_dispatch_) return -999;

  // 引数を準備（COMディスパッチのために逆順）
  VARIANT args[2];
  VariantInit(&args[0]);
  args[0].vt = VT_BSTR;
  args[0].bstrVal = convertUtf8ToBSTR(key);  // keyパラメータ
  VariantInit(&args[1]);
  args[1].vt = VT_BSTR;
  args[1].bstrVal = convertUtf8ToBSTR(dataspec);  // dataspecパラメータ

  VARIANT result;
  VariantInit(&result);

  // JVRTOpenを呼び出し
  HRESULT hr = invokeMethod(jvlink::dispid::JV_RT_OPEN, DISPATCH_METHOD, args, 2, &result);

  // BSTRのコピーをクリーンアップ
  SysFreeString(args[0].bstrVal);
  SysFreeString(args[1].bstrVal);

  if (FAILED(hr)) {
    spdlog::error("JVRTOpen COM invocation failed with HRESULT: {:#x}", hr);
    return -999;
  }

  long return_code = result.lVal;

  // 成功または特定のエラーをログに記録
  if (return_code == 0) {
    spdlog::info("JVRTOpen successful - dataspec: {}, key: {}", dataspec, key);
  } else {
    switch (return_code) {
      case -1:
        spdlog::info("JVRTOpen: No data available for key: {}", key);
        break;
      case -111:
        spdlog::error("JVRTOpen failed: dataspec parameter invalid: {}", dataspec);
        break;
      case -114:
        spdlog::error("JVRTOpen failed: key parameter invalid: {}", key);
        break;
      case -201:
        spdlog::error("JVRTOpen failed: JVInit not called");
        break;
      case -202:
        spdlog::error("JVRTOpen failed: previous JVOpen/JVRTOpen not closed");
        break;
      case -301:
        spdlog::error("JVRTOpen failed: authentication error");
        break;
      case -302:
        spdlog::error("JVRTOpen failed: service key expired");
        break;
      case -303:
        spdlog::error("JVRTOpen failed: service key not set");
        break;
      case -504:
        spdlog::error("JVRTOpen failed: server under maintenance");
        break;
      default:
        spdlog::error("JVRTOpen failed with error code: {}", return_code);
    }
  }
  return return_code;
}

long JVLinkWrapper::skipCurrentFile() {
  // 初期化状態をチェック
  if (!is_initialized_) {
    spdlog::error("JVLinkWrapper not initialized - cannot skip");
    return -201;
  }

  // COMスレッドで実行
  if (!m_comWorker || !m_comWorker->isRunning() || m_comWorker->isInComThread()) {
    return performJVSkip();
  }
  return m_comWorker->invokeTask<long>([this]() { return performJVSkip(); });
}

bool JVLinkWrapper::startEventWatch() {
  /**
   * @brief JVWatchEventメソッドのシグネチャ: Long JVWatchEvent()
   *
   * @details
   * リアルタイム更新のためのイベント通知スレッドを開始します：
   * - JVEvtPay: 払戻確定
   * - JVEvtJockeyChange: 騎手変更
   * - JVEvtWeather: 天候・馬場状態変更
   * - JVEvtCourseChange: コース変更
   * - JVEvtAvoid: 出走取消・竵走除外
   * - JVEvtTimeChange: 発走時刻変更
   * - JVEvtWeight: 馬体重発表
   *
   * @return 戻り値：
   *   0: 正常
   *   -201: JVInitが実行されていない
   *   その他負数: エラー
   */
  if (!jvlink_dispatch_) return false;

  // COMスレッドでJVWatchEventを実行
  long return_code = m_comWorker->invokeTask<long>([this]() {
    VARIANT result;
    VariantInit(&result);
    HRESULT hr = invokeMethod(jvlink::dispid::JV_WATCH_EVENT, DISPATCH_METHOD, nullptr, 0, &result);
    if (FAILED(hr)) {
      spdlog::error("JVWatchEvent invoke failed with HRESULT: {:#x}", hr);
      return -999L;
    }
    return result.lVal;
  });

  spdlog::info("JVWatchEvent returned: {}", return_code);

  if (return_code == 0) {
    // COMスレッドはすでにメッセージポンプを実行しているので、
    // 追加のアクションは不要
    spdlog::info("Event watch started successfully");
  }

  return return_code == 0;
}

bool JVLinkWrapper::stopEventWatch() {
  /**
   * @brief JVWatchEventCloseメソッドのシグネチャ: Long JVWatchEventClose()
   *
   * @details
   * イベント通知スレッドを終了します。
   *
   * @return 戻り値：
   *   0: 正常
   *   -1: エラー
   */
  if (!jvlink_dispatch_) return false;

  // COMスレッドでJVWatchEventCloseを実行
  long return_code = m_comWorker->invokeTask<long>([this]() {
    VARIANT result;
    VariantInit(&result);
    HRESULT hr = invokeMethod(jvlink::dispid::JV_WATCH_EVENT_CLOSE, DISPATCH_METHOD, nullptr, 0, &result);
    if (FAILED(hr)) {
      spdlog::error("JVWatchEventClose invoke failed with HRESULT: {:#x}", hr);
      return -1L;
    }
    return result.lVal;
  });

  spdlog::info("JVWatchEventClose returned: {}", return_code);
  return return_code == 0;
}

void JVLinkWrapper::setEventHandler(EventHandler handler) {
  m_eventHandler = handler;
  if (!m_comWorker) {
    return;
  }

  if (m_comWorker->isInComThread()) {
    if (m_eventHandler) {
      connectEventSink();
    } else {
      disconnectEventSink();
    }
    return;
  }

  if (m_eventHandler) {
    // COMスレッドでイベントシンクを接続
    if (!m_comWorker->postTask([this]() { connectEventSink(); })) {
      spdlog::warn("Failed to enqueue connectEventSink task; COM worker may be stopping");
    }
  } else {
    // COMスレッドでイベントシンクを切断
    if (!m_comWorker->postTask([this]() { disconnectEventSink(); })) {
      spdlog::warn("Failed to enqueue disconnectEventSink task; COM worker may be stopping");
    }
  }
}

bool JVLinkWrapper::connectEventSink() {
  spdlog::info("connectEventSink called - Thread ID: {}", GetCurrentThreadId());

  if (!jvlink_dispatch_ || !m_eventHandler) {
    spdlog::debug("connectEventSink: jvlink_dispatch_={}, m_eventHandler={}", (void*)jvlink_dispatch_,
                  m_eventHandler ? "set" : "null");
    return false;
  }
  if (m_pConnectionPoint) {  // すでに接続済み
    spdlog::debug("connectEventSink: Already connected");
    return true;
  }

  spdlog::info("Connecting JV-Link event sink...");

  // COMスレッド内で実行されていることを確認
  if (!m_comWorker->isInComThread()) {
    spdlog::error("connectEventSink must be called from COM thread!");
    return false;
  }

  IConnectionPointContainer* pCPC = nullptr;
  HRESULT hr = jvlink_dispatch_->QueryInterface(IID_IConnectionPointContainer, (void**)&pCPC);
  if (FAILED(hr)) {
    spdlog::error("Failed to get IConnectionPointContainer: HRESULT={:#x}", hr);
    return false;
  }
  spdlog::debug("Got IConnectionPointContainer successfully");

  hr = pCPC->FindConnectionPoint(IID_IJVLinkEvents, &m_pConnectionPoint);
  pCPC->Release();
  if (FAILED(hr)) {
    spdlog::error("Failed to find connection point for IID_IJVLinkEvents: HRESULT={:#x}", hr);
    return false;
  }
  spdlog::debug("Found connection point for IID_IJVLinkEvents");

  m_pEventSink = new JVLinkEventSink(m_eventHandler);
  m_pEventSink->AddRef();
  spdlog::debug("Created JVLinkEventSink instance");

  hr = m_pConnectionPoint->Advise(m_pEventSink, &m_dwConnectionCookie);
  if (FAILED(hr)) {
    spdlog::error("Failed to advise event sink: HRESULT={:#x}", hr);
    m_pConnectionPoint->Release();
    m_pConnectionPoint = nullptr;
    m_pEventSink->Release();
    m_pEventSink = nullptr;
    return false;
  }

  spdlog::info("JV-Link event sink connected successfully (cookie={}, thread={})", m_dwConnectionCookie,
               GetCurrentThreadId());
  return true;
}

void JVLinkWrapper::disconnectEventSink() {
  if (m_pConnectionPoint) {
    spdlog::info("Disconnecting JV-Link event sink (cookie={})", m_dwConnectionCookie);
    m_pConnectionPoint->Unadvise(m_dwConnectionCookie);
    m_pConnectionPoint->Release();
    m_pConnectionPoint = nullptr;
  }
  if (m_pEventSink) {
    m_pEventSink->Release();
    m_pEventSink = nullptr;
  }
}

long JVLinkWrapper::performJVFukuFile(const std::string& pattern, const std::string& filepath) {
  /**
   * @brief JVFukuFileメソッドのシグネチャ: Long JVFukuFile(String pattern, String filepath)
   *
   * @details
   * 勝負服の色柄表示から50x50ピクセル、24ビットビットマップ画像を作成します。
   * 画像が作成できない場合は「No Image」画像が出力されます。
   *
   * @param pattern 勝負服の色柄表示（最大30全角文字）例："水色，赤山形一本輪，水色袖"
   * @param filepath 出力する画像ファイルのフルパス（存在するフォルダ必須）
   * @return 戻り値：
   *   0: 正常処理
   *   負値: エラー（認証エラー、サーバーエラーなど）
   */
  if (!jvlink_dispatch_) return -999;

  spdlog::info("Generating uniform image - pattern: {}, filepath: {}", pattern, filepath);

  // ファイルパスのディレクトリが存在するか確認
  std::string directory = filepath.substr(0, filepath.find_last_of("\\/"));
  struct stat st;
  if (stat(directory.c_str(), &st) != 0 || !(st.st_mode & S_IFDIR)) {
    spdlog::warn("Directory does not exist: {}", directory);
  }

  // 引数を準備（COMでは引数は逆順で渡す）
  VARIANT args[2];
  VariantInit(&args[0]);
  VariantInit(&args[1]);

  args[0].vt = VT_BSTR;
  args[0].bstrVal = convertUtf8ToBSTR(filepath);  // filepath (2番目の引数)

  args[1].vt = VT_BSTR;
  args[1].bstrVal = convertUtf8ToBSTR(pattern);  // pattern (1番目の引数)

  VARIANT result;
  VariantInit(&result);

  // JVFukuFileを呼び出し
  HRESULT hr = invokeMethod(jvlink::dispid::JV_FUKU_FILE, DISPATCH_METHOD, args, 2, &result);

  // BSTRのコピーをクリーンアップ
  SysFreeString(args[0].bstrVal);
  SysFreeString(args[1].bstrVal);

  if (FAILED(hr)) {
    spdlog::error("JVFukuFile COM invocation failed with HRESULT: {:#x}", hr);

    // より詳細なエラー情報を取得
    if (hr == E_UNEXPECTED) {
      spdlog::error("E_UNEXPECTED: The method may not be supported or DISPID may be incorrect");
    } else if (hr == (HRESULT)0x80020003) {  // DISP_E_MEMBERNOTFOUND
      spdlog::error("DISP_E_MEMBERNOTFOUND: Method with DISPID {:#x} not found", jvlink::dispid::JV_FUKU_FILE);
    } else if (hr == E_NOINTERFACE) {
      spdlog::error("E_NOINTERFACE: Interface not supported");
    }

    return -999;
  }

  long return_code = result.lVal;

  // 結果をログに記録
  if (return_code == 0) {
    spdlog::info("JVFukuFile successful - uniform image saved to: {}", filepath);
  } else if (return_code == -1) {
    spdlog::warn("JVFukuFile: No data - 'No Image' was generated");
  } else {
    spdlog::error("JVFukuFile failed with error code: {}", return_code);
  }

  VariantClear(&result);
  return return_code;
}

long JVLinkWrapper::performJVFuku(const std::string& pattern, BYTE** buff, long* size) {
  /**
   * @brief JVFukuメソッドのシグネチャ: Long JVFuku(String pattern, Byte Array buff)
   *
   * @details
   * 勝負服の色柄表示から50x50ピクセル、24ビットビットマップ画像データを返します。
   * 画像が作成できない場合は「No Image」のデータが返されます。
   *
   * @param pattern 勝負服の色柄表示（最大30全角文字）
   * @param buff 画像データを受け取るバイト配列へのポインタ
   * @return 戻り値：
   *   0: 正常処理
   *   負値: エラー
   */
  if (!jvlink_dispatch_) return -999;

  spdlog::info("Generating uniform image binary - pattern: {}", pattern);

  // 引数を準備
  VARIANT args[2];
  VariantInit(&args[0]);
  VariantInit(&args[1]);

  // バイト配列を受け取るためのSAFEARRAYを準備
  SAFEARRAY* pSafeArray = NULL;

  args[0].vt = VT_BYREF | VT_ARRAY | VT_UI1;
  args[0].pparray = &pSafeArray;

  args[1].vt = VT_BSTR;
  args[1].bstrVal = convertUtf8ToBSTR(pattern);

  VARIANT result;
  VariantInit(&result);

  // JVFukuを呼び出し
  HRESULT hr = invokeMethod(jvlink::dispid::JV_FUKU, DISPATCH_METHOD, args, 2, &result);

  // BSTRのコピーをクリーンアップ
  SysFreeString(args[1].bstrVal);

  if (FAILED(hr)) {
    spdlog::error("JVFuku COM invocation failed with HRESULT: {:#x}", hr);
    return -999;
  }

  long return_code = result.lVal;

  // 正常画像または"No Image"画像が返る場合、SAFEARRAYからデータを抽出
  if ((return_code == 0 || return_code == -1) && pSafeArray != NULL) {
    BYTE* pData = NULL;
    hr = SafeArrayAccessData(pSafeArray, (void**)&pData);
    if (SUCCEEDED(hr)) {
      // SAFEARRAYのサイズを取得
      long lBound, uBound;
      SafeArrayGetLBound(pSafeArray, 1, &lBound);
      SafeArrayGetUBound(pSafeArray, 1, &uBound);
      *size = uBound - lBound + 1;

      // データをコピー
      *buff = new BYTE[*size];
      memcpy(*buff, pData, *size);

      SafeArrayUnaccessData(pSafeArray);
      if (return_code == 0) {
        spdlog::info("JVFuku successful - image size: {} bytes", *size);
      } else {
        spdlog::warn("JVFuku: No data - fallback image size: {} bytes", *size);
      }
    }
    SafeArrayDestroy(pSafeArray);
  } else if (return_code == -1) {
    spdlog::warn("JVFuku: No data - 'No Image' was generated");
  } else {
    spdlog::error("JVFuku failed with error code: {}", return_code);
  }

  VariantClear(&result);
  return return_code;
}

long JVLinkWrapper::performJVCourseFile(const std::string& key, std::string& filepath, std::string& explanation) {
  /**
   * @brief JVCourseFileメソッドのシグネチャ: Long JVCourseFile(String key, String filepath, String explanation)
   *
   * @details
   * 指定されたレースのコース図を取得し、説明文と共に返します。
   * 画像は256x200ピクセルのGIFで、m_savepathのpicturesフォルダに一時保存されます。
   *
   * @param key リクエストキー（YYYYMMDDJJKKKKTT）最新を取得する場合はYYYYMMDDに"99999999"を指定
   * @param filepath 保存された画像のファイルパス（出力）
   * @param explanation コース説明文（出力、最大6800バイト）
   * @return 戻り値：
   *   0: 正常処理
   *   -1: データなし
   *   負値: エラー
   */
  if (!jvlink_dispatch_) return -999;

  spdlog::info("Retrieving course map - key: {}", key);

  // 引数を準備
  VARIANT args[3];
  VariantInit(&args[0]);
  VariantInit(&args[1]);
  VariantInit(&args[2]);

  // explanation は COM の逆順引数で先頭に置く必要がある
  BSTR bstrExplanation = NULL;
  args[0].vt = VT_BYREF | VT_BSTR;
  args[0].pbstrVal = &bstrExplanation;

  // filepath は 2 番目の out 引数
  BSTR bstrFilepath = NULL;
  args[1].vt = VT_BYREF | VT_BSTR;
  args[1].pbstrVal = &bstrFilepath;

  args[2].vt = VT_BSTR;
  args[2].bstrVal = convertUtf8ToBSTR(key);

  VARIANT result;
  VariantInit(&result);

  // JVCourseFileを呼び出し
  HRESULT hr = invokeMethod(jvlink::dispid::JV_COURSE_FILE, DISPATCH_METHOD, args, 3, &result);

  // BSTRのコピーをクリーンアップ
  SysFreeString(args[2].bstrVal);

  if (FAILED(hr)) {
    spdlog::error("JVCourseFile COM invocation failed with HRESULT: {:#x}", hr);
    SysFreeString(bstrFilepath);
    SysFreeString(bstrExplanation);
    return -999;
  }

  long return_code = result.lVal;

  // 成功した場合、出力パラメータを設定
  if (return_code == 0) {
    filepath = convertBSTRToString(bstrFilepath);
    explanation = convertBSTRToString(bstrExplanation);
    spdlog::info("JVCourseFile successful - course map saved to: {}", filepath);
  } else if (return_code == -1) {
    spdlog::warn("JVCourseFile: No data found for key: {}", key);
  } else {
    spdlog::error("JVCourseFile failed with error code: {}", return_code);
  }

  // BSTRをクリーンアップ
  SysFreeString(bstrFilepath);
  SysFreeString(bstrExplanation);
  VariantClear(&result);

  return return_code;
}

long JVLinkWrapper::performJVCourseFile2(const std::string& key, const std::string& filepath) {
  /**
   * @brief JVCourseFile2メソッドのシグネチャ: Long JVCourseFile2(String key, String filepath)
   *
   * @details
   * 指定されたレースのコース図を取得し、指定パスに保存します。
   * 画像は256x200ピクセルのGIFです。
   *
   * @param key リクエストキー（YYYYMMDDJJKKKKTT）最新を取得する場合はYYYYMMDDに"99999999"を指定
   * @param filepath 出力するコース図ファイルのフルパス（存在するフォルダ必須）
   * @return 戻り値：
   *   0: 正常処理
   *   -1: データなし
   *   -118: filepathパラメータが無効
   *   負値: エラー
   */
  if (!jvlink_dispatch_) return -999;

  spdlog::info("Retrieving course map - key: {}, filepath: {}", key, filepath);

  // 引数を準備
  VARIANT args[2];
  VariantInit(&args[0]);
  VariantInit(&args[1]);

  args[0].vt = VT_BSTR;
  args[0].bstrVal = convertUtf8ToBSTR(filepath);

  args[1].vt = VT_BSTR;
  args[1].bstrVal = convertUtf8ToBSTR(key);

  VARIANT result;
  VariantInit(&result);

  // JVCourseFile2を呼び出し
  HRESULT hr = invokeMethod(jvlink::dispid::JV_COURSE_FILE2, DISPATCH_METHOD, args, 2, &result);

  // BSTRのコピーをクリーンアップ
  SysFreeString(args[0].bstrVal);
  SysFreeString(args[1].bstrVal);

  if (FAILED(hr)) {
    spdlog::error("JVCourseFile2 COM invocation failed with HRESULT: {:#x}", hr);
    return -999;
  }

  long return_code = result.lVal;

  // 結果をログに記録
  if (return_code == 0) {
    spdlog::info("JVCourseFile2 successful - course map saved to: {}", filepath);
  } else if (return_code == -1) {
    spdlog::warn("JVCourseFile2: No data found for key: {}", key);
  } else if (return_code == jvlink::error::JV_ERROR_PARAM_FILEPATH_INVALID) {
    spdlog::error("JVCourseFile2: Invalid filepath parameter: {}", filepath);
  } else {
    spdlog::error("JVCourseFile2 failed with error code: {}", return_code);
  }

  VariantClear(&result);
  return return_code;
}
