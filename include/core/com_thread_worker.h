#pragma once

#include <Windows.h>

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <functional>
#include <future>
#include <memory>
#include <mutex>
#include <queue>
#include <string>
#include <stdexcept>
#include <string_view>
#include <thread>
#include <type_traits>

class ComTaskTimeoutException : public std::runtime_error {
 public:
  ComTaskTimeoutException(std::string task_name, std::chrono::milliseconds timeout)
      : std::runtime_error("COM task timed out: " + task_name), task_name_(std::move(task_name)), timeout_(timeout) {}

  const std::string& taskName() const noexcept { return task_name_; }
  std::chrono::milliseconds timeout() const noexcept { return timeout_; }

 private:
  std::string task_name_;
  std::chrono::milliseconds timeout_;
};

struct ComWorkerHealthSnapshot {
  bool running = false;
  bool accepting_tasks = false;
  bool faulted = false;
  int64_t last_fault_timestamp = 0;
  std::string last_fault_message;
};

/**
 * @brief COMオブジェクトを専用スレッドで管理するワーカークラス
 *
 * STAモデルのCOMオブジェクトは、作成されたスレッドと同じスレッドで
 * すべての操作を行う必要があります。このクラスは専用のスレッドを作成し、
 * そのスレッド内でCOMオブジェクトの作成、操作、メッセージポンプを実行します。
 */
class ComThreadWorker {
 public:
  using Task = std::function<void()>;

  ComThreadWorker();
  ~ComThreadWorker();

  // 開始と停止
  bool start();
  void stop();

  // タスクの実行（非同期）
  bool postTask(Task task);

  // タスクの実行（同期的に結果を待つ）
  template <typename ResultType>
  ResultType invokeTask(std::function<ResultType()> task) {
    return invokeTask<ResultType>("unnamed", std::chrono::milliseconds::zero(), std::move(task));
  }

  template <typename ResultType>
  ResultType invokeTask(std::string_view task_name, std::chrono::milliseconds timeout, std::function<ResultType()> task) {
    if (isInComThread()) {
      return task();
    }
    if (!isRunning()) {
      throw std::runtime_error("ComThreadWorker is not running");
    }
    if (m_faulted.load()) {
      throw std::runtime_error(getLastFaultMessage());
    }

    auto promise = std::make_shared<std::promise<ResultType>>();
    auto future = promise->get_future();

    bool enqueued = postTask([task, promise]() {
      try {
        if constexpr (std::is_void_v<ResultType>) {
          task();
          promise->set_value();
        } else {
          promise->set_value(task());
        }
      } catch (...) {
        promise->set_exception(std::current_exception());
      }
    });

    if (!enqueued) {
      throw std::runtime_error("ComThreadWorker is stopping and no longer accepts tasks");
    }

    if (timeout.count() > 0) {
      if (future.wait_for(timeout) == std::future_status::timeout) {
        recordFault("COM task timed out: " + std::string(task_name));
        throw ComTaskTimeoutException(std::string(task_name), timeout);
      }
    }

    return future.get();
  }

  // COMスレッドのIDを取得
  DWORD getThreadId() const { return m_threadId; }

  // COMスレッドで実行中かチェック
  bool isInComThread() const { return GetCurrentThreadId() == m_threadId; }

  // ワーカーの稼働状態を取得
  bool isRunning() const { return m_running.load(); }
  bool isFaulted() const { return m_faulted.load(); }
  std::string getLastFaultMessage() const;
  ComWorkerHealthSnapshot getHealthSnapshot() const;

 private:
  void threadFunc();
  void processMessages();
  void executeQueuedTasks();
  void recordFault(std::string message);

  std::thread m_thread;
  std::atomic<bool> m_running{false};
  std::atomic<bool> m_acceptingTasks{false};
  std::atomic<DWORD> m_threadId{0};
  std::atomic<bool> m_faulted{false};
  std::atomic<int64_t> m_lastFaultTimestamp{0};

  // タスクキュー
  std::queue<Task> m_taskQueue;
  std::mutex m_taskMutex;
  std::condition_variable m_taskCondition;

  mutable std::mutex m_faultMutex;
  std::string m_lastFaultMessage;

  // イベント処理用
  HANDLE m_wakeEvent = nullptr;
};
