#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/export_public_snapshot.sh <version> [source_ref] [public_base]

Examples:
  scripts/export_public_snapshot.sh v0.8.0
  scripts/export_public_snapshot.sh v0.8.0 develop/main public/main
  # public/main が未作成（空リポ）でも実行可能

Defaults:
  source_ref  = develop/main
  public_base = public/main

This script:
  1) checks out export branch from public/main (or creates orphan if missing)
  2) overlays develop/main while excluding internal files
  3) removes excluded paths from snapshot
  4) creates a release snapshot commit
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -lt 1 ]]; then
  usage
  exit 0
fi

VERSION="$1"
SOURCE_REF="${2:-develop/main}"
PUBLIC_BASE="${3:-public/main}"
EXPORT_BRANCH="export-public"
PUBLIC_GIT_AUTHOR_NAME="${PUBLIC_GIT_AUTHOR_NAME:-nyoki-mtl}"
PUBLIC_GIT_AUTHOR_EMAIL="${PUBLIC_GIT_AUTHOR_EMAIL:-charmer.popopo@gmail.com}"

EXCLUDE_PATHS=(
  "AGENTS.md"
  "CLAUDE.md"
  "GEMINI.md"
  ".cursor/**"
  ".claude/**"
  "agent-docs/**"
  "_refs/**"
  ".sandbox/**"
  ".serena/**"
)

REMOVE_PATHS=(
  "AGENTS.md"
  "CLAUDE.md"
  "GEMINI.md"
  ".cursor"
  ".claude"
  "agent-docs"
  "_refs"
  ".sandbox"
  ".serena"
)

echo "[1/5] Fetch remotes"
git fetch develop
git fetch public

HAS_PUBLIC_BASE=0
if git rev-parse --verify --quiet "${PUBLIC_BASE}" >/dev/null; then
  HAS_PUBLIC_BASE=1
fi

echo "[2/5] Prepare export branch"
if [[ "${HAS_PUBLIC_BASE}" -eq 1 ]]; then
  echo "  base: ${PUBLIC_BASE}"
  git checkout -B "${EXPORT_BRANCH}" "${PUBLIC_BASE}"
else
  echo "  base: (none, creating orphan branch)"
  git checkout --orphan "${EXPORT_BRANCH}"
  git rm -r --ignore-unmatch . >/dev/null 2>&1 || true
  git clean -fd >/dev/null 2>&1 || true
fi

echo "[3/5] Overlay ${SOURCE_REF} with excluded dev-only paths"
CHECKOUT_ARGS=("${SOURCE_REF}" -- .)
for p in "${EXCLUDE_PATHS[@]}"; do
  CHECKOUT_ARGS+=(":(exclude)${p}")
done
git checkout "${CHECKOUT_ARGS[@]}"

echo "[4/5] Remove excluded paths from public snapshot"
git rm -r --ignore-unmatch "${REMOVE_PATHS[@]}" >/dev/null 2>&1 || true
for p in "${REMOVE_PATHS[@]}"; do
  rm -rf -- "${p}"
done

echo "[5/5] Reflect deletions from ${SOURCE_REF}"
if [[ "${HAS_PUBLIC_BASE}" -eq 1 ]]; then
  while IFS= read -r path; do
    [[ -z "${path}" ]] && continue
    git rm --ignore-unmatch -- "${path}" >/dev/null 2>&1 || true
  done < <(git diff --name-only --diff-filter=D "${PUBLIC_BASE}..${SOURCE_REF}")
fi

git add -A

if git diff --cached --quiet; then
  echo "No changes to export."
  exit 0
fi

GIT_AUTHOR_NAME="${PUBLIC_GIT_AUTHOR_NAME}" \
GIT_AUTHOR_EMAIL="${PUBLIC_GIT_AUTHOR_EMAIL}" \
GIT_COMMITTER_NAME="${PUBLIC_GIT_AUTHOR_NAME}" \
GIT_COMMITTER_EMAIL="${PUBLIC_GIT_AUTHOR_EMAIL}" \
git commit -m "Release ${VERSION}"

cat <<EOF
Snapshot commit created on branch '${EXPORT_BRANCH}'.
Next:
  git push public HEAD:main
EOF
