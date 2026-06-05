#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Patch whitespace check"
git diff --check

echo "==> AI privacy prompt audit"
if rg -n "warnings\\[:10\\]|student_no.*generate|student_name.*generate|Student ID|主要预警" backend/app backend/tests; then
  echo "Potential raw student identifier usage found in AI generation path." >&2
  exit 1
fi

echo "==> Backend tests"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"
if [[ -x "$ROOT_DIR/.venv/bin/pytest" ]]; then
  "$ROOT_DIR/.venv/bin/pytest" backend/tests -q
else
  python -m pytest backend/tests -q
fi

echo "==> Frontend production build"
(cd frontend && npm run build)

echo "==> Delivery verification passed"
