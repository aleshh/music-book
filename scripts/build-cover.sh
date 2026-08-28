#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

find_cover_python() {
  local candidate

  if [[ -n "${PYTHON_BIN:-}" ]]; then
    candidate="$PYTHON_BIN"
    if [[ -x "$candidate" ]] && "$candidate" -c 'import reportlab' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return
    fi
  fi

  if command -v python3 >/dev/null 2>&1; then
    candidate="$(command -v python3)"
    if "$candidate" -c 'import reportlab' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return
    fi
  fi

  if [[ -n "${HOME:-}" ]]; then
    candidate="${HOME}/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
    if [[ -x "$candidate" ]] && "$candidate" -c 'import reportlab' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return
    fi
  fi

  printf '%s\n' "build-cover: Python 3 with reportlab is required; set PYTHON_BIN or install reportlab" >&2
  exit 1
}

cover_python="$(find_cover_python)"
if [[ "${1:-}" == "--text-only" ]]; then
  shift
  exec "$cover_python" scripts/build-cover-text.py "$@"
fi
exec "$cover_python" scripts/build-cover.py "$@"
