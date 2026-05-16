from __future__ import annotations

from backend.app.core.database import SessionLocal
from backend.app.services.analysis_run_service import ensure_teacher_demo_data


def main() -> None:
    db = SessionLocal()
    try:
        ensure_teacher_demo_data(db, force=True)
        print("Demo data seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
