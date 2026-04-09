#include "server/openapi_handler.h"

#include <utility>

#include "json.hpp"
#include "server/api_version.h"

namespace jvlink {

using json = nlohmann::json;

namespace {

json makeSchemaRef(const char* ref) {
  json schema = json::object();
  schema["$ref"] = ref;
  return schema;
}

json makeObjectSchema(json properties, json required = json()) {
  json schema = json::object();
  schema["type"] = "object";
  schema["properties"] = std::move(properties);
  if (!required.is_null()) {
    schema["required"] = std::move(required);
  }
  return schema;
}

json makeJsonContent(json schema) {
  json content = json::object();
  content["application/json"] = json{{"schema", std::move(schema)}};
  return content;
}

json makeTextContent(const char* media_type, const char* description) {
  json schema = json::object();
  schema["type"] = "string";
  schema["description"] = description;

  json content = json::object();
  content[media_type] = json{{"schema", std::move(schema)}};
  return content;
}

json makeBinaryContent(const char* media_type, const char* description) {
  json schema = json::object();
  schema["type"] = "string";
  schema["format"] = "binary";
  schema["description"] = description;

  json content = json::object();
  content[media_type] = json{{"schema", std::move(schema)}};
  return content;
}

json makeResponse(const char* description, json content) {
  json response = json::object();
  response["description"] = description;
  response["content"] = std::move(content);
  return response;
}

json makeObjectResponse(const char* description, json properties, json required = json()) {
  return makeResponse(description, makeJsonContent(makeObjectSchema(std::move(properties), std::move(required))));
}

json makeErrorResponse(const char* description) {
  return makeResponse(description, makeJsonContent(makeSchemaRef("#/components/schemas/Error")));
}

json makeBusyErrorResponse(const char* description) {
  json response = makeErrorResponse(description);
  response["headers"] = {{"Retry-After",
                          {{"description", "Suggested retry delay in seconds"}, {"schema", {{"type", "integer"}}}}},
                         {"X-Request-Id",
                          {{"description", "Request identifier for the rejected request"},
                           {"schema", {{"type", "string"}, {"example", "req-1711111111000-1"}}}}},
                         {"X-JVLink-Busy",
                          {{"description", "Indicates the request was rejected because the single JV-Link session is busy"},
                           {"schema", {{"type", "string"}, {"example", "1"}}}}},
                         {"X-JVLink-Operation",
                          {{"description", "Operation name associated with the busy rejection"},
                           {"schema", {{"type", "string"}, {"example", "query_stored"}}}}},
                         {"X-JVLink-Session-Request-Id",
                          {{"description", "Request identifier of the active session holder"},
                           {"schema", {{"type", "string"}, {"example", "req-1711111110000-7"}}}}},
                         {"X-JVLink-Session-Path",
                          {{"description", "Path of the active session holder"},
                           {"schema", {{"type", "string"}, {"example", "/query/stored"}}}}},
                         {"X-JVLink-Session-Started-At",
                          {{"description", "Unix timestamp when the active session started"},
                           {"schema", {{"type", "integer"}}}}},
                         {"X-JVLink-Session-Elapsed-Ms",
                          {{"description", "Elapsed milliseconds since the active session started"},
                           {"schema", {{"type", "integer"}}}}}};
  return response;
}

json makeServiceUnavailableResponse(const char* description) {
  json response = makeBusyErrorResponse(description);
  response["headers"]["X-JVLink-Unavailable"] = {
      {"description", "Indicates JV-Link is unavailable or faulted inside the server"},
      {"schema", {{"type", "string"}, {"example", "1"}}},
  };
  return response;
}

json makeRequestBody(json schema) {
  json request_body = json::object();
  request_body["required"] = true;
  request_body["content"] = makeJsonContent(std::move(schema));
  return request_body;
}

}  // namespace

OpenAPIHandler::OpenAPIHandler(std::string host, int port) : host_(std::move(host)), port_(port) {}

/**
 * OpenAPI仕様書リクエストを処理する
 *
 * OpenAPI 3.0.3形式でAPI仕様書を動的に生成し、
 * JSON形式でクライアントに返す。
 */
void OpenAPIHandler::handleOpenAPIRequest(const httplib::Request&, httplib::Response& res) {
  try {
    std::string spec = generateOpenAPISpec();
    res.set_content(spec, "application/json");
    res.status = 200;
  } catch (const std::exception& e) {
    json error = {{"error",
                   {{"code", "OPENAPI_GENERATION_ERROR"},
                    {"message", "Failed to generate OpenAPI specification"},
                    {"details", e.what()}}}};
    res.set_content(error.dump(), "application/json");
    res.status = 500;
  }
}

/**
 * OpenAPI仕様書を生成する
 *
 * JVLink Server APIの全エンドポイントを記述した
 * OpenAPI 3.0.3準拠の仕様書を生成する。
 *
 * @return OpenAPI仕様書のJSON文字列
 */
std::string OpenAPIHandler::generateOpenAPISpec() const {
  const std::string server_url = "http://" + host_ + ":" + std::to_string(port_);

  json paths = json::object();

  {
    json op = json::object();
    op["summary"] = "Health check endpoint";
    op["description"] = "Check if the server is running and healthy";
    op["operationId"] = "getHealth";

    json session_schema = makeObjectSchema(
        {{"busy", {{"type", "boolean"}, {"example", true}}},
         {"operation", {{"type", "string"}, {"nullable", true}, {"example", "query_stored"}}},
         {"path", {{"type", "string"}, {"nullable", true}, {"example", "/query/stored"}}},
         {"dataspec", {{"type", "string"}, {"nullable", true}, {"example", "RACE"}}},
         {"key", {{"type", "string"}, {"nullable", true}, {"example", "202401070511"}}},
         {"request_id", {{"type", "string"}, {"nullable", true}, {"example", "req-1711111110000-7"}}},
         {"remote_addr", {{"type", "string"}, {"nullable", true}, {"example", "127.0.0.1"}}},
         {"started_at", {{"type", "integer"}, {"nullable", true}, {"example", 1711111111}}},
         {"elapsed_ms", {{"type", "integer"}, {"example", 1200}}},
         {"watch_active", {{"type", "boolean"}, {"example", false}}}});
    json busy_metrics_schema = makeObjectSchema(
        {{"count", {{"type", "integer"}, {"example", 3}}},
         {"last_timestamp", {{"type", "integer"}, {"nullable", true}, {"example", 1711112222}}}});
    json unavailable_metrics_schema = makeObjectSchema(
        {{"count", {{"type", "integer"}, {"example", 1}}},
         {"last_timestamp", {{"type", "integer"}, {"nullable", true}, {"example", 1711113333}}}});
    json worker_schema = makeObjectSchema(
        {{"running", {{"type", "boolean"}, {"example", true}}},
         {"accepting_tasks", {{"type", "boolean"}, {"example", true}}},
         {"faulted", {{"type", "boolean"}, {"example", false}}},
         {"last_fault_message", {{"type", "string"}, {"nullable", true}}},
         {"last_fault_timestamp", {{"type", "integer"}, {"nullable", true}}}});
    json components_schema = makeObjectSchema({
        {"http_server",
         makeObjectSchema({{"status", {{"type", "string"}, {"example", "healthy"}}},
                           {"port", {{"type", "integer"}, {"example", 8765}}}})},
        {"jvlink",
         makeObjectSchema({{"status", {{"type", "string"}, {"example", "healthy"}}},
                           {"initialized", {{"type", "boolean"}, {"example", true}}},
                           {"operational", {{"type", "boolean"}, {"example", true}}},
                           {"faulted", {{"type", "boolean"}, {"example", false}}},
                           {"current_operation", {{"type", "string"}, {"nullable", true}}},
                           {"current_operation_started_at", {{"type", "integer"}, {"nullable", true}}},
                           {"event_watch_active", {{"type", "boolean"}, {"example", false}}},
                           {"last_fault_message", {{"type", "string"}, {"nullable", true}}},
                           {"last_fault_timestamp", {{"type", "integer"}, {"nullable", true}}},
                           {"worker", std::move(worker_schema)}})},
    });
    json metrics_schema =
        makeObjectSchema({{"busy", std::move(busy_metrics_schema)}, {"unavailable", std::move(unavailable_metrics_schema)}});
    json health_properties = {{"status", {{"type", "string"}, {"example", "healthy"}}},
                              {"timestamp", {{"type", "integer"}, {"example", 1711111111}}},
                              {"components", std::move(components_schema)},
                              {"metrics", std::move(metrics_schema)},
                              {"session", session_schema}};

    json responses = json::object();
    responses["200"] = makeObjectResponse("Server is healthy", health_properties);
    responses["503"] = makeObjectResponse("Server is unhealthy", health_properties);
    op["responses"] = std::move(responses);
    paths["/health"] = json{{"get", std::move(op)}};
  }

  {
    json op = json::object();
    op["summary"] = "Get current session state";
    op["description"] = "Returns the currently active single-session holder and watch status";
    op["operationId"] = "getSession";
    op["responses"] = json{{"200",
                            makeObjectResponse(
                                "Current session snapshot",
                                {{"busy", {{"type", "boolean"}, {"example", true}}},
                                 {"operation", {{"type", "string"}, {"nullable", true}}},
                                 {"path", {{"type", "string"}, {"nullable", true}}},
                                 {"dataspec", {{"type", "string"}, {"nullable", true}}},
                                 {"key", {{"type", "string"}, {"nullable", true}}},
                                 {"request_id", {{"type", "string"}, {"nullable", true}}},
                                 {"remote_addr", {{"type", "string"}, {"nullable", true}}},
                                 {"started_at", {{"type", "integer"}, {"nullable", true}}},
                                 {"elapsed_ms", {{"type", "integer"}, {"example", 1200}}},
                                 {"watch_active", {{"type", "boolean"}, {"example", false}}}})}};
    paths["/session"] = json{{"get", std::move(op)}};
  }

  {
    json op = json::object();
    op["summary"] = "Reset the active session";
    op["description"] = "Request cancellation of the active session or recycle the worker when running under supervisor";
    op["operationId"] = "resetSession";
    op["responses"] = json{
        {"200",
         makeObjectResponse("Session reset completed",
                            {{"status", {{"type", "string"}, {"example", "success"}}},
                             {"action", {{"type", "string"}, {"example", "released"}}},
                             {"message", {{"type", "string"}}},
                             {"session", {{"type", "object"}}}})},
        {"202",
         makeObjectResponse("Session reset accepted",
                            {{"status", {{"type", "string"}, {"example", "accepted"}}},
                             {"action", {{"type", "string"}, {"example", "cancel_requested"}}},
                             {"message", {{"type", "string"}}},
                             {"session", {{"type", "object"}}}})},
        {"503", makeServiceUnavailableResponse("JV-Link worker is unavailable")},
    };
    paths["/session/reset"] = json{{"post", std::move(op)}};
  }

  {
    json server_schema = makeObjectSchema(
        {{"name", {{"type", "string"}, {"example", "JVLinkServer"}}},
         {"build_date", {{"type", "string"}}},
         {"build_time", {{"type", "string"}}}});

    json op = json::object();
    op["summary"] = "Get API version information";
    op["description"] = "Returns the current API version and supported versions";
    op["operationId"] = "getVersion";

    json responses = json::object();
    responses["200"] = makeObjectResponse(
        "Version information",
        {{"api_version", {{"type", "string"}, {"example", "v1"}}},
         {"api_version_major", {{"type", "integer"}, {"example", 1}}},
         {"api_version_minor", {{"type", "integer"}, {"example", 0}}},
         {"api_version_patch", {{"type", "integer"}, {"example", 0}}},
         {"supported_versions", {{"type", "array"}, {"items", {{"type", "string"}}}, {"example", json::array({"v1"})}}},
         {"server", std::move(server_schema)}});
    op["responses"] = std::move(responses);
    paths["/version"] = json{{"get", std::move(op)}};
  }

  {
    json request_schema = makeObjectSchema(
        {{"data_spec", {{"type", "string"}, {"description", "Data specification code"}, {"example", "RACE"}}},
         {"from_date",
          {{"type", "string"},
           {"description", "Start time (YYYYMMDDHHMMSS) or range (YYYYMMDDHHMMSS-YYYYMMDDHHMMSS)"},
           {"example", "20240101000000"}}},
         {"option",
          {{"type", "integer"},
           {"description", "Query option (1: Normal, 2: This week, 3: Setup, 4: Setup no dialog)"},
           {"default", 1},
           {"enum", json::array({1, 2, 3, 4})}}},
         {"max_records",
          {{"type", "integer"}, {"description", "Maximum records to stream (-1 means unlimited)"}, {"default", -1}}},
         {"auto_retry",
          {{"type", "boolean"}, {"description", "Auto retry when corrupted files are detected"}, {"default", true}}},
         {"max_retries", {{"type", "integer"}, {"description", "Maximum retry attempts"}, {"default", 3}}},
         {"retry_delay_ms", {{"type", "integer"}, {"description", "Retry delay in milliseconds"}, {"default", 1000}}},
         {"record_types",
          {{"type", "array"},
           {"description", "Filter by record types (e.g., [\"RA\", \"SE\", \"HR\"])"},
           {"items", {{"type", "string"}}},
           {"example", json::array({"RA", "SE", "HR"})}}}},
        json::array({"data_spec", "from_date"}));

    json op = json::object();
    op["summary"] = "Query JV-Link data";
    op["description"] = "Retrieve stored JV-Link data as NDJSON stream";
    op["operationId"] = "queryData";
    op["requestBody"] = makeRequestBody(std::move(request_schema));

    json responses = json::object();
    responses["200"] = makeResponse("NDJSON stream (first line: meta or error, following lines: records)",
                                    makeTextContent("application/x-ndjson", "Line-delimited JSON payloads"));
    responses["400"] = makeErrorResponse("Bad request");
    responses["503"] = makeServiceUnavailableResponse("JV-Link session busy or unavailable");
    responses["500"] = makeErrorResponse("Internal server error");
    op["responses"] = std::move(responses);
    paths["/query/stored"] = json{{"post", std::move(op)}};
  }

  {
    json request_schema = makeObjectSchema(
        {{"dataspec", {{"type", "string"}, {"description", "Real-time data specification"}, {"example", "0B12"}}},
         {"key",
          {{"type", "string"},
           {"description", "Required realtime request key (dataspec-specific race/day/event key)"},
           {"example", "202401070511"}}}},
        json::array({"dataspec", "key"}));

    json op = json::object();
    op["summary"] = "Open real-time data stream";
    op["description"] = "Start receiving realtime JV-Link data as NDJSON stream";
    op["operationId"] = "openRealtime";
    op["requestBody"] = makeRequestBody(std::move(request_schema));

    json responses = json::object();
    responses["200"] = makeResponse("NDJSON stream (first line: meta or error, following lines: records)",
                                    makeTextContent("application/x-ndjson", "Line-delimited JSON payloads"));
    responses["400"] = makeErrorResponse("Bad request");
    responses["503"] = makeServiceUnavailableResponse("JV-Link session busy or unavailable");
    responses["500"] = makeErrorResponse("Internal server error");
    op["responses"] = std::move(responses);
    paths["/query/realtime"] = json{{"post", std::move(op)}};
  }

  {
    json op = json::object();
    op["summary"] = "Start event monitoring";
    op["description"] = "Begin monitoring for JV-Link events";
    op["operationId"] = "startEventMonitoring";

    json responses = json::object();
    responses["200"] = makeObjectResponse(
        "Event monitoring started",
        {{"status", {{"type", "string"}, {"example", "started"}}}, {"message", {{"type", "string"}}}});
    responses["503"] = makeServiceUnavailableResponse("JV-Link session busy or unavailable");
    op["responses"] = std::move(responses);
    paths["/event/start"] = json{{"post", std::move(op)}};
  }

  {
    json op = json::object();
    op["summary"] = "Stop event monitoring";
    op["description"] = "Stop monitoring for JV-Link events";
    op["operationId"] = "stopEventMonitoring";

    json responses = json::object();
    responses["200"] = makeObjectResponse(
        "Event monitoring stopped",
        {{"status", {{"type", "string"}, {"example", "stopped"}}}, {"message", {{"type", "string"}}}});
    responses["503"] = makeServiceUnavailableResponse("JV-Link session busy or unavailable");
    op["responses"] = std::move(responses);
    paths["/event/stop"] = json{{"post", std::move(op)}};
  }

  {
    json op = json::object();
    op["summary"] = "Stream JV-Link events";
    op["description"] = "Server-Sent Events stream for real-time JV-Link notifications";
    op["operationId"] = "streamEvents";

    json responses = json::object();
    responses["200"] = makeResponse("SSE event stream", makeTextContent("text/event-stream", "Server-Sent Events stream"));
    op["responses"] = std::move(responses);
    paths["/events/stream"] = json{{"get", std::move(op)}};
  }

  {
    json request_schema = makeObjectSchema(
        {{"filename",
          {{"type", "string"}, {"description", "Name of the file to delete"}, {"example", "RACE20240101.jvd"}}}},
        json::array({"filename"}));

    json op = json::object();
    op["summary"] = "Delete downloaded file";
    op["description"] = "Delete a downloaded JV-Link file to resolve errors";
    op["operationId"] = "deleteFile";
    op["requestBody"] = makeRequestBody(std::move(request_schema));

    json responses = json::object();
    responses["200"] = makeObjectResponse(
        "File deleted successfully",
        {{"status", {{"type", "string"}, {"example", "success"}}},
         {"message", {{"type", "string"}}},
         {"filename", {{"type", "string"}}}});
    op["responses"] = std::move(responses);
    paths["/files/delete"] = json{{"post", std::move(op)}};
  }

  {
    json request_schema = makeObjectSchema(
        {{"pattern",
          {{"type", "string"},
           {"description", "Racing uniform pattern (max 30 full-width chars)"},
           {"example", "水色，赤山形一本輪，水色袖"}}},
         {"filepath",
          {{"type", "string"}, {"description", "Full path for output image file"}, {"example", "C:\\temp\\uniform.bmp"}}}},
        json::array({"pattern", "filepath"}));

    json op = json::object();
    op["summary"] = "Generate racing uniform image to file";
    op["description"] = "Generate a 50x50 pixel BMP image of racing uniform and save to file";
    op["operationId"] = "generateUniformFile";
    op["requestBody"] = makeRequestBody(std::move(request_schema));

    json responses = json::object();
    responses["200"] = makeObjectResponse(
        "Uniform image generated successfully",
        {{"status", {{"type", "string"}, {"example", "success"}}},
         {"message", {{"type", "string"}}},
         {"pattern", {{"type", "string"}}},
         {"filepath", {{"type", "string"}}}});
    op["responses"] = std::move(responses);
    paths["/uniform/file"] = json{{"post", std::move(op)}};
  }

  {
    json request_schema = makeObjectSchema(
        {{"pattern",
          {{"type", "string"},
           {"description", "Racing uniform pattern (max 30 full-width chars)"},
           {"example", "水色，赤山形一本輪，水色袖"}}}},
        json::array({"pattern"}));

    json op = json::object();
    op["summary"] = "Generate racing uniform image";
    op["description"] = "Generate a 50x50 pixel BMP image of racing uniform and return as binary";
    op["operationId"] = "generateUniformImage";
    op["requestBody"] = makeRequestBody(std::move(request_schema));

    json responses = json::object();
    responses["200"] = makeResponse("Uniform image data", makeBinaryContent("image/bmp", "50x50 pixel 24-bit BMP image"));
    op["responses"] = std::move(responses);
    paths["/uniform/image"] = json{{"post", std::move(op)}};
  }

  {
    json request_schema = makeObjectSchema(
        {{"key",
          {{"type", "string"},
           {"description", "Request key (YYYYMMDDJJKKKKTT, use 99999999 for latest)"},
           {"example", "20240101011604TT"}}}},
        json::array({"key"}));

    json op = json::object();
    op["summary"] = "Get course map with explanation";
    op["description"] = "Retrieve course map (256x200 GIF) with explanation text";
    op["operationId"] = "getCourseFile";
    op["requestBody"] = makeRequestBody(std::move(request_schema));

    json responses = json::object();
    responses["200"] = makeObjectResponse(
        "Course map retrieved successfully",
        {{"status", {{"type", "string"}, {"example", "success"}}},
         {"message", {{"type", "string"}}},
         {"key", {{"type", "string"}}},
         {"filepath", {{"type", "string"}}},
         {"explanation", {{"type", "string"}}}});
    op["responses"] = std::move(responses);
    paths["/course/file"] = json{{"post", std::move(op)}};
  }

  {
    json request_schema = makeObjectSchema(
        {{"key",
          {{"type", "string"},
           {"description", "Request key (YYYYMMDDJJKKKKTT, use 99999999 for latest)"},
           {"example", "20240101011604TT"}}},
         {"filepath",
          {{"type", "string"}, {"description", "Full path for output course map file"}, {"example", "C:\\temp\\course.gif"}}}},
        json::array({"key", "filepath"}));

    json op = json::object();
    op["summary"] = "Save course map to file";
    op["description"] = "Retrieve course map (256x200 GIF) and save to specified file";
    op["operationId"] = "saveCourseFile";
    op["requestBody"] = makeRequestBody(std::move(request_schema));

    json responses = json::object();
    responses["200"] = makeObjectResponse(
        "Course map saved successfully",
        {{"status", {{"type", "string"}, {"example", "success"}}},
         {"message", {{"type", "string"}}},
         {"key", {{"type", "string"}}},
         {"filepath", {{"type", "string"}}}});
    op["responses"] = std::move(responses);
    paths["/course/file2"] = json{{"post", std::move(op)}};
  }

  {
    json request_schema = makeObjectSchema(
        {{"key",
          {{"type", "string"},
           {"description", "Request key (YYYYMMDDJJKKKKTT, use 99999999 for latest)"},
           {"example", "20240101011604TT"}}}},
        json::array({"key"}));

    json op = json::object();
    op["summary"] = "Get course map image";
    op["description"] = "Retrieve course map (256x200 GIF) as binary data with explanation in header";
    op["operationId"] = "getCourseImage";
    op["requestBody"] = makeRequestBody(std::move(request_schema));

    json response = makeResponse("Course map image data", makeBinaryContent("image/gif", "256x200 pixel GIF image"));
    response["headers"] = {
        {"X-Course-Explanation", {{"description", "Course explanation text (legacy raw header)"},
                                   {"schema", {{"type", "string"}}}}},
        {"X-Course-Explanation-Base64",
         {{"description", "Course explanation text encoded as base64 UTF-8"},
          {"schema", {{"type", "string"}}}}}};

    json responses = json::object();
    responses["200"] = std::move(response);
    op["responses"] = std::move(responses);
    paths["/course/image"] = json{{"post", std::move(op)}};
  }

  {
    json op = json::object();
    op["summary"] = "Shutdown server";
    op["description"] = "Gracefully shutdown the JVLink server";
    op["operationId"] = "shutdownServer";

    json responses = json::object();
    responses["200"] = makeObjectResponse(
        "Server shutting down",
        {{"message", {{"type", "string"}, {"example", "Server is shutting down"}}}});
    op["responses"] = std::move(responses);
    paths["/shutdown"] = json{{"post", std::move(op)}};
  }

  json error_payload_schema = makeObjectSchema(
      {{"code", {{"oneOf", json::array({json{{"type", "integer"}}, json{{"type", "string"}}})}}},
       {"message", {{"type", "string"}}},
       {"details", {{"type", "string"}}}});

  json spec = json::object();
  spec["openapi"] = "3.0.3";
  spec["info"] = {{"title", "JVLink Server API"},
                  {"description", "HTTP API server for JV-Link COM component to access JRA-VAN horse racing data"},
                  {"version", server::getApiVersion()},
                  {"contact", {{"name", "JVLink Server Support"}}}};
  spec["servers"] = json::array({{{"url", server_url}, {"description", "Default local server"}},
                                 {{"url", server_url + "/v1"}, {"description", "Version 1 API"}}});
  spec["paths"] = std::move(paths);
  spec["components"] = {{"schemas", {{"Error", makeObjectSchema({{"error", std::move(error_payload_schema)}})}}}};

  return spec.dump(2);
}

}  // namespace jvlink
