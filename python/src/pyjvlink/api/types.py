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


class SessionInfo(TypedDict, total=False):
    """Current single-session snapshot."""

    busy: bool
    operation: str | None
    path: str | None
    dataspec: str | None
    key: str | None
    request_id: str | None
    remote_addr: str | None
    started_at: int | None
    elapsed_ms: int
    watch_active: bool


class HealthServiceInfo(TypedDict, total=False):
    name: str
    version: str
    uptime: int


class HealthComponentInfo(TypedDict, total=False):
    status: str
    port: int
    initialized: bool
    operational: bool
    faulted: bool
    current_operation: str | None
    current_operation_started_at: int | None
    last_fault_message: str | None
    last_fault_timestamp: int | None


class HealthWorkerInfo(TypedDict, total=False):
    running: bool
    accepting_tasks: bool
    faulted: bool
    last_fault_message: str | None
    last_fault_timestamp: int | None


class HealthJVLinkComponentInfo(HealthComponentInfo, total=False):
    event_watch_active: bool
    worker: HealthWorkerInfo


class HealthComponentsInfo(TypedDict, total=False):
    http_server: HealthComponentInfo
    jvlink: HealthJVLinkComponentInfo


class HealthBusyMetricsInfo(TypedDict, total=False):
    count: int
    last_timestamp: int | None


class HealthMetricsInfo(TypedDict, total=False):
    busy: HealthBusyMetricsInfo
    unavailable: HealthBusyMetricsInfo


class HealthResponse(TypedDict, total=False):
    status: str
    timestamp: int | str
    service: HealthServiceInfo
    components: HealthComponentsInfo
    metrics: HealthMetricsInfo
    session: SessionInfo
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


class SessionResetResponse(TypedDict, total=False):
    status: str
    action: str
    message: str
    session: SessionInfo
