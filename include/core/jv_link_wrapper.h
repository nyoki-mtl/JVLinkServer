#pragma once

#ifndef NOMINMAX
#define NOMINMAX 1
#endif
#include <Ole2.h>
#include <OleAuto.h>
#include <comdef.h>
#include <comutil.h>

#include <atomic>
#include <chrono>
#include <functional>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "core/com_thread_worker.h"
#include "core/jv_link_dispid.h"
#include "core/jv_link_error_codes.h"
#include "core/jv_link_event_sink.h"

interface IDispatch;

/**
 * @brief Result structure for JV-Link query operations
 *
 * Contains metadata about the query operation including counts, timestamps,
 * and any error information. Used as a callback parameter for streaming operations.
 */
struct JVQueryResult {
  bool success = false;              // Whether the operation succeeded
  int read_count = 0;                // Total number of files matching query conditions (from JVOpen)
  int download_count = 0;            // Number of files that need to be downloaded (from JVOpen)
  int error_code = 0;                // JV-Link specific error code (negative values indicate errors)
  std::string last_file_timestamp;   // Timestamp of newest file (YYYYMMDDhhmmss format)
  std::string error_message;         // Human-readable error description
};

/**
 * @brief Exception for stream-read failures with JV-Link error code context
 */
class JVStreamReadException : public std::runtime_error {
 public:
  JVStreamReadException(int error_code, const std::string& message)
      : std::runtime_error(message), error_code_(error_code) {}

  int errorCode() const noexcept { return error_code_; }

 private:
  int error_code_;
};

/**
 * @brief Exception for cooperative stream cancellation
 */
class JVOperationCanceledException : public std::runtime_error {
 public:
  explicit JVOperationCanceledException(const std::string& message) : std::runtime_error(message) {}
};

class JVLinkFatalException : public std::runtime_error {
 public:
  explicit JVLinkFatalException(const std::string& message) : std::runtime_error(message) {}
};

struct JVLinkHealthSnapshot {
  bool initialized = false;
  bool operational = false;
  bool faulted = false;
  bool event_watch_active = false;
  int64_t current_operation_started_at = 0;
  int64_t last_fault_timestamp = 0;
  std::string status;
  std::string current_operation;
  std::string last_fault_message;
  ComWorkerHealthSnapshot worker;
};

/**
 * @brief Wrapper class for JV-Link COM component
 *
 * Provides a C++ interface to the JV-Link COM API for accessing JRA-VAN horse racing data.
 * Handles COM lifecycle, character encoding conversion (Shift_JIS to UTF-8), and
 * streaming data access.
 *
 * This implementation only includes methods actually used by the Python client:
 * - queryStored: For accumulated data (option=1,2,3), uses JVGets by default
 * - queryRealtime: For real-time data
 * - startEventWatch/stopEventWatch: For event monitoring
 *
 * Buffer allocation:
 * - Uses 120KB buffer (20% margin over largest record of 103KB)
 * - Buffer is reused across records to minimize allocations
 *
 * Error handling:
 * - Detailed error logging with specific JV-Link error codes
 * - JVOpen/JVRTOpen parameter/availability errors are returned via callbacks
 * - Critical stream-read failures throw exceptions to allow upper layers to emit terminal stream errors
 *
 * Thread safety:
 * - Not thread-safe - use single instance per thread
 */
class JVLinkWrapper {
 public:
  /**
   * @brief Configuration for auto-retry behavior
   */
  struct RetryConfig {
    bool auto_retry_on_corruption = true;  // Enable auto-retry for corrupted files (-402, -403)
    int max_retry_attempts = 3;            // Maximum number of retry attempts
    int retry_delay_ms = 1000;             // Delay between retries in milliseconds
  };

  struct TimeoutConfig {
    std::chrono::milliseconds open_timeout{std::chrono::seconds(60)};
    std::chrono::milliseconds setup_open_timeout{std::chrono::seconds(300)};
    std::chrono::milliseconds realtime_open_timeout{std::chrono::seconds(45)};
    std::chrono::milliseconds stream_read_timeout{std::chrono::seconds(30)};
    std::chrono::milliseconds status_timeout{std::chrono::seconds(10)};
    std::chrono::milliseconds control_timeout{std::chrono::seconds(30)};
  };

  JVLinkWrapper();
  ~JVLinkWrapper();

  JVLinkWrapper(const JVLinkWrapper&) = delete;
  JVLinkWrapper& operator=(const JVLinkWrapper&) = delete;
  JVLinkWrapper(JVLinkWrapper&&) = delete;
  JVLinkWrapper& operator=(JVLinkWrapper&&) = delete;

  /**
   * @brief Initializes JV-Link wrapper and performs JVInit
   *
   * Must be called first before any other JV-Link operations.
   * Initializes COM, creates JV-Link instance, and calls JVInit.
   *
   * @param sid Software ID (max 64 bytes) to identify calling software.
   *            Used as User-Agent HTTP header. Default "UNKNOWN".
   *            Allowed chars: alphanumeric, space, underscore, period, slash.
   * @return true if initialization succeeded, false otherwise
   *
   * @note Error codes from JVInit:
   *   0: Normal
   *   -101: sid not set
   *   -102: sid exceeds 64 bytes
   *   -103: sid is invalid (first character is space)
   */
  bool initialize(const std::string& sid = "UNKNOWN");

  /**
   * @brief Shuts down JV-Link wrapper and releases COM resources
   *
   * Releases the JV-Link COM instance and marks wrapper as uninitialized.
   * Safe to call multiple times.
   */
  void shutdown();

  /**
   * @brief Checks if JV-Link wrapper is initialized
   *
   * @return true if initialize() has been called successfully, false otherwise
   */
  bool isInitialized() const { return is_initialized_; }

  /**
   * @brief Sets the retry configuration for corrupted file handling
   *
   * @param config Retry configuration settings
   */
  void setRetryConfig(const RetryConfig& config) { retry_config_ = config; }

  /**
   * @brief Gets the current retry configuration
   *
   * @return Current retry configuration
   */
  const RetryConfig& getRetryConfig() const { return retry_config_; }
  void setTimeoutConfig(const TimeoutConfig& config) { timeout_config_ = config; }
  const TimeoutConfig& getTimeoutConfig() const { return timeout_config_; }
  bool isOperational() const;
  bool hasFatalFault() const;
  JVLinkHealthSnapshot getHealthSnapshot() const;

  /**
   * @brief Queries and streams accumulated data using modern JVGets API (default)
   *
   * Performs JVOpen to request data, waits for download if needed,
   * then streams records via callback using JVGets for optimal performance.
   * Automatically handles file switching.
   *
   * @param dataspec Concatenated string of 4-digit data type IDs (e.g., "RACE", "TOKU")
   * @param fromdate Start point time in YYYYMMDD or YYYYMMDDhhmmss format.
   *                 Can include range: "YYYYMMDDhhmmss-YYYYMMDDhhmmss"
   * @param option Query option:
   *   1: Normal data (difference data)
   *   2: This week's data
   *   3: Setup data
   *   4: Setup data without dialog
   * @param max_records Maximum records to read (0 or negative = read all)
   * @param record_callback Called for each record read
   * @param meta_callback Called once with query metadata (counts, timestamps)
   *
   * @note Common JVOpen error codes:
   *   0: Normal
   *   -1: No relevant data found
   *   -111 to -116: Parameter invalid
   *   -201: JVInit not called
   *   -301: Authentication error
   *   -504: Server under maintenance
   */
  void queryStored(const std::string& dataspec, const std::string& fromdate, long option, int max_records,
                   const std::function<void(const std::string&)>& record_callback,
                   const std::function<void(const JVQueryResult&)>& meta_callback,
                   const std::vector<std::string>& filter_record_types = {},
                   const std::function<bool()>& cancel_requested = {});

  /**
   * @brief Queries and streams real-time data from JV-Link
   *
   * Performs JVRTOpen to request real-time data and streams records via callback.
   * No download wait needed as data is retrieved directly from server.
   *
   * @param dataspec 4-digit data type ID (e.g., "0B11", "0B12")
   * @param key Request key varies by data type:
   *   - Per race: "YYYYMMDDJJKKHHRR" or "YYYYMMDDJJRR"
   *   - Per event day: "YYYYMMDD"
   *   - Per change event: Parameter from JVWatchEvent
   * @param record_callback Called for each record read
   * @param meta_callback Called once with operation status
   *
   * @note When using event parameter as key:
   *   - Refund confirmation: dataspec="0B12"
   *   - Jockey change: dataspec="0B16"
   *   - Weather/track: dataspec="0B16"
   *   - Horse weight: dataspec="0B11"
   */
  void queryRealtime(const std::string& dataspec, const std::string& key,
                     const std::function<void(const std::string&)>& record_callback,
                     const std::function<void(const JVQueryResult&)>& meta_callback,
                     const std::function<bool()>& cancel_requested = {});

  /**
   * @brief Skips remaining records in current file and moves to next file
   *
   * Can only be called during an active JVOpen session (not effective for JVRTOpen).
   * Useful for quickly scanning through accumulated data files when you determine
   * the current file contains unwanted record types.
   *
   * Important notes:
   * - Accumulated data files contain only one record type per file
   * - Check the record type (first 2 chars) of the first record to decide
   * - Real-time data (JVRTOpen) returns only one file, so skip has no effect
   *
   * @return 0 if successful, negative error code otherwise
   *   -201: JVInit not called
   *   -203: JVOpen not called
   */
  long skipCurrentFile();

  /**
   * @brief Starts event notification thread for real-time updates
   *
   * Starts JV-Link event monitoring for:
   * - Refund confirmation (JVEvtPay)
   * - Jockey changes (JVEvtJockeyChange)
   * - Weather/track changes (JVEvtWeather)
   * - Course changes (JVEvtCourseChange)
   * - Race cancellations (JVEvtAvoid)
   * - Start time changes (JVEvtTimeChange)
   * - Horse weight announcements (JVEvtWeight)
   *
   * @return true if event watch started successfully
   * @note Requires event handler to be set via setEventHandler()
   */
  bool startEventWatch();

  /**
   * @brief Stops event notification thread
   *
   * @return true if event watch stopped successfully
   */
  bool stopEventWatch();

  /**
   * @brief Deletes a downloaded file from the JV-Link save path
   *
   * Useful for resolving errors during JVRead/JVGets by deleting problematic files
   * and re-attempting the JVOpen process. The file must be in the JV-Link save path.
   *
   * @param filename Name of the file to delete (not the full path)
   * @return 0 for successful deletion, -1 for errors
   *
   * @note Common error codes:
   *   0: Normal (file deleted successfully)
   *   -1: Error (file not found, access denied, etc.)
   *   -201: JVInit not called
   */
  long deleteFile(const std::string& filename);

  /**
   * @brief Requests racing uniform image and saves it to a file
   *
   * Creates a 50x50 pixel, 24-bit bitmap image from the uniform pattern.
   * Outputs "No Image" if the image cannot be created.
   *
   * @param pattern Racing uniform color and pattern display (max 30 full-width chars)
   *                Example: "水色，赤山形一本輪，水色袖"
   * @param filepath Full path for the output image file (must be existing folder)
   * @return 0 for success, negative error code otherwise
   *   -201: JVInit not called
   *   -301: Authentication error
   *   -504: Server under maintenance
   */
  long fukuFile(const std::string& pattern, const std::string& filepath);

  /**
   * @brief Requests racing uniform image as binary data
   *
   * Returns a 50x50 pixel, 24-bit bitmap image data.
   * Returns "No Image" data if the image cannot be created.
   *
   * @param pattern Racing uniform color and pattern display (max 30 full-width chars)
   * @param buff Output parameter that receives allocated byte array with image data
   * @param size Output parameter that receives the size of the image data
   * @return 0 for success, negative error code otherwise
   * @note Caller is responsible for freeing the allocated buffer
   */
  long fuku(const std::string& pattern, BYTE** buff, long* size);

  /**
   * @brief Requests course map information and saves to file
   *
   * Retrieves course map for specified race with explanation text.
   * Image is 256x200 pixel GIF saved temporarily in pictures folder.
   *
   * @param key Request key (YYYYMMDDJJKKKKTT). Use "99999999" for YYYYMMDD to get latest
   * @param filepath Returns the file path of the saved image
   * @param explanation Returns course explanation text (max 6800 bytes)
   * @return 0 for success, negative error code otherwise
   */
  long courseFile(const std::string& key, std::string& filepath, std::string& explanation);

  /**
   * @brief Requests course map and saves to specified file
   *
   * Retrieves course map for specified race and saves to filepath.
   * Image is 256x200 pixel GIF.
   *
   * @param key Request key (YYYYMMDDJJKKKKTT). Use "99999999" for YYYYMMDD to get latest
   * @param filepath Full path for output course map file (must be existing folder)
   * @return 0 for success, negative error code otherwise
   */
  long courseFile2(const std::string& key, const std::string& filepath);

  void setEventHandler(EventHandler handler);

  bool isConnected() const { return jvlink_dispatch_ != nullptr; }

 private:
  /**
   * @brief RAII guard for JV-Link session management
   *
   * Ensures that JVClose is called when the guard goes out of scope,
   * even if an exception is thrown. This guarantees proper cleanup of
   * JV-Link sessions.
   */
  class JVSessionGuard {
   public:
    explicit JVSessionGuard(JVLinkWrapper* wrapper) : wrapper_(wrapper), should_close_(true) {}

    ~JVSessionGuard() {
      if (!should_close_ || !wrapper_) {
        return;
      }

      JVLinkWrapper* wrapper = wrapper_;
      ComThreadWorker* worker = wrapper->m_comWorker.get();

      try {
        if (!worker || !worker->isRunning() || worker->isInComThread()) {
          (void)wrapper->performJVClose();
          return;
        }

        (void)worker->invokeTask<bool>("jv_close", wrapper->timeout_config_.control_timeout,
                                       [wrapper]() { return wrapper->performJVClose(); });
      } catch (...) {
        // Destructors must not throw.
      }
    }

    // Disable closing (for cases where we don't want automatic cleanup)
    void disableClose() { should_close_ = false; }

    // Non-copyable, non-movable
    JVSessionGuard(const JVSessionGuard&) = delete;
    JVSessionGuard& operator=(const JVSessionGuard&) = delete;
    JVSessionGuard(JVSessionGuard&&) = delete;
    JVSessionGuard& operator=(JVSessionGuard&&) = delete;

   private:
    JVLinkWrapper* wrapper_;
    bool should_close_;
  };

  bool createJVLinkInstance();
  void shutdownOnComThread();
  long performJVInit(const std::string& sid);
  long performJVOpen(const std::string& dataspec, const std::string& fromdate, long option, long& read_count,
                     long& download_count, std::string& last_timestamp);
  long performJVRTOpen(const std::string& dataspec, const std::string& key);
  bool waitForDownload(long download_count, long* last_status_code = nullptr,
                       const std::function<bool()>& cancel_requested = {});
  bool performJVClose();
  long performJVStatus();
  bool performJVCancel();
  long jvGets(BYTE** buff, long* size, char* filename);
  long jvGetsWithRetry(BYTE** buff, long* size, char* filename);
  long performJVSkip();
  long performJVFiledelete(const std::string& filename);
  long performJVFukuFile(const std::string& pattern, const std::string& filepath);
  long performJVFuku(const std::string& pattern, BYTE** buff, long* size);
  long performJVCourseFile(const std::string& key, std::string& filepath, std::string& explanation);
  long performJVCourseFile2(const std::string& key, const std::string& filepath);

  HRESULT invokeMethod(DISPID dispId, WORD wFlags, VARIANT* pArgs, int cArgs, VARIANT* pResult) const;
  BSTR convertUtf8ToBSTR(const std::string& value) const;

  /**
   * @brief Converts BSTR from JV-Link to UTF-8 string
   *
   * JV-Link exposes text through COM BSTR values. This method treats the input
   * as UTF-16 and converts it directly to UTF-8.
   *
   * @param bstr COM string from JV-Link
   * @return UTF-8 encoded string
   */
  std::string convertBSTRToString(BSTR bstr) const;

  std::string getErrorMessage(HRESULT hr) const;

  bool connectEventSink();
  void disconnectEventSink();

  template <typename ResultType, typename Callable>
  ResultType invokeComCall(const char* operation_name, std::chrono::milliseconds timeout, Callable&& callable);
  void beginOperationTracking(const std::string& operation_name);
  void finishOperationTracking();
  void markFatalFault(const std::string& message);
  std::chrono::milliseconds getStoredOpenTimeout(long option) const;

  std::unique_ptr<ComThreadWorker> m_comWorker;
  IDispatch* jvlink_dispatch_;
  bool is_initialized_;
  std::string current_sid_;

  JVLinkEventSink* m_pEventSink;
  IConnectionPoint* m_pConnectionPoint;
  DWORD m_dwConnectionCookie;
  EventHandler m_eventHandler;
  RetryConfig retry_config_;  // Retry configuration for corrupted file handling
  TimeoutConfig timeout_config_;
  mutable std::mutex health_mutex_;
  bool faulted_ = false;
  bool event_watch_active_ = false;
  int64_t current_operation_started_at_ = 0;
  int64_t last_fault_timestamp_ = 0;
  std::string current_operation_;
  std::string last_fault_message_;

  static const CLSID CLSID_JVLink;
};

template <typename ResultType, typename Callable>
ResultType JVLinkWrapper::invokeComCall(const char* operation_name, std::chrono::milliseconds timeout, Callable&& callable) {
  if (hasFatalFault()) {
    std::lock_guard<std::mutex> lock(health_mutex_);
    throw JVLinkFatalException(last_fault_message_.empty() ? "JV-Link wrapper is faulted" : last_fault_message_);
  }

  beginOperationTracking(operation_name);

  try {
    if (!m_comWorker || !m_comWorker->isRunning() || m_comWorker->isInComThread()) {
      ResultType result = callable();
      finishOperationTracking();
      return result;
    }

    ResultType result =
        m_comWorker->invokeTask<ResultType>(operation_name, timeout, std::function<ResultType()>(std::forward<Callable>(callable)));
    finishOperationTracking();
    return result;
  } catch (const ComTaskTimeoutException&) {
    markFatalFault(std::string("JV-Link COM task timed out during ") + operation_name);
    throw JVLinkFatalException(std::string("JV-Link COM task timed out during ") + operation_name);
  } catch (...) {
    finishOperationTracking();
    throw;
  }
}
