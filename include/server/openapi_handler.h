#pragma once

#include <httplib.h>

#include <string>

namespace jvlink {

class OpenAPIHandler {
 public:
  explicit OpenAPIHandler(std::string host, int port);
  ~OpenAPIHandler() = default;

  void handleOpenAPIRequest(const httplib::Request& req, httplib::Response& res);

 private:
  std::string generateOpenAPISpec() const;
  std::string host_;
  int port_;
};

}  // namespace jvlink