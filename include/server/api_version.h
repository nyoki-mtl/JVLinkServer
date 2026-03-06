#pragma once

#include <string>

namespace jvlink {
namespace server {

// APIバージョン情報
constexpr const char* API_VERSION_MAJOR = "1";
constexpr const char* API_VERSION_MINOR = "0";
constexpr const char* API_VERSION_PATCH = "0";

// APIバージョン文字列
inline std::string getApiVersion() {
  return std::string(API_VERSION_MAJOR) + "." + std::string(API_VERSION_MINOR) + "." + std::string(API_VERSION_PATCH);
}

}  // namespace server
}  // namespace jvlink