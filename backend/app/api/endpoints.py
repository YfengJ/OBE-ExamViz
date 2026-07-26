from __future__ import annotations

from datetime import UTC, date, datetime
from io import BytesIO

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.ai.deepseek_client import DeepSeekClient
from backend.app.core.database import get_db
from backend.app.models.analysis_run import AnalysisRun
from backend.app.models.assessment_component import AssessmentComponent
from backend.app.models.course import Course
from backend.app.models.exam import Exam
from backend.app.models.generated_content import GeneratedContent
from backend.app.models.obe_outcome import OBEOutcome
from backend.app.models.question import Question
from backend.app.models.student import Student
from backend.app.models.student_component_score import StudentComponentScore
from backend.app.models.student_exam_score import StudentExamScore
from backend.app.models.student_question_score import StudentQuestionScore
from backend.app.models.warning_result import WarningResult
from backend.app.models.warning_rule import WarningRule
from backend.app.reports.excel_report import build_score_report_excel
from backend.app.schemas.course import CourseCreate, CourseUpdate
from backend.app.schemas.exam import ExamCreate, ExamUpdate
from backend.app.schemas.question import QuestionCreate, QuestionUpdate
from backend.app.schemas.student import StudentCreate, StudentUpdate
from backend.app.schemas.warning import WarningGenerateRequest
from backend.app.services.analysis_service import (
    ensure_seed_data_for_demo,
    obe_achievement,
    question_analysis,
    score_trend,
    score_statistics,
)
from backend.app.services.import_service import (
    import_exam_scores,
    import_question_scores,
    import_questions,
    import_students,
)
from backend.app.services.syllabus_service import create_course_from_syllabus
from backend.app.services.warning_service import generate_warnings, list_warnings, update_warning_status
from backend.app.utils.errors import conflict, not_found
from backend.app.utils.response import ok

router = APIRouter()
ai_client = DeepSeekClient()


@router.get("/students")
def get_students(
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=5000),
    class_name: str | None = None,
    db: Session = Depends(get_db),
):
    ensure_seed_data_for_demo(db)
    query = db.query(Student)
    if class_name:
        query = query.filter(Student.class_name == class_name)
    rows = query.offset(skip).limit(limit).all()
    return ok([_student_to_dict(item) for item in rows])


@router.post("/students")
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    item = Student(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise conflict(f"student_no already exists: {payload.student_no}")
    db.refresh(item)
    return ok(_student_to_dict(item))


@router.put("/students/{student_id}")
def update_student(student_id: int, payload: StudentUpdate, db: Session = Depends(get_db)):
    item = db.query(Student).filter(Student.id == student_id).first()
    if not item:
        raise not_found("student", student_id)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return ok(_student_to_dict(item))


@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    item = db.query(Student).filter(Student.id == student_id).first()
    if not item:
        raise not_found("student", student_id)
    _ensure_student_can_delete(db, student_id)
    db.delete(item)
    db.commit()
    return ok(True)


@router.get("/courses")
def get_courses(db: Session = Depends(get_db)):
    ensure_seed_data_for_demo(db)
    rows = db.query(Course).order_by(Course.id.asc()).all()
    return ok([_course_to_dict(item) for item in rows])


@router.post("/courses")
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    item = Course(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise conflict(f"course_code already exists: {payload.course_code}")
    db.refresh(item)
    return ok(_course_to_dict(item))


@router.post("/courses/from-syllabus")
def create_course_from_syllabus_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    result = create_course_from_syllabus(db, file)
    return ok(
        {
            "course": _course_to_dict(result["course"]),
            "outcomes": [_obe_outcome_to_dict(item) for item in result["outcomes"]],
        }
    )


@router.put("/courses/{course_id}")
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)):
    item = db.query(Course).filter(Course.id == course_id).first()
    if not item:
        raise not_found("course", course_id)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return ok(_course_to_dict(item))


@router.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    item = db.query(Course).filter(Course.id == course_id).first()
    if not item:
        raise not_found("course", course_id)
    _delete_course_related_data(db, course_id)
    db.delete(item)
    db.commit()
    return ok(True)


@router.get("/exams")
def get_exams(db: Session = Depends(get_db)):
    ensure_seed_data_for_demo(db)
    rows = db.query(Exam).order_by(Exam.id.asc()).all()
    return ok([_exam_to_dict(item) for item in rows])


@router.post("/exams")
def create_exam(payload: ExamCreate, db: Session = Depends(get_db)):
    item = Exam(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise conflict("exam violates a uniqueness constraint")
    db.refresh(item)
    return ok(_exam_to_dict(item))


@router.put("/exams/{exam_id}")
def update_exam(exam_id: int, payload: ExamUpdate, db: Session = Depends(get_db)):
    item = db.query(Exam).filter(Exam.id == exam_id).first()
    if not item:
        raise not_found("exam", exam_id)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return ok(_exam_to_dict(item))


@router.delete("/exams/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    item = db.query(Exam).filter(Exam.id == exam_id).first()
    if not item:
        raise not_found("exam", exam_id)
    _ensure_exam_can_delete(db, exam_id)
    db.delete(item)
    db.commit()
    return ok(True)


@router.get("/questions")
def get_questions(exam_id: int, db: Session = Depends(get_db)):
    rows = db.query(Question).filter(Question.exam_id == exam_id).order_by(Question.qno.asc()).all()
    return ok([_question_to_dict(item) for item in rows])


@router.post("/questions")
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    item = Question(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return ok(_question_to_dict(item))


@router.put("/questions/{question_id}")
def update_question(question_id: int, payload: QuestionUpdate, db: Session = Depends(get_db)):
    item = db.query(Question).filter(Question.id == question_id).first()
    if not item:
        raise not_found("question", question_id)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return ok(_question_to_dict(item))


@router.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    item = db.query(Question).filter(Question.id == question_id).first()
    if not item:
        raise not_found("question", question_id)
    _ensure_question_can_delete(db, question_id)
    db.delete(item)
    db.commit()
    return ok(True)


@router.get("/score-statistics")
def get_score_statistics(course_id: int, class_name: str | None = None, db: Session = Depends(get_db)):
    ensure_seed_data_for_demo(db)
    return ok(score_statistics(db, course_id=course_id, class_name=class_name))


@router.get("/question-analysis")
def get_question_analysis(exam_id: int, db: Session = Depends(get_db)):
    return ok(question_analysis(db, exam_id=exam_id))


@router.get("/obe-achievement")
def get_obe_achievement(course_id: int, exam_id: int | None = None, db: Session = Depends(get_db)):
    return ok(obe_achievement(db, course_id=course_id, exam_id=exam_id))


@router.get("/warnings")
def get_warnings(
    course_id: int | None = None,
    level: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return ok(list_warnings(db, course_id=course_id, level=level, status=status))


@router.post("/warnings/generate")
def post_generate_warnings(payload: WarningGenerateRequest, db: Session = Depends(get_db)):
    ensure_seed_data_for_demo(db)
    rows = generate_warnings(db, course_id=payload.course_id, term=payload.term)
    return ok(rows)


@router.patch("/warnings/{warning_id}")
def patch_warning_status(warning_id: int, status: str, db: Session = Depends(get_db)):
    row = update_warning_status(db, warning_id=warning_id, status=status)
    if not row:
        raise not_found("warning", warning_id)
    return ok(row)


@router.post("/warnings/{warning_id}/ai-summary")
async def generate_ai_summary(warning_id: int, db: Session = Depends(get_db)):
    warning = db.query(WarningResult).filter(WarningResult.id == warning_id).first()
    if not warning:
        raise not_found("warning", warning_id)

    summary = await ai_client.generate_warning_summary("anonymous", warning.reasons_json)
    warning.ai_summary = summary
    db.commit()
    db.refresh(warning)
    return ok({"id": warning.id, "ai_summary": warning.ai_summary})


@router.post("/warnings/ai-summary/batch")
async def generate_ai_summary_batch(warning_ids: list[int], db: Session = Depends(get_db)):
    updated = 0
    for warning_id in warning_ids:
        warning = db.query(WarningResult).filter(WarningResult.id == warning_id).first()
        if not warning:
            continue
        warning.ai_summary = await ai_client.generate_warning_summary("anonymous", warning.reasons_json)
        updated += 1
    db.commit()
    return ok({"updated": updated})


@router.get("/export-score-report")
def export_score_report(course_id: int, exam_id: int, class_name: str | None = None, db: Session = Depends(get_db)):
    stats = score_statistics(db, course_id=course_id, class_name=class_name)
    question_rows = question_analysis(db, exam_id=exam_id)
    obe_rows = obe_achievement(db, course_id=course_id, exam_id=exam_id)
    trend_rows = score_trend(db, course_id=course_id)
    warning_rows = list_warnings(db, course_id=course_id)
    content = build_score_report_excel(
        stats=stats,
        question_rows=question_rows,
        obe_rows=obe_rows,
        warning_rows=warning_rows,
        trend_rows=trend_rows,
        meta={
            "course_id": course_id,
            "exam_id": exam_id,
            "class_name": class_name or "ALL",
            "generated_at": datetime.now(UTC).isoformat(),
        },
    )
    from urllib.parse import quote
    filename = f"成绩分析报告_{course_id}_{exam_id}.xlsx"
    encoded_filename = quote(filename)

    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"},
    )


@router.get("/score-trend")
def get_score_trend(course_id: int, db: Session = Depends(get_db)):
    ensure_seed_data_for_demo(db)
    return ok(score_trend(db, course_id=course_id))


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    contents = await file.read()
    df = pd.read_csv(BytesIO(contents))
    return ok({"filename": file.filename, "rows": _to_safe_records(df)})


@router.post("/import/students")
def import_students_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return ok(import_students(db, file))


@router.post("/import/exam-scores")
def import_exam_scores_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return ok(import_exam_scores(db, file))


@router.post("/import/questions")
def import_questions_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return ok(import_questions(db, file))


@router.post("/import/question-scores")
def import_question_scores_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return ok(import_question_scores(db, file))


@router.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith((".xlsx", ".xls", ".xlsm")):
        raise HTTPException(status_code=400, detail="Only Excel files are supported")

    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))
    return ok({"filename": file.filename, "rows": _to_safe_records(df)})


def _to_safe_records(df: pd.DataFrame) -> list[dict]:
    cleaned = df.replace([np.inf, -np.inf], np.nan)
    cleaned = cleaned.where(pd.notna(cleaned), None)
    return cleaned.to_dict(orient="records")


def _student_to_dict(item: Student) -> dict:
    return {
        "id": item.id,
        "student_no": item.student_no,
        "name": item.name,
        "class_name": item.class_name,
        "major": item.major,
        "grade_year": item.grade_year,
    }


def _course_to_dict(item: Course) -> dict:
    return {
        "id": item.id,
        "course_code": item.course_code,
        "course_name": item.course_name,
        "term": item.term,
        "department": item.department,
        "major": item.major,
        "credit": item.credit,
        "owner": item.owner,
        "description": item.description,
    }


def _obe_outcome_to_dict(item: OBEOutcome) -> dict:
    return {
        "id": item.id,
        "course_id": item.course_id,
        "co_code": item.co_code,
        "co_name": item.co_name,
        "indicator": item.indicator,
        "description": item.description,
        "threshold": item.threshold,
    }


def _exam_to_dict(item: Exam) -> dict:
    return {
        "id": item.id,
        "course_id": item.course_id,
        "exam_type": item.exam_type,
        "name": item.name,
        "date": item.date.isoformat() if isinstance(item.date, (datetime, date)) else str(item.date),
        "total_score": item.total_score,
    }


def _question_to_dict(item: Question) -> dict:
    return {
        "id": item.id,
        "exam_id": item.exam_id,
        "qno": item.qno,
        "qtype": item.qtype,
        "qgroup_name": item.qgroup_name,
        "sub_qno": item.sub_qno,
        "score": item.score,
        "section": item.section,
        "knowledge_point": item.knowledge_point,
        "co_code": item.co_code,
        "indicator_code": item.indicator_code,
        "co_weight": item.co_weight,
        "expected_threshold": item.expected_threshold,
    }


def _conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=409, detail=detail)


def _ensure_student_can_delete(db: Session, student_id: int) -> None:
    if db.query(StudentExamScore.id).filter(StudentExamScore.student_id == student_id).first():
        raise _conflict("student has exam scores and cannot be deleted")
    if db.query(StudentComponentScore.id).filter(StudentComponentScore.student_id == student_id).first():
        raise _conflict("student has component scores and cannot be deleted")
    if db.query(StudentQuestionScore.id).filter(StudentQuestionScore.student_id == student_id).first():
        raise _conflict("student has question scores and cannot be deleted")
    if db.query(WarningResult.id).filter(WarningResult.student_id == student_id).first():
        raise _conflict("student has warning records and cannot be deleted")


def _delete_course_related_data(db: Session, course_id: int) -> None:
    exam_ids = _scalar_ids(db.query(Exam.id).filter(Exam.course_id == course_id).all())
    question_ids = (
        _scalar_ids(db.query(Question.id).filter(Question.exam_id.in_(exam_ids)).all())
        if exam_ids
        else []
    )
    component_ids = _scalar_ids(db.query(AssessmentComponent.id).filter(AssessmentComponent.course_id == course_id).all())
    run_filter = [AnalysisRun.course_id == course_id]
    if exam_ids:
        run_filter.append(AnalysisRun.exam_id.in_(exam_ids))
    run_ids = _scalar_ids(db.query(AnalysisRun.id).filter(or_(*run_filter)).all())

    if run_ids:
        db.query(GeneratedContent).filter(GeneratedContent.run_id.in_(run_ids)).delete(synchronize_session=False)
        db.query(AnalysisRun).filter(AnalysisRun.id.in_(run_ids)).delete(synchronize_session=False)
    if question_ids:
        db.query(StudentQuestionScore).filter(StudentQuestionScore.question_id.in_(question_ids)).delete(synchronize_session=False)
        db.query(Question).filter(Question.id.in_(question_ids)).delete(synchronize_session=False)
    if exam_ids:
        db.query(StudentExamScore).filter(StudentExamScore.exam_id.in_(exam_ids)).delete(synchronize_session=False)
        db.query(Exam).filter(Exam.id.in_(exam_ids)).delete(synchronize_session=False)
    if component_ids:
        db.query(StudentComponentScore).filter(StudentComponentScore.component_id.in_(component_ids)).delete(
            synchronize_session=False
        )
        db.query(AssessmentComponent).filter(AssessmentComponent.id.in_(component_ids)).delete(synchronize_session=False)

    db.query(OBEOutcome).filter(OBEOutcome.course_id == course_id).delete(synchronize_session=False)
    db.query(WarningRule).filter(WarningRule.course_id == course_id).delete(synchronize_session=False)
    db.query(WarningResult).filter(WarningResult.course_id == course_id).delete(synchronize_session=False)


def _scalar_ids(rows) -> list[int]:
    return [int(row[0]) for row in rows]


def _ensure_exam_can_delete(db: Session, exam_id: int) -> None:
    if db.query(Question.id).filter(Question.exam_id == exam_id).first():
        raise _conflict("exam has questions and cannot be deleted")
    if db.query(StudentExamScore.id).filter(StudentExamScore.exam_id == exam_id).first():
        raise _conflict("exam has student scores and cannot be deleted")
    if db.query(AnalysisRun.id).filter(AnalysisRun.exam_id == exam_id).first():
        raise _conflict("exam is referenced by analysis runs and cannot be deleted")


def _ensure_question_can_delete(db: Session, question_id: int) -> None:
    if db.query(StudentQuestionScore.id).filter(StudentQuestionScore.question_id == question_id).first():
        raise _conflict("question has student scores and cannot be deleted")
