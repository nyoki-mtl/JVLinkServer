"""Transport event models."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from pyjvlink._internal.protocol.validators import to_int, to_str


@dataclass(frozen=True, slots=True)
class JVLinkEvent:
    """Typed event payload."""

    type: str
    param: str | None
    timestamp: int | None


def decode_event(payload: Mapping[str, Any]) -> JVLinkEvent | None:
    event_type = to_str(payload.get("type"))
    if event_type is None:
        return None
    return JVLinkEvent(type=event_type, param=to_str(payload.get("param")), timestamp=to_int(payload.get("timestamp")))
