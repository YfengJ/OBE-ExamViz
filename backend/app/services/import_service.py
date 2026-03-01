from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.models.exam import Exam
from backend.app.models.question import Question
from backend.app.models.student import Student
from backend.app.models.student_exam_score import StudentExamScore
from backend.app.models.student_question_score import StudentQuestionScore


def _read_tabular_file(file: UploadFile) -> pd.DataFrame:
    content = file.file.read()
    file.file.seek(0)
    name = (file.filename or "").lower()
    if name.endswith(".csv"):
        return pd.read_csv(BytesIO(content))
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(BytesIO(content))
    raise HTTPException(status_code=400, detail="Only CSV/XLSX files are supported")


def _result(total: int, inserted: int, updated: int, skipped: int, errors: list[str]) -> dict[str, Any]:
    return {
        "total": total,
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "errors_preview": errors[:20],
    }


def import_students(db: Session, file: UploadFile) -> dict[str, Any]:
    df = _read_tabular_file(file)
    required = {"student_no", "class_name", "major", "grade_year"}
    if not required.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Missing required columns: {sorted(required)}")

    inserted = updated = skipped = 0
    errors: list[str] = []

    for idx, row in enumerate(df.to_dict(orient="records"), start=1):
        student_no = str(row.get("student_no", "")).strip()
        if not student_no:
            skipped += 1
            errors.append(f"row {idx}: empty student_no")
            continue

        existing = db.query(Student).filter(Student.student_no == student_no).first()
        payload = {
            "name": (str(row.get("name")).strip() if pd.notna(row.get("name")) else None),
            "class_name": str(row.get("class_name", "")).strip(),
            "major": str(row.get("major", "")).strip(),
            "grade_year": str(row.get("grade_year", "")).strip(),
        }

        if existing:
            for k, v in payload.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(Student(student_no=student_no, **payload))
            inserted += 1

    db.commit()
    return _result(len(df), inserted, updated, skipped, errors)


def import_exam_scores(db: Session, file: UploadFile) -> dict[str, Any]:
    df = _read_tabular_file(file)
    required = {"student_no", "course_id", "exam_type", "total_score"}
    if not required.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Missing required columns: {sorted(required)}")

    student_map = {item.student_no: item.id for item in db.query(Student).all()}
    inserted = updated = skipped = 0
    errors: list[str] = []

    for idx, row in enumerate(df.to_dict(orient="records"), start=1):
        student_no = str(row.get("student_no", "")).strip()
        student_id = student_map.get(student_no)
        if not student_id:
            skipped += 1
            errors.append(f"row {idx}: student_no not found {student_no}")
            continue

        course_id = int(row.get("course_id"))
        exam_type = str(row.get("exam_type", "final")).strip()
        exam = (
            db.query(Exam)
            .filter(Exam.course_id == course_id, Exam.exam_type == exam_type)
            .order_by(Exam.date.desc())
            .first()
        )
        if not exam:
            skipped += 1
            errors.append(f"row {idx}: exam not found for course_id={course_id}, type={exam_type}")
            continue

        score = float(row.get("total_score", 0))
        existing = (
            db.query(StudentExamScore)
            .filter(StudentExamScore.student_id == student_id, StudentExamScore.exam_id == exam.id)
            .first()
        )
        if existing:
            existing.total_score = score
            updated += 1
        else:
            db.add(StudentExamScore(student_id=student_id, exam_id=exam.id, total_score=score))
            inserted += 1

    db.commit()
    return _result(len(df), inserted, updated, skipped, errors)


def import_questions(db: Session, file: UploadFile) -> dict[str, Any]:
    df = _read_tabular_file(file)
    required = {"exam_id", "qno", "qtype", "score"}
    if not required.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Missing required columns: {sorted(required)}")

    inserted = updated = skipped = 0
    errors: list[str] = []

    for idx, row in enumerate(df.to_dict(orient="records"), start=1):
        try:
            exam_id = int(row.get("exam_id"))
        except Exception:
            skipped += 1
            errors.append(f"row {idx}: invalid exam_id")
            continue

        qno = str(row.get("qno", "")).strip()
        if not qno:
            skipped += 1
            errors.append(f"row {idx}: empty qno")
            continue

        payload = {
            "qtype": str(row.get("qtype", "")).strip(),
            "score": float(row.get("score", 0)),
            "section": (str(row.get("section")).strip() if pd.notna(row.get("section")) else None),
            "knowledge_point": (
                str(row.get("knowledge_point")).strip() if pd.notna(row.get("knowledge_point")) else None
            ),
            "co_code": (str(row.get("co_code")).strip() if pd.notna(row.get("co_code")) else None),
            "indicator_code": (
                str(row.get("indicator_code")).strip() if pd.notna(row.get("indicator_code")) else None
            ),
        }

        existing = db.query(Question).filter(Question.exam_id == exam_id, Question.qno == qno).first()
        if existing:
            for k, v in payload.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(Question(exam_id=exam_id, qno=qno, **payload))
            inserted += 1

    db.commit()
    return _result(len(df), inserted, updated, skipped, errors)


def import_question_scores(db: Session, file: UploadFile) -> dict[str, Any]:
    df = _read_tabular_file(file)
    required_any = ({"student_no", "question_id", "score"}, {"student_no", "exam_id", "qno", "score"})
    if not any(required.issubset(df.columns) for required in required_any):
        raise HTTPException(
            status_code=400,
            detail="Columns must include either [student_no,question_id,score] or [student_no,exam_id,qno,score]",
        )

    student_map = {item.student_no: item.id for item in db.query(Student).all()}
    inserted = updated = skipped = 0
    errors: list[str] = []

    for idx, row in enumerate(df.to_dict(orient="records"), start=1):
        student_no = str(row.get("student_no", "")).strip()
        student_id = student_map.get(student_no)
        if not student_id:
            skipped += 1
            errors.append(f"row {idx}: student not found")
            continue

        question_id = row.get("question_id")
        if pd.isna(question_id) or question_id is None:
            exam_id = row.get("exam_id")
            qno = row.get("qno")
            if pd.isna(exam_id) or pd.isna(qno):
                skipped += 1
                errors.append(f"row {idx}: missing question locator")
                continue
            question = db.query(Question).filter(Question.exam_id == int(exam_id), Question.qno == str(qno)).first()
            if not question:
                skipped += 1
                errors.append(f"row {idx}: question not found")
                continue
            question_id = question.id

        score = float(row.get("score", 0))
        existing = (
            db.query(StudentQuestionScore)
            .filter(StudentQuestionScore.student_id == student_id, StudentQuestionScore.question_id == int(question_id))
            .first()
        )
        if existing:
            existing.score = score
            updated += 1
        else:
            db.add(StudentQuestionScore(student_id=student_id, question_id=int(question_id), score=score))
            inserted += 1

    db.commit()
    return _result(len(df), inserted, updated, skipped, errors)
