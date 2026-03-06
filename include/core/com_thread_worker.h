#pragma once

#include <Windows.h>

#include <atomic>
#include <condition_variable>
#include <functional>
#include <future>
#include <memory>
#include <mutex>
#include <queue>
#include <stdexcept>
#include <thread>
#include <type_traits>

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
    if (isInComThread()) {
      return task();
    }
    if (!isRunning()) {
      throw std::runtime_error("ComThreadWorker is not running");
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

    return future.get();
  }

  // COMスレッドのIDを取得
  DWORD getThreadId() const { return m_threadId; }

  // COMスレッドで実行中かチェック
  bool isInComThread() const { return GetCurrentThreadId() == m_threadId; }

  // ワーカーの稼働状態を取得
  bool isRunning() const { return m_running.load(); }

 private:
  void threadFunc();
  void processMessages();
  void executeQueuedTasks();

  std::thread m_thread;
  std::atomic<bool> m_running{false};
  std::atomic<bool> m_acceptingTasks{false};
  std::atomic<DWORD> m_threadId{0};

  // タスクキュー
  std::queue<Task> m_taskQueue;
  std::mutex m_taskMutex;
  std::condition_variable m_taskCondition;

  // イベント処理用
  HANDLE m_wakeEvent = nullptr;
};
