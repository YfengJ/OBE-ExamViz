from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.models.analysis_run import AnalysisRun
from backend.app.models.assessment_component import AssessmentComponent
from backend.app.models.exam import Exam
from backend.app.models.question import Question
from backend.app.models.student import Student
from backend.app.models.student_component_score import StudentComponentScore
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


def _normalize_columns(df: pd.DataFrame, alias_map: dict[str, str]) -> pd.DataFrame:
    renamed = {}
    for column in df.columns:
        key = str(column).strip()
        renamed[column] = alias_map.get(key, key)
    return df.rename(columns=renamed)


def _get_run(db: Session, run_id: int | None) -> AnalysisRun | None:
    if not run_id:
        return None
    return db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()


def _get_or_create_component(db: Session, course_id: int, name: str, weight: float) -> AssessmentComponent:
    component = (
        db.query(AssessmentComponent)
        .filter(AssessmentComponent.course_id == course_id, AssessmentComponent.name == name)
        .first()
    )
    if component:
        return component
    component = AssessmentComponent(course_id=course_id, name=name, weight=weight)
    db.add(component)
    db.commit()
    db.refresh(component)
    return component


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
    df = _normalize_columns(
        df,
        {
            "题号": "qno",
            "题型": "qtype",
            "分值": "score",
            "章节": "section",
            "知识点": "knowledge_point",
            "课程目标": "co_code",
            "指标点": "indicator_code",
            "题组": "qgroup_name",
            "题型分组": "qgroup_name",
            "小题号": "sub_qno",
            "课程目标权重": "co_weight",
            "达成阈值": "expected_threshold",
            "考试ID": "exam_id",
        },
    )
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
            "qgroup_name": (str(row.get("qgroup_name")).strip() if pd.notna(row.get("qgroup_name")) else None),
            "sub_qno": (str(row.get("sub_qno")).strip() if pd.notna(row.get("sub_qno")) else None),
            "score": float(row.get("score", 0)),
            "section": (str(row.get("section")).strip() if pd.notna(row.get("section")) else None),
            "knowledge_point": (
                str(row.get("knowledge_point")).strip() if pd.notna(row.get("knowledge_point")) else None
            ),
            "co_code": (str(row.get("co_code")).strip() if pd.notna(row.get("co_code")) else None),
            "indicator_code": (
                str(row.get("indicator_code")).strip() if pd.notna(row.get("indicator_code")) else None
            ),
            "co_weight": float(row.get("co_weight", 0) or 0),
            "expected_threshold": float(row.get("expected_threshold", 0.65) or 0.65),
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


def import_question_scores(
    db: Session,
    file: UploadFile,
    run_id: int | None = None,
    exam_id: int | None = None,
) -> dict[str, Any]:
    return _import_question_scores(db, file, run_id=run_id, exam_id=exam_id)


def _import_question_scores(
    db: Session,
    file: UploadFile,
    run_id: int | None = None,
    exam_id: int | None = None,
) -> dict[str, Any]:
    df = _read_tabular_file(file)
    df = _normalize_columns(
        df,
        {
            "学号": "student_no",
            "题号": "qno",
            "考试ID": "exam_id",
            "题目ID": "question_id",
            "得分": "score",
        },
    )
    run = _get_run(db, run_id)
    target_exam_id = exam_id or (run.exam_id if run else None)

    has_question_id_locator = {"student_no", "question_id", "score"}.issubset(df.columns)
    has_exam_qno_locator = {"student_no", "exam_id", "qno", "score"}.issubset(df.columns)
    has_run_scoped_locator = {"student_no", "qno", "score"}.issubset(df.columns) and target_exam_id is not None
    if not (has_question_id_locator or has_exam_qno_locator or has_run_scoped_locator):
        raise HTTPException(
            status_code=400,
            detail=(
                "Columns must include either [student_no,question_id,score], "
                "[student_no,exam_id,qno,score], or [student_no,qno,score] when run_id/exam_id is provided"
            ),
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
            exam_id_value = row.get("exam_id")
            qno = str(row.get("qno", "")).strip()
            if pd.isna(exam_id_value) or exam_id_value is None:
                exam_id_value = target_exam_id
            if pd.isna(exam_id_value) or exam_id_value is None or not qno:
                skipped += 1
                errors.append(f"row {idx}: missing question locator")
                continue
            question = db.query(Question).filter(Question.exam_id == int(exam_id_value), Question.qno == qno).first()
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


def import_component_scores(
    db: Session,
    file: UploadFile,
    component_name: str,
    default_weight: float,
    run_id: int | None = None,
    course_id: int | None = None,
) -> dict[str, Any]:
    df = _read_tabular_file(file)
    df = _normalize_columns(
        df,
        {
            "学号": "student_no",
            "成绩": "score",
            "分数": "score",
            "平时成绩": "score",
            "期中成绩": "score",
            "姓名": "name",
        },
    )
    if not {"student_no", "score"}.issubset(df.columns):
        raise HTTPException(status_code=400, detail="Missing required columns: ['student_no', 'score']")

    run = _get_run(db, run_id)
    target_course_id = course_id or (run.course_id if run else None)
    if not target_course_id:
        raise HTTPException(status_code=400, detail="run_id or course_id is required")

    component = _get_or_create_component(db, target_course_id, component_name, default_weight)
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
        score = float(row.get("score", 0) or 0)
        existing = (
            db.query(StudentComponentScore)
            .filter(StudentComponentScore.student_id == student_id, StudentComponentScore.component_id == component.id)
            .first()
        )
        if existing:
            existing.score = score
            updated += 1
        else:
            db.add(StudentComponentScore(student_id=student_id, component_id=component.id, score=score))
            inserted += 1

    db.commit()
    return _result(len(df), inserted, updated, skipped, errors)


def import_final_scores(
    db: Session,
    file: UploadFile,
    run_id: int | None = None,
    exam_id: int | None = None,
    course_id: int | None = None,
) -> dict[str, Any]:
    df = _read_tabular_file(file)
    df = _normalize_columns(
        df,
        {
            "学号": "student_no",
            "成绩": "total_score",
            "总分": "total_score",
            "期末成绩": "total_score",
            "考试ID": "exam_id",
            "课程ID": "course_id",
        },
    )
    if not {"student_no", "total_score"}.issubset(df.columns):
        raise HTTPException(status_code=400, detail="Missing required columns: ['student_no', 'total_score']")

    run = _get_run(db, run_id)
    target_exam_id = exam_id or (run.exam_id if run else None)
    if not target_exam_id:
        if course_id:
            exam = (
                db.query(Exam)
                .filter(Exam.course_id == course_id, Exam.exam_type == "final")
                .order_by(Exam.date.desc())
                .first()
            )
            target_exam_id = exam.id if exam else None
    if not target_exam_id:
        raise HTTPException(status_code=400, detail="run_id, exam_id, or course_id is required")

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
        total_score = float(row.get("total_score", 0) or 0)
        existing = (
            db.query(StudentExamScore)
            .filter(StudentExamScore.student_id == student_id, StudentExamScore.exam_id == target_exam_id)
            .first()
        )
        if existing:
            existing.total_score = total_score
            updated += 1
        else:
            db.add(StudentExamScore(student_id=student_id, exam_id=target_exam_id, total_score=total_score))
            inserted += 1
    db.commit()
    return _result(len(df), inserted, updated, skipped, errors)


def import_paper_structure(
    db: Session,
    file: UploadFile,
    run_id: int | None = None,
    exam_id: int | None = None,
) -> dict[str, Any]:
    df = _read_tabular_file(file)
    df = _normalize_columns(
        df,
        {
            "考试ID": "exam_id",
            "题号": "qno",
            "题型": "qtype",
            "题组": "qgroup_name",
            "题型分组": "qgroup_name",
            "小题号": "sub_qno",
            "分值": "score",
            "章节": "section",
            "知识点": "knowledge_point",
            "课程目标": "co_code",
            "指标点": "indicator_code",
            "课程目标权重": "co_weight",
            "达成阈值": "expected_threshold",
        },
    )
    target_exam_id = exam_id
    run = _get_run(db, run_id)
    if not target_exam_id and run:
        target_exam_id = run.exam_id
    if target_exam_id and "exam_id" not in df.columns:
        df["exam_id"] = target_exam_id
    return import_questions(db, _dataframe_to_upload(df, file.filename or "paper_structure.xlsx"))


def _dataframe_to_upload(df: pd.DataFrame, filename: str) -> UploadFile:
    buffer = BytesIO()
    if filename.lower().endswith(".csv"):
        df.to_csv(buffer, index=False)
    else:
        df.to_excel(buffer, index=False)
    buffer.seek(0)
    return UploadFile(filename=filename, file=buffer)
