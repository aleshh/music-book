#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

find_cover_python() {
  local candidate

  if [[ -n "${PYTHON_BIN:-}" ]]; then
    candidate="$PYTHON_BIN"
    if [[ -x "$candidate" ]] && "$candidate" -c 'import PIL, pypdf, reportlab' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return
    fi
  fi

  if command -v python3 >/dev/null 2>&1; then
    candidate="$(command -v python3)"
    if "$candidate" -c 'import PIL, pypdf, reportlab' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return
    fi
  fi

  candidate="${HOME}/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
  if [[ -x "$candidate" ]] && "$candidate" -c 'import PIL, pypdf, reportlab' >/dev/null 2>&1; then
    printf '%s\n' "$candidate"
    return
  fi

  printf '%s\n' "paperback-cover: Python 3 with Pillow, pypdf, and reportlab is required" >&2
  exit 1
}

cover_python="$(find_cover_python)"
exec "$cover_python" scripts/build-paperback-cover.py "$@"
