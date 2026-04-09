#include "server/supervisor_http_server.h"

#include <httplib.h>
#include <windows.h>

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <memory>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "json.hpp"
#include "server/api_version.h"
#include "server/openapi_handler.h"
#include "spdlog/spdlog.h"

using json = nlohmann::json;

namespace {

constexpr const char* kBusyHeaderName = "X-JVLink-Busy";
constexpr const char* kBusyOperationHeaderName = "X-JVLink-Operation";
constexpr const char* kRequestIdHeaderName = "X-Request-Id";
constexpr const char* kRetryAfterHeaderName = "Retry-After";
constexpr const char* kUnavailableHeaderName = "X-JVLink-Unavailable";
constexpr int kBusyRetryAfterSec = 1;
constexpr int kDefaultSocketTimeoutSec = 65;
constexpr int kDefaultWorkerStartupTimeoutSec = 30;
constexpr int kDefaultInternalConnectTimeoutSec = 1;
constexpr int kDefaultInternalReadTimeoutSec = 70;
constexpr int kDefaultInternalWriteTimeoutSec = 70;

int64_t currentUnixTimestampSec() {
  return std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count();
}

int getPositiveEnvInt(const char* name, int def) {
  char* value = nullptr;
  size_t len = 0;
  if (_dupenv_s(&value, &len, name) != 0 || value == nullptr) {
    return def;
  }

  const int parsed = std::atoi(value);
  free(value);
  return parsed > 0 ? parsed : def;
}

std::string getExecutablePath() {
  char exe_path[MAX_PATH];
  DWORD len = GetModuleFileNameA(nullptr, exe_path, MAX_PATH);
  if (len == 0 || len >= MAX_PATH) {
    throw std::runtime_error("Failed to resolve current executable path");
  }
  return std::string(exe_path, len);
}

std::string quoteCommandArg(const std::string& value) {
  std::string escaped = "\"";
  for (char ch : value) {
    if (ch == '"') {
      escaped += "\\\"";
    } else {
      escaped += ch;
    }
  }
  escaped += "\"";
  return escaped;
}

bool shouldSkipRequestHeader(const std::string& header_name) {
  return _stricmp(header_name.c_str(), "Host") == 0 || _stricmp(header_name.c_str(), "Connection") == 0 ||
         _stricmp(header_name.c_str(), "Keep-Alive") == 0 || _stricmp(header_name.c_str(), "Transfer-Encoding") == 0 ||
         _stricmp(header_name.c_str(), "Content-Length") == 0;
}

bool shouldSkipResponseHeader(const std::string& header_name) {
  return _stricmp(header_name.c_str(), "Connection") == 0 || _stricmp(header_name.c_str(), "Keep-Alive") == 0 ||
         _stricmp(header_name.c_str(), "Transfer-Encoding") == 0 || _stricmp(header_name.c_str(), "Content-Length") == 0;
}

int allocateLoopbackPort() {
  SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
  if (sock == INVALID_SOCKET) {
    throw std::runtime_error("Failed to create socket for internal worker port allocation");
  }

  sockaddr_in addr = {};
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
  addr.sin_port = 0;

  if (bind(sock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == SOCKET_ERROR) {
    closesocket(sock);
    throw std::runtime_error("Failed to bind loopback socket for internal worker port allocation");
  }

  int addr_len = sizeof(addr);
  if (getsockname(sock, reinterpret_cast<sockaddr*>(&addr), &addr_len) == SOCKET_ERROR) {
    closesocket(sock);
    throw std::runtime_error("Failed to resolve allocated loopback port");
  }

  const int port = static_cast<int>(ntohs(addr.sin_port));
  closesocket(sock);
  if (port <= 0) {
    throw std::runtime_error("Allocated internal worker port was invalid");
  }
  return port;
}

void applyRequestHeaders(const httplib::Request& req, httplib::Request& upstream_req) {
  upstream_req.method = req.method;
  upstream_req.path = req.path;
  upstream_req.body = req.body;
  for (const auto& header : req.headers) {
    if (shouldSkipRequestHeader(header.first)) {
      continue;
    }
    upstream_req.headers.emplace(header.first, header.second);
  }
}

void applyResponseHeaders(const httplib::Response& upstream_res, httplib::Response& res) {
  res.status = upstream_res.status;
  for (const auto& header : upstream_res.headers) {
    if (shouldSkipResponseHeader(header.first)) {
      continue;
    }
    res.headers.emplace(header.first, header.second);
  }
}

void setUnavailableResponse(httplib::Response& res, const std::string& operation, const std::string& message) {
  res.status = 503;
  res.set_header(kUnavailableHeaderName, "1");
  res.set_header(kBusyOperationHeaderName, operation);
  res.set_header(kRetryAfterHeaderName, std::to_string(kBusyRetryAfterSec));
  json error_response = {
      {"error", {{"code", -50301}, {"message", message}}},
      {"operation", operation},
  };
  res.set_content(error_response.dump(), "application/json; charset=utf-8");
}

struct WorkerProbeResult {
  bool reachable = false;
  bool healthy = false;
  int http_status = 0;
  json payload = json::object();
  std::string status = "unreachable";
  std::string fault_message;
};

struct WorkerRuntimeSnapshot {
  bool process_running = false;
  int worker_port = 0;
  uint64_t generation = 0;
  uint64_t restart_count = 0;
  int64_t last_restart_timestamp = 0;
  std::string last_restart_reason;
  DWORD last_exit_code = STILL_ACTIVE;
  WorkerProbeResult probe;
};

struct StreamingProxyState {
  std::mutex mutex;
  std::condition_variable cv;
  std::deque<std::string> chunks;
  bool headers_ready = false;
  bool finished = false;
  bool downstream_canceled = false;
  bool transport_failed = false;
  int upstream_status = 0;
  httplib::Headers upstream_headers;
  std::string content_type = "application/octet-stream";
  httplib::Error transport_error = httplib::Error::Unknown;
  bool should_restart = false;
  std::string restart_reason;
  std::thread worker_thread;
};

class WorkerProcessManager {
 public:
  WorkerProcessManager(std::string sid, std::string log_level)
      : sid_(std::move(sid)),
        log_level_(std::move(log_level)),
        executable_path_(getExecutablePath()),
        startup_timeout_sec_(getPositiveEnvInt("JVLINK_WORKER_STARTUP_TIMEOUT_SEC", kDefaultWorkerStartupTimeoutSec)),
        internal_connect_timeout_sec_(
            getPositiveEnvInt("JVLINK_INTERNAL_CONNECT_TIMEOUT_SEC", kDefaultInternalConnectTimeoutSec)),
        internal_read_timeout_sec_(getPositiveEnvInt("JVLINK_INTERNAL_READ_TIMEOUT_SEC", kDefaultInternalReadTimeoutSec)),
        internal_write_timeout_sec_(
            getPositiveEnvInt("JVLINK_INTERNAL_WRITE_TIMEOUT_SEC", kDefaultInternalWriteTimeoutSec)) {}

  ~WorkerProcessManager() { stop(); }

  WorkerProcessManager(const WorkerProcessManager&) = delete;
  WorkerProcessManager& operator=(const WorkerProcessManager&) = delete;

  bool ensureWorkerReady() {
    std::lock_guard<std::mutex> lock(mutex_);
    return ensureWorkerReadyLocked("ensure-ready");
  }

  void stop() {
    std::lock_guard<std::mutex> lock(mutex_);
    stopWorkerLocked("supervisor stop");
  }

  void restart(const std::string& reason) {
    std::lock_guard<std::mutex> lock(mutex_);
    restartWorkerLocked(reason);
  }

  void restartIfWorkerUnhealthy(const std::string& reason) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!hasLiveProcessLocked()) {
      restartWorkerLocked(reason + ": process not running");
      return;
    }

    WorkerProbeResult probe = probeWorkerLocked();
    last_probe_ = probe;
    if (!probe.healthy) {
      restartWorkerLocked(reason + ": " + deriveProbeSummary(probe));
    }
  }

  WorkerRuntimeSnapshot snapshot() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (has_process_) {
      (void)hasExitedLocked();
    }

    WorkerRuntimeSnapshot snapshot;
    snapshot.process_running = has_process_;
    snapshot.worker_port = worker_port_;
    snapshot.generation = generation_;
    snapshot.restart_count = restart_count_;
    snapshot.last_restart_timestamp = last_restart_timestamp_;
    snapshot.last_restart_reason = last_restart_reason_;
    snapshot.last_exit_code = last_exit_code_;
    snapshot.probe = has_process_ ? probeWorkerLocked() : WorkerProbeResult{};
    last_probe_ = snapshot.probe;
    return snapshot;
  }

  int workerPort() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return worker_port_;
  }

 private:
  std::unique_ptr<httplib::Client> createWorkerClientLocked() const {
    auto client = std::make_unique<httplib::Client>("127.0.0.1", worker_port_);
    client->set_keep_alive(false);
    client->set_tcp_nodelay(true);
    client->set_connection_timeout(internal_connect_timeout_sec_, 0);
    client->set_read_timeout(internal_read_timeout_sec_, 0);
    client->set_write_timeout(internal_write_timeout_sec_, 0);
    return client;
  }

  bool ensureWorkerReadyLocked(const std::string& reason) {
    if (!hasLiveProcessLocked()) {
      return startWorkerLocked(reason + ": process not running");
    }

    WorkerProbeResult probe = probeWorkerLocked();
    last_probe_ = probe;
    if (probe.healthy) {
      return true;
    }

    return restartWorkerLocked(reason + ": " + deriveProbeSummary(probe));
  }

  bool startWorkerLocked(const std::string& reason) {
    if (has_process_) {
      return true;
    }

    worker_port_ = allocateLoopbackPort();
    std::string command_line = quoteCommandArg(executable_path_) + " --mode worker --port " +
                               std::to_string(worker_port_) + " --log-level " + quoteCommandArg(log_level_) +
                               " --sid " + quoteCommandArg(sid_);

    STARTUPINFOA startup_info = {};
    startup_info.cb = sizeof(startup_info);
    PROCESS_INFORMATION process_info = {};
    std::vector<char> mutable_command(command_line.begin(), command_line.end());
    mutable_command.push_back('\0');

    BOOL created = CreateProcessA(nullptr, mutable_command.data(), nullptr, nullptr, FALSE, CREATE_NO_WINDOW, nullptr,
                                  nullptr, &startup_info, &process_info);
    if (!created) {
      last_restart_reason_ = reason + ": CreateProcess failed";
      last_restart_timestamp_ = currentUnixTimestampSec();
      last_exit_code_ = GetLastError();
      worker_port_ = 0;
      spdlog::error("Failed to launch JV-Link worker process: GetLastError={}", last_exit_code_);
      return false;
    }

    process_info_ = process_info;
    has_process_ = true;
    generation_++;
    restart_count_++;
    last_restart_reason_ = reason;
    last_restart_timestamp_ = currentUnixTimestampSec();
    last_exit_code_ = STILL_ACTIVE;
    spdlog::info("Started JV-Link worker process on internal port {} (generation={}, reason={})", worker_port_,
                 generation_, reason);

    WorkerProbeResult probe = waitForHealthyWorkerLocked();
    last_probe_ = probe;
    if (!probe.healthy) {
      spdlog::error("JV-Link worker failed to become healthy on internal port {}: {}", worker_port_,
                    deriveProbeSummary(probe));
      stopWorkerLocked("worker startup failed");
      return false;
    }

    return true;
  }

  bool restartWorkerLocked(const std::string& reason) {
    stopWorkerLocked(reason);
    return startWorkerLocked(reason);
  }

  void stopWorkerLocked(const std::string& reason) {
    if (!has_process_) {
      return;
    }

    spdlog::warn("Stopping JV-Link worker process (reason={})", reason);
    try {
      auto client = createWorkerClientLocked();
      (void)client->Post("/shutdown");
    } catch (...) {
    }

    DWORD wait_result = WaitForSingleObject(process_info_.hProcess, 3000);
    if (wait_result == WAIT_TIMEOUT) {
      TerminateProcess(process_info_.hProcess, 1);
      WaitForSingleObject(process_info_.hProcess, 2000);
    }

    GetExitCodeProcess(process_info_.hProcess, &last_exit_code_);
    closeProcessHandlesLocked();
    has_process_ = false;
    worker_port_ = 0;
  }

  bool hasLiveProcessLocked() {
    if (!has_process_) {
      return false;
    }
    return !hasExitedLocked();
  }

  bool hasExitedLocked() {
    if (!has_process_) {
      return true;
    }

    DWORD wait_result = WaitForSingleObject(process_info_.hProcess, 0);
    if (wait_result != WAIT_OBJECT_0) {
      return false;
    }

    GetExitCodeProcess(process_info_.hProcess, &last_exit_code_);
    closeProcessHandlesLocked();
    has_process_ = false;
    worker_port_ = 0;
    return true;
  }

  void closeProcessHandlesLocked() {
    if (process_info_.hThread) {
      CloseHandle(process_info_.hThread);
      process_info_.hThread = nullptr;
    }
    if (process_info_.hProcess) {
      CloseHandle(process_info_.hProcess);
      process_info_.hProcess = nullptr;
    }
  }

  WorkerProbeResult waitForHealthyWorkerLocked() {
    WorkerProbeResult last_probe;
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(startup_timeout_sec_);
    while (std::chrono::steady_clock::now() < deadline) {
      if (!hasLiveProcessLocked()) {
        last_probe.status = "exited";
        return last_probe;
      }

      last_probe = probeWorkerLocked();
      if (last_probe.healthy) {
        return last_probe;
      }

      std::this_thread::sleep_for(std::chrono::milliseconds(250));
    }

    if (last_probe.status == "unreachable") {
      last_probe.status = "startup_timeout";
    }
    return last_probe;
  }

  WorkerProbeResult probeWorkerLocked() const {
    WorkerProbeResult probe;
    if (!has_process_ || worker_port_ <= 0) {
      return probe;
    }

    auto client = createWorkerClientLocked();
    auto result = client->Get("/health");
    if (!result) {
      return probe;
    }

    probe.reachable = true;
    probe.http_status = result->status;
    probe.status = result->status == 200 ? "healthy" : "unhealthy";

    json payload = json::parse(result->body, nullptr, false);
    if (!payload.is_discarded() && payload.is_object()) {
      probe.payload = std::move(payload);
      if (probe.payload.contains("status") && probe.payload["status"].is_string()) {
        probe.status = probe.payload["status"].get<std::string>();
      }

      auto components_it = probe.payload.find("components");
      if (components_it != probe.payload.end() && components_it->is_object()) {
        auto jvlink_it = components_it->find("jvlink");
        if (jvlink_it != components_it->end() && jvlink_it->is_object()) {
          auto fault_it = jvlink_it->find("last_fault_message");
          if (fault_it != jvlink_it->end() && fault_it->is_string()) {
            probe.fault_message = fault_it->get<std::string>();
          }
        }
      }
    }

    probe.healthy = result->status == 200 && probe.status == "healthy";
    return probe;
  }

  std::string deriveProbeSummary(const WorkerProbeResult& probe) const {
    if (!probe.reachable) {
      return "worker unreachable";
    }
    if (!probe.fault_message.empty()) {
      return probe.status + ": " + probe.fault_message;
    }
    std::ostringstream oss;
    oss << probe.status << " (status=" << probe.http_status << ")";
    return oss.str();
  }

  mutable std::mutex mutex_;
  PROCESS_INFORMATION process_info_ = {};
  bool has_process_ = false;
  int worker_port_ = 0;
  uint64_t generation_ = 0;
  uint64_t restart_count_ = 0;
  int64_t last_restart_timestamp_ = 0;
  std::string last_restart_reason_;
  DWORD last_exit_code_ = STILL_ACTIVE;
  WorkerProbeResult last_probe_;
  std::string sid_;
  std::string log_level_;
  std::string executable_path_;
  int startup_timeout_sec_ = kDefaultWorkerStartupTimeoutSec;
  int internal_connect_timeout_sec_ = kDefaultInternalConnectTimeoutSec;
  int internal_read_timeout_sec_ = kDefaultInternalReadTimeoutSec;
  int internal_write_timeout_sec_ = kDefaultInternalWriteTimeoutSec;
};

}  // namespace

class SupervisorHTTPServer::Impl {
 public:
  Impl(int port, std::string sid, std::string log_level);
  ~Impl();

  bool start(bool blocking);
  void stop();
  bool isRunning() const;

 private:
  void setupRoutes();
  void setupErrorHandlers();
  std::unique_ptr<httplib::Client> createWorkerClient() const;
  void handleHealth(const httplib::Request& req, httplib::Response& res);
  void handleSessionReset(const httplib::Request& req, httplib::Response& res);
  void handleVersion(const httplib::Request& req, httplib::Response& res);
  void handleShutdown(const httplib::Request& req, httplib::Response& res);
  void proxyStandardRequest(const httplib::Request& req, httplib::Response& res);
  void proxyStreamingRequest(const httplib::Request& req, httplib::Response& res);

  int port_;
  std::string sid_;
  std::string log_level_;
  WorkerProcessManager worker_manager_;
  std::unique_ptr<httplib::Server> server_;
  std::unique_ptr<jvlink::OpenAPIHandler> openapi_handler_;
  bool running_ = false;
  std::thread server_thread_;
};

SupervisorHTTPServer::SupervisorHTTPServer(int port, std::string sid, std::string log_level)
    : impl_(new Impl(port, std::move(sid), std::move(log_level))) {}

SupervisorHTTPServer::~SupervisorHTTPServer() { delete impl_; }

bool SupervisorHTTPServer::start(bool blocking) { return impl_->start(blocking); }

void SupervisorHTTPServer::stop() { impl_->stop(); }

bool SupervisorHTTPServer::isRunning() const { return impl_->isRunning(); }

SupervisorHTTPServer::Impl::Impl(int port, std::string sid, std::string log_level)
    : port_(port),
      sid_(std::move(sid)),
      log_level_(std::move(log_level)),
      worker_manager_(sid_, log_level_),
      server_(std::make_unique<httplib::Server>()),
      openapi_handler_(std::make_unique<jvlink::OpenAPIHandler>("127.0.0.1", port_)) {
  server_->set_tcp_nodelay(true);
  setupRoutes();
  setupErrorHandlers();
}

SupervisorHTTPServer::Impl::~Impl() { stop(); }

bool SupervisorHTTPServer::Impl::start(bool blocking) {
  if (running_) {
    spdlog::warn("Supervisor server is already running on port {}", port_);
    return false;
  }

  if (!worker_manager_.ensureWorkerReady()) {
    spdlog::error("Failed to start healthy JV-Link worker before exposing public server");
    return false;
  }

  running_ = true;
  spdlog::warn("JVLinkServer supervisor started on port {}", port_);

  if (blocking) {
    return server_->listen("0.0.0.0", port_);
  }

  server_thread_ = std::thread([this]() { server_->listen("0.0.0.0", port_); });
  return true;
}

void SupervisorHTTPServer::Impl::stop() {
  if (!running_) {
    worker_manager_.stop();
    return;
  }

  spdlog::info("Stopping supervisor HTTP server...");
  running_ = false;

  if (server_) {
    server_->stop();
  }

  if (server_thread_.joinable()) {
    server_thread_.join();
  }

  worker_manager_.stop();
  spdlog::info("Supervisor HTTP server stop completed");
}

bool SupervisorHTTPServer::Impl::isRunning() const { return running_; }

void SupervisorHTTPServer::Impl::setupRoutes() {
  int read_to_sec = getPositiveEnvInt("JVLINK_SERVER_READ_TIMEOUT", kDefaultSocketTimeoutSec);
  int write_to_sec = getPositiveEnvInt("JVLINK_SERVER_WRITE_TIMEOUT", kDefaultSocketTimeoutSec);
  server_->set_read_timeout(read_to_sec, 0);
  server_->set_write_timeout(write_to_sec, 0);

  server_->set_pre_routing_handler([](const httplib::Request&, httplib::Response& res) {
    res.set_header("Access-Control-Allow-Origin", "*");
    res.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.set_header("Access-Control-Allow-Headers", "Content-Type");
    return httplib::Server::HandlerResponse::Unhandled;
  });

  server_->Options(".*", [](const httplib::Request&, httplib::Response& res) { res.set_content("", "text/plain"); });

  server_->Get("/health", [this](const httplib::Request& req, httplib::Response& res) { handleHealth(req, res); });
  server_->Get("/session",
               [this](const httplib::Request& req, httplib::Response& res) { proxyStandardRequest(req, res); });
  server_->Get("/v1/session",
               [this](const httplib::Request& req, httplib::Response& res) { proxyStandardRequest(req, res); });
  server_->Post("/session/reset",
                [this](const httplib::Request& req, httplib::Response& res) { handleSessionReset(req, res); });
  server_->Post("/v1/session/reset",
                [this](const httplib::Request& req, httplib::Response& res) { handleSessionReset(req, res); });
  server_->Get("/version", [this](const httplib::Request& req, httplib::Response& res) { handleVersion(req, res); });
  server_->Get("/openapi.json",
               [this](const httplib::Request& req, httplib::Response& res) { openapi_handler_->handleOpenAPIRequest(req, res); });
  server_->Post("/shutdown", [this](const httplib::Request& req, httplib::Response& res) { handleShutdown(req, res); });
  server_->Post("/v1/shutdown",
                [this](const httplib::Request& req, httplib::Response& res) { handleShutdown(req, res); });

  server_->Post("/query/stored",
                [this](const httplib::Request& req, httplib::Response& res) { proxyStreamingRequest(req, res); });
  server_->Post("/v1/query/stored",
                [this](const httplib::Request& req, httplib::Response& res) { proxyStreamingRequest(req, res); });
  server_->Post("/query/realtime",
                [this](const httplib::Request& req, httplib::Response& res) { proxyStreamingRequest(req, res); });
  server_->Post("/v1/query/realtime",
                [this](const httplib::Request& req, httplib::Response& res) { proxyStreamingRequest(req, res); });
  server_->Get("/events/stream",
               [this](const httplib::Request& req, httplib::Response& res) { proxyStreamingRequest(req, res); });
  server_->Get("/v1/events/stream",
               [this](const httplib::Request& req, httplib::Response& res) { proxyStreamingRequest(req, res); });

  const std::vector<std::string> proxied_posts = {
      "/event/start",      "/v1/event/start",   "/event/stop",      "/v1/event/stop", "/files/delete",
      "/v1/files/delete",  "/uniform/file",     "/v1/uniform/file", "/uniform/image", "/v1/uniform/image",
      "/course/file",      "/v1/course/file",   "/course/file2",    "/v1/course/file2", "/course/image",
      "/v1/course/image",
  };

  for (const auto& path : proxied_posts) {
    server_->Post(path, [this](const httplib::Request& req, httplib::Response& res) { proxyStandardRequest(req, res); });
  }
}

void SupervisorHTTPServer::Impl::setupErrorHandlers() {
  server_->set_error_handler([](const httplib::Request& req, httplib::Response& res) {
    if (res.status == 503 && res.get_header_value(kBusyHeaderName) == "1") {
      return;
    }

    spdlog::error("HTTP Error: {} for {} from {}", res.status, req.path, req.remote_addr);
    if (!res.body.empty()) {
      return;
    }

    std::string error_message = "Request failed";
    if (res.status == 404) {
      error_message = "Not found";
    } else if (res.status >= 500) {
      error_message = "Internal Server Error";
    }

    json error_response = {{"error", {{"message", error_message}}}};
    res.set_content(error_response.dump(), "application/json; charset=utf-8");
  });

  server_->set_exception_handler([](const httplib::Request& req, httplib::Response& res, std::exception_ptr ep) {
    try {
      std::rethrow_exception(ep);
    } catch (const std::exception& e) {
      spdlog::error("Exception in request to {}: {}", req.path, e.what());
      res.status = 500;
      json error_response = {{"error", {{"message", "Internal Server Error"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    } catch (...) {
      spdlog::error("Unknown exception in request to {}", req.path);
      res.status = 500;
      json error_response = {{"error", {{"message", "Internal Server Error"}}}};
      res.set_content(error_response.dump(), "application/json; charset=utf-8");
    }
  });
}

std::unique_ptr<httplib::Client> SupervisorHTTPServer::Impl::createWorkerClient() const {
  const int worker_port = worker_manager_.workerPort();
  auto client = std::make_unique<httplib::Client>("127.0.0.1", worker_port);
  client->set_keep_alive(false);
  client->set_tcp_nodelay(true);
  client->set_connection_timeout(kDefaultInternalConnectTimeoutSec, 0);
  client->set_read_timeout(kDefaultInternalReadTimeoutSec, 0);
  client->set_write_timeout(kDefaultInternalWriteTimeoutSec, 0);
  return client;
}

void SupervisorHTTPServer::Impl::handleHealth(const httplib::Request& req, httplib::Response& res) {
  try {
    spdlog::debug("Supervisor health check requested from {}", req.remote_addr);
    WorkerRuntimeSnapshot worker = worker_manager_.snapshot();
    const bool healthy = worker.probe.healthy;

    json jvlink_component = {
        {"status", worker.probe.status},
        {"operational", worker.probe.healthy},
        {"faulted", false},
        {"last_fault_message", worker.probe.fault_message.empty() ? json(nullptr) : json(worker.probe.fault_message)},
    };
    if (worker.probe.payload.contains("components") && worker.probe.payload["components"].is_object() &&
        worker.probe.payload["components"].contains("jvlink")) {
      jvlink_component = worker.probe.payload["components"]["jvlink"];
    }

    json response;
    response["status"] = healthy ? "healthy" : "unhealthy";
    response["timestamp"] = currentUnixTimestampSec();
    response["service"] = {
        {"name", "JVLinkServer"},
        {"mode", "supervisor"},
        {"version", jvlink::server::getApiVersion()},
        {"uptime",
         std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now().time_since_epoch()).count()},
    };
    response["components"] = {
        {"http_server", {{"status", "healthy"}, {"port", port_}}},
        {"worker_process",
         {{"status", worker.process_running ? "running" : "stopped"},
          {"port", worker.worker_port > 0 ? json(worker.worker_port) : json(nullptr)},
          {"generation", worker.generation},
          {"restart_count", worker.restart_count},
          {"last_restart_reason", worker.last_restart_reason.empty() ? json(nullptr) : json(worker.last_restart_reason)},
          {"last_restart_timestamp", worker.last_restart_timestamp > 0 ? json(worker.last_restart_timestamp)
                                                                      : json(nullptr)},
          {"last_exit_code", worker.last_exit_code == STILL_ACTIVE ? json(nullptr) : json(worker.last_exit_code)}}},
        {"jvlink", std::move(jvlink_component)},
    };
    if (worker.probe.payload.contains("session") && worker.probe.payload["session"].is_object()) {
      response["session"] = worker.probe.payload["session"];
    }
    response["metrics"] = {
        {"worker_restarts", worker.restart_count},
        {"worker_generation", worker.generation},
        {"worker_http_status", worker.probe.reachable ? json(worker.probe.http_status) : json(nullptr)},
    };

    if (!healthy) {
      res.status = 503;
    }
    res.set_content(response.dump(), "application/json; charset=utf-8");
  } catch (const std::exception& e) {
    spdlog::error("Error in supervisor health check: {}", e.what());
    res.status = 503;
    json error_response = {{"status", "unhealthy"}, {"error", e.what()}};
    res.set_content(error_response.dump(), "application/json; charset=utf-8");
  }
}

void SupervisorHTTPServer::Impl::handleSessionReset(const httplib::Request& req, httplib::Response& res) {
  const std::string request_id = req.get_header_value(kRequestIdHeaderName);
  if (!request_id.empty()) {
    res.set_header(kRequestIdHeaderName, request_id);
  }

  WorkerRuntimeSnapshot before = worker_manager_.snapshot();
  bool worker_busy = false;
  if (before.probe.payload.contains("session") && before.probe.payload["session"].is_object()) {
    worker_busy = before.probe.payload["session"].value("busy", false);
  }

  if (!before.process_running || !before.probe.healthy || worker_busy) {
    const std::string reason = worker_busy ? "admin session reset while busy" : "admin session reset";
    worker_manager_.restart(reason);
  }

  WorkerRuntimeSnapshot after = worker_manager_.snapshot();
  if (!after.process_running || !after.probe.healthy) {
    setUnavailableResponse(res, "/session/reset", "JV-Link worker is unavailable after reset");
    return;
  }

  json response = {
      {"status", "success"},
      {"action", worker_busy || !before.probe.healthy || !before.process_running ? "worker_restarted" : "noop"},
      {"message", worker_busy ? "Worker restarted to release the stuck session." : "No active session to reset."},
  };
  if (after.probe.payload.contains("session") && after.probe.payload["session"].is_object()) {
    response["session"] = after.probe.payload["session"];
  }
  res.set_content(response.dump(), "application/json; charset=utf-8");
}

void SupervisorHTTPServer::Impl::handleVersion(const httplib::Request& req, httplib::Response& res) {
  spdlog::debug("Supervisor version info requested from {}", req.remote_addr);
  json response = {{"version", jvlink::server::getApiVersion()}, {"mode", "supervisor"}};
  res.set_content(response.dump(), "application/json; charset=utf-8");
}

void SupervisorHTTPServer::Impl::handleShutdown(const httplib::Request& req, httplib::Response& res) {
  spdlog::info("Supervisor shutdown request from {}", req.remote_addr);
  json response = {{"status", "ok"}, {"message", "Server is shutting down"}};
  res.set_content(response.dump(), "application/json; charset=utf-8");

  std::thread([this]() {
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    stop();
  }).detach();
}

void SupervisorHTTPServer::Impl::proxyStandardRequest(const httplib::Request& req, httplib::Response& res) {
  const std::string operation = req.path;
  if (!worker_manager_.ensureWorkerReady()) {
    setUnavailableResponse(res, operation, "JV-Link worker is unavailable");
    return;
  }

  httplib::Request upstream_req;
  applyRequestHeaders(req, upstream_req);
  auto client = createWorkerClient();
  auto result = client->send(upstream_req);
  if (!result) {
    worker_manager_.restart("upstream transport failure for " + operation);
    setUnavailableResponse(res, operation, "JV-Link worker transport failed");
    return;
  }

  applyResponseHeaders(*result, res);
  res.body = result->body;

  if (result->status == 503 && result->get_header_value(kUnavailableHeaderName) == "1") {
    worker_manager_.restart("worker reported unavailable for " + operation);
  }
}

void SupervisorHTTPServer::Impl::proxyStreamingRequest(const httplib::Request& req, httplib::Response& res) {
  const std::string operation = req.path;
  if (!worker_manager_.ensureWorkerReady()) {
    setUnavailableResponse(res, operation, "JV-Link worker is unavailable");
    return;
  }

  auto state = std::make_shared<StreamingProxyState>();
  const int worker_port = worker_manager_.workerPort();
  httplib::Request req_copy = req;
  state->worker_thread = std::thread([state, req_copy, worker_port, operation]() {
    httplib::Client client("127.0.0.1", worker_port);
    client.set_keep_alive(false);
    client.set_tcp_nodelay(true);
    client.set_connection_timeout(kDefaultInternalConnectTimeoutSec, 0);
    client.set_read_timeout(kDefaultInternalReadTimeoutSec, 0);
    client.set_write_timeout(kDefaultInternalWriteTimeoutSec, 0);

    httplib::Request upstream_req;
    applyRequestHeaders(req_copy, upstream_req);
    upstream_req.response_handler = [state, operation](const httplib::Response& upstream_res) {
      std::lock_guard<std::mutex> lock(state->mutex);
      state->upstream_status = upstream_res.status;
      state->upstream_headers = upstream_res.headers;
      state->content_type = upstream_res.get_header_value("Content-Type", "application/octet-stream");
      state->headers_ready = true;
      if (upstream_res.status == 503 && upstream_res.get_header_value(kUnavailableHeaderName) == "1") {
        state->should_restart = true;
        state->restart_reason = "worker reported unavailable for " + operation;
      }
      state->cv.notify_all();
      return true;
    };
    upstream_req.content_receiver = [state](const char* data, size_t data_length, uint64_t, uint64_t) {
      std::lock_guard<std::mutex> lock(state->mutex);
      if (state->downstream_canceled) {
        return false;
      }
      state->chunks.emplace_back(data, data_length);
      state->cv.notify_all();
      return true;
    };

    httplib::Response upstream_res;
    httplib::Error error = httplib::Error::Success;
    bool ok = client.send(upstream_req, upstream_res, error);

    std::lock_guard<std::mutex> lock(state->mutex);
    state->finished = true;
    if (!ok && !(state->downstream_canceled && error == httplib::Error::Canceled)) {
      state->transport_failed = true;
      state->transport_error = error;
      if (!state->should_restart) {
        state->should_restart = true;
        state->restart_reason = !state->headers_ready ? "worker transport failure before streaming headers for " + operation
                                                      : "worker transport failure during streaming for " + operation;
      }
    }
    state->cv.notify_all();
  });

  {
    std::unique_lock<std::mutex> lock(state->mutex);
    state->cv.wait(lock, [&]() { return state->headers_ready || state->finished; });
    if (!state->headers_ready) {
      lock.unlock();
      if (state->worker_thread.joinable()) {
        state->worker_thread.join();
      }
      if (state->should_restart) {
        worker_manager_.restart(state->restart_reason);
      }
      setUnavailableResponse(res, operation, "JV-Link worker failed before streaming response started");
      return;
    }
  }

  res.status = state->upstream_status;
  for (const auto& header : state->upstream_headers) {
    if (shouldSkipResponseHeader(header.first) || _stricmp(header.first.c_str(), "Content-Type") == 0) {
      continue;
    }
    res.headers.emplace(header.first, header.second);
  }

  const std::string content_type = state->content_type;
  res.set_chunked_content_provider(
      content_type,
      [state](size_t, httplib::DataSink& sink) {
        while (true) {
          std::string chunk;
          {
            std::unique_lock<std::mutex> lock(state->mutex);
            state->cv.wait(lock, [&]() { return !state->chunks.empty() || state->finished; });
            if (!state->chunks.empty()) {
              chunk = std::move(state->chunks.front());
              state->chunks.pop_front();
            } else if (state->finished) {
              sink.done();
              return true;
            }
          }

          if (!sink.is_writable() || !sink.write(chunk.c_str(), chunk.size())) {
            std::lock_guard<std::mutex> lock(state->mutex);
            state->downstream_canceled = true;
            state->cv.notify_all();
            return false;
          }
        }
      },
      [this, state, operation](bool) {
        {
          std::lock_guard<std::mutex> lock(state->mutex);
          state->downstream_canceled = true;
          state->cv.notify_all();
        }

        if (state->worker_thread.joinable()) {
          state->worker_thread.join();
        }

        if (state->should_restart) {
          worker_manager_.restart(state->restart_reason);
        } else {
          worker_manager_.restartIfWorkerUnhealthy("post-stream health check for " + operation);
        }
      });
}
