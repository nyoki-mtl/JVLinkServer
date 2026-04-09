"""Public package entrypoint."""

import logging

__version__ = "0.8.2"
__author__ = "Hiroki Taniai"

from pyjvlink.api import Client
from pyjvlink.errors import (
    JVAuthError,
    JVBusyError,
    JVConnectionError,
    JVDataError,
    JVFileCorruptedError,
    JVInvalidDataSpecError,
    JVInvalidFromTimeError,
    JVInvalidKeyError,
    JVInvalidOptionError,
    JVInvalidParameterError,
    JVLinkError,
    JVNoDataError,
    JVOpenError,
    JVServerError,
    JVTimeoutError,
    JVUnavailableError,
    JVValidationError,
)
from pyjvlink.types import JVDataSpec, JVServerConfig, QueryOption, RaceKeyParts, build_race_key, build_race_key_short

# Avoid emitting warnings via logging.lastResort when the application does not configure logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "Client",
    "JVAuthError",
    "JVBusyError",
    "JVConnectionError",
    "JVDataError",
    "JVDataSpec",
    "JVFileCorruptedError",
    "JVInvalidDataSpecError",
    "JVInvalidFromTimeError",
    "JVInvalidKeyError",
    "JVInvalidOptionError",
    "JVInvalidParameterError",
    "JVLinkError",
    "JVNoDataError",
    "JVOpenError",
    "JVServerConfig",
    "JVServerError",
    "JVTimeoutError",
    "JVUnavailableError",
    "JVValidationError",
    "QueryOption",
    "RaceKeyParts",
    "build_race_key",
    "build_race_key_short",
]
