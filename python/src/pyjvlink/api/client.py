"""Facade client for the redesigned pyjvlink architecture."""

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Any, cast

from pyjvlink._internal.codecs.record_decoder import RecordDecoder, decode_record_envelopes
from pyjvlink._internal.domain.models import DomainRecord
from pyjvlink._internal.protocol.models import WireRecord
from pyjvlink._internal.runtime import ProcessManager
from pyjvlink._internal.transport import HttpTransport, JVLinkEvent
from pyjvlink._internal.transport.events import decode_event
from pyjvlink._internal.transport.stream import wire_record_envelopes
from pyjvlink.types import (
    DATASPEC_TO_RECORDS,
    JVDataSpec,
    JVServerConfig,
    QueryOption,
    RealtimeKeyInput,
    StoredDataspecInput,
)

from .models import RealtimeResult, StoredResult
from .types import (
    CourseFileResponse,
    DeleteFileResponse,
    HealthResponse,
    RealtimeQueryMeta,
    SaveCourseResponse,
    SaveUniformResponse,
    SessionInfo,
    SessionResetResponse,
    StoredQueryMeta,
    VersionResponse,
)
from .validation import (
    StoredQueryInput,
    validate_busy_retry_overrides,
    validate_max_records,
    validate_non_empty_text,
    validate_realtime_query_input,
    validate_retry_overrides,
    validate_stored_query_input,
)


class Client:
    """Public facade that delegates to transport/runtime/codecs."""

    def __init__(
        self,
        config: JVServerConfig | None = None,
        *,
        decoder: RecordDecoder | None = None,
    ) -> None:
        self.config = config or JVServerConfig()
        self._transport = HttpTransport(self.config)
        self._runtime = ProcessManager(self.config)
        self._decoder = decoder or RecordDecoder()

    async def __aenter__(self) -> "Client":
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        _ = (exc_type, exc_val, exc_tb)
        await self.stop()

    async def start(self) -> None:
        await self._runtime.start()
        try:
            await self._transport.start()
        except Exception:
            await self._runtime.stop()
            raise

    async def stop(self) -> None:
        transport_error: Exception | None = None
        runtime_error: Exception | None = None

        try:
            await self._transport.stop()
        except Exception as exc:  # pragma: no cover - defensive path
            transport_error = exc

        try:
            await self._runtime.stop()
        except Exception as exc:  # pragma: no cover - defensive path
            runtime_error = exc

        if transport_error is not None:
            if runtime_error is not None:
                raise transport_error from runtime_error
            raise transport_error
        if runtime_error is not None:
            raise runtime_error

    @staticmethod
    def _meta_int(value: Any) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return 0
        return 0

    @staticmethod
    def _upsert_per_dataspec_meta(
        aggregate_meta: dict[str, Any],
        dataspec: str,
        payload: Mapping[str, Any],
    ) -> None:
        per_dataspec = cast(list[dict[str, Any]], aggregate_meta.setdefault("per_dataspec", []))
        next_value = {"dataspec": dataspec, **dict(payload)}
        for idx, entry in enumerate(per_dataspec):
            if isinstance(entry, Mapping) and entry.get("dataspec") == dataspec:
                per_dataspec[idx] = next_value
                return
        per_dataspec.append(next_value)

    @staticmethod
    def _build_stored_meta_base(
        *,
        dataspec: str,
        dataspecs: tuple[str, ...],
        fanout: bool,
    ) -> dict[str, Any]:
        return {
            "fanout": fanout,
            "dataspec": dataspec,
            "dataspecs": list(dataspecs),
            "read_count": 0,
            "download_count": 0,
            "last_file_timestamp": "",
            "resume_from_datetime_by_dataspec": dict.fromkeys(dataspecs),
            "per_dataspec": [{"dataspec": spec, "pending": True} for spec in dataspecs],
            "streamed_records": 0,
            "completed": False,
        }

    @classmethod
    def _merge_stored_meta(
        cls,
        aggregate_meta: dict[str, Any],
        dataspec: str,
        spec_meta: Mapping[str, Any],
    ) -> None:
        aggregate_meta["read_count"] = cls._meta_int(aggregate_meta.get("read_count")) + cls._meta_int(
            spec_meta.get("read_count")
        )
        aggregate_meta["download_count"] = cls._meta_int(aggregate_meta.get("download_count")) + cls._meta_int(
            spec_meta.get("download_count")
        )

        spec_last_file_timestamp = spec_meta.get("last_file_timestamp")
        if isinstance(spec_last_file_timestamp, str) and spec_last_file_timestamp:
            current_last_file_timestamp = aggregate_meta.get("last_file_timestamp")
            current_ts = current_last_file_timestamp if isinstance(current_last_file_timestamp, str) else ""
            if spec_last_file_timestamp > current_ts:
                aggregate_meta["last_file_timestamp"] = spec_last_file_timestamp

        resume_points = cast(dict[str, str | None], aggregate_meta.setdefault("resume_from_datetime_by_dataspec", {}))
        resume_points[dataspec] = spec_last_file_timestamp if isinstance(spec_last_file_timestamp, str) else None

        cls._upsert_per_dataspec_meta(aggregate_meta, dataspec, spec_meta)

    async def _query_stored_raw_fanout(
        self,
        *,
        normalized: StoredQueryInput,
        option: int,
        max_records: int,
        auto_retry: bool | None,
        max_retries: int | None,
        retry_delay_ms: int | None,
        busy_retry_enabled: bool | None,
        busy_max_retries: int | None,
        busy_backoff_ms: int | None,
        respect_retry_after: bool | None,
        exclude_deletions: bool,
        stream_read_timeout: int | None,
        include_raw: bool,
    ) -> StoredResult[WireRecord]:
        effective_specs: list[str] = []
        per_spec_record_types: dict[str, list[str] | None] = {}
        aggregate_meta = self._build_stored_meta_base(
            dataspec=normalized.dataspec,
            dataspecs=normalized.dataspecs,
            fanout=True,
        )

        for spec in normalized.dataspecs:
            spec_record_types = normalized.record_types
            if normalized.record_types is not None:
                allowed_record_types = set(DATASPEC_TO_RECORDS.get(JVDataSpec(spec), ()))
                spec_record_types = [
                    record_type for record_type in normalized.record_types if record_type in allowed_record_types
                ]
                if not spec_record_types:
                    self._upsert_per_dataspec_meta(
                        aggregate_meta,
                        spec,
                        {
                            "skipped": True,
                            "reason": "record_types_filter",
                        },
                    )
                    continue

            effective_specs.append(spec)
            per_spec_record_types[spec] = spec_record_types

        if not effective_specs:

            async def empty_rows() -> AsyncIterator[dict[str, Any]]:
                if False:
                    yield {}

            aggregate_meta["completed"] = True
            return StoredResult(
                meta=cast(StoredQueryMeta, aggregate_meta),
                records=wire_record_envelopes(empty_rows(), include_raw=include_raw),
            )

        remaining_records: int | None = None if max_records < 0 else max_records
        all_specs_processed = False

        first_spec = effective_specs[0]
        first_max_records = remaining_records if remaining_records is not None else -1
        first_meta, first_records = await self._transport.query_stored(
            dataspec=first_spec,
            from_datetime=normalized.from_datetime,
            option=option,
            max_records=first_max_records,
            to_date=normalized.to_date,
            record_types=per_spec_record_types[first_spec],
            auto_retry=auto_retry,
            max_retries=max_retries,
            retry_delay_ms=retry_delay_ms,
            busy_retry_enabled=busy_retry_enabled,
            busy_max_retries=busy_max_retries,
            busy_backoff_ms=busy_backoff_ms,
            respect_retry_after=respect_retry_after,
            exclude_deletions=exclude_deletions,
            stream_read_timeout=stream_read_timeout,
        )
        self._merge_stored_meta(aggregate_meta, first_spec, first_meta)

        async def iterate_rows(rows: AsyncIterator[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
            nonlocal remaining_records
            try:
                if remaining_records is not None and remaining_records <= 0:
                    return
                async for row in rows:
                    aggregate_meta["streamed_records"] = self._meta_int(aggregate_meta.get("streamed_records")) + 1
                    if remaining_records is not None:
                        remaining_records -= 1
                    yield row
                    if remaining_records is not None and remaining_records <= 0:
                        return
            finally:
                close_method = getattr(rows, "aclose", None)
                if callable(close_method):
                    close_result = close_method()
                    if close_result is not None:
                        await close_result

        async def combined_rows() -> AsyncIterator[dict[str, Any]]:
            nonlocal remaining_records
            nonlocal all_specs_processed
            try:
                async for row in iterate_rows(first_records):
                    yield row

                if remaining_records is not None and remaining_records <= 0:
                    return

                for spec in effective_specs[1:]:
                    if remaining_records is not None and remaining_records <= 0:
                        return

                    spec_max_records = remaining_records if remaining_records is not None else -1
                    spec_meta, spec_rows = await self._transport.query_stored(
                        dataspec=spec,
                        from_datetime=normalized.from_datetime,
                        option=option,
                        max_records=spec_max_records,
                        to_date=normalized.to_date,
                        record_types=per_spec_record_types[spec],
                        auto_retry=auto_retry,
                        max_retries=max_retries,
                        retry_delay_ms=retry_delay_ms,
                        busy_retry_enabled=busy_retry_enabled,
                        busy_max_retries=busy_max_retries,
                        busy_backoff_ms=busy_backoff_ms,
                        respect_retry_after=respect_retry_after,
                        exclude_deletions=exclude_deletions,
                        stream_read_timeout=stream_read_timeout,
                    )
                    self._merge_stored_meta(aggregate_meta, spec, spec_meta)

                    async for row in iterate_rows(spec_rows):
                        yield row
                all_specs_processed = True
            finally:
                aggregate_meta["completed"] = all_specs_processed or (
                    remaining_records is not None and remaining_records <= 0
                )

        return StoredResult(
            meta=cast(StoredQueryMeta, aggregate_meta),
            records=wire_record_envelopes(combined_rows(), include_raw=include_raw),
        )

    async def query_stored_raw(
        self,
        dataspec: StoredDataspecInput,
        from_datetime: str,
        option: int | QueryOption,
        max_records: int = -1,
        to_date: str | None = None,
        record_types: list[str] | None = None,
        auto_retry: bool | None = None,
        max_retries: int | None = None,
        retry_delay_ms: int | None = None,
        exclude_deletions: bool = False,
        stream_read_timeout: int | None = None,
        *,
        include_raw: bool = False,
        busy_retry_enabled: bool | None = None,
        busy_max_retries: int | None = None,
        busy_backoff_ms: int | None = None,
        respect_retry_after: bool | None = None,
    ) -> StoredResult[WireRecord]:
        normalized = validate_stored_query_input(
            dataspec=dataspec,
            from_datetime=from_datetime,
            option=option,
            to_date=to_date,
            record_types=record_types,
        )
        normalized_max_records = validate_max_records(max_records)
        normalized_option = int(option)
        max_retries, retry_delay_ms = validate_retry_overrides(max_retries=max_retries, retry_delay_ms=retry_delay_ms)
        busy_retry_enabled, busy_max_retries, busy_backoff_ms, respect_retry_after = validate_busy_retry_overrides(
            busy_retry_enabled=busy_retry_enabled,
            busy_max_retries=busy_max_retries,
            busy_backoff_ms=busy_backoff_ms,
            respect_retry_after=respect_retry_after,
        )

        if len(normalized.dataspecs) > 1:
            return await self._query_stored_raw_fanout(
                normalized=normalized,
                option=normalized_option,
                max_records=normalized_max_records,
                auto_retry=auto_retry,
                max_retries=max_retries,
                retry_delay_ms=retry_delay_ms,
                busy_retry_enabled=busy_retry_enabled,
                busy_max_retries=busy_max_retries,
                busy_backoff_ms=busy_backoff_ms,
                respect_retry_after=respect_retry_after,
                exclude_deletions=exclude_deletions,
                stream_read_timeout=stream_read_timeout,
                include_raw=include_raw,
            )

        single_spec = normalized.dataspecs[0]
        meta, records = await self._transport.query_stored(
            dataspec=normalized.dataspec,
            from_datetime=normalized.from_datetime,
            option=normalized_option,
            max_records=normalized_max_records,
            to_date=normalized.to_date,
            record_types=normalized.record_types,
            auto_retry=auto_retry,
            max_retries=max_retries,
            retry_delay_ms=retry_delay_ms,
            busy_retry_enabled=busy_retry_enabled,
            busy_max_retries=busy_max_retries,
            busy_backoff_ms=busy_backoff_ms,
            respect_retry_after=respect_retry_after,
            exclude_deletions=exclude_deletions,
            stream_read_timeout=stream_read_timeout,
        )
        normalized_meta = self._build_stored_meta_base(
            dataspec=normalized.dataspec,
            dataspecs=normalized.dataspecs,
            fanout=False,
        )
        self._merge_stored_meta(normalized_meta, single_spec, meta)

        remaining_records: int | None = None if normalized_max_records < 0 else normalized_max_records
        stream_exhausted = False

        async def counted_rows() -> AsyncIterator[dict[str, Any]]:
            nonlocal remaining_records
            nonlocal stream_exhausted
            try:
                if remaining_records is not None and remaining_records <= 0:
                    stream_exhausted = True
                    return
                async for row in records:
                    normalized_meta["streamed_records"] = self._meta_int(normalized_meta.get("streamed_records")) + 1
                    if remaining_records is not None:
                        remaining_records -= 1
                    yield row
                    if remaining_records is not None and remaining_records <= 0:
                        return
                stream_exhausted = True
            finally:
                close_method = getattr(records, "aclose", None)
                if callable(close_method):
                    close_result = close_method()
                    if close_result is not None:
                        await close_result
                normalized_meta["completed"] = stream_exhausted or (
                    remaining_records is not None and remaining_records <= 0
                )

        wire_stream = wire_record_envelopes(counted_rows(), include_raw=include_raw)
        return StoredResult(meta=cast(StoredQueryMeta, normalized_meta), records=wire_stream)

    async def query_realtime_raw(
        self,
        dataspec: str | JVDataSpec,
        key: RealtimeKeyInput,
        *,
        include_raw: bool = False,
        busy_retry_enabled: bool | None = None,
        busy_max_retries: int | None = None,
        busy_backoff_ms: int | None = None,
        respect_retry_after: bool | None = None,
    ) -> RealtimeResult[WireRecord]:
        normalized_dataspec, normalized_key = validate_realtime_query_input(dataspec=dataspec, key=key)
        busy_retry_enabled, busy_max_retries, busy_backoff_ms, respect_retry_after = validate_busy_retry_overrides(
            busy_retry_enabled=busy_retry_enabled,
            busy_max_retries=busy_max_retries,
            busy_backoff_ms=busy_backoff_ms,
            respect_retry_after=respect_retry_after,
        )
        meta, records = await self._transport.query_realtime(
            dataspec=normalized_dataspec,
            key=normalized_key,
            busy_retry_enabled=busy_retry_enabled,
            busy_max_retries=busy_max_retries,
            busy_backoff_ms=busy_backoff_ms,
            respect_retry_after=respect_retry_after,
        )
        wire_stream = wire_record_envelopes(records, include_raw=include_raw)
        return RealtimeResult(meta=cast(RealtimeQueryMeta, meta), records=wire_stream)

    async def query_stored(
        self,
        dataspec: StoredDataspecInput,
        from_datetime: str,
        option: int | QueryOption,
        max_records: int = -1,
        to_date: str | None = None,
        record_types: list[str] | None = None,
        auto_retry: bool | None = None,
        max_retries: int | None = None,
        retry_delay_ms: int | None = None,
        exclude_deletions: bool = False,
        stream_read_timeout: int | None = None,
        *,
        include_raw: bool = False,
        busy_retry_enabled: bool | None = None,
        busy_max_retries: int | None = None,
        busy_backoff_ms: int | None = None,
        respect_retry_after: bool | None = None,
    ) -> StoredResult[DomainRecord]:
        raw_result = await self.query_stored_raw(
            dataspec=dataspec,
            from_datetime=from_datetime,
            option=option,
            max_records=max_records,
            to_date=to_date,
            record_types=record_types,
            auto_retry=auto_retry,
            max_retries=max_retries,
            retry_delay_ms=retry_delay_ms,
            exclude_deletions=exclude_deletions,
            stream_read_timeout=stream_read_timeout,
            include_raw=include_raw,
            busy_retry_enabled=busy_retry_enabled,
            busy_max_retries=busy_max_retries,
            busy_backoff_ms=busy_backoff_ms,
            respect_retry_after=respect_retry_after,
        )
        decoded_stream = decode_record_envelopes(raw_result.records, self._decoder)
        return StoredResult(meta=raw_result.meta, records=decoded_stream)

    async def query_realtime(
        self,
        dataspec: str | JVDataSpec,
        key: RealtimeKeyInput,
        *,
        include_raw: bool = False,
        busy_retry_enabled: bool | None = None,
        busy_max_retries: int | None = None,
        busy_backoff_ms: int | None = None,
        respect_retry_after: bool | None = None,
    ) -> RealtimeResult[DomainRecord]:
        raw_result = await self.query_realtime_raw(
            dataspec=dataspec,
            key=key,
            include_raw=include_raw,
            busy_retry_enabled=busy_retry_enabled,
            busy_max_retries=busy_max_retries,
            busy_backoff_ms=busy_backoff_ms,
            respect_retry_after=respect_retry_after,
        )
        decoded_stream = decode_record_envelopes(raw_result.records, self._decoder)
        return RealtimeResult(meta=raw_result.meta, records=decoded_stream)

    async def get_health(self) -> HealthResponse:
        return cast(HealthResponse, await self._transport.get_health())

    async def get_session(self) -> SessionInfo:
        return cast(SessionInfo, await self._transport.get_session())

    async def reset_session(self) -> SessionResetResponse:
        return cast(SessionResetResponse, await self._transport.reset_session())

    async def get_version(self) -> VersionResponse:
        return cast(VersionResponse, await self._transport.get_version())

    async def delete_file(self, filename: str) -> DeleteFileResponse:
        normalized_filename = validate_non_empty_text("filename", filename)
        return cast(DeleteFileResponse, await self._transport.delete_file(normalized_filename))

    async def get_uniform(self, pattern: str) -> bytes:
        normalized_pattern = validate_non_empty_text("pattern", pattern)
        return await self._transport.get_uniform(normalized_pattern)

    async def save_uniform(self, pattern: str, filepath: str) -> SaveUniformResponse:
        normalized_pattern = validate_non_empty_text("pattern", pattern)
        normalized_filepath = validate_non_empty_text("filepath", filepath)
        return cast(
            SaveUniformResponse,
            await self._transport.save_uniform(normalized_pattern, normalized_filepath),
        )

    async def get_course(self, key: str) -> tuple[bytes, str]:
        normalized_key = validate_non_empty_text("key", key)
        return await self._transport.get_course(normalized_key)

    async def get_course_file(self, key: str) -> CourseFileResponse:
        normalized_key = validate_non_empty_text("key", key)
        return cast(CourseFileResponse, await self._transport.get_course_file(normalized_key))

    async def save_course(self, key: str, filepath: str) -> SaveCourseResponse:
        normalized_key = validate_non_empty_text("key", key)
        normalized_filepath = validate_non_empty_text("filepath", filepath)
        return cast(
            SaveCourseResponse,
            await self._transport.save_course(normalized_key, normalized_filepath),
        )

    async def stream_events_raw(self) -> AsyncIterator[dict[str, Any]]:
        async for event in self._transport.stream_events():
            yield event

    async def stream_events(self) -> AsyncIterator[JVLinkEvent]:
        async for event in self.stream_events_raw():
            decoded = decode_event(event)
            if decoded is not None:
                yield decoded

    @asynccontextmanager
    async def watch_events_raw(self) -> AsyncIterator[AsyncIterator[dict[str, Any]]]:
        await self.start_event_watch()
        stream = self.stream_events_raw()
        close_error: Exception | None = None
        try:
            yield stream
        finally:
            close_method = getattr(stream, "aclose", None)
            if callable(close_method):
                try:
                    close_result = close_method()
                    if close_result is not None:
                        await close_result
                except Exception as exc:  # pragma: no cover - defensive path
                    close_error = exc

            try:
                await self.stop_event_watch()
            except Exception as exc:
                if close_error is not None:
                    raise close_error from exc
                raise

            if close_error is not None:
                raise close_error

    @asynccontextmanager
    async def watch_events(self) -> AsyncIterator[AsyncIterator[JVLinkEvent]]:
        await self.start_event_watch()
        stream = self.stream_events()
        close_error: Exception | None = None
        try:
            yield stream
        finally:
            close_method = getattr(stream, "aclose", None)
            if callable(close_method):
                try:
                    close_result = close_method()
                    if close_result is not None:
                        await close_result
                except Exception as exc:  # pragma: no cover - defensive path
                    close_error = exc

            try:
                await self.stop_event_watch()
            except Exception as exc:
                if close_error is not None:
                    raise close_error from exc
                raise

            if close_error is not None:
                raise close_error

    async def start_event_watch(self) -> dict[str, Any]:
        return await self._transport.start_event_watch()

    async def stop_event_watch(self) -> dict[str, Any]:
        return await self._transport.stop_event_watch()
