#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PACKAGE_DIR="${PACKAGE_DIR:-$ROOT_DIR/output/release}"
PACKAGE_NAME="${PACKAGE_NAME:-OBE-ExamViz-teacher.zip}"
PACKAGE_PREFIX="${PACKAGE_PREFIX:-OBE-ExamViz-teacher}"
PACKAGE_PATH="$PACKAGE_DIR/$PACKAGE_NAME"
PYTHON_BIN="${PYTHON_BIN:-}"

if [[ -z "$PYTHON_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "Python is required to build the release package." >&2
    exit 1
  fi
fi

mkdir -p "$PACKAGE_DIR"
rm -f "$PACKAGE_PATH"

"$PYTHON_BIN" - "$PACKAGE_PATH" "$PACKAGE_PREFIX" <<'PY'
from __future__ import annotations

import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path


package_path = Path(sys.argv[1])
package_prefix = sys.argv[2].strip("/").replace("\\", "/")
root = Path.cwd()

tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).split(b"\0")
paths = [Path(item.decode("utf-8")) for item in tracked if item]

deny_path_patterns = [
    re.compile(r"(^|/)\.env($|\.)", re.IGNORECASE),
    re.compile(r"(^|/)(data|output|tmp|temp|node_modules|\.venv|\.git|\.idea|\.pytest_cache|\.playwright-cli|\.run|tasks)/", re.IGNORECASE),
    re.compile(r"(^|/)obe_analysis\.db$", re.IGNORECASE),
    re.compile(r"\.(db|sqlite|sqlite3|log|pyc|pyo|pyd)$", re.IGNORECASE),
    re.compile(r"(^|/)前端界面截图/", re.IGNORECASE),
]

secret_patterns = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
]
allowed_deepseek_values = {
    "",
    "your_deepseek_api_key",
    "这里填写自己的Key",
    "你的真实Key",
}

binary_suffixes = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".docx",
    ".xlsx",
}


def rel_text(path: Path) -> str:
    return path.as_posix()


def is_allowed_binary(path: Path) -> bool:
    rel = rel_text(path)
    if path.suffix.lower() in {".docx", ".xlsx", ".xls", ".xlsm"}:
        return rel.startswith("backend/templates/")
    return True


def is_denied(path: Path) -> str | None:
    rel = rel_text(path)
    if rel.endswith(".env.example"):
        return None
    for pattern in deny_path_patterns:
        if pattern.search(rel):
            return f"denied path pattern: {pattern.pattern}"
    if path.suffix.lower() in {".docx", ".xls", ".xlsx", ".xlsm"} and not is_allowed_binary(path):
        return "office files are allowed only under backend/templates/"
    return None


bad_paths: list[str] = []
for path in paths:
    reason = is_denied(path)
    if reason:
        bad_paths.append(f"{path}: {reason}")

if bad_paths:
    print("Refusing to package risky tracked paths:", file=sys.stderr)
    for item in bad_paths:
        print(f"- {item}", file=sys.stderr)
    raise SystemExit(1)

package_path.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in paths:
        source = root / path
        if not source.is_file():
            continue
        rel = rel_text(path)
        if not is_allowed_binary(path):
            raise SystemExit(f"Refusing to package unsupported binary file: {rel}")
        archive.write(source, f"{package_prefix}/{rel}")

with zipfile.ZipFile(package_path, "r") as archive:
    names = archive.namelist()
    risky_names = []
    for name in names:
        rel = name.split("/", 1)[1] if "/" in name else name
        reason = is_denied(Path(rel))
        if reason:
            risky_names.append(f"{name}: {reason}")
    if risky_names:
        print("Package audit failed:", file=sys.stderr)
        for item in risky_names:
            print(f"- {item}", file=sys.stderr)
        raise SystemExit(1)

    secret_hits: list[str] = []
    for name in names:
        rel = name.split("/", 1)[1] if "/" in name else name
        suffix = Path(rel).suffix.lower()
        if suffix in binary_suffixes:
            continue
        data = archive.read(name)
        if len(data) > 1_000_000:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in secret_patterns:
            if pattern.search(text):
                secret_hits.append(f"{name}: {pattern.pattern}")
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            key, separator, value = stripped.partition("=")
            if separator and key.strip() == "DEEPSEEK_API_KEY":
                normalized = value.strip().strip('"').strip("'")
                if normalized not in allowed_deepseek_values:
                    secret_hits.append(f"{name}:{line_number}: DEEPSEEK_API_KEY contains a non-placeholder value")

    if secret_hits:
        print("Package secret audit failed:", file=sys.stderr)
        for item in secret_hits:
            print(f"- {item}", file=sys.stderr)
        raise SystemExit(1)

size_mb = os.path.getsize(package_path) / (1024 * 1024)
print(f"Created {package_path} ({size_mb:.2f} MiB, {len(paths)} tracked files audited)")
PY
