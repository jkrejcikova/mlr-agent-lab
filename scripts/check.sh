#!/usr/bin/env bash
# Run every project check. Exits non-zero if any check fails.
# This is the definition of "done" for this repo. See AGENTS.md.
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0
run() {
  label="$1"
  shift
  printf '\n=== %s ===\n' "$label"
  if "$@"; then
    echo "PASS: $*"
  else
    echo "FAIL: $*"
    fail=1
  fi
}

run "uv lock --check" uv lock --check
run "ruff check" uv run ruff check .
run "ruff format --check" uv run ruff format --check .
run "pytest" uv run pytest -q

printf '\n========================================\n'
if [ "$fail" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
else
  echo "CHECKS FAILED"
fi
exit "$fail"
