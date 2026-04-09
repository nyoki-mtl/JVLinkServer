cmake_minimum_required(VERSION 3.10)

project(JVLinkServer VERSION 1.0 LANGUAGES CXX)

# C++標準バージョンの設定 (例: C++17)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_EXTENSIONS OFF)

# ログディレクトリの設定
set(PYTHON_LOG_DIR "${CMAKE_SOURCE_DIR}/python/logs")

# ログディレクトリを作成
file(MAKE_DIRECTORY ${PYTHON_LOG_DIR})

# spdlogライブラリの追加
include(FetchContent)
FetchContent_Declare(
  spdlog
  GIT_REPOSITORY https://github.com/gabime/spdlog.git
  GIT_TAG        v1.12.0
)
FetchContent_MakeAvailable(spdlog)

# nlohmann/jsonライブラリの追加
FetchContent_Declare(
  json
  GIT_REPOSITORY https://github.com/nlohmann/json.git
  GIT_TAG        v3.11.2
)
FetchContent_MakeAvailable(json)

# MSVC固有の設定
if(MSVC)
    # ソースファイルのUTF-8扱い
    add_compile_options(/utf-8)

    # マルチスレッドDLLランタイム (/MD または /MDd)
    # CMAKE_MSVC_RUNTIME_LIBRARY は Debug/Release等のCONFIGに応じて自動で設定されます。
    # "MultiThreadedDLL" は /MD に、"MultiThreadedDebugDLL" は /MDd に対応します。
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL")
    
    # HTTPライブラリ用の追加設定
    add_compile_definitions(HTTPLIB_USE_STATIC_LIBRARY)
    add_compile_definitions(_WIN32_WINNT=0x0601)  # Windows 7 以降
endif()

# Source files for the library logic
set(JVLINK_LIB_SOURCES
    src/core/jv_link_wrapper.cpp
    src/core/jv_link_event_sink.cpp
    src/core/com_thread_worker.cpp
)

file(GLOB PARSER_SOURCES "src/data/parsers/*.cpp")
file(GLOB RECORD_SOURCES "src/data/records/*.cpp")

set(RECORD_PARSER_SOURCES
    src/data/record_parser.cpp
    ${PARSER_SOURCES}
    ${RECORD_SOURCES}
)

# Server executable
add_executable(JVLinkServer
    src/server/main.cpp
    src/server/supervisor_http_server.cpp
    src/server/openapi_handler.cpp
    ${JVLINK_LIB_SOURCES}
    ${RECORD_PARSER_SOURCES}
)

target_include_directories(JVLinkServer PUBLIC include)
target_link_libraries(JVLinkServer PUBLIC
    ole32       # ole32.lib
    oleaut32    # oleaut32.lib
    user32      # user32.lib
    gdi32       # gdi32.lib
    advapi32    # advapi32.lib
    comsuppw    # comsuppw.lib
    ws2_32      # winsock2.lib (HTTPサーバー用)
    wsock32     # winsock.lib (HTTPサーバー用)
    spdlog::spdlog
    nlohmann_json::nlohmann_json
)

# JVLinkServer の出力先設定（標準のビルドディレクトリを使用）
# GitHubリリースで配布するため、特別な出力先設定は不要

# 開発用: ビルド後にPythonパッケージディレクトリにコピー
set(PYTHON_LIB_DIR "${CMAKE_SOURCE_DIR}/python/src/pyjvlink/lib")
file(MAKE_DIRECTORY ${PYTHON_LIB_DIR})

add_custom_command(TARGET JVLinkServer POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
    $<TARGET_FILE:JVLinkServer>
    ${PYTHON_LIB_DIR}/JVLinkServer.exe
    COMMENT "Copying JVLinkServer.exe to Python package for development"
)

# JVLinkServerにライブラリをリンク（spdlog追加）
target_link_libraries(JVLinkServer PRIVATE
    ole32       # ole32.lib
    oleaut32    # oleaut32.lib
    user32      # user32.lib
    gdi32       # gdi32.lib
    advapi32    # advapi32.lib
    comsuppw    # comsuppw.lib
    spdlog::spdlog
    nlohmann_json::nlohmann_json
)

# ログディレクトリパスをコンパイル時定数として定義
target_compile_definitions(JVLinkServer PRIVATE 
    LOG_DIR_PATH="${PYTHON_LOG_DIR}"
)

# /EHsc をターゲットに明示的に設定する場合
if(MSVC)
    target_compile_options(JVLinkServer PRIVATE /EHsc /W4)
    target_link_options(JVLinkServer PRIVATE /NXCOMPAT /DYNAMICBASE)
endif()

# コンソールアプリケーションとして設定 (Windows用)
# /SUBSYSTEM:CONSOLE と同等
if(WIN32)
    set_target_properties(JVLinkServer PROPERTIES
        WIN32_EXECUTABLE OFF
    )
endif()

# Test executable
# include(FetchContent)
# FetchContent_Declare(
#   googletest
#   GIT_REPOSITORY https://github.com/google/googletest.git
#   GIT_TAG        release-1.12.1
# )
# FetchContent_MakeAvailable(googletest)

# add_executable(JVLinkTest
#     tests/unit/test_jv_link_wrapper.cpp
#     ${JVLINK_LIB_SOURCES}
#     ${RECORD_PARSER_SOURCES}
# )
# target_include_directories(JVLinkTest PUBLIC include)
# target_link_libraries(JVLinkTest PRIVATE
#     gtest_main
#     ole32 oleaut32 user32 gdi32 advapi32 comsuppw
#     ws2_32 wsock32
#     spdlog::spdlog
# )
# if(MSVC)
#     target_compile_options(JVLinkTest PRIVATE /EHsc)
# endif()

# ターゲットごとのインクルードディレクトリ設定
target_include_directories(JVLinkServer PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
# target_include_directories(JVLinkTest PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
