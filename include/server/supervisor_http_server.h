#pragma once

#include <string>

class SupervisorHTTPServer {
 public:
  SupervisorHTTPServer(int port, std::string sid, std::string log_level);
  ~SupervisorHTTPServer();

  SupervisorHTTPServer(const SupervisorHTTPServer&) = delete;
  SupervisorHTTPServer& operator=(const SupervisorHTTPServer&) = delete;
  SupervisorHTTPServer(SupervisorHTTPServer&&) = delete;
  SupervisorHTTPServer& operator=(SupervisorHTTPServer&&) = delete;

  bool start(bool blocking = false);
  void stop();
  bool isRunning() const;

 private:
  class Impl;
  Impl* impl_;
};
