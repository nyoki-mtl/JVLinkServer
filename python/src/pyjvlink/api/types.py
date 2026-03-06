"""Public API typed response models."""

from typing import Any, TypedDict


class StoredQueryMeta(TypedDict):
    """Metadata returned by query_stored/query_stored_raw."""

    fanout: bool
    dataspec: str
    dataspecs: list[str]
    read_count: int
    download_count: int
    last_file_timestamp: str
    resume_from_datetime_by_dataspec: dict[str, str | None]
    per_dataspec: list[dict[str, Any]]
    streamed_records: int
    completed: bool


class RealtimeQueryMeta(TypedDict, total=False):
    """Metadata returned by query_realtime/query_realtime_raw."""

    count: int
    event_type: str
    read_count: int
    download_count: int
    last_file_timestamp: str


class HealthServiceInfo(TypedDict, total=False):
    name: str
    version: str
    uptime: int


class HealthComponentInfo(TypedDict, total=False):
    status: str
    port: int
    initialized: bool


class HealthComponentsInfo(TypedDict, total=False):
    http_server: HealthComponentInfo
    jvlink: HealthComponentInfo


class HealthResponse(TypedDict, total=False):
    status: str
    timestamp: int | str
    service: HealthServiceInfo
    components: HealthComponentsInfo
    error: str


class VersionServerInfo(TypedDict, total=False):
    name: str
    version: str
    build_date: str
    build_time: str


class VersionEnvironmentInfo(TypedDict, total=False):
    jvlink_version: str


class VersionResponse(TypedDict, total=False):
    api_version: str
    api_version_major: int
    api_version_minor: int
    api_version_patch: int
    supported_versions: list[str]
    server: VersionServerInfo
    environment: VersionEnvironmentInfo


class DeleteFileResponse(TypedDict, total=False):
    status: str
    message: str
    filename: str


class SaveUniformResponse(TypedDict, total=False):
    status: str
    message: str
    pattern: str
    filepath: str


class CourseFileResponse(TypedDict, total=False):
    status: str
    message: str
    key: str
    filepath: str
    explanation: str


class SaveCourseResponse(TypedDict, total=False):
    status: str
    message: str
    key: str
    filepath: str
