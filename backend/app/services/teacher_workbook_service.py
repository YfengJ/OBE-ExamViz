from __future__ import annotations

import hashlib
import re
from datetime import date
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.app.models.analysis_run import AnalysisRun
from backend.app.models.course import Course
from backend.app.models.exam import Exam
from backend.app.models.obe_outcome import OBEOutcome
from backend.app.models.question import Question
from backend.app.models.student import Student
from backend.app.models.student_exam_score import StudentExamScore
from backend.app.models.student_question_score import StudentQuestionScore
from backend.app.reports.teacher_template_report import (
    enrich_context_with_course_catalog,
    load_teacher_workbook_context,
    preview_teacher_template_workbook,
)
from backend.app.services.analysis_run_service import refresh_analysis_run

TEACHER_COURSE_PREFIX = "TCHR-"
DEFAULT_DEPARTMENT = "计算机科学与技术系"


def import_teacher_workbook_as_run(
    db: Session,
    file: UploadFile,
    exam_date_override: str | None = None,
) -> dict[str, Any]:
    parsed = load_teacher_workbook_context(file, exam_date_override=exam_date_override)
    context = parsed["context"]
    meta = context["meta"]

    course = _upsert_course(db, meta)
    _apply_existing_course_catalog(db, course, context)
    exam = _upsert_exam(db, course, meta, context)
    _rebuild_outcomes(db, course, context)
    question_map = _rebuild_questions(db, exam, context)
    student_map = _upsert_students(db, context)
    _rebuild_final_scores(db, exam, context, student_map)
    _rebuild_question_scores(db, context, student_map, question_map)
    run = _upsert_run(db, course, exam, meta, context)
    refresh_analysis_run(db, run.id)
    db.refresh(run)

    return {
        "preview": preview_teacher_template_workbook(file, exam_date_override=exam_date_override),
        "run_overview": {
            "run": _serialize_run(run),
            "course_name": course.course_name,
            "exam_name": exam.name,
            "progress": {
                "has_students": True,
                "has_final_scores": True,
                "has_questions": bool(question_map),
                "has_component_scores": False,
            },
        },
        "template_binding": {
            "input_template": "teacher_input_template.xlsx",
            "output_template": "teacher_report_template.docx",
        },
    }


def _upsert_course(db: Session, meta: dict[str, Any]) -> Course:
    parsed_course_code = str(meta.get("course_code") or "").strip()
    course = _find_existing_course(db, meta)
    course_code = parsed_course_code or (course.course_code if course else _teacher_course_code(meta.get("course_name"), meta.get("class_name")))
    term = _normalize_term_label(meta.get("academic_year") or (course.term if course else ""))
    payload = {
        "course_code": course_code,
        "course_name": str(meta.get("course_name") or (course.course_name if course else "") or "未命名课程"),
        "term": term,
        "department": str(meta.get("department") or (course.department if course else "") or DEFAULT_DEPARTMENT),
        "major": str((course.major if course else "") or _infer_major(str(meta.get("class_name") or ""))),
        "credit": float((course.credit if course else 0.0) or 0.0),
        "owner": (course.owner if course else None),
        "description": (course.description if course else None) or "成绩工作簿导入",
    }
    if course:
        for key, value in payload.items():
            setattr(course, key, value)
    else:
        course = Course(**payload)
        db.add(course)
        db.flush()
    return course


def _find_existing_course(db: Session, meta: dict[str, Any]) -> Course | None:
    course_code = str(meta.get("course_code") or "").strip()
    if course_code:
        course = db.query(Course).filter(Course.course_code == course_code).first()
        if course:
            return course

    course_name = str(meta.get("course_name") or "").strip()
    if course_name:
        course = db.query(Course).filter(Course.course_name == course_name).order_by(Course.id).first()
        if course:
            return course
    return None


def _apply_existing_course_catalog(db: Session, course: Course, context: dict[str, Any]) -> None:
    meta = context.setdefault("meta", {})
    meta["course_code"] = course.course_code
    meta["course_name"] = meta.get("course_name") or course.course_name
    meta["academic_year"] = _normalize_term_label(meta.get("academic_year") or course.term)
    meta["department"] = meta.get("department") or course.department or DEFAULT_DEPARTMENT
    meta["teacher_name"] = meta.get("teacher_name") or course.owner or ""

    existing_outcomes = (
        db.query(OBEOutcome)
        .filter(OBEOutcome.course_id == course.id)
        .order_by(OBEOutcome.co_code)
        .all()
    )
    if not existing_outcomes:
        return
    catalog = [
        {
            "co_code": item.co_code,
            "co_name": item.co_name,
            "label": item.co_name,
            "indicator": item.indicator or "",
            "description": item.description or "",
            "threshold": item.threshold or 0.65,
        }
        for item in existing_outcomes
    ]
    enrich_context_with_course_catalog(
        context,
        catalog,
        remap_score_only=context.get("input_mode") == "score_only_workbook",
    )


def _upsert_exam(db: Session, course: Course, meta: dict[str, Any], context: dict[str, Any]) -> Exam:
    exam = db.query(Exam).filter(Exam.course_id == course.id, Exam.exam_type == "final").first()
    payload = {
        "course_id": course.id,
        "exam_type": "final",
        "name": f"{course.course_name}期末考试",
        "date": _parse_exam_date(meta.get("exam_date")),
        "total_score": _exam_total_score(context),
    }
    if exam:
        for key, value in payload.items():
            setattr(exam, key, value)
    else:
        exam = Exam(**payload)
        db.add(exam)
        db.flush()
    return exam


def _rebuild_outcomes(db: Session, course: Course, context: dict[str, Any]) -> None:
    existing_outcomes = {
        item.co_code: item
        for item in db.query(OBEOutcome).filter(OBEOutcome.course_id == course.id).all()
    }
    db.query(OBEOutcome).filter(OBEOutcome.course_id == course.id).delete()
    for index, item in enumerate(context.get("course_outcomes") or [], start=1):
        co_code = str(item.get("co_code") or f"CO{index}")
        existing = existing_outcomes.get(co_code)
        db.add(
            OBEOutcome(
                course_id=course.id,
                co_code=co_code,
                co_name=str(item.get("label") or item.get("co_name") or (existing.co_name if existing else "") or f"课程目标{index}"),
                indicator=str(item.get("indicator") or (existing.indicator if existing else "") or "") or None,
                description=str(item.get("description") or (existing.description if existing else "") or "") or None,
                threshold=float(item.get("threshold") or (existing.threshold if existing else 0.65) or 0.65),
            )
        )
    db.flush()


def _rebuild_questions(db: Session, exam: Exam, context: dict[str, Any]) -> dict[str, Question]:
    question_ids = [item[0] for item in db.query(Question.id).filter(Question.exam_id == exam.id).all()]
    if question_ids:
        db.query(StudentQuestionScore).filter(StudentQuestionScore.question_id.in_(question_ids)).delete(
            synchronize_session=False
        )
        db.query(Question).filter(Question.exam_id == exam.id).delete(synchronize_session=False)

    group_to_outcome = _group_to_outcome_map(context)
    outcome_full_scores = {
        str(item.get("co_code") or ""): float(item.get("full_score") or 0)
        for item in context.get("course_outcomes") or []
    }
    outcome_meta = _outcome_meta_map(context)
    question_map: dict[str, Question] = {}
    for index, item in enumerate(context.get("question_items") or [], start=1):
        label = str(item.get("label") or f"题目{index}")
        group_name = str(item.get("qgroup_name") or item.get("label") or f"题型{index}")
        direct_co_code = str(item.get("co_code") or "").strip()
        co_code = (
            direct_co_code
            or group_to_outcome.get(group_name)
            or group_to_outcome.get(_canonical_group_name(group_name))
            or _default_co_code(context, index)
        )
        full_score = float(item.get("full_score") or 0)
        co_total = outcome_full_scores.get(co_code) or full_score or 1.0
        meta = outcome_meta.get(co_code, {})
        question = Question(
            exam_id=exam.id,
            qno=str(index),
            qtype=group_name,
            qgroup_name=group_name,
            sub_qno=_extract_sub_qno(label, group_name),
            score=full_score,
            section="成绩工作簿导入",
            knowledge_point=label,
            co_code=co_code,
            indicator_code=str(meta.get("indicator") or co_code),
            co_weight=round(full_score / co_total, 4),
            expected_threshold=_outcome_threshold(context, co_code),
        )
        db.add(question)
        db.flush()
        question_map[label] = question
    return question_map


def _upsert_students(db: Session, context: dict[str, Any]) -> dict[str, Student]:
    class_name = str(context["meta"].get("class_name") or "未命名班级")
    major = _infer_major(class_name)
    grade_year = _infer_grade_year(class_name)
    student_map: dict[str, Student] = {}
    for item in context.get("students") or []:
        student_no = str(item.get("student_no") or "").strip()
        if not student_no:
            continue
        student = db.query(Student).filter(Student.student_no == student_no).first()
        payload = {
            "name": str(item.get("name") or "").strip() or student_no,
            "class_name": class_name,
            "major": major,
            "grade_year": grade_year,
        }
        if student:
            for key, value in payload.items():
                setattr(student, key, value)
        else:
            student = Student(student_no=student_no, **payload)
            db.add(student)
            db.flush()
        student_map[student_no] = student
    _cleanup_stale_orphan_students(db, class_name, set(student_map))
    return student_map


def _cleanup_stale_orphan_students(db: Session, class_name: str, active_student_nos: set[str]) -> None:
    if not active_student_nos:
        return

    stale_students = (
        db.query(Student)
        .filter(
            Student.class_name == class_name,
            ~Student.student_no.in_(active_student_nos),
            ~Student.exam_scores.any(),
            ~Student.component_scores.any(),
            ~Student.question_scores.any(),
            ~Student.warnings.any(),
        )
        .all()
    )
    for student in stale_students:
        db.delete(student)
    db.flush()


def _rebuild_final_scores(db: Session, exam: Exam, context: dict[str, Any], student_map: dict[str, Student]) -> None:
    db.query(StudentExamScore).filter(StudentExamScore.exam_id == exam.id).delete(synchronize_session=False)

    for item in context.get("students") or []:
        student = student_map.get(str(item.get("student_no") or "").strip())
        if not student:
            continue
        db.add(
            StudentExamScore(
                student_id=student.id,
                exam_id=exam.id,
                total_score=float(item.get("final_score") or 0),
            )
        )
    db.flush()


def _rebuild_question_scores(
    db: Session,
    context: dict[str, Any],
    student_map: dict[str, Student],
    question_map: dict[str, Question],
) -> None:
    for item in context.get("students") or []:
        student = student_map.get(str(item.get("student_no") or "").strip())
        if not student:
            continue
        for label, score in (item.get("question_scores") or {}).items():
            question = question_map.get(label)
            if not question:
                continue
            db.add(StudentQuestionScore(student_id=student.id, question_id=question.id, score=float(score or 0)))
    db.flush()


def _upsert_run(
    db: Session,
    course: Course,
    exam: Exam,
    meta: dict[str, Any],
    context: dict[str, Any],
) -> AnalysisRun:
    class_name = str(meta.get("class_name") or "未命名班级")
    run = (
        db.query(AnalysisRun)
        .filter(
            AnalysisRun.course_id == course.id,
            AnalysisRun.exam_id == exam.id,
            AnalysisRun.class_name == class_name,
        )
        .first()
    )
    payload = {
        "course_id": course.id,
        "exam_id": exam.id,
        "class_name": class_name,
        "academic_year": _normalize_term_label(meta.get("academic_year") or course.term),
        "term_label": _normalize_term_label(meta.get("academic_year") or course.term),
        "teacher_name": str(meta.get("teacher_name") or ""),
        "department": str(meta.get("department") or course.department or DEFAULT_DEPARTMENT),
        "major": str(course.major or _infer_major(class_name)),
        "exam_date": _parse_exam_date(meta.get("exam_date")),
        "student_count_expected": int(meta.get("student_count_expected") or len(context.get("students") or [])),
        "student_count_actual": int(meta.get("student_count_actual") or len(context.get("students") or [])),
        "outcome_threshold": _default_threshold(context),
        "usual_weight": 0.0,
        "midterm_weight": 0.0,
        "final_weight": 1.0,
        "status": "ready",
    }
    if run:
        for key, value in payload.items():
            setattr(run, key, value)
    else:
        run = AnalysisRun(**payload)
        db.add(run)
        db.flush()
    db.commit()
    return run


def _teacher_course_code(course_name: Any, class_name: Any) -> str:
    raw = f"{course_name or ''}|{class_name or ''}".encode("utf-8")
    digest = hashlib.sha1(raw).hexdigest()[:10].upper()
    return f"{TEACHER_COURSE_PREFIX}{digest}"


def _normalize_term_label(value: Any) -> str:
    text = str(value or "").strip()
    return text or "成绩工作簿导入"


def _parse_exam_date(value: Any) -> date:
    text = str(value or "").strip()
    if not text:
        return date.today()
    match = re.search(r"(20\d{2})\D{0,3}(\d{1,2})\D{0,3}(\d{1,2})", text)
    if match:
        year, month, day = (int(part) for part in match.groups())
        try:
            return date(year, month, day)
        except ValueError:
            return date.today()
    return date.today()


def _infer_major(class_name: str) -> str:
    text = class_name.strip()
    return re.sub(r"\d+班?$", "", text).strip() or text or "待补充"


def _infer_grade_year(class_name: str) -> str:
    match = re.search(r"(\d{2})\d{2}班?$", class_name.strip())
    if not match:
        return "未知"
    return f"20{match.group(1)}"


def _exam_total_score(context: dict[str, Any]) -> float:
    total = sum(float(item.get("full_score") or 0) for item in context.get("question_items") or [])
    return round(total or 100.0, 2)


def _group_to_outcome_map(context: dict[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for index, item in enumerate(context.get("course_outcomes") or [], start=1):
        code = str(item.get("co_code") or f"CO{index}")
        for group_name in item.get("supporting_groups") or []:
            mapping[str(group_name)] = code
            mapping[_canonical_group_name(group_name)] = code
    return mapping


def _outcome_meta_map(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("co_code") or ""): item
        for item in context.get("course_outcomes") or []
        if item.get("co_code")
    }


def _default_co_code(context: dict[str, Any], index: int) -> str:
    outcomes = context.get("course_outcomes") or []
    if outcomes:
        return str(outcomes[min(index - 1, len(outcomes) - 1)].get("co_code") or f"CO{index}")
    return f"CO{index}"


def _canonical_group_name(value: Any) -> str:
    text = re.sub(r"\s+", "", str(value or ""))
    text = re.sub(r"\d+(?:\.\d+)?分$", "", text)
    text = text.replace("单选题", "选择题")
    text = text.replace("综合应用", "综合题")
    return text


def _outcome_threshold(context: dict[str, Any], co_code: str) -> float:
    for item in context.get("course_outcomes") or []:
        if str(item.get("co_code") or "") == co_code:
            return float(item.get("threshold") or 0.65)
    return 0.65


def _default_threshold(context: dict[str, Any]) -> float:
    outcomes = context.get("course_outcomes") or []
    if not outcomes:
        return 0.65
    return round(sum(float(item.get("threshold") or 0.65) for item in outcomes) / len(outcomes), 4)


def _extract_sub_qno(label: str, group_name: str) -> str | None:
    suffix = label.replace(group_name, "", 1).strip()
    return suffix or None


def _serialize_run(run: AnalysisRun) -> dict[str, Any]:
    return {
        "id": run.id,
        "course_id": run.course_id,
        "exam_id": run.exam_id,
        "class_name": run.class_name,
        "academic_year": run.academic_year,
        "term_label": run.term_label,
        "teacher_name": run.teacher_name,
        "department": run.department,
        "major": run.major,
        "exam_date": run.exam_date.isoformat() if run.exam_date else None,
        "student_count_expected": run.student_count_expected,
        "student_count_actual": run.student_count_actual,
        "outcome_threshold": run.outcome_threshold,
        "usual_weight": run.usual_weight,
        "midterm_weight": run.midterm_weight,
        "final_weight": run.final_weight,
        "status": run.status,
        "created_at": run.created_at.isoformat() if run.created_at else "",
        "updated_at": run.updated_at.isoformat() if run.updated_at else "",
    }
