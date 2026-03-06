"""Server binary discovery utilities."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ServerBinary:
    """Resolved server binary information."""

    path: Path
    exists: bool


def discover_server_binary(root: Path | None = None) -> ServerBinary:
    """Discover the packaged JVLinkServer binary path."""

    package_root = root or Path(__file__).resolve().parents[2]
    binary_path = package_root / "lib" / "JVLinkServer.exe"
    return ServerBinary(path=binary_path, exists=binary_path.exists())
