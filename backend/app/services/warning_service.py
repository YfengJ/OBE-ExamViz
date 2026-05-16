from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.models.warning_result import WarningResult
from backend.app.services.analysis_service import get_course_score_dataframe


CRITICAL_SCORE = 60
WARNING_SCORE = 70


def list_warnings(
    db: Session, course_id: int | None = None, level: str | None = None, status: str | None = None
) -> list[dict]:
    query = (
        db.query(
            WarningResult,
            Student.student_no,
            Student.class_name,
            Course.course_name,
        )
        .join(Student, Student.id == WarningResult.student_id)
        .join(Course, Course.id == WarningResult.course_id)
        .order_by(WarningResult.created_at.desc())
    )

    if course_id is not None:
        query = query.filter(WarningResult.course_id == course_id)
    if level:
        query = query.filter(WarningResult.level == level)
    if status:
        query = query.filter(WarningResult.status == status)

    rows = query.all()
    return [
        {
            "id": row.WarningResult.id,
            "student_id": row.WarningResult.student_id,
            "student_no": row.student_no,
            "class_name": row.class_name,
            "course_id": row.WarningResult.course_id,
            "course_name": row.course_name,
            "term": row.WarningResult.term,
            "level": row.WarningResult.level,
            "status": row.WarningResult.status or "pending",
            "reasons": row.WarningResult.reasons_json,
            "ai_summary": row.WarningResult.ai_summary,
            "created_at": row.WarningResult.created_at,
        }
        for row in rows
    ]


def generate_warnings(db: Session, course_id: int, term: str) -> list[dict]:
    score_df = get_course_score_dataframe(db, course_id)
    if score_df.empty:
        return []

    student_map = {s.student_no: s for s in db.query(Student).all()}

    created_or_updated: list[WarningResult] = []
    for row in score_df.to_dict(orient="records"):
        student_no = str(row["student_no"])
        score = float(row["total_score"])

        level = None
        reasons: list[str] = []

        if score < CRITICAL_SCORE:
            level = "critical"
            reasons.append(f"final score below {CRITICAL_SCORE}")
        elif score < WARNING_SCORE:
            level = "warning"
            reasons.append(f"final score below {WARNING_SCORE}")

        if level is None:
            continue

        student = student_map.get(student_no)
        if not student:
            continue

        warning = (
            db.query(WarningResult)
            .filter(
                WarningResult.student_id == student.id,
                WarningResult.course_id == course_id,
                WarningResult.term == term,
            )
            .first()
        )
        if warning:
            warning.level = level
            warning.status = "pending"
            warning.reasons_json = reasons
            warning.ai_summary = None
            warning.created_at = datetime.now(timezone.utc)
        else:
            warning = WarningResult(
                student_id=student.id,
                course_id=course_id,
                term=term,
                level=level,
                status="pending",
                reasons_json=reasons,
                ai_summary=None,
                created_at=datetime.now(timezone.utc),
            )
            db.add(warning)
        created_or_updated.append(warning)

    db.commit()
    for item in created_or_updated:
        db.refresh(item)

    return list_warnings(db, course_id=course_id)


def update_warning_status(db: Session, warning_id: int, status: str) -> dict | None:
    warning = db.query(WarningResult).filter(WarningResult.id == warning_id).first()
    if not warning:
        return None
    warning.status = status
    db.commit()
    db.refresh(warning)
    return {
        "id": warning.id,
        "status": warning.status,
    }
