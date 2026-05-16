from __future__ import annotations

import os
from pathlib import Path


TEST_DB_PATH = Path(__file__).resolve().parents[2] / "tmp" / "pytest_obe_analysis.db"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")


def pytest_sessionstart(session) -> None:
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
