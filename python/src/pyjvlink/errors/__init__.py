"""PyJVLink exception hierarchy."""

from typing import Any, NoReturn


class JVLinkError(Exception):
    """Base exception for PyJVLink."""


class JVServerError(JVLinkError):
    """JVLinkServer-related error."""

    def __init__(self, message: str, error_code: int | None = None):
        super().__init__(message)
        self.error_code = error_code


class JVBusyError(JVServerError):
    """The single JV-Link session is busy and the request can be retried."""

    def __init__(
        self,
        message: str,
        error_code: int | None = None,
        retry_after: int | None = None,
        *,
        operation: str | None = None,
        path: str | None = None,
        request_id: str | None = None,
        started_at: int | None = None,
        elapsed_ms: int | None = None,
        dataspec: str | None = None,
        key: str | None = None,
        session: dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code=error_code)
        self.retry_after = retry_after
        self.operation = operation
        self.path = path
        self.request_id = request_id
        self.started_at = started_at
        self.elapsed_ms = elapsed_ms
        self.dataspec = dataspec
        self.key = key
        self.session = session


class JVUnavailableError(JVServerError):
    """JVLinkServer is reachable but JV-Link itself is unavailable or faulted."""


class JVOpenError(JVServerError):
    """JVOpen error returned by JV-Link."""


class JVAuthError(JVServerError):
    """Authentication or authorization error."""


class JVFileCorruptedError(JVServerError):
    """Downloaded file is corrupted."""


class JVConnectionError(JVLinkError):
    """Connection error between client and server."""


class JVDataError(JVLinkError):
    """Data processing error."""


class JVValidationError(JVDataError):
    """Base class for input validation errors."""


class JVTimeoutError(JVLinkError):
    """Timeout waiting for server response."""


class JVInvalidDataSpecError(JVValidationError):
    """Invalid dataspec."""


class JVInvalidOptionError(JVValidationError):
    """Invalid option."""


class JVInvalidFromTimeError(JVValidationError):
    """Invalid from_datetime or to_date."""


class JVInvalidKeyError(JVValidationError):
    """Invalid realtime key."""


class JVInvalidParameterError(JVValidationError):
    """Invalid parameter other than key."""


class JVNoDataError(JVDataError):
    """Compatibility exception for no-data conditions."""


# Mapping from JV-Link error codes to specific exception types.
# Used by the transport layer to raise precise exceptions.
_ERROR_CODE_MAP: dict[int, type[JVLinkError]] = {
    -1: JVNoDataError,
    -202: JVBusyError,
    -50301: JVUnavailableError,
    -111: JVInvalidDataSpecError,
    -112: JVInvalidParameterError,
    -113: JVInvalidFromTimeError,
    -114: JVInvalidKeyError,
    -115: JVInvalidOptionError,
    -116: JVInvalidParameterError,
    -118: JVInvalidParameterError,
    -301: JVAuthError,
    -302: JVAuthError,
    -303: JVAuthError,
    -304: JVAuthError,
    -305: JVAuthError,
    -402: JVFileCorruptedError,
    -403: JVFileCorruptedError,
}


def build_error_for_code(
    error_code: int,
    message: str,
    *,
    default_exc: type[JVLinkError] = JVOpenError,
    retry_after: int | None = None,
    busy_context: dict[str, Any] | None = None,
) -> JVLinkError:
    """Build the appropriate exception instance for a JV-Link error code."""
    exc_cls = _ERROR_CODE_MAP.get(error_code, default_exc)
    try:
        if exc_cls is JVBusyError:
            return exc_cls(message, error_code=error_code, retry_after=retry_after, **(busy_context or {}))
        return exc_cls(message, error_code=error_code)
    except TypeError:
        # Validation errors do not accept error_code in the constructor.
        exc = exc_cls(message)
        exc.error_code = error_code  # type: ignore[attr-defined]
        return exc


def raise_for_error_code(
    error_code: int,
    message: str,
    *,
    default_exc: type[JVLinkError] = JVOpenError,
) -> NoReturn:
    """Raise the appropriate exception for a JV-Link error code."""
    raise build_error_for_code(error_code, message, default_exc=default_exc)


__all__ = [
    "JVAuthError",
    "JVBusyError",
    "JVConnectionError",
    "JVDataError",
    "JVFileCorruptedError",
    "JVInvalidDataSpecError",
    "JVInvalidFromTimeError",
    "JVInvalidKeyError",
    "JVInvalidOptionError",
    "JVInvalidParameterError",
    "JVLinkError",
    "JVNoDataError",
    "JVOpenError",
    "JVServerError",
    "JVTimeoutError",
    "JVUnavailableError",
    "JVValidationError",
    "build_error_for_code",
    "raise_for_error_code",
]
