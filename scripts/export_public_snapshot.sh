#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PS1_SCRIPT="${SCRIPT_DIR}/export_public_snapshot.ps1"

usage() {
  cat <<'EOF'
Usage:
  scripts/export_public_snapshot.sh <version> [source_ref] [public_base]

This repository is Windows-native. The shell entrypoint is a thin wrapper
around the canonical PowerShell implementation:
  powershell -ExecutionPolicy Bypass -File scripts/export_public_snapshot.ps1 <version> [source_ref] [public_base]
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -lt 1 ]]; then
  usage
  exit 0
fi

if command -v powershell.exe >/dev/null 2>&1; then
  exec powershell.exe -ExecutionPolicy Bypass -File "${PS1_SCRIPT}" "$@"
fi

if command -v powershell >/dev/null 2>&1; then
  exec powershell -ExecutionPolicy Bypass -File "${PS1_SCRIPT}" "$@"
fi

if command -v pwsh >/dev/null 2>&1; then
  exec pwsh -ExecutionPolicy Bypass -File "${PS1_SCRIPT}" "$@"
fi

echo "PowerShell is required. Run scripts/export_public_snapshot.ps1 on Windows." >&2
exit 1
