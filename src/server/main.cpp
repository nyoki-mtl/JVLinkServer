#include <httplib.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/spdlog.h>
#include <windows.h>

#include <chrono>
#include <condition_variable>
#include <csignal>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <atomic>
#include <mutex>
#include <queue>
#include <regex>
#include <sstream>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "core/jv_link_wrapper.h"
#include "data/record_parser.h"
#include "json.hpp"
#include "server/api_version.h"
#include "server/openapi_handler.h"

using json = nlohmann::json;

namespace {

std::string resolveRecordTypeForOutput(const ParsedRecord& record) {
  const std::string mapped = ::recordTypeToString(record.type);
  if (mapped != "UNKNOWN") {
    return mapped;
  }

  if (!record.record_type_id.empty()) {
    return record.record_type_id;
  }

  if (record.raw_data.size() >= 2) {
    return record.raw_data.substr(0, 2);
  }

  return mapped;
}

void writeStreamErrorLine(httplib::DataSink& sink, std::mutex& sink_mutex, const std::string& message, int code) {
  if (!sink.is_writable()) {
    return;
  }

  json payload = {{"error", {{"message", message}, {"code", code}}}};
  std::string line = payload.dump();

  std::lock_guard<std::mutex> lock(sink_mutex);
  if (!sink.is_writable()) {
    return;
  }
  sink.write(line.c_str(), line.length());
  sink.write("\n", 1);
}

}  // namespace

/**
 * ログ機能を初期化する
 *
 * ログファイルの作成、コンソール出力設定、ログレベルの設定を行う。
 * ログファイルは実行ファイルと同じディレクトリの logs/JVLinkServer_YYYYMMDD_HHMMSS.log 形式で保存される。
 *
 * @param log_level ログレベル文字列 ("debug", "info", "warn", "error")
 */
void initializeLogging(const std::string& log_level = "info") {
  try {
    // 実行ファイルのパスを取得
    char exe_path[MAX_PATH];
    GetModuleFileNameA(NULL, exe_path, MAX_PATH);

    // ディレクトリパスを抽出
    std::string exe_dir = exe_path;
    size_t last_slash = exe_dir.find_last_of("\\/");
    if (last_slash != std::string::npos) {
      exe_dir = exe_dir.substr(0, last_slash);
    }

    // ログディレクトリを実行ファイルと同じ場所に作成
    std::string log_dir = exe_dir + "\\logs";

    // Windowsでディレクトリを作成（既存の場合はエラーを無視）
    std::string create_dir_cmd = "mkdir \"" + log_dir + "\" 2>nul";
    system(create_dir_cmd.c_str());

    // タイムスタンプをファイル名に使用するため現在時刻を取得
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);

    std::stringstream ss;
    ss << std::put_time(std::localtime(&time_t), "%Y%m%d_%H%M%S");
    std::string timestamp = ss.str();

    // タイムスタンプ付きのログファイルパスを生成
    std::string log_file_path = log_dir + "\\JVLinkServer_" + timestamp + ".log";

    // 文字列からログレベルを決定
    spdlog::level::level_enum level = spdlog::level::info;
    if (log_level == "debug")
      level = spdlog::level::debug;
    else if (log_level == "warn")
      level = spdlog::level::warn;
    else if (log_level == "error")
      level = spdlog::level::err;

    // ファイル出力用シンクを作成（全てのログを記録）
    auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>(log_file_path);
    file_sink->set_level(level);

    // コンソール出力用シンクを作成（警告以上のみ表示）
    auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    console_sink->set_level(spdlog::level::warn);

    // 複数のシンクを持つロガーを作成
    std::vector<spdlog::sink_ptr> sinks{file_sink, console_sink};
    auto logger = std::make_shared<spdlog::logger>("JVLinkServer", sinks.begin(), sinks.end());

    logger->set_level(level);
    logger->flush_on(spdlog::level::info);

    // グローバルデフォルトロガーとして設定
    spdlog::set_default_logger(logger);

    // ログ出力フォーマットを設定
    spdlog::set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%l] [%n] %v");

    // 初期化成功をコンソールにも通知（warnレベル使用）
    spdlog::warn("JVLinkServer logging initialized - log file: {}", log_file_path);

    // 詳細情報はファイルにのみ記録
    spdlog::info("JVLinkServer logging initialized");
    spdlog::info("Log file: {}", log_file_path);
    spdlog::info("Log level: {}", log_level);

  } catch (const std::exception& e) {
    std::cerr << "Failed to initialize logging: " << e.what() << std::endl;
  }
}

/**
 * JV-Link HTTPサーバークラス
 *
 * JV-Link COMコンポーネントをHTTP APIとして公開するサーバー実装。
 * Pythonクライアントからのリクエストを受け付け、JRA-VANの競馬データを提供する。
 *
 * 主要エンドポイント:
 * - GET  /health: サーバーヘルスチェック
 * - GET  /version: バージョン情報
 * - POST /query/stored: 蓄積系データ取得（ストリーミング）
 * - POST /query/realtime: リアルタイムデータ取得
 * - POST /event/start: イベント監視開始
 * - POST /event/stop: イベント監視停止
 * - GET  /events/stream: イベントSSEストリーミング
 * - POST /shutdown: サーバー停止
 */
class JVLinkHTTPServer {
 private:
  std::unique_ptr<httplib::Server> server_;
  std::unique_ptr<JVLinkWrapper> jvlink_wrapper_;
  std::unique_ptr<jvlink::OpenAPIHandler> openapi_handler_;
  int port_;
  std::string sid_;
  bool running_;
  std::thread server_thread_;

  // イベントキュー（Server-Sent Events配信用）
  struct JVEvent {
    std::string type;
    std::string param;
    int64_t timestamp;
  };
  std::queue<JVEvent> event_queue_;
  std::mutex event_queue_mutex_;
  std::condition_variable event_cv_;
  std::mutex jvlink_operation_mutex_;

 public:
  /**
   * コンストラクタ
   *
   * HTTPサーバー、JV-Linkラッパー、OpenAPIハンドラーを初期化する。
   * イベントハンドラーの設定とルート定義も行う。
   *
   * @param port HTTPサーバーの待機ポート番号
   */
  explicit JVLinkHTTPServer(int port, std::string sid) : port_(port), sid_(std::move(sid)), running_(false) {
    server_ = std::make_unique<httplib::Server>();
    jvlink_wrapper_ = std::make_unique<JVLinkWrapper>();
    openapi_handler_ = std::make_unique<jvlink::OpenAPIHandler>("127.0.0.1", port_);

    // JV-Linkイベントを受信するためのハンドラーを設定
    jvlink_wrapper_->setEventHandler(
        [this](DISPID dispId, const std::wstring& param) { handleJvLinkEvent(dispId, param); });

    setupRoutes();
    setupErrorHandlers();
  }

  /**
   * デストラクタ
   *
   * サーバーが実行中の場合は停止処理を実行する。
   */
  ~JVLinkHTTPServer() {
    spdlog::info("JVLinkHTTPServer destructor called");
    stop();
  }

  /**
   * HTTPサーバーを開始する
   *
   * JV-Linkの初期化とHTTPサーバーの起動を行う。
   * ブロッキングモードでは呼び出し元スレッドで実行され、
   * 非ブロッキングモードでは別スレッドで実行される。
   *
   * @param blocking true: ブロッキング実行, false: バックグラウンド実行
   * @return 起動に成功した場合true
   */
  bool start(bool blocking = false) {
    if (running_) {
      spdlog::warn("Server is already running on port {}", port_);
      return false;
    }

    // JV-Link COMコンポーネントを初期化
    if (!jvlink_wrapper_->initialize(sid_)) {
      spdlog::error("Failed to initialize JVLink");
      return false;
    }

    running_ = true;
    // サーバー起動をコンソールにも通知（warnレベル使用）
    spdlog::warn("JVLinkServer started on port {}", port_);

    if (blocking) {
      return server_->listen("127.0.0.1", port_);
    } else {
      server_thread_ = std::thread([this]() { server_->listen("127.0.0.1", port_); });

      // サーバースレッドの起動を待機
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
      return true;
    }
  }

  /**
   * HTTPサーバーを停止する
   *
   * HTTPサーバーの停止、サーバースレッドの終了待機、
   * JV-Linkのシャットダウンを順次実行する。
   */
  void stop() {
    if (!running_) {
      return;
    }

    spdlog::info("Stopping HTTP server...");
    running_ = false;

    if (server_) {
      server_->stop();
    }

    if (server_thread_.joinable()) {
      server_thread_.join();
    }

    if (jvlink_wrapper_) {
      jvlink_wrapper_->shutdown();
      spdlog::info("JV-Link shutdown completed");
    }

    // 全ログを確実に書き込む
    spdlog::info("HTTP server stop completed");
    spdlog::flush_on(spdlog::level::info);
  }

  /**
   * サーバーの実行状態を確認する
   *
   * @return サーバーが実行中の場合true
   */
  bool isRunning() const { return running_; }

 private:
  void setBusyResponse(httplib::Response& res, const std::string& operation) {
    res.status = 503;
    json error_response = {{"error", {{"code", -202}, {"message", "JV-Link session is busy"}}},
                           {"operation", operation}};
    res.set_content(error_response.dump(), "application/json; charset=utf-8");
  }

  bool tryBeginOperation(std::unique_lock<std::mutex>& op_lock, httplib::Response& res, const std::string& operation) {
    op_lock = std::unique_lock<std::mutex>(jvlink_operation_mutex_, std::try_to_lock);
    if (op_lock.owns_lock()) {
      return true;
    }
    setBusyResponse(res, operation);
    return false;
  }

  /**
   * HTTPルートとハンドラーを設定する
   *
   * 全てのAPIエンドポイントのルーティングを定義し、
   * タイムアウト設定とCORS設定を行う。
   */
  void setupRoutes() {
    // ストリーミング対応のためタイムアウトを設定（環境変数で調整可能）
    auto get_env_int = [](const char* name, int def) {
      const char* v = std::getenv(name);
      if (!v) return def;
      int parsed = std::atoi(v);
      return parsed > 0 ? parsed : def;
    };
    int read_to_sec = get_env_int("JVLINK_SERVER_READ_TIMEOUT", 65);
    int write_to_sec = get_env_int("JVLINK_SERVER_WRITE_TIMEOUT", 65);
    server_->set_read_timeout(read_to_sec, 0);
    server_->set_write_timeout(write_to_sec, 0);

    // Cross-Origin Resource Sharing (CORS) を設定
    server_->set_pre_routing_handler([](const httplib::Request&, httplib::Response& res) {
      res.set_header("Access-Control-Allow-Origin", "*");
      res.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
      res.set_header("Access-Control-Allow-Headers", "Content-Type");
      return httplib::Server::HandlerResponse::Unhandled;
    });

    // CORSプリフライトリクエストを処理
    server_->Options(".*", [](const httplib::Request&, httplib::Response& res) { res.set_content("", "text/plain"); });

    // OpenAPI仕様書エンドポイント
    server_->Get("/openapi.json", [this](const httplib::Request& req, httplib::Response& res) {
      openapi_handler_->handleOpenAPIRequest(req, res);
    });

    // サーバー状態確認用エンドポイント
    server_->Get("/health", [this](const httplib::Request& req, httplib::Response& res) { handleHealth(req, res); });

    // APIバージョン情報エンドポイント
    server_->Get("/version", [this](const httplib::Request& req, httplib::Response& res) { handleVersion(req, res); });

    // 蓄積系データ取得エンドポイント（バージョニング対応）
    server_->Post("/query/stored",
                  [this](const httplib::Request& req, httplib::Response& res) { handleQuery(req, res); });
    server_->Post("/v1/query/stored",
                  [this](const httplib::Request& req, httplib::Response& res) { handleQuery(req, res); });

    // サーバーシャットダウンエンドポイント
    server_->Post("/shutdown",
                  [this](const httplib::Request& req, httplib::Response& res) { handleShutdown(req, res); });
    server_->Post("/v1/shutdown",
                  [this](const httplib::Request& req, httplib::Response& res) { handleShutdown(req, res); });

    // 速報系データ取得エンドポイント
    server_->Post("/query/realtime",
                  [this](const httplib::Request& req, httplib::Response& res) { handleRealtimeOpen(req, res); });
    server_->Post("/v1/query/realtime",
                  [this](const httplib::Request& req, httplib::Response& res) { handleRealtimeOpen(req, res); });

    // イベント監視開始エンドポイント
    server_->Post("/event/start",
                  [this](const httplib::Request& req, httplib::Response& res) { handleEventStart(req, res); });
    server_->Post("/v1/event/start",
                  [this](const httplib::Request& req, httplib::Response& res) { handleEventStart(req, res); });

    server_->Post("/event/stop",
                  [this](const httplib::Request& req, httplib::Response& res) { handleEventStop(req, res); });
    server_->Post("/v1/event/stop",
                  [this](const httplib::Request& req, httplib::Response& res) { handleEventStop(req, res); });

    // Server-Sent Eventsによるイベントストリーミング
    server_->Get("/events/stream",
                 [this](const httplib::Request& req, httplib::Response& res) { handleEventStream(req, res); });
    server_->Get("/v1/events/stream",
                 [this](const httplib::Request& req, httplib::Response& res) { handleEventStream(req, res); });

    // ファイル削除エンドポイント
    server_->Post("/files/delete",
                  [this](const httplib::Request& req, httplib::Response& res) { handleFileDelete(req, res); });
    server_->Post("/v1/files/delete",
                  [this](const httplib::Request& req, httplib::Response& res) { handleFileDelete(req, res); });

    // 勝負服画像生成エンドポイント（ファイル保存）
    server_->Post("/uniform/file",
                  [this](const httplib::Request& req, httplib::Response& res) { handleUniformFile(req, res); });
    server_->Post("/v1/uniform/file",
                  [this](const httplib::Request& req, httplib::Response& res) { handleUniformFile(req, res); });

    // 勝負服画像生成エンドポイント（バイナリ返却）
    server_->Post("/uniform/image",
                  [this](const httplib::Request& req, httplib::Response& res) { handleUniformImage(req, res); });
    server_->Post("/v1/uniform/image",
                  [this](const httplib::Request& req, httplib::Response& res) { handleUniformImage(req, res); });

    // コース図取得エンドポイント（説明文付き）
    server_->Post("/course/file",
                  [this](const httplib::Request& req, httplib::Response& res) { handleCourseFile(req, res); });
    server_->Post("/v1/course/file",
                  [this](const httplib::Request& req, httplib::Response& res) { handleCourseFile(req, res); });

    // コース図取得エンドポイント（ファイル保存）
    server_->Post("/course/file2",
                  [this](const httplib::Request& req, httplib::Response& res) { handleCourseFile2(req, res); });
    server_->Post("/v1/course/file2",
                  [this](const httplib::Request& req, httplib::Response& res) { handleCourseFile2(req, res); });

    // コース図取得エンドポイント（バイナリ返却）
    server_->Post("/course/image",
                  [this](const httplib::Request& req, httplib::Response& res) { handleCourseImage(req, res); });
    server_->Post("/v1/course/image",
                  [this](const httplib::Request& req, httplib::Response& res) { handleCourseImage(req, res); });
  }

  /**
   * HTTPエラーハンドラーを設定する
   *
   * リクエスト処理中のエラーや例外を捕捉し、
   * 適切なJSONレスポンスを返す。
   */
  void setupErrorHandlers() {
    server_->set_error_handler([](const httplib::Request& req, httplib::Response& res) {
      spdlog::error("HTTP Error: {} for {} from {}", res.status, req.path, req.remote_addr);

      // ハンドラーがすでに詳細なエラー本文を設定している場合は上書きしない
      if (!res.body.empty()) {
        return;
      }

      std::string error_message = "Request failed";
      if (res.status == 404) {
        error_message = "Not found";
      } else if (res.status >= 500) {
        error_message = "Internal server error";
      }

      json error_response = {
          {"status", "error"},   {"error_message", error_message}, {"read_count", -1},
          {"download_count", 0}, {"last_file_timestamp", nullptr}, {"records", json::array()}};

      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    });

    server_->set_exception_handler([](const httplib::Request& req, httplib::Response& res, std::exception_ptr ep) {
      try {
        std::rethrow_exception(ep);
      } catch (const std::exception& e) {
        spdlog::error("Exception in request to {}: {}", req.path, e.what());

        json error_response = {{"status", "error"},
                               {"error_message", std::string("Exception: ") + e.what()},
                               {"read_count", -1},
                               {"download_count", 0},
                               {"last_file_timestamp", nullptr},
                               {"records", json::array()}};

        res.set_content(error_response.dump(), "application/json; charset=utf-8");
      } catch (...) {
        spdlog::error("Unknown exception in request to {}", req.path);

        json error_response = {
            {"status", "error"},   {"error_message", "Unknown exception"}, {"read_count", -1},
            {"download_count", 0}, {"last_file_timestamp", nullptr},       {"records", json::array()}};

        res.set_content(error_response.dump(), "application/json; charset=utf-8");
      }
    });
  }

  /**
   * ヘルスチェックリクエストを処理する
   *
   * サーバーとJV-Linkコンポーネントの状態を確認し、
   * JSON形式でヘルス情報を返す。
   */
  void handleHealth(const httplib::Request& req, httplib::Response& res) {
    try {
      spdlog::debug("Health check requested from {}", req.remote_addr);

      // JV-Linkコンポーネントの初期化状態を確認
      bool jvlink_initialized = jvlink_wrapper_ && jvlink_wrapper_->isInitialized();

      json health_response = {
          {"status", "healthy"},
          {"timestamp",
           std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch())
               .count()},
          {"service",
           {{"name", "JVLinkServer"},
            {"version", jvlink::server::getApiVersion()},
            {"uptime",
             std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now().time_since_epoch())
                 .count()}}},
          {"components",
           {{"http_server", {{"status", "healthy"}, {"port", port_}}},
            {"jvlink",
             {{"status", jvlink_initialized ? "healthy" : "unhealthy"}, {"initialized", jvlink_initialized}}}}}};

      res.set_content(health_response.dump(), "application/json; charset=utf-8");
    } catch (const std::exception& e) {
      spdlog::error("Error in health check: {}", e.what());
      res.status = 503;
      json error_response = {{"status", "unhealthy"}, {"error", e.what()}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  }

  /**
   * バージョン情報リクエストを処理する
   *
   * APIバージョン、サポートされるバージョン、
   * ビルド情報をJSON形式で返す。
   */
  void handleVersion(const httplib::Request& req, httplib::Response& res) {
    try {
      spdlog::debug("Version info requested from {}", req.remote_addr);

      json version_response = {
          {"api_version", jvlink::server::getApiVersion()},
          {"api_version_major", jvlink::server::API_VERSION_MAJOR},
          {"api_version_minor", jvlink::server::API_VERSION_MINOR},
          {"api_version_patch", jvlink::server::API_VERSION_PATCH},
          {"supported_versions", {"v1"}},
          {"server", {{"name", "JVLinkServer"}, {"build_date", __DATE__}, {"build_time", __TIME__}}}};

      res.set_content(version_response.dump(), "application/json; charset=utf-8");
    } catch (const std::exception& e) {
      spdlog::error("Error getting version info: {}", e.what());
      res.status = 500;
      json error_response = {{"error", e.what()}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  }

  /**
   * 蓄積系データ取得リクエストを処理する
   *
   * JVOpenを使用して過去のデータを取得し、
   * ストリーミング形式でクライアントに返す。
   * 必要に応じてダウンロード待機も行う。
   */
  void handleQuery(const httplib::Request& req, httplib::Response& res) {
    try {
      spdlog::info("Received /query/stored request from {}", req.remote_addr);

      if (req.body.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Request body is empty"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      json request_json;
      try {
        request_json = json::parse(req.body);
      } catch (const json::parse_error&) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Invalid JSON format"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      std::string data_spec = request_json.value("data_spec", "");
      std::string from_date = request_json.value("from_date", "");
      int option = request_json.value("option", 1);
      int max_records_req = request_json.value("max_records", -1);

      // 自動リトライ設定の取得
      bool auto_retry = request_json.value("auto_retry", true);         // デフォルトで自動リトライ有効
      int max_retries = request_json.value("max_retries", 3);           // デフォルトで3回試行
      int retry_delay_ms = request_json.value("retry_delay_ms", 1000);  // デフォルトで1秒待機

      // レコード種別フィルタリングパラメータ（オプション）
      std::vector<std::string> filter_record_types;
      if (request_json.contains("record_types") && request_json["record_types"].is_array()) {
        for (const auto& rt : request_json["record_types"]) {
          if (rt.is_string()) {
            filter_record_types.push_back(rt.get<std::string>());
          }
        }
      }

      spdlog::info("Query parameters - data_spec: '{}', from_date: '{}', option: {}, max_records: {}", data_spec,
                   from_date, option, max_records_req);

      if (!filter_record_types.empty()) {
        std::string filter_str = "";
        for (const auto& rt : filter_record_types) {
          if (!filter_str.empty()) filter_str += ", ";
          filter_str += rt;
        }
        spdlog::info("Record type filter enabled: [{}]", filter_str);
      }

      if (max_retries < 0 || retry_delay_ms < 0) {
        res.status = 400;
        json error_response = {
            {"error", {{"message", "max_retries and retry_delay_ms must be greater than or equal to 0"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      // リトライ設定をログに出力
      if (!auto_retry) {
        spdlog::info("Auto-retry disabled by client");
      } else if (max_retries != 3 || retry_delay_ms != 1000) {
        spdlog::info("Auto-retry config - max_retries: {}, retry_delay_ms: {}", max_retries, retry_delay_ms);
      }

      if (data_spec.empty() || from_date.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Missing required parameters: data_spec, from_date"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      auto session_lock = std::make_shared<std::unique_lock<std::mutex>>(jvlink_operation_mutex_, std::try_to_lock);
      if (!session_lock->owns_lock()) {
        setBusyResponse(res, "query_stored");
        return;
      }

      // JVLinkWrapperにリトライ設定を適用
      JVLinkWrapper::RetryConfig retry_config;
      retry_config.auto_retry_on_corruption = auto_retry;
      retry_config.max_retry_attempts = max_retries;
      retry_config.retry_delay_ms = retry_delay_ms;
      jvlink_wrapper_->setRetryConfig(retry_config);

      // Keep-Alive を明示
      res.set_header("Connection", "keep-alive");

      res.set_chunked_content_provider(
          "application/x-ndjson; charset=utf-8", [this, data_spec, from_date, option, max_records_req,
                                               filter_record_types, session_lock](size_t offset,
                                                                                  httplib::DataSink& sink) {
            (void)session_lock;
            if (offset == 0) {
              // 初回呼び出し時にストリーミング処理を開始

              // メタデータコールバック: ヘッダー情報を送信
              std::mutex sink_mutex;
              std::atomic<bool> streaming_active{true};

              auto safe_write = [&](const char* data, size_t len) {
                std::lock_guard<std::mutex> lock(sink_mutex);
                return sink.write(data, len);
              };

              auto meta_callback = [&](const JVQueryResult& meta_result) {
                json meta_json;
                if (meta_result.success) {
                  meta_json["meta"] = {{"read_count", meta_result.read_count},
                                       {"download_count", meta_result.download_count},
                                       {"last_file_timestamp", meta_result.last_file_timestamp}};
                } else {
                  meta_json["error"] = {{"message", meta_result.error_message}, {"code", meta_result.error_code}};
                }
                std::string meta_str = meta_json.dump();
                safe_write(meta_str.c_str(), meta_str.length());
                safe_write("\n", 1);
              };

              // カスタム例外クラス（クライアント切断用）
              class ClientDisconnectedException : public std::exception {
                const char* what() const noexcept override { return "Client disconnected during streaming"; }
              };

              // レコードコールバック: 各レコードをストリーミング
              auto record_callback = [&](const std::string& record_str) {
                // クライアントの接続状態をチェック
                if (!sink.is_writable()) {
                  spdlog::warn("Client disconnected during streaming for data_spec: {}", data_spec);
                  throw ClientDisconnectedException();  // 例外をスローしてループを中断
                }

                try {
                  // フィルタリングはC++側のJVSkipで行われるため、ここではパースして送信するだけ
                  auto parsed_record = RecordParser::parseRecord(record_str);
                  if (parsed_record) {
                    json record_json;
                    record_json["type"] = resolveRecordTypeForOutput(*parsed_record);
                    record_json["data"] = parsed_record->structured_data;
                    std::string record_json_str = record_json.dump();

                    bool write_success = safe_write(record_json_str.c_str(), record_json_str.length());
                    if (write_success) {
                      safe_write("\n", 1);
                    } else {
                      spdlog::warn("Failed to write record to client for data_spec: {}", data_spec);
                      throw ClientDisconnectedException();
                    }
                  }
                } catch (const ClientDisconnectedException&) {
                  throw;  // 再スロー
                } catch (const std::exception& e) {
                  // エラーをログに記録して処理を継続
                  spdlog::error("Record parsing exception in stream: {}", e.what());
                }
              };

              // ハートビート（空行）を定期送信してクライアントのread timeoutを跨ぐ
              int heartbeat_sec = 0;
              if (const char* hb = std::getenv("JVLINK_SERVER_STREAM_HEARTBEAT_SEC")) {
                int v = std::atoi(hb);
                if (v > 0) heartbeat_sec = v;
              }
              std::thread heartbeat_thread;
              if (heartbeat_sec > 0) {
                heartbeat_thread = std::thread([&]() {
                  spdlog::debug("Streaming heartbeat started ({}s)", heartbeat_sec);
                  while (streaming_active.load()) {
                    for (int i = 0; i < heartbeat_sec && streaming_active.load(); ++i) {
                      std::this_thread::sleep_for(std::chrono::seconds(1));
                    }
                    if (!streaming_active.load()) break;
                    if (!sink.is_writable()) break;
                    if (!safe_write("\n", 1)) break;  // 空行
                  }
                  spdlog::debug("Streaming heartbeat stopped");
                });
              }

              // JVGetsを使用した高性能な実装
              try {
                spdlog::debug("Using JVGets for better performance");
                // クエリ実行（max_records と record_types を反映）
                jvlink_wrapper_->queryStored(data_spec, from_date, option, max_records_req, record_callback,
                                             meta_callback, filter_record_types);
                streaming_active.store(false);
                if (heartbeat_thread.joinable()) heartbeat_thread.join();
              } catch (const ClientDisconnectedException&) {
                // クライアント切断は正常な終了として扱う
                spdlog::info(
                    "Streaming terminated due to client disconnection for data_spec: {}. JVClose will be called "
                    "automatically by RAII guard.",
                    data_spec);
                streaming_active.store(false);
                if (heartbeat_thread.joinable()) heartbeat_thread.join();
              } catch (const JVStreamReadException& e) {
                spdlog::error("Streaming JV read error in /query/stored: {} (code: {})", e.what(), e.errorCode());
                writeStreamErrorLine(
                    sink, sink_mutex, std::string("Streaming JV read error in /query/stored: ") + e.what(),
                    e.errorCode());
                streaming_active.store(false);
                if (heartbeat_thread.joinable()) heartbeat_thread.join();
              } catch (const std::exception& e) {
                spdlog::error("Streaming error in /query/stored: {}", e.what());
                writeStreamErrorLine(
                    sink, sink_mutex, std::string("Streaming error in /query/stored: ") + e.what(), -500);
                streaming_active.store(false);
                if (heartbeat_thread.joinable()) heartbeat_thread.join();
              }
            }

            // ストリーミング終了を通知
            sink.done();
            return true;
          });

    } catch (const std::exception& e) {
      spdlog::error("An error occurred in handleQuery: {}", e.what());
      res.status = 500;
      json error_response = {{"error", {{"message", "Internal Server Error"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  }

  /**
   * サーバーシャットダウンリクエストを処理する
   *
   * クライアントに即座にレスポンスを返し、
   * 非同期でサーバー停止処理を実行する。
   */
  void handleShutdown(const httplib::Request& req, httplib::Response& res) {
    spdlog::info("Shutdown request from {}", req.remote_addr);

    json response = {{"status", "ok"}, {"message", "Server is shutting down"}};
    res.set_content(response.dump(), "application/json; charset=utf-8");

    // 別スレッドでサーバー停止処理を実行
    std::thread([this]() {
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
      stop();
    }).detach();

    spdlog::info("Shutdown sequence initiated");
  }

  /**
   * ファイル削除リクエストを処理する
   *
   * JVFiledeleteを使用してダウンロード済みファイルを削除する。
   * エラーファイルの削除と再ダウンロードに使用される。
   */
  void handleFileDelete(const httplib::Request& req, httplib::Response& res) {
    try {
      spdlog::info("Received /files/delete request from {}", req.remote_addr);
      std::unique_lock<std::mutex> op_lock;
      if (!tryBeginOperation(op_lock, res, "files_delete")) {
        return;
      }

      if (req.body.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Request body is empty"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      json request_json;
      try {
        request_json = json::parse(req.body);
      } catch (const json::parse_error&) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Invalid JSON format"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      std::string filename = request_json.value("filename", "");

      if (filename.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Missing required parameter: filename"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      spdlog::info("Deleting file: {}", filename);

      // JVFiledeleteを呼び出し
      long result = jvlink_wrapper_->deleteFile(filename);

      json response;
      if (result == 0) {
        response = {{"status", "success"}, {"message", "File deleted successfully"}, {"filename", filename}};
        res.status = 200;
      } else {
        std::string error_message;
        switch (result) {
          case -1:
            error_message = "File not found or access denied";
            res.status = 404;
            break;
          case -201:
            error_message = "JVInit not called";
            res.status = 503;
            break;
          default:
            error_message = "Unknown error: " + std::to_string(result);
            res.status = 500;
        }

        response = {
            {"status", "error"}, {"error", {{"code", result}, {"message", error_message}}}, {"filename", filename}};
      }

      res.set_content(response.dump(), "application/json; charset=utf-8");

    } catch (const std::exception& e) {
      spdlog::error("Exception in handleFileDelete: {}", e.what());
      res.status = 500;
      json error_response = {{"error", {{"message", "Internal Server Error"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  }

  /**
   * 勝負服画像生成リクエストを処理する（ファイル保存）
   *
   * JVFukuFileを使用して勝負服パターンから画像ファイルを生成する。
   */
  void handleUniformFile(const httplib::Request& req, httplib::Response& res) {
    try {
      spdlog::info("Received /uniform/file request from {}", req.remote_addr);
      std::unique_lock<std::mutex> op_lock;
      if (!tryBeginOperation(op_lock, res, "uniform_file")) {
        return;
      }

      if (req.body.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Request body is empty"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      json request_json;
      try {
        request_json = json::parse(req.body);
      } catch (const json::parse_error&) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Invalid JSON format"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      std::string pattern = request_json.value("pattern", "");
      std::string filepath = request_json.value("filepath", "");

      if (pattern.empty() || filepath.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Missing required parameters: pattern, filepath"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      spdlog::info("Generating uniform image - pattern: {}, filepath: {}", pattern, filepath);

      // JVFukuFileを呼び出し
      long result = jvlink_wrapper_->fukuFile(pattern, filepath);

      json response;
      if (result == 0) {
        response = {{"status", "success"},
                    {"message", "Uniform image generated successfully"},
                    {"pattern", pattern},
                    {"filepath", filepath}};
        res.status = 200;
      } else if (result == -1) {
        response = {
            {"status", "success"}, {"message", "No Image generated"}, {"pattern", pattern}, {"filepath", filepath}};
        res.status = 200;
      } else {
        std::string error_message;
        switch (result) {
          case jvlink::error::JV_ERROR_PARAM_FILEPATH_INVALID:
            error_message = "Invalid filepath parameter";
            res.status = 400;
            break;
          case -201:
            error_message = "JVInit not called";
            res.status = 500;
            break;
          case -301:
            error_message = "Authentication error";
            res.status = 401;
            break;
          case -504:
            error_message = "Server under maintenance";
            res.status = 503;
            break;
          default:
            error_message = "Unknown error: " + std::to_string(result);
            res.status = 500;
        }

        response = {
            {"status", "error"}, {"error", {{"code", result}, {"message", error_message}}}, {"pattern", pattern}};
      }

      res.set_content(response.dump(), "application/json; charset=utf-8");

    } catch (const std::exception& e) {
      spdlog::error("Exception in handleUniformFile: {}", e.what());
      res.status = 500;
      json error_response = {{"error", {{"message", "Internal Server Error"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  }

  /**
   * 勝負服画像生成リクエストを処理する（バイナリ返却）
   *
   * JVFukuを使用して勝負服パターンから画像データを生成し、バイナリで返す。
   */
  void handleUniformImage(const httplib::Request& req, httplib::Response& res) {
    try {
      spdlog::info("Received /uniform/image request from {}", req.remote_addr);
      std::unique_lock<std::mutex> op_lock;
      if (!tryBeginOperation(op_lock, res, "uniform_image")) {
        return;
      }

      if (req.body.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Request body is empty"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      json request_json;
      try {
        request_json = json::parse(req.body);
      } catch (const json::parse_error&) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Invalid JSON format"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      std::string pattern = request_json.value("pattern", "");

      if (pattern.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Missing required parameter: pattern"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      spdlog::info("Generating uniform image binary - pattern: {}", pattern);

      // JVFukuを呼び出し
      BYTE* image_data = nullptr;
      long image_size = 0;
      long result = jvlink_wrapper_->fuku(pattern, &image_data, &image_size);

      if (result == 0 && image_data != nullptr && image_size > 0) {
        // 画像データをバイナリとして返す（BMPフォーマット）
        res.set_content(reinterpret_cast<const char*>(image_data), image_size, "image/bmp");
        res.status = 200;

        // メモリを解放
        delete[] image_data;
      } else if (result == -1) {
        // No Imageの場合もバイナリデータが返されることがある
        if (image_data != nullptr && image_size > 0) {
          res.set_content(reinterpret_cast<const char*>(image_data), image_size, "image/bmp");
          res.status = 200;
          delete[] image_data;
        } else {
          res.status = 404;
          json error_response = {{"error", {{"message", "No image data available"}}}};
          res.set_content(error_response.dump(), "application/json; charset=utf-8");
        }
      } else {
        std::string error_message;
        switch (result) {
          case -201:
            error_message = "JVInit not called";
            res.status = 500;
            break;
          case -301:
            error_message = "Authentication error";
            res.status = 401;
            break;
          case -504:
            error_message = "Server under maintenance";
            res.status = 503;
            break;
          default:
            error_message = "Unknown error: " + std::to_string(result);
            res.status = 500;
        }

        json error_response = {{"error", {{"code", result}, {"message", error_message}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
      }

    } catch (const std::exception& e) {
      spdlog::error("Exception in handleUniformImage: {}", e.what());
      res.status = 500;
      json error_response = {{"error", {{"message", "Internal Server Error"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  }

  /**
   * コース図取得リクエストを処理する（説明文付き）
   *
   * JVCourseFileを使用してコース図と説明文を取得する。
   */
  void handleCourseFile(const httplib::Request& req, httplib::Response& res) {
    try {
      spdlog::info("Received /course/file request from {}", req.remote_addr);
      std::unique_lock<std::mutex> op_lock;
      if (!tryBeginOperation(op_lock, res, "course_file")) {
        return;
      }

      if (req.body.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Request body is empty"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      json request_json;
      try {
        request_json = json::parse(req.body);
      } catch (const json::parse_error&) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Invalid JSON format"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      std::string key = request_json.value("key", "");

      if (key.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Missing required parameter: key"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      spdlog::info("Retrieving course map - key: {}", key);

      // JVCourseFileを呼び出し
      std::string filepath;
      std::string explanation;
      long result = jvlink_wrapper_->courseFile(key, filepath, explanation);

      json response;
      if (result == 0) {
        response = {{"status", "success"},
                    {"message", "Course map retrieved successfully"},
                    {"key", key},
                    {"filepath", filepath},
                    {"explanation", explanation}};
        res.status = 200;
      } else if (result == -1) {
        response = {{"status", "error"},
                    {"error", {{"code", result}, {"message", "No data found for the specified key"}}},
                    {"key", key}};
        res.status = 404;
      } else {
        std::string error_message;
        switch (result) {
          case -114:
            error_message = "Invalid key parameter";
            res.status = 400;
            break;
          case -201:
            error_message = "JVInit not called";
            res.status = 500;
            break;
          case -301:
            error_message = "Authentication error";
            res.status = 401;
            break;
          case -504:
            error_message = "Server under maintenance";
            res.status = 503;
            break;
          default:
            error_message = "Unknown error: " + std::to_string(result);
            res.status = 500;
        }

        response = {{"status", "error"}, {"error", {{"code", result}, {"message", error_message}}}, {"key", key}};
      }

      res.set_content(response.dump(), "application/json; charset=utf-8");

    } catch (const std::exception& e) {
      spdlog::error("Exception in handleCourseFile: {}", e.what());
      res.status = 500;
      json error_response = {{"error", {{"message", "Internal Server Error"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  }

  /**
   * コース図取得リクエストを処理する（ファイル保存）
   *
   * JVCourseFile2を使用してコース図を指定パスに保存する。
   */
  void handleCourseFile2(const httplib::Request& req, httplib::Response& res) {
    try {
      spdlog::info("Received /course/file2 request from {}", req.remote_addr);
      std::unique_lock<std::mutex> op_lock;
      if (!tryBeginOperation(op_lock, res, "course_file2")) {
        return;
      }

      if (req.body.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Request body is empty"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      json request_json;
      try {
        request_json = json::parse(req.body);
      } catch (const json::parse_error&) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Invalid JSON format"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      std::string key = request_json.value("key", "");
      std::string filepath = request_json.value("filepath", "");

      if (key.empty() || filepath.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Missing required parameters: key, filepath"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      spdlog::info("Retrieving course map - key: {}, filepath: {}", key, filepath);

      // JVCourseFile2を呼び出し
      long result = jvlink_wrapper_->courseFile2(key, filepath);

      json response;
      if (result == 0) {
        response = {
            {"status", "success"}, {"message", "Course map saved successfully"}, {"key", key}, {"filepath", filepath}};
        res.status = 200;
      } else if (result == -1) {
        response = {{"status", "error"},
                    {"error", {{"code", result}, {"message", "No data found for the specified key"}}},
                    {"key", key}};
        res.status = 404;
      } else {
        std::string error_message;
        switch (result) {
          case -114:
            error_message = "Invalid key parameter";
            res.status = 400;
            break;
          case jvlink::error::JV_ERROR_PARAM_FILEPATH_INVALID:
            error_message = "Invalid filepath parameter";
            res.status = 400;
            break;
          case -201:
            error_message = "JVInit not called";
            res.status = 500;
            break;
          case -301:
            error_message = "Authentication error";
            res.status = 401;
            break;
          case -504:
            error_message = "Server under maintenance";
            res.status = 503;
            break;
          default:
            error_message = "Unknown error: " + std::to_string(result);
            res.status = 500;
        }

        response = {{"status", "error"}, {"error", {{"code", result}, {"message", error_message}}}, {"key", key}};
      }

      res.set_content(response.dump(), "application/json; charset=utf-8");

    } catch (const std::exception& e) {
      spdlog::error("Exception in handleCourseFile2: {}", e.what());
      res.status = 500;
      json error_response = {{"error", {{"message", "Internal Server Error"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  }

  /**
   * コース図画像取得リクエストを処理する（バイナリデータ返却）
   *
   * JVCourseFileを使用してコース図を取得し、画像データをバイナリで返す。
   */
  void handleCourseImage(const httplib::Request& req, httplib::Response& res) {
    try {
      spdlog::info("Received /course/image request from {}", req.remote_addr);
      std::unique_lock<std::mutex> op_lock;
      if (!tryBeginOperation(op_lock, res, "course_image")) {
        return;
      }

      if (req.body.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Request body is empty"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      json request_json;
      try {
        request_json = json::parse(req.body);
      } catch (const json::parse_error&) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Invalid JSON format"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      std::string key = request_json.value("key", "");

      if (key.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Missing required parameter: key"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      spdlog::info("Retrieving course map image - key: {}", key);

      // JVCourseFileを呼び出し
      std::string filepath;
      std::string explanation;
      long result = jvlink_wrapper_->courseFile(key, filepath, explanation);

      if (result == 0) {
        // ファイルを読み込んでバイナリデータとして返す
        std::ifstream file(filepath, std::ios::binary);
        if (!file) {
          res.status = 500;
          json error_response = {{"error", {{"message", "Failed to read course image file"}}}};
          res.set_content(error_response.dump(), "application/json; charset=utf-8");
          return;
        }

        std::vector<char> buffer((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        file.close();

        // 生ヘッダーは後方互換のため残し、UTF-8 安全な base64 版も併記する
        res.set_header("X-Course-Explanation", explanation);
        res.set_header("X-Course-Explanation-Base64", httplib::detail::base64_encode(explanation));
        res.set_content(buffer.data(), buffer.size(), "image/gif");
        res.status = 200;
      } else if (result == -1) {
        res.status = 404;
        json error_response = {{"error", {{"code", result}, {"message", "No data found for the specified key"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
      } else {
        std::string error_message;
        switch (result) {
          case -114:
            error_message = "Invalid key parameter";
            res.status = 400;
            break;
          case -201:
            error_message = "JVInit not called";
            res.status = 500;
            break;
          case -301:
            error_message = "Authentication error";
            res.status = 401;
            break;
          case -504:
            error_message = "Server under maintenance";
            res.status = 503;
            break;
          default:
            error_message = "Unknown error: " + std::to_string(result);
            res.status = 500;
        }

        json error_response = {{"error", {{"code", result}, {"message", error_message}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
      }

    } catch (const std::exception& e) {
      spdlog::error("Exception in handleCourseImage: {}", e.what());
      res.status = 500;
      json error_response = {{"error", {{"message", "Internal Server Error"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  }

  /**
   * リアルタイムデータ取得リクエストを処理する
   *
   * JVRTOpenを使用して指定されたキーのデータを取得し、
   * ストリーミング形式でクライアントに返す。
   */
  void handleRealtimeOpen(const httplib::Request& req, httplib::Response& res) {
    try {
      if (req.body.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Request body is empty"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      json json_body;
      try {
        json_body = json::parse(req.body);
      } catch (const json::parse_error&) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Invalid JSON format"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      if (!json_body.contains("dataspec") || !json_body["dataspec"].is_string()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "Missing required parameter: dataspec"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      std::string data_spec = json_body["dataspec"].get<std::string>();
      if (data_spec.empty()) {
        res.status = 400;
        json error_response = {{"error", {{"message", "dataspec must not be empty"}}}};
        res.set_content(error_response.dump(), "application/json; charset=utf-8");
        return;
      }

      std::string key;

      if (json_body.contains("key") && !json_body["key"].is_null()) {
        if (!json_body["key"].is_string()) {
          res.status = 400;
          json error_response = {{"error", {{"message", "key must be a string"}}}};
          res.set_content(error_response.dump(), "application/json; charset=utf-8");
          return;
        }
        key = json_body["key"].get<std::string>();
      } else {
        key = "";
      }

      spdlog::info("Realtime open stream request received. dataspec: {}, key: {}", data_spec, key);

      auto session_lock = std::make_shared<std::unique_lock<std::mutex>>(jvlink_operation_mutex_, std::try_to_lock);
      if (!session_lock->owns_lock()) {
        setBusyResponse(res, "query_realtime");
        return;
      }

      // Keep-Alive を明示
      res.set_header("Connection", "keep-alive");

      res.set_chunked_content_provider(
          "application/x-ndjson; charset=utf-8",
          [this, data_spec, key, session_lock](size_t offset, httplib::DataSink& sink) {
            (void)session_lock;
            if (offset == 0) {
              // カスタム例外クラス（クライアント切断用）
              class ClientDisconnectedException : public std::exception {
                const char* what() const noexcept override { return "Client disconnected during realtime streaming"; }
              };

              std::mutex sink_mutex;
              std::atomic<bool> streaming_active{true};

              auto safe_write = [&](const char* data, size_t len) {
                std::lock_guard<std::mutex> lock(sink_mutex);
                return sink.write(data, len);
              };

              auto meta_callback = [&](const JVQueryResult& meta_result) {
                json meta_json;
                if (meta_result.success) {
                  // 成功時もメタデータを送信してストリーミング開始を通知
                  meta_json["meta"] = json::object();
                } else {
                  meta_json["error"] = {{"message", meta_result.error_message}, {"code", meta_result.error_code}};
                }
                std::string meta_str = meta_json.dump();
                safe_write(meta_str.c_str(), meta_str.length());
                safe_write("\n", 1);
              };

              auto record_callback = [&](const std::string& record_str) {
                // クライアントの接続状態をチェック
                if (!sink.is_writable()) {
                  spdlog::warn("Client disconnected during realtime streaming for dataspec: {}", data_spec);
                  throw ClientDisconnectedException();
                }

                try {
                  auto parsed_record = RecordParser::parseRecord(record_str);
                  if (parsed_record) {
                    json record_json;
                    record_json["type"] = resolveRecordTypeForOutput(*parsed_record);
                    record_json["data"] = parsed_record->structured_data;
                    std::string record_json_str = record_json.dump();

                    bool write_success = safe_write(record_json_str.c_str(), record_json_str.length());
                    if (write_success) {
                      safe_write("\n", 1);
                    } else {
                      spdlog::warn("Failed to write realtime record to client for dataspec: {}", data_spec);
                      throw ClientDisconnectedException();
                    }
                  }
                } catch (const ClientDisconnectedException&) {
                  throw;  // 再スロー
                } catch (const std::exception& e) {
                  spdlog::error("Record parsing exception in realtime stream: {}", e.what());
                }
              };

              // ハートビート（空行）を定期送信してクライアントのread timeoutを跨ぐ
              int heartbeat_sec = 0;
              if (const char* hb = std::getenv("JVLINK_SERVER_STREAM_HEARTBEAT_SEC")) {
                int v = std::atoi(hb);
                if (v > 0) heartbeat_sec = v;
              }
              std::thread heartbeat_thread;
              if (heartbeat_sec > 0) {
                heartbeat_thread = std::thread([&]() {
                  spdlog::debug("Realtime streaming heartbeat started ({}s)", heartbeat_sec);
                  while (streaming_active.load()) {
                    for (int i = 0; i < heartbeat_sec && streaming_active.load(); ++i) {
                      std::this_thread::sleep_for(std::chrono::seconds(1));
                    }
                    if (!streaming_active.load()) break;
                    if (!sink.is_writable()) break;
                    if (!safe_write("\n", 1)) break;
                  }
                  spdlog::debug("Realtime streaming heartbeat stopped");
                });
              }

              try {
                jvlink_wrapper_->queryRealtime(data_spec, key, record_callback, meta_callback);
                streaming_active.store(false);
                if (heartbeat_thread.joinable()) heartbeat_thread.join();
              } catch (const ClientDisconnectedException&) {
                // クライアント切断は正常な終了として扱う
                spdlog::info(
                    "Realtime streaming terminated due to client disconnection for dataspec: {}. JVClose will be "
                    "called automatically by RAII guard.",
                    data_spec);
                streaming_active.store(false);
                if (heartbeat_thread.joinable()) heartbeat_thread.join();
              } catch (const JVStreamReadException& e) {
                spdlog::error("Streaming JV read error in /query/realtime: {} (code: {})", e.what(), e.errorCode());
                writeStreamErrorLine(
                    sink, sink_mutex, std::string("Streaming JV read error in /query/realtime: ") + e.what(),
                    e.errorCode());
                streaming_active.store(false);
                if (heartbeat_thread.joinable()) heartbeat_thread.join();
              } catch (const std::exception& e) {
                spdlog::error("Streaming error in /query/realtime: {}", e.what());
                writeStreamErrorLine(
                    sink, sink_mutex, std::string("Streaming error in /query/realtime: ") + e.what(), -500);
                streaming_active.store(false);
                if (heartbeat_thread.joinable()) heartbeat_thread.join();
              }
            }
            sink.done();
            return true;
          });

    } catch (const json::parse_error& e) {
      spdlog::error("JSON parse error in handleRealtimeOpen: {}", e.what());
      res.status = 400;
      json error_response = {{"error", {{"message", "Invalid JSON format"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    } catch (const std::exception& e) {
      spdlog::error("Exception in handleRealtimeOpen: {}", e.what());
      res.status = 500;
      json error_response = {{"error", {{"message", "Internal Server Error"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  }

  /**
   * JV-Linkイベントを処理する
   *
   * JV-Link COMコンポーネントからのイベント通知を受け取り、
   * イベントタイプを判定してキューに追加する。
   */
  void handleJvLinkEvent(DISPID dispId, const std::wstring& param) {
    try {
      if (param.empty()) {
        spdlog::info("Received JV-Link Event: DISPID={}, Param=''", dispId);
        return;
      }

      // Wide文字列 (UTF-16) をUTF-8文字列に変換
      int size_needed = WideCharToMultiByte(CP_UTF8, 0, &param[0], (int)param.size(), NULL, 0, NULL, NULL);
      std::string param_utf8(size_needed, 0);
      WideCharToMultiByte(CP_UTF8, 0, &param[0], (int)param.size(), &param_utf8[0], size_needed, NULL, NULL);

      spdlog::info("Received JV-Link Event: DISPID={}, Param='{}'", dispId, param_utf8);

      // DISPIDからイベントタイプを判定
      std::string event_type;

      // デバッグ用にDISPIDをログ出力
      spdlog::debug("Event DISPID: {} (0x{:X})", dispId, dispId);

      // JV-Linkイベントタイプのマッピング
      // JVDTLab.dll タイプライブラリ (_IJVLinkEvents) より
      switch (dispId) {
        case jvlink::dispid::JVEVT_PAY:
          event_type = "JVEvtPay";
          break;  // 出走取消・競走除外
        case jvlink::dispid::JVEVT_JOCKEY_CHANGE:
          event_type = "JVEvtJockeyChange";
          break;  // 騎手変更
        case jvlink::dispid::JVEVT_WEATHER:
          event_type = "JVEvtWeather";
          break;  // 天候・馬場状態変更
        case jvlink::dispid::JVEVT_COURSE_CHANGE:
          event_type = "JVEvtCourseChange";
          break;  // コース変更
        case jvlink::dispid::JVEVT_AVOID:
          event_type = "JVEvtAvoid";
          break;  // 騎手変更（落馬等）
        case jvlink::dispid::JVEVT_TIME_CHANGE:
          event_type = "JVEvtTimeChange";
          break;  // 発走時刻変更
        case jvlink::dispid::JVEVT_WEIGHT:
          event_type = "JVEvtWeight";
          break;  // 馬体重発表

        default:
          event_type = "Unknown";
          spdlog::warn("Unknown event DISPID: {} (0x{:X}), param: '{}'", dispId, dispId, param_utf8);
          break;
      }

      // イベントデータをキューに追加
      {
        std::lock_guard<std::mutex> lock(event_queue_mutex_);
        event_queue_.push(
            {event_type, param_utf8,
             std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch())
                 .count()});
        // キューサイズ上限を100件に制限
        while (event_queue_.size() > 100) {
          event_queue_.pop();
        }
      }
      event_cv_.notify_all();

      // イベントパラメータ形式の検証（デバッグ用）
      if (event_type == "JVEvtPay" || event_type == "JVEvtWeight") {
        // JVEvtPay/JVEvtWeight: YYYYMMDDJJRR形式（12文字）
        if (param_utf8.length() != 12) {
          spdlog::warn("{} parameter length mismatch: expected 12, got {}", event_type, param_utf8.length());
        }
      } else if (event_type != "Unknown") {
        // その他のイベント: TTYYYYMMDDJJRRNNNNNNNNNNNNNN形式（28文字）
        if (param_utf8.length() != 28) {
          spdlog::warn("{} parameter length mismatch: expected 28, got {}", event_type, param_utf8.length());
        }
      }
    } catch (const std::exception& e) {
      spdlog::error("Error converting event parameter: {}", e.what());
    }
  }

  void handleEventStart(const httplib::Request&, httplib::Response& res) {
    spdlog::info("Handling /event/start request...");
    std::unique_lock<std::mutex> op_lock;
    if (!tryBeginOperation(op_lock, res, "event_start")) {
      return;
    }
    json response;

    if (jvlink_wrapper_->startEventWatch()) {
      response = {{"status", "success"}, {"message", "Event watch started successfully."}};
      res.status = 200;
    } else {
      response = {{"status", "error"}, {"error_message", "Failed to start event watch."}};
      res.status = 500;
    }
    res.set_content(response.dump(), "application/json");
  }

  void handleEventStop(const httplib::Request&, httplib::Response& res) {
    spdlog::info("Handling /event/stop request...");
    std::unique_lock<std::mutex> op_lock;
    if (!tryBeginOperation(op_lock, res, "event_stop")) {
      return;
    }
    json response;

    if (jvlink_wrapper_->stopEventWatch()) {
      response = {{"status", "success"}, {"message", "Event watch stopped successfully."}};
      res.status = 200;
    } else {
      response = {{"status", "error"}, {"error_message", "Failed to stop event watch."}};
      res.status = 500;
    }
    res.set_content(response.dump(), "application/json");
  }

  /**
   * Server-Sent Eventsストリーミングを処理する
   *
   * クライアントに対してJV-Linkイベントをリアルタイムで
   * ストリーミング配信する。ハートビートも定期送信。
   */
  void handleEventStream(const httplib::Request&, httplib::Response& res) {
    spdlog::info("New SSE client connected for event streaming");

    // Server-Sent Events用のHTTPヘッダーを設定
    res.set_header("Content-Type", "text/event-stream");
    res.set_header("Cache-Control", "no-cache");
    res.set_header("Connection", "keep-alive");
    res.set_header("Access-Control-Allow-Origin", "*");

    // チャンク化されたストリーミングレスポンスを設定
    res.set_chunked_content_provider(
        "text/event-stream",
        [this](size_t /*offset*/, httplib::DataSink& sink) {
          // 接続成功メッセージを送信
          std::string init_msg = "event: connected\ndata: {\"message\": \"Connected to JVLink event stream\"}\n\n";
          if (!sink.write(init_msg.c_str(), init_msg.length())) {
            return false;
          }

          auto last_ping = std::chrono::steady_clock::now();

          // メインイベントループ
          while (running_) {
            std::unique_lock<std::mutex> lock(event_queue_mutex_);

            // 条件変数でイベントを待機（1秒タイムアウト）
            if (event_cv_.wait_for(lock, std::chrono::seconds(1),
                                   [this] { return !event_queue_.empty() || !running_; })) {
              // キュー内の全イベントを順次送信
              while (!event_queue_.empty()) {
                auto event = event_queue_.front();
                event_queue_.pop();

                json event_data = {{"type", event.type}, {"param", event.param}, {"timestamp", event.timestamp}};

                std::string message = "event: jvlink_event\n";
                message += "data: " + event_data.dump() + "\n\n";

                if (!sink.write(message.c_str(), message.length())) {
                  spdlog::info("SSE client disconnected");
                  return false;
                }
              }
            }

            // 定期的にハートビートを送信（30秒間隔）
            auto now = std::chrono::steady_clock::now();
            if (std::chrono::duration_cast<std::chrono::seconds>(now - last_ping).count() >= 30) {
              std::string ping = ":ping\n\n";
              if (!sink.write(ping.c_str(), ping.length())) {
                spdlog::info("SSE client disconnected (ping failed)");
                return false;
              }
              last_ping = now;
            }
          }

          return true;
        },
        [](bool /*success*/) {
          // クリーンアップコールバック（現在は未使用）
        });
  }
};

/**
 * サーバー設定を保持する構造体
 *
 * コマンドライン引数から取得した設定値を格納する。
 */
struct ServerConfig {
  int port = 8765;                 // HTTPサーバーのポート番号（Pythonクライアントのデフォルト）
  std::string sid = "UNKNOWN";     // JVInit時のSID
  std::string log_level = "info";  // ログ出力レベル
  bool help = false;
  bool version = false;
};

/**
 * コマンドライン引数を解析する
 *
 * 指定された引数を解析し、ServerConfig構造体に
 * 設定値を格納して返す。
 *
 * @param argc 引数の数
 * @param argv 引数配列
 * @return 解析結果を含むServerConfig構造体
 */
ServerConfig parseArguments(int argc, char* argv[]) {
  ServerConfig config;

  // 環境変数からデフォルト値を設定
  const char* env_port = std::getenv("JVLINK_SERVER_PORT");
  if (env_port != nullptr) {
    config.port = std::atoi(env_port);
  }

  const char* env_log_level = std::getenv("JVLINK_LOG_LEVEL");
  if (env_log_level != nullptr) {
    config.log_level = env_log_level;
  }

  const char* env_sid = std::getenv("JVLINK_SID");
  if (env_sid != nullptr) {
    config.sid = env_sid;
  }

  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];

    if (arg == "--help" || arg == "-h") {
      config.help = true;
    } else if (arg == "--version" || arg == "-v") {
      config.version = true;
    } else if (arg == "--port" || arg == "-p") {
      if (i + 1 < argc) {
        config.port = std::atoi(argv[++i]);
      }
    } else if (arg == "--log-level" || arg == "-l") {
      if (i + 1 < argc) {
        config.log_level = argv[++i];
      }
    } else if (arg == "--sid") {
      if (i + 1 < argc) {
        config.sid = argv[++i];
      }
    }
  }

  return config;
}

/**
 * プログラムの使用方法を表示する
 *
 * コマンドラインオプションの説明を標準出力に表示する。
 *
 * @param program_name プログラム名
 */
void printUsage(const char* program_name) {
  std::cout << "Usage: " << program_name << " [options]\n"
            << "Options:\n"
            << "  -p, --port <port>         Server port (default: 8765)\n"
            << "  -l, --log-level <level>   Log level: debug, info, warn, error (default: info)\n"
            << "      --sid <sid>           Software ID for JVInit (default: UNKNOWN)\n"
            << "  -h, --help                Show this help message\n"
            << "  -v, --version             Show version information\n"
            << std::endl;
}

/**
 * プログラムのバージョン情報を表示する
 *
 * バージョン番号とビルド情報を標準出力に表示する。
 */
void printVersion() {
  std::cout << "JVLinkServer v1.0\n"
            << "JV-Link HTTP Server for Python Client\n"
            << "Built with spdlog logging support\n"
            << std::endl;
}

/**
 * プログラムのエントリポイント
 *
 * コマンドライン引数を解析し、ログを初期化し、
 * HTTPサーバーを起動する。SIGINTシグナルの
 * ハンドリングも行う。
 *
 * @param argc コマンドライン引数の数
 * @param argv コマンドライン引数配列
 * @return 終了コード (0: 正常終了, 1: エラー)
 */
int main(int argc, char* argv[]) {
  // コマンドラインオプションを解析
  ServerConfig config = parseArguments(argc, argv);

  // --helpオプションの処理
  if (config.help) {
    printUsage(argv[0]);
    return 0;
  }

  // --versionオプションの処理
  if (config.version) {
    printVersion();
    return 0;
  }

  // ログシステムを初期化
  initializeLogging(config.log_level);

  std::unique_ptr<JVLinkHTTPServer> server;

  // シグナルハンドラーからアクセスできるようグローバルポインタを保持
  static std::unique_ptr<JVLinkHTTPServer>* global_server_ptr = nullptr;

  try {
    // SIGINT (Ctrl+C) シグナルハンドラーを設定
    std::signal(SIGINT, [](int) {
      spdlog::warn("SIGINT received, shutting down gracefully...");

      // サーバーインスタンスが存在すれば停止
      if (global_server_ptr && *global_server_ptr) {
        (*global_server_ptr)->stop();
      }

      // 終了前にログをフラッシュ
      spdlog::info("Flushing logs before exit...");
      spdlog::shutdown();

      exit(0);
    });

    // JVLinkHTTPサーバーインスタンスを作成
    server = std::make_unique<JVLinkHTTPServer>(config.port, config.sid);
    global_server_ptr = &server;  // シグナルハンドラー用に参照を保存

    if (!server->start(true)) {
      spdlog::error("Failed to start server on port {}", config.port);
      // エラー時のログフラッシュ
      spdlog::shutdown();
      return 1;
    }

  } catch (const std::exception& e) {
    spdlog::error("Server exception: {}", e.what());
    // ログフラッシュ
    spdlog::shutdown();
    return 1;
  } catch (...) {
    spdlog::error("Unknown server exception occurred");
    // ログフラッシュ
    spdlog::shutdown();
    return 1;
  }

  spdlog::warn("Server shutdown completed");

  // プログラム終了前の最終ログフラッシュ
  spdlog::info("Final log flush before program termination");
  spdlog::shutdown();

  return 0;
}
