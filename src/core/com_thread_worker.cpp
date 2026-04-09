#include "core/com_thread_worker.h"

#include <locale.h>

#include <spdlog/spdlog.h>

namespace {

int64_t currentUnixTimestampSec() {
  return std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count();
}

}  // namespace

ComThreadWorker::ComThreadWorker() {
  m_wakeEvent = CreateEvent(nullptr, FALSE, FALSE, nullptr);
}

ComThreadWorker::~ComThreadWorker() {
  stop();
  if (m_wakeEvent) {
    CloseHandle(m_wakeEvent);
  }
}

bool ComThreadWorker::start() {
  if (m_running.exchange(true)) {
    spdlog::warn("ComThreadWorker already running");
    return true;
  }

  m_acceptingTasks = true;
  spdlog::info("Starting COM thread worker");
  m_thread = std::thread(&ComThreadWorker::threadFunc, this);

  // スレッドIDが設定されるまで待つ
  while (m_threadId == 0 && m_running.load()) {
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }

  if (m_threadId == 0) {
    m_acceptingTasks = false;
    if (m_thread.joinable()) {
      m_thread.join();
    }
    spdlog::error("Failed to start COM thread worker");
    return false;
  }

  spdlog::info("COM thread worker started with thread ID: {}", m_threadId.load());
  return true;
}

void ComThreadWorker::stop() {
  if (!m_running.load() && !m_thread.joinable()) {
    return;
  }

  spdlog::info("Stopping COM thread worker");
  m_acceptingTasks = false;

  // WM_QUITを送信してメッセージループを終了
  if (m_threadId != 0) {
    PostThreadMessage(m_threadId, WM_QUIT, 0, 0);
  }

  // イベントも設定
  SetEvent(m_wakeEvent);

  if (m_thread.joinable()) {
    m_thread.join();
  }

  m_running = false;
  m_threadId = 0;
  spdlog::info("COM thread worker stopped");
}

std::string ComThreadWorker::getLastFaultMessage() const {
  std::lock_guard<std::mutex> lock(m_faultMutex);
  if (!m_lastFaultMessage.empty()) {
    return m_lastFaultMessage;
  }
  return "COM worker is faulted";
}

ComWorkerHealthSnapshot ComThreadWorker::getHealthSnapshot() const {
  std::lock_guard<std::mutex> lock(m_faultMutex);
  ComWorkerHealthSnapshot snapshot;
  snapshot.running = m_running.load();
  snapshot.accepting_tasks = m_acceptingTasks.load();
  snapshot.faulted = m_faulted.load();
  snapshot.last_fault_timestamp = m_lastFaultTimestamp.load();
  snapshot.last_fault_message = m_lastFaultMessage;
  return snapshot;
}

void ComThreadWorker::recordFault(std::string message) {
  {
    std::lock_guard<std::mutex> lock(m_faultMutex);
    m_lastFaultMessage = std::move(message);
  }
  m_lastFaultTimestamp.store(currentUnixTimestampSec());
  m_faulted.store(true);
  m_acceptingTasks.store(false);
}

bool ComThreadWorker::postTask(Task task) {
  if (!m_running.load() || !m_acceptingTasks.load() || m_faulted.load()) {
    return false;
  }

  {
    std::lock_guard<std::mutex> lock(m_taskMutex);
    if (!m_running.load() || !m_acceptingTasks.load() || m_faulted.load()) {
      return false;
    }
    m_taskQueue.push(std::move(task));
  }

  // スレッドを起こす
  SetEvent(m_wakeEvent);
  return true;
}

void ComThreadWorker::threadFunc() {
  // JV-Link runs inside this STA thread. Fix the thread locale to Japanese so
  // Automation string coercion does not depend on the host Windows user locale.
  _configthreadlocale(_ENABLE_PER_THREAD_LOCALE);
  setlocale(LC_ALL, ".932");
  SetThreadLocale(MAKELCID(MAKELANGID(LANG_JAPANESE, SUBLANG_DEFAULT), SORT_DEFAULT));

  // COMをSTAモードで初期化
  HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
  if (FAILED(hr)) {
    spdlog::error("Failed to initialize COM in worker thread: {:#x}", hr);
    m_running = false;
    m_acceptingTasks = false;
    return;
  }

  m_threadId = GetCurrentThreadId();
  spdlog::info("COM worker thread started with ID: {}", m_threadId.load());

  // メッセージループ
  while (m_running) {
    processMessages();
  }

  CoUninitialize();
  m_threadId = 0;
  spdlog::info("COM worker thread exiting");
}

void ComThreadWorker::processMessages() {
  // タスクキューを処理
  executeQueuedTasks();

  // Windowsメッセージを処理
  MSG msg;
  while (PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE)) {
    if (msg.message == WM_QUIT) {
      spdlog::info("WM_QUIT received in COM thread");
      executeQueuedTasks();
      m_running = false;
      return;
    }

    TranslateMessage(&msg);
    DispatchMessage(&msg);
  }

  // イベントで待機（タイムアウト付き）
  if (m_running) {
    DWORD result = MsgWaitForMultipleObjects(1, &m_wakeEvent, FALSE, 100, QS_ALLINPUT);

    if (result == WAIT_OBJECT_0) {
      // イベントがシグナル状態になった（新しいタスクがある）
      ResetEvent(m_wakeEvent);
    }
  }
}

void ComThreadWorker::executeQueuedTasks() {
  std::queue<Task> tasks;
  {
    std::lock_guard<std::mutex> lock(m_taskMutex);
    tasks.swap(m_taskQueue);
  }

  while (!tasks.empty()) {
    try {
      tasks.front()();
    } catch (const std::exception& e) {
      spdlog::error("Exception in COM thread task: {}", e.what());
    } catch (...) {
      spdlog::error("Unknown exception in COM thread task");
    }
    tasks.pop();
  }
}
