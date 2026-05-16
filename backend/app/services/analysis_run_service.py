from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from backend.app.ai.deepseek_client import DeepSeekClient
from backend.app.core.config import settings
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
from backend.app.services.analysis_service import ensure_seed_data_for_demo
from backend.app.services.report_lineage import (
    build_course_objective_lineage,
    build_data_source_overview,
    build_input_requirements,
    build_report_section_lineage,
    build_transfer_checklist,
)

ROOT_DIR = Path(__file__).resolve().parents[3]
SAMPLE_DIR = ROOT_DIR / "sample_data"
TEACHER_COURSE_PREFIX = "TCHR-"
REPORT_NARRATIVE_CONTENT = "report_narrative"
AI_SUGGESTION_CONTENT = "ai_suggestion"
GENERATION_SOURCE_KEY = "_generation_source"
AI_SUGGESTION_MARKER = "deepseek_ai_suggestion_v3"
AI_SUGGESTION_TEMPLATE_KEY = "_suggestion_template"
AI_SUGGESTION_TEMPLATE_FREE = "free"
AI_SUGGESTION_TEMPLATE_PER_OUTCOME = "per_outcome"


def ensure_teacher_demo_data(db: Session, force: bool = False) -> None:
    if not force and not settings.AUTO_SEED_DEMO_DATA:
        return

    ensure_seed_data_for_demo(db, force=force)
    _seed_all_exam_scores(db)
    _seed_components_and_scores(db)
    _seed_missing_questions(db)
    _seed_obe_outcomes(db)
    _seed_analysis_runs(db)


def list_analysis_runs(db: Session) -> list[dict]:
    ensure_teacher_demo_data(db)
    refresh_all_analysis_runs(db)
    query = db.query(AnalysisRun)
    runs = query.order_by(AnalysisRun.created_at.desc(), AnalysisRun.id.desc()).all()
    return [_serialize_run_overview(db, run) for run in runs]


def create_analysis_run(db: Session, payload) -> dict:
    ensure_teacher_demo_data(db)
    run = AnalysisRun(**payload.model_dump())
    if not run.exam_date:
        exam = db.query(Exam).filter(Exam.id == run.exam_id).first()
        run.exam_date = exam.date if exam else None
    if not run.student_count_expected:
        run.student_count_expected = _count_students(db, run.class_name)
    if not run.student_count_actual:
        run.student_count_actual = _count_exam_students(db, run.exam_id, run.class_name)
    run.status = _calculate_run_status(db, run)
    db.add(run)
    db.commit()
    db.refresh(run)
    refresh_analysis_run(db, run.id)
    db.refresh(run)
    return _serialize_run_overview(db, run)


def get_run_dashboard(db: Session, run_id: int) -> dict:
    ensure_teacher_demo_data(db)
    refresh_analysis_run(db, run_id)
    run = _get_run(db, run_id)
    if not run:
        return {}

    context = _build_run_context(db, run)
    narrative = _build_rule_based_narrative(context)

    return {
        "run": _serialize_run(run),
        "meta": context["meta"],
        "score_stats": context["score_stats"],
        "score_segments": context["score_segments"],
        "difficulty_label": context["difficulty_label"],
        "question_groups": context["question_groups"],
        "question_items": context["question_items"],
        "component_summary": context["component_summary"],
        "course_outcomes": context["course_outcomes"],
        "course_outcome_chart": context["course_outcome_chart"],
        "student_outcomes": context["student_outcomes"],
        "warnings": context["warnings"],
        "narrative_preview": narrative,
    }


def get_run_course_outcomes(db: Session, run_id: int) -> dict:
    ensure_teacher_demo_data(db)
    refresh_analysis_run(db, run_id)
    run = _get_run(db, run_id)
    if not run:
        return {}
    context = _build_run_context(db, run)
    return {
        "run": _serialize_run(run),
        "summary": context["course_outcomes"],
        "students": context["student_outcomes"],
        "chart": context["course_outcome_chart"],
    }


def get_run_data_lineage(db: Session, run_id: int) -> dict:
    ensure_teacher_demo_data(db)
    refresh_analysis_run(db, run_id)
    run = _get_run(db, run_id)
    if not run:
        return {}
    context = _build_run_context(db, run)
    return {
        "run": _serialize_run(run),
        "meta": context["meta"],
        "input_requirements": build_input_requirements(context),
        "data_sources": build_data_source_overview(context),
        "report_sections": build_report_section_lineage(context),
        "course_objectives": build_course_objective_lineage(context),
        "transfer_checklist": build_transfer_checklist(),
    }


def get_run_paper_summary_cache(db: Session, run_id: int) -> dict:
    ensure_teacher_demo_data(db)
    refresh_analysis_run(db, run_id)
    run = _get_run(db, run_id)
    if not run:
        return {}
    context = _build_run_context(db, run)
    cached = _get_generated_content(db, run_id, AI_SUGGESTION_CONTENT)
    fallback_narrative = _build_rule_based_narrative(context)
    has_ai_suggestion = _is_ai_generated_content(cached, fallback_narrative, required_marker=AI_SUGGESTION_MARKER)
    return {
        "run": _serialize_run(run),
        "score_stats": context["score_stats"],
        "difficulty_label": context["difficulty_label"],
        "warnings": context["warnings"],
        "narrative": _strip_generation_metadata(cached.payload) if has_ai_suggestion and cached else None,
        "ai_enabled": has_ai_suggestion,
        "cached": has_ai_suggestion,
        "suggestion_template": _suggestion_template_from_payload(cached.payload if cached else None),
    }


async def get_run_paper_summary(
    db: Session,
    run_id: int,
    *,
    template: str = AI_SUGGESTION_TEMPLATE_FREE,
    force: bool = False,
) -> dict:
    ensure_teacher_demo_data(db)
    refresh_analysis_run(db, run_id)
    run = _get_run(db, run_id)
    if not run:
        return {}
    context = _build_run_context(db, run)
    suggestion_template = _normalize_suggestion_template(template)
    fallback_narrative = _build_rule_based_narrative(context, suggestion_template=suggestion_template)
    cached = _get_generated_content(db, run_id, AI_SUGGESTION_CONTENT)
    if not force and _is_ai_generated_content(cached, fallback_narrative, required_marker=AI_SUGGESTION_MARKER):
        return {
            "run": _serialize_run(run),
            "score_stats": context["score_stats"],
            "difficulty_label": context["difficulty_label"],
            "warnings": context["warnings"],
            "narrative": _strip_generation_metadata(cached.payload),
            "ai_enabled": True,
            "cached": True,
            "suggestion_template": _suggestion_template_from_payload(cached.payload, suggestion_template),
        }

    narrative = fallback_narrative
    ai_client = DeepSeekClient()
    used_ai = False
    try:
        generated = await ai_client.generate_report_narrative(
            meta=context["meta"],
            score_stats=context["score_stats"],
            score_segments=context["score_segments"],
            question_groups=context["question_groups"],
            course_outcomes=context["course_outcomes"],
            warnings=context["warnings"],
            fallback_sections=fallback_narrative,
            suggestion_template=suggestion_template,
        )
        if generated is not fallback_narrative:
            narrative = generated
            used_ai = ai_client.is_configured
    except Exception:
        pass
    payload = _with_generation_marker(narrative, AI_SUGGESTION_MARKER, suggestion_template) if used_ai else narrative
    _save_generated_content(db, run_id, AI_SUGGESTION_CONTENT, payload, used_ai)
    return {
        "run": _serialize_run(run),
        "score_stats": context["score_stats"],
        "difficulty_label": context["difficulty_label"],
        "warnings": context["warnings"],
        "narrative": _strip_generation_metadata(payload),
        "ai_enabled": used_ai,
        "cached": False,
        "suggestion_template": suggestion_template,
    }


def get_cached_run_narrative(db: Session, run_id: int) -> dict:
    ensure_teacher_demo_data(db)
    refresh_analysis_run(db, run_id)
    run = _get_run(db, run_id)
    if not run:
        return {}
    cached = _get_generated_content(db, run_id, REPORT_NARRATIVE_CONTENT)
    ai_client = DeepSeekClient()
    return {
        "run": _serialize_run(run),
        "narrative": cached.payload if cached else None,
        "ai_enabled": bool(cached.ai_enabled) if cached else ai_client.is_configured,
        "cached": bool(cached),
    }


async def get_run_narrative(db: Session, run_id: int) -> dict:
    ensure_teacher_demo_data(db)
    refresh_analysis_run(db, run_id)
    run = _get_run(db, run_id)
    if not run:
        return {}
    context = _build_run_context(db, run)
    cached = _get_generated_content(db, run_id, REPORT_NARRATIVE_CONTENT)
    if cached:
        return {"run": _serialize_run(run), "narrative": cached.payload, "ai_enabled": bool(cached.ai_enabled), "cached": True}

    fallback_narrative = _build_rule_based_narrative(context)
    narrative = fallback_narrative
    ai_client = DeepSeekClient()
    used_ai = False
    try:
        generated = await ai_client.generate_report_narrative(
            meta=context["meta"],
            score_stats=context["score_stats"],
            score_segments=context["score_segments"],
            question_groups=context["question_groups"],
            course_outcomes=context["course_outcomes"],
            warnings=context["warnings"],
            fallback_sections=fallback_narrative,
        )
        if generated is not fallback_narrative:
            narrative = generated
            used_ai = ai_client.is_configured
    except Exception:
        pass
    _save_generated_content(db, run_id, REPORT_NARRATIVE_CONTENT, narrative, used_ai)
    return {"run": _serialize_run(run), "narrative": narrative, "ai_enabled": used_ai, "cached": False}


def get_run_export_context(db: Session, run_id: int) -> dict:
    ensure_teacher_demo_data(db)
    refresh_analysis_run(db, run_id)
    run = _get_run(db, run_id)
    if not run:
        return {}
    context = _build_run_context(db, run)
    fallback_narrative = _build_rule_based_narrative(context)
    cached_ai = _get_generated_content(db, run_id, AI_SUGGESTION_CONTENT)
    cached_report = _get_generated_content(db, run_id, REPORT_NARRATIVE_CONTENT)
    if _is_ai_generated_content(cached_ai, fallback_narrative, required_marker=AI_SUGGESTION_MARKER) and cached_ai:
        narrative = _strip_generation_metadata(cached_ai.payload)
        narrative_source = "ai_suggestion_cache"
    elif cached_report:
        narrative = cached_report.payload
        narrative_source = "report_narrative_cache"
    else:
        narrative = fallback_narrative
        narrative_source = "rule_based"
    context["run"] = _serialize_run(run)
    context["narrative"] = narrative
    context["narrative_source"] = narrative_source
    return context


def _build_run_context(db: Session, run: AnalysisRun) -> dict:
    course = db.query(Course).filter(Course.id == run.course_id).first()
    exam = db.query(Exam).filter(Exam.id == run.exam_id).first()
    students_df = _students_df(db, run.class_name)
    final_df = _final_scores_df(db, run.exam_id, run.class_name)
    usual_df = _component_scores_df(db, run.course_id, run.class_name, "usual")
    midterm_df = _component_scores_df(db, run.course_id, run.class_name, "midterm")
    questions = (
        db.query(Question)
        .filter(Question.exam_id == run.exam_id)
        .order_by(Question.id.asc())
        .all()
    )
    question_df = _question_scores_df(db, run, questions, final_df)
    student_scores = _student_total_df(students_df, final_df, usual_df, midterm_df, run)
    question_items = _question_items(question_df, questions, final_df)
    question_groups = _question_group_summary(question_df, questions)
    course_outcomes, student_outcomes = _course_outcomes(db, run, question_df, questions, students_df)
    warnings = _warning_rows(student_scores)
    score_stats = _score_stats(final_df)
    outcome_chart = [
        {
            "co_code": item["co_code"],
            "threshold": item["threshold"],
            "achievement": item["achievement"],
        }
        for item in course_outcomes
    ]

    return {
        "meta": {
            "course_name": course.course_name if course else "",
            "course_code": course.course_code if course else "",
            "teacher_name": run.teacher_name or "未填写教师",
            "department": run.department or (course.department if course else ""),
            "major": run.major or (course.major if course else ""),
            "class_name": run.class_name,
            "academic_year": run.academic_year,
            "term_label": run.term_label,
            "exam_name": exam.name if exam else "",
            "exam_date": (run.exam_date or (exam.date if exam else None)).isoformat() if (run.exam_date or (exam.date if exam else None)) else "",
            "student_count_expected": run.student_count_expected,
            "student_count_actual": run.student_count_actual,
        },
        "score_stats": score_stats,
        "score_segments": _segment_rows(final_df),
        "difficulty_label": _difficulty_label(final_df, exam.total_score if exam else 100.0),
        "question_items": question_items,
        "question_groups": question_groups,
        "component_summary": _component_summary(student_scores, run),
        "course_outcomes": course_outcomes,
        "course_outcome_chart": outcome_chart,
        "student_outcomes": student_outcomes,
        "warnings": warnings,
        "student_scores": student_scores.to_dict(orient="records"),
        "question_records": question_df.to_dict(orient="records"),
    }


def refresh_analysis_run(db: Session, run_id: int) -> None:
    run = _get_run(db, run_id)
    if not run:
        return
    course = db.query(Course).filter(Course.id == run.course_id).first()
    if course:
        run.department = run.department or course.department
        run.major = run.major or course.major
        run.term_label = run.term_label or course.term
    actual = _count_exam_students(db, run.exam_id, run.class_name)
    if course and str(course.course_code or "").startswith(TEACHER_COURSE_PREFIX):
        run.student_count_actual = actual
        run.student_count_expected = run.student_count_expected or actual
    else:
        run.student_count_expected = _count_students(db, run.class_name)
        run.student_count_actual = actual
    run.status = _calculate_run_status(db, run)
    db.commit()


def refresh_all_analysis_runs(db: Session) -> None:
    runs = db.query(AnalysisRun).all()
    changed = False
    for run in runs:
        course = db.query(Course).filter(Course.id == run.course_id).first()
        if course and not run.department:
            run.department = course.department
            changed = True
        if course and not run.major:
            run.major = course.major
            changed = True
        actual = _count_exam_students(db, run.exam_id, run.class_name)
        expected = run.student_count_expected or actual if course and str(course.course_code or "").startswith(TEACHER_COURSE_PREFIX) else _count_students(db, run.class_name)
        status = _calculate_run_status(db, run)
        if run.student_count_expected != expected:
            run.student_count_expected = expected
            changed = True
        if run.student_count_actual != actual:
            run.student_count_actual = actual
            changed = True
        if run.status != status:
            run.status = status
            changed = True
    if changed:
        db.commit()


def _students_df(db: Session, class_name: str) -> pd.DataFrame:
    rows = (
        db.query(Student.id, Student.student_no, Student.name, Student.class_name, Student.major)
        .filter(Student.class_name == class_name)
        .order_by(Student.student_no.asc())
        .all()
    )
    return pd.DataFrame(
        [
            {
                "student_id": row.id,
                "student_no": row.student_no,
                "name": row.name or "",
                "class_name": row.class_name,
                "major": row.major,
            }
            for row in rows
        ],
        columns=["student_id", "student_no", "name", "class_name", "major"],
    )


def _final_scores_df(db: Session, exam_id: int, class_name: str) -> pd.DataFrame:
    rows = (
        db.query(Student.id, Student.student_no, StudentExamScore.total_score)
        .join(StudentExamScore, StudentExamScore.student_id == Student.id)
        .filter(Student.class_name == class_name, StudentExamScore.exam_id == exam_id)
        .all()
    )
    return pd.DataFrame(
        [{"student_id": row.id, "student_no": row.student_no, "final_score": _safe_number(row.total_score)} for row in rows],
        columns=["student_id", "student_no", "final_score"],
    )


def _component_scores_df(db: Session, course_id: int, class_name: str, component_name: str) -> pd.DataFrame:
    rows = (
        db.query(Student.id, Student.student_no, StudentComponentScore.score)
        .join(StudentComponentScore, StudentComponentScore.student_id == Student.id)
        .join(AssessmentComponent, AssessmentComponent.id == StudentComponentScore.component_id)
        .filter(Student.class_name == class_name, AssessmentComponent.course_id == course_id, AssessmentComponent.name == component_name)
        .all()
    )
    score_key = f"{component_name}_score"
    return pd.DataFrame(
        [{"student_id": row.id, "student_no": row.student_no, score_key: _safe_number(row.score)} for row in rows],
        columns=["student_id", "student_no", score_key],
    )


def _student_total_df(
    students_df: pd.DataFrame,
    final_df: pd.DataFrame,
    usual_df: pd.DataFrame,
    midterm_df: pd.DataFrame,
    run: AnalysisRun,
) -> pd.DataFrame:
    merged = students_df.merge(final_df, on=["student_id", "student_no"], how="left")
    merged = merged.merge(usual_df, on=["student_id", "student_no"], how="left")
    merged = merged.merge(midterm_df, on=["student_id", "student_no"], how="left")
    if "final_score" not in merged:
        merged["final_score"] = 0.0
    if "usual_score" not in merged:
        merged["usual_score"] = 0.0
    if "midterm_score" not in merged:
        merged["midterm_score"] = 0.0
    merged["final_score"] = merged["final_score"].fillna(0.0)
    merged["usual_score"] = merged["usual_score"].fillna(0.0)
    merged["midterm_score"] = merged["midterm_score"].fillna(0.0)
    merged["course_total_score"] = (
        merged["usual_score"] * run.usual_weight
        + merged["midterm_score"] * run.midterm_weight
        + merged["final_score"] * run.final_weight
    )
    merged["course_total_score"] = merged["course_total_score"].round(2)
    return merged


def _question_scores_df(db: Session, run: AnalysisRun, questions: list[Question], final_df: pd.DataFrame) -> pd.DataFrame:
    if not questions or final_df.empty:
        return pd.DataFrame(columns=["student_id", "student_no", "question_id", "qno", "qtype", "qgroup_name", "co_code", "score", "full_score"])

    question_ids = [item.id for item in questions]
    rows = (
        db.query(Student.id, Student.student_no, StudentQuestionScore.question_id, StudentQuestionScore.score)
        .join(StudentQuestionScore, StudentQuestionScore.student_id == Student.id)
        .filter(Student.class_name == run.class_name, StudentQuestionScore.question_id.in_(question_ids))
        .all()
    )
    question_map = {item.id: item for item in questions}
    df = pd.DataFrame(
        [
            {
                "student_id": row.id,
                "student_no": row.student_no,
                "question_id": row.question_id,
                "qno": question_map[row.question_id].qno,
                "qtype": question_map[row.question_id].qtype,
                "qgroup_name": question_map[row.question_id].qgroup_name or question_map[row.question_id].qtype,
                "co_code": question_map[row.question_id].co_code or "COX",
                "score": _safe_number(row.score),
                "full_score": _safe_number(question_map[row.question_id].score),
            }
            for row in rows
            if row.question_id in question_map
        ]
    )

    expected_rows = len(final_df) * len(questions)
    if expected_rows == 0 or len(df) >= max(1, int(expected_rows * 0.6)):
        return df
    return _synthesized_question_scores(final_df, questions)


def _synthesized_question_scores(final_df: pd.DataFrame, questions: list[Question]) -> pd.DataFrame:
    if final_df.empty or not questions:
        return pd.DataFrame()
    exam_total = sum(max(_safe_number(question.score), 1.0) for question in questions)
    rows: list[dict] = []
    for _, student in final_df.iterrows():
        ratio = min(max(_safe_number(student["final_score"]) / exam_total, 0.2), 0.98)
        digits = "".join(ch for ch in str(student["student_no"]) if ch.isdigit())
        seed = int(digits[-2:]) if len(digits) >= 2 else sum(ord(ch) for ch in str(student["student_no"])) % 97
        for index, question in enumerate(questions):
            modifier = 0.88 + ((seed + index) % 5) * 0.03
            score = min(_safe_number(question.score), max(0.0, round(_safe_number(question.score) * ratio * modifier, 2)))
            rows.append(
                {
                    "student_id": int(student["student_id"]),
                    "student_no": student["student_no"],
                    "question_id": question.id,
                    "qno": question.qno,
                    "qtype": question.qtype,
                    "qgroup_name": question.qgroup_name or question.qtype,
                    "co_code": question.co_code or "COX",
                    "score": score,
                    "full_score": _safe_number(question.score),
                }
            )
    return pd.DataFrame(rows)


def _question_items(question_df: pd.DataFrame, questions: list[Question], final_df: pd.DataFrame) -> list[dict]:
    if not questions:
        return []
    totals = pd.Series(dtype=float)
    if not question_df.empty:
        pivot = question_df.pivot_table(index="student_id", columns="question_id", values="score", aggfunc="mean").fillna(0.0)
        totals = pivot.sum(axis=1)
    question_items: list[dict] = []
    for question in questions:
        rows = question_df[question_df["question_id"] == question.id] if not question_df.empty else pd.DataFrame()
        full_score = max(_safe_number(question.score), 1.0)
        avg_score = _safe_number(rows["score"].mean() if not rows.empty else 0.0)
        pass_rate = _safe_number(((rows["score"] >= full_score * 0.6).sum() / len(rows)) if len(rows) else 0.0)
        difficulty = _safe_number(avg_score / full_score)
        discrimination = 0.0
        if not rows.empty and not totals.empty:
            merged = rows.merge(totals.rename("total_score"), left_on="student_id", right_index=True, how="left")
            if merged["score"].nunique() > 1 and merged["total_score"].nunique() > 1:
                discrimination = _safe_number(merged["score"].corr(merged["total_score"]))
        question_items.append(
            {
                "question_id": question.id,
                "qno": question.qno,
                "qtype": question.qtype,
                "qgroup_name": question.qgroup_name or question.qtype,
                "full_score": round(full_score, 2),
                "avg_score": round(avg_score, 2),
                "difficulty": round(difficulty, 4),
                "discrimination": round(discrimination, 4),
                "pass_rate": round(pass_rate, 4),
            }
        )
    return question_items


def _question_group_summary(question_df: pd.DataFrame, questions: list[Question]) -> list[dict]:
    if not questions:
        return []
    full_map: dict[str, float] = defaultdict(float)
    for question in questions:
        full_map[question.qgroup_name or question.qtype] += _safe_number(question.score)

    grouped = pd.DataFrame()
    if not question_df.empty:
        student_group_scores = question_df.groupby(["student_id", "qgroup_name"], as_index=False)["score"].sum()
        grouped = student_group_scores.groupby("qgroup_name", as_index=False)["score"].mean()
    rows: list[dict] = []
    for group_name, full_score in full_map.items():
        avg_score = 0.0
        if not grouped.empty:
            match = grouped[grouped["qgroup_name"] == group_name]
            avg_score = _safe_number(match["score"].iloc[0] if not match.empty else 0.0)
        rows.append(
            {
                "qgroup_name": group_name,
                "full_score": round(full_score, 2),
                "avg_score": round(avg_score, 2),
                "achievement": round(_safe_number(avg_score / full_score) if full_score else 0.0, 4),
            }
        )
    return rows


def _course_outcomes(
    db: Session,
    run: AnalysisRun,
    question_df: pd.DataFrame,
    questions: list[Question],
    students_df: pd.DataFrame,
) -> tuple[list[dict], list[dict]]:
    if not questions or question_df.empty:
        return [], []
    outcome_map = {
        item.co_code: item
        for item in db.query(OBEOutcome).filter(OBEOutcome.course_id == run.course_id).all()
    }
    question_meta = defaultdict(lambda: {"full_score": 0.0, "supporting_groups": []})
    for question in questions:
        code = question.co_code or "COX"
        question_meta[code]["full_score"] += _safe_number(question.score)
        group_name = question.qgroup_name or question.qtype
        if group_name and group_name not in question_meta[code]["supporting_groups"]:
            question_meta[code]["supporting_groups"].append(group_name)

    summary: list[dict] = []
    student_rows: list[dict] = []
    outcome_scores = (
        question_df.groupby(["student_id", "student_no", "co_code"], as_index=False)["score"].sum()
        .sort_values(["student_no", "co_code"])
    )
    student_name_map = dict(zip(students_df["student_id"], students_df["name"])) if not students_df.empty else {}
    for _, row in outcome_scores.iterrows():
        meta = question_meta[row["co_code"]]
        full_score = max(meta["full_score"], 1.0)
        threshold = _safe_number(outcome_map.get(row["co_code"]).threshold if outcome_map.get(row["co_code"]) else run.outcome_threshold)
        achievement = _safe_number(row["score"] / full_score)
        student_rows.append(
            {
                "student_id": int(row["student_id"]),
                "student_no": row["student_no"],
                "student_name": student_name_map.get(int(row["student_id"]), ""),
                "co_code": row["co_code"],
                "co_score": round(_safe_number(row["score"]), 2),
                "full_score": round(full_score, 2),
                "achievement": round(achievement, 4),
                "threshold": threshold,
                "is_attained": achievement >= threshold,
            }
        )

    summary_df = outcome_scores.groupby("co_code", as_index=False)["score"].mean()
    total_full_score = sum(meta["full_score"] for meta in question_meta.values()) or 1.0
    for _, row in summary_df.iterrows():
        meta = question_meta[row["co_code"]]
        full_score = max(meta["full_score"], 1.0)
        outcome = outcome_map.get(row["co_code"])
        threshold = _safe_number(outcome.threshold if outcome else run.outcome_threshold)
        achievement = _safe_number(row["score"] / full_score)
        weight = _safe_number(meta["full_score"] / total_full_score)
        summary.append(
            {
                "co_code": row["co_code"],
                "co_name": outcome.co_name if outcome else f"课程目标{row['co_code']}",
                "indicator": outcome.indicator if outcome else "",
                "description": outcome.description if outcome else "",
                "full_score": round(full_score, 2),
                "avg_score": round(_safe_number(row["score"]), 2),
                "achievement": round(achievement, 4),
                "threshold": threshold,
                "weight": round(weight, 4),
                "result": round(_safe_number(weight * achievement), 4),
                "supporting_groups": list(meta["supporting_groups"]),
            }
        )
    return summary, student_rows


def _warning_rows(student_scores: pd.DataFrame) -> list[dict]:
    warnings: list[dict] = []
    if student_scores.empty:
        return warnings
    for _, row in student_scores.iterrows():
        reasons: list[str] = []
        level = ""
        if _safe_number(row["final_score"]) < 60:
            reasons.append("期末卷面成绩低于60分")
            level = "critical"
        elif _safe_number(row["final_score"]) < 70:
            reasons.append("期末卷面成绩低于70分")
            level = "warning"
        if _safe_number(row["course_total_score"]) < 65:
            reasons.append("课程总评偏低")
            level = level or "warning"
        if not level:
            continue
        warnings.append(
            {
                "student_no": row["student_no"],
                "student_name": row["name"],
                "final_score": round(_safe_number(row["final_score"]), 2),
                "course_total_score": round(_safe_number(row["course_total_score"]), 2),
                "level": level,
                "reasons": reasons,
            }
        )
    return warnings


def _component_summary(student_scores: pd.DataFrame, run: AnalysisRun) -> list[dict]:
    if student_scores.empty:
        return []
    return [
        {
            "component": "平时成绩",
            "weight": run.usual_weight,
            "average_score": round(_safe_number(student_scores["usual_score"].mean()), 2),
        },
        {
            "component": "期中成绩",
            "weight": run.midterm_weight,
            "average_score": round(_safe_number(student_scores["midterm_score"].mean()), 2),
        },
        {
            "component": "期末成绩",
            "weight": run.final_weight,
            "average_score": round(_safe_number(student_scores["final_score"].mean()), 2),
        },
        {
            "component": "课程总评",
            "weight": 1.0,
            "average_score": round(_safe_number(student_scores["course_total_score"].mean()), 2),
        },
    ]


def _score_stats(final_df: pd.DataFrame) -> dict:
    if final_df.empty:
        return {
            "total_students": 0,
            "average_score": 0.0,
            "max_score": 0.0,
            "min_score": 0.0,
            "pass_rate": 0.0,
        }
    scores = final_df["final_score"]
    return {
        "total_students": int(len(scores)),
        "average_score": round(_safe_number(scores.mean()), 2),
        "max_score": round(_safe_number(scores.max()), 2),
        "min_score": round(_safe_number(scores.min()), 2),
        "pass_rate": round(_safe_number((scores >= 60).sum() / len(scores)), 4),
    }


def _segment_rows(final_df: pd.DataFrame) -> list[dict]:
    if final_df.empty:
        return []
    scores = final_df["final_score"]
    total = len(scores) or 1
    buckets = [
        ("90-100", (scores >= 90) & (scores <= 100)),
        ("80-89", (scores >= 80) & (scores < 90)),
        ("70-79", (scores >= 70) & (scores < 80)),
        ("60-69", (scores >= 60) & (scores < 70)),
        ("<60", scores < 60),
    ]
    return [{"label": label, "count": int(mask.sum()), "rate": round(_safe_number(mask.sum() / total), 4)} for label, mask in buckets]


def _difficulty_label(final_df: pd.DataFrame, exam_total: float) -> str:
    if final_df.empty or exam_total <= 0:
        return "未知"
    ratio = _safe_number(final_df["final_score"].mean() / exam_total)
    if ratio >= 0.8:
        return "容易"
    if ratio >= 0.6:
        return "中等"
    return "较难"


def _build_rule_based_narrative(
    context: dict,
    *,
    suggestion_template: str = AI_SUGGESTION_TEMPLATE_FREE,
) -> dict:
    stats = context["score_stats"]
    warnings = context["warnings"]
    top_outcomes = context["course_outcomes"]
    weak = [item for item in top_outcomes if item["achievement"] < item["threshold"]]
    score_segments = context["score_segments"]
    largest_segment = max(score_segments, key=lambda item: item["count"]) if score_segments else {"label": "无数据", "count": 0}
    score_summary = (
        f"本次考试共纳入 {stats['total_students']} 名学生，平均分 {stats['average_score']} 分，"
        f"最高分 {stats['max_score']} 分，最低分 {stats['min_score']} 分，及格率 {round(stats['pass_rate'] * 100, 2)}%。"
        f"学生主要集中在 {largest_segment['label']} 分段，共 {largest_segment['count']} 人，试题整体难度判断为“{context['difficulty_label']}”。"
    )
    support_analysis = "各题型对课程目标的支撑关系清晰，"
    if top_outcomes:
        support_analysis += "其中 " + "、".join(
            [f"{item['co_code']} 达成度 {round(item['achievement'] * 100, 1)}%" for item in top_outcomes]
        ) + "。"
    else:
        support_analysis += "但当前尚未形成有效的课程目标映射数据。"

    if weak:
        attainment_analysis = "学生作答对课程目标的达成存在短板，" + "、".join(
            [f"{item['co_code']} 未达到阈值 {round(item['threshold'] * 100, 1)}%" for item in weak]
        ) + "。"
    else:
        attainment_analysis = "学生作答情况整体能够支撑课程目标达成，主要课程目标均达到预设阈值。"

    improvement_actions = (
        _build_per_outcome_improvement_actions(context)
        if suggestion_template == AI_SUGGESTION_TEMPLATE_PER_OUTCOME
        else _build_improvement_actions(context, weak, warnings)
    )

    return {
        "score_summary": score_summary,
        "support_analysis": support_analysis,
        "attainment_analysis": attainment_analysis,
        "improvement_actions": improvement_actions,
    }


def _build_improvement_actions(context: dict, weak_outcomes: list[dict], warnings: list[dict]) -> str:
    outcomes = context.get("course_outcomes") or []
    question_groups = context.get("question_groups") or []
    score_segments = context.get("score_segments") or []
    largest_segment = max(score_segments, key=lambda item: item.get("count", 0)) if score_segments else {"label": "无数据", "count": 0}
    focus_outcomes = weak_outcomes or sorted(outcomes, key=lambda item: _safe_number(item.get("achievement")))[:2]
    low_groups = _focus_question_groups(question_groups)

    outcome_text = "、".join(
        f"{item.get('co_code') or item.get('co_name')}（达成度{_percent_text(item.get('achievement'))}，"
        f"阈值{_percent_text(item.get('threshold') or 0.65)}，关联{_join_names(item.get('supporting_groups'))}）"
        for item in focus_outcomes
    ) or "达成度相对靠后的课程目标"
    group_text = "、".join(
        f"{item.get('qgroup_name', '相关题型')}得分率{_percent_text(item.get('achievement'))}"
        for item in low_groups
    ) or "低得分题型"
    warning_text = (
        f"{len(warnings)}名重点关注学生"
        if warnings
        else f"成绩集中在{largest_segment.get('label', '中间')}分段的学生"
    )

    return (
        "结合本次成绩分布、题型得分率和课程目标达成情况，后续教学建议从四个方面持续改进："
        f"1）围绕{outcome_text}开展专题复盘，把相关知识点拆成“概念辨析、方法步骤、综合应用”三个层次，"
        "在课堂讲评中用典型错例说明失分原因，并安排同类型变式练习巩固；"
        f"2）针对{group_text}建立小测和课后练习清单，下一轮教学中适当增加课堂即时反馈，"
        "对学生容易混淆的公式、模型、步骤或设计思路进行板书化归纳；"
        f"3）对{warning_text}实施分层辅导，优先安排一对一答疑、错题订正检查和阶段性学习记录，"
        "同时给中高分学生布置拓展题，避免只补低分而忽视能力提升；"
        "4）在期中或单元结束后增加一次阶段性检测，将检测结果与本次薄弱目标对照，形成“讲评、练习、反馈、再检测”的闭环，"
        "并把改进结果记录到下一次试卷分析中，持续跟踪教学策略是否真正改善达成度。"
    )


def _build_per_outcome_improvement_actions(context: dict) -> str:
    outcomes = context.get("course_outcomes") or []
    if not outcomes:
        return _build_improvement_actions(context, [], context.get("warnings") or [])

    course_name = str(context.get("meta", {}).get("course_name") or "本课程")
    question_groups = {str(item.get("qgroup_name") or ""): item for item in context.get("question_groups") or []}
    paragraphs: list[str] = []
    for index, outcome in enumerate(outcomes, start=1):
        co_code = str(outcome.get("co_code") or outcome.get("co_name") or f"CO{index}")
        co_name = str(outcome.get("co_name") or f"课程目标{index}")
        description = str(outcome.get("description") or co_name)
        threshold = _safe_number(outcome.get("threshold") or 0.65)
        achievement = _safe_number(outcome.get("achievement"))
        supporting_groups = [str(value) for value in outcome.get("supporting_groups") or [] if value]
        linked_groups = [question_groups[name] for name in supporting_groups if name in question_groups]
        weakest_group = min(linked_groups, key=lambda item: _safe_number(item.get("achievement"))) if linked_groups else None
        group_text = (
            f"{weakest_group.get('qgroup_name')}得分率{_percent_text(weakest_group.get('achievement'))}"
            if weakest_group
            else f"关联题型{_join_names(supporting_groups)}"
        )
        status_text = "低于阈值，需作为后续改进重点" if achievement < threshold else "已达到阈值，但仍需通过巩固练习保持稳定"
        paragraphs.append(
            f"{index}）{course_name}{co_code}（{description}）达成度{_percent_text(achievement)}，"
            f"阈值{_percent_text(threshold)}，{status_text}。建议围绕{_join_names(supporting_groups)}和{group_text}，"
            "在课堂讲评中先回扣该课程目标对应的核心概念、方法步骤和典型失分点，"
            "再布置同类型分层练习；对低分学生安排错题订正和答疑跟踪，对中高分学生增加综合应用或拓展任务，"
            "并在下一单元通过小测复核该目标的掌握情况。"
        )
    return " ".join(paragraphs)


def _focus_question_groups(question_groups: list[dict]) -> list[dict]:
    if not question_groups:
        return []
    weak_groups = [item for item in question_groups if _safe_number(item.get("achievement")) < 0.65]
    candidates = weak_groups or sorted(question_groups, key=lambda item: _safe_number(item.get("achievement")))[:2]
    return sorted(candidates, key=lambda item: _safe_number(item.get("achievement")))[:3]


def _join_names(values: list[str] | None) -> str:
    names = [str(value) for value in values or [] if value]
    return "、".join(names) if names else "相关题型"


def _percent_text(value) -> str:
    return f"{round(_safe_number(value) * 100, 1)}%"


def _serialize_run_overview(db: Session, run: AnalysisRun) -> dict:
    course = db.query(Course).filter(Course.id == run.course_id).first()
    exam = db.query(Exam).filter(Exam.id == run.exam_id).first()
    return {
        "run": _serialize_run(run),
        "course_name": course.course_name if course else "",
        "exam_name": exam.name if exam else "",
        "progress": {
            "has_students": _count_students(db, run.class_name) > 0,
            "has_final_scores": _count_exam_students(db, run.exam_id, run.class_name) > 0,
            "has_questions": db.query(Question.id).filter(Question.exam_id == run.exam_id).count() > 0,
            "has_component_scores": _count_component_scores(db, run.course_id, run.class_name) > 0,
        },
    }


def _serialize_run(run: AnalysisRun) -> dict:
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
        "exam_date": run.exam_date.isoformat() if isinstance(run.exam_date, date) else None,
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


def _get_run(db: Session, run_id: int) -> AnalysisRun | None:
    return db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()


def _get_generated_content(db: Session, run_id: int, content_type: str) -> GeneratedContent | None:
    return (
        db.query(GeneratedContent)
        .filter(GeneratedContent.run_id == run_id, GeneratedContent.content_type == content_type)
        .first()
    )


def _save_generated_content(db: Session, run_id: int, content_type: str, payload: dict, ai_enabled: bool) -> GeneratedContent:
    record = _get_generated_content(db, run_id, content_type)
    if record:
        record.payload = payload
        record.ai_enabled = ai_enabled
    else:
        record = GeneratedContent(run_id=run_id, content_type=content_type, payload=payload, ai_enabled=ai_enabled)
        db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _is_ai_generated_content(
    record: GeneratedContent | None,
    fallback_payload: dict | None = None,
    required_marker: str | None = None,
) -> bool:
    if not record or not record.ai_enabled:
        return False
    payload = record.payload or {}
    if required_marker and payload.get(GENERATION_SOURCE_KEY) != required_marker:
        return False
    if fallback_payload is not None and _strip_generation_metadata(payload) == fallback_payload:
        return False
    return True


def _normalize_suggestion_template(value: str | None) -> str:
    if value == AI_SUGGESTION_TEMPLATE_PER_OUTCOME:
        return AI_SUGGESTION_TEMPLATE_PER_OUTCOME
    return AI_SUGGESTION_TEMPLATE_FREE


def _suggestion_template_from_payload(payload: dict | None, default: str = AI_SUGGESTION_TEMPLATE_FREE) -> str:
    if not payload:
        return default
    return _normalize_suggestion_template(str(payload.get(AI_SUGGESTION_TEMPLATE_KEY) or default))


def _with_generation_marker(
    payload: dict,
    marker: str,
    suggestion_template: str | None = None,
) -> dict:
    data = {**payload, GENERATION_SOURCE_KEY: marker}
    if suggestion_template:
        data[AI_SUGGESTION_TEMPLATE_KEY] = _normalize_suggestion_template(suggestion_template)
    return data


def _strip_generation_metadata(payload: dict | None) -> dict | None:
    if payload is None:
        return None
    return {key: value for key, value in payload.items() if not str(key).startswith("_")}


def _seed_all_exam_scores(db: Session) -> None:
    path = SAMPLE_DIR / "exam_scores.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    student_map = {item.student_no: item.id for item in db.query(Student).all()}
    exam_map = {(item.course_id, item.exam_type): item.id for item in db.query(Exam).all()}
    inserted = False
    for row in df.to_dict(orient="records"):
        student_id = student_map.get(str(row["student_no"]).strip())
        exam_id = exam_map.get((int(row["course_id"]), str(row["exam_type"]).strip()))
        if not student_id or not exam_id:
            continue
        exists = (
            db.query(StudentExamScore.id)
            .filter(StudentExamScore.student_id == student_id, StudentExamScore.exam_id == exam_id)
            .first()
        )
        if exists:
            continue
        db.add(StudentExamScore(student_id=student_id, exam_id=exam_id, total_score=_safe_number(row["total_score"])))
        inserted = True
    if inserted:
        db.commit()


def _seed_components_and_scores(db: Session) -> None:
    courses = db.query(Course).all()
    student_map = {item.student_no: item.id for item in db.query(Student).all()}
    exam_scores = pd.read_csv(SAMPLE_DIR / "exam_scores.csv") if (SAMPLE_DIR / "exam_scores.csv").exists() else pd.DataFrame()
    for course in courses:
        usual = _get_or_create_component(db, course.id, "usual", 0.2)
        midterm = _get_or_create_component(db, course.id, "midterm", 0.2)
        if exam_scores.empty:
            continue
        course_rows = exam_scores[(exam_scores["course_id"] == course.id) & (exam_scores["exam_type"] == "final")]
        for row in course_rows.to_dict(orient="records"):
            student_id = student_map.get(str(row["student_no"]).strip())
            if not student_id:
                continue
            final_score = _safe_number(row["total_score"])
            for component, derived_score in (
                (usual, min(100.0, round(final_score * 0.75 + 18, 2))),
                (midterm, min(100.0, round(final_score * 0.85 + 10, 2))),
            ):
                exists = (
                    db.query(StudentComponentScore.id)
                    .filter(StudentComponentScore.student_id == student_id, StudentComponentScore.component_id == component.id)
                    .first()
                )
                if exists:
                    continue
                db.add(StudentComponentScore(student_id=student_id, component_id=component.id, score=derived_score))
    db.commit()


def _seed_obe_outcomes(db: Session) -> None:
    questions = db.query(Question).all()
    existing = {(item.course_id, item.co_code) for item in db.query(OBEOutcome).all()}
    course_exam_map = {item.id: item.course_id for item in db.query(Exam).all()}
    created = False
    for question in questions:
        co_code = (question.co_code or "").strip()
        if not co_code:
            continue
        course_id = course_exam_map.get(question.exam_id)
        if not course_id or (course_id, co_code) in existing:
            continue
        db.add(
            OBEOutcome(
                course_id=course_id,
                co_code=co_code,
                co_name=f"课程目标{co_code}",
                threshold=_safe_number(question.expected_threshold) or 0.65,
            )
        )
        existing.add((course_id, co_code))
        created = True
    if created:
        db.commit()


def _seed_missing_questions(db: Session) -> None:
    final_exams = db.query(Exam).filter(Exam.exam_type == "final").all()
    blueprint = [
        ("1", "单选题", "单选题", None, 10.0, "第1章", "基础概念", "CO1", "IND1", 0.15, 0.65),
        ("2", "单选题", "单选题", None, 10.0, "第2章", "核心知识", "CO1", "IND1", 0.15, 0.65),
        ("3", "填空题", "填空题", None, 15.0, "第3章", "关键方法", "CO2", "IND2", 0.20, 0.65),
        ("4", "简答题", "简答题", None, 15.0, "第4章", "过程分析", "CO2", "IND2", 0.20, 0.65),
        ("5", "综合题", "综合题", "5-1", 25.0, "第5章", "综合应用", "CO3", "IND3", 0.15, 0.65),
        ("6", "综合题", "综合题", "6-1", 25.0, "第6章", "迁移与优化", "CO4", "IND4", 0.15, 0.65),
    ]
    created = False
    for exam in final_exams:
        if db.query(Question.id).filter(Question.exam_id == exam.id).count() > 0:
            continue
        for qno, qtype, group_name, sub_qno, score, section, kp, co_code, ind_code, co_weight, threshold in blueprint:
            db.add(
                Question(
                    exam_id=exam.id,
                    qno=qno,
                    qtype=qtype,
                    qgroup_name=group_name,
                    sub_qno=sub_qno,
                    score=score,
                    section=section,
                    knowledge_point=kp,
                    co_code=co_code,
                    indicator_code=ind_code,
                    co_weight=co_weight,
                    expected_threshold=threshold,
                )
            )
            created = True
    if created:
        db.commit()


def _seed_analysis_runs(db: Session) -> None:
    if db.query(AnalysisRun.id).count() > 0:
        return
    classes = [item[0] for item in db.query(Student.class_name).distinct().order_by(Student.class_name.asc()).all()]
    final_exams = db.query(Exam).filter(Exam.exam_type == "final").order_by(Exam.course_id.asc()).all()
    created = False
    for exam in final_exams[:6]:
        course = db.query(Course).filter(Course.id == exam.course_id).first()
        if not course:
            continue
        for class_name in classes[:2]:
            expected = _count_students(db, class_name)
            actual = _count_exam_students(db, exam.id, class_name)
            if expected == 0:
                continue
            db.add(
                AnalysisRun(
                    course_id=course.id,
                    exam_id=exam.id,
                    class_name=class_name,
                    academic_year="2025-2026",
                    term_label=course.term,
                    teacher_name="未填写教师",
                    department=course.department,
                    major=course.major,
                    exam_date=exam.date,
                    student_count_expected=expected,
                    student_count_actual=actual,
                    outcome_threshold=0.65,
                    usual_weight=0.2,
                    midterm_weight=0.2,
                    final_weight=0.6,
                    status="ready" if actual else "draft",
                )
            )
            created = True
    if created:
        db.commit()


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


def _count_students(db: Session, class_name: str) -> int:
    return db.query(Student.id).filter(Student.class_name == class_name).count()


def _count_exam_students(db: Session, exam_id: int, class_name: str) -> int:
    return (
        db.query(StudentExamScore.id)
        .join(Student, Student.id == StudentExamScore.student_id)
        .filter(Student.class_name == class_name, StudentExamScore.exam_id == exam_id)
        .count()
    )


def _count_component_scores(db: Session, course_id: int, class_name: str) -> int:
    return (
        db.query(StudentComponentScore.id)
        .join(Student, Student.id == StudentComponentScore.student_id)
        .join(AssessmentComponent, AssessmentComponent.id == StudentComponentScore.component_id)
        .filter(Student.class_name == class_name, AssessmentComponent.course_id == course_id)
        .count()
    )


def _calculate_run_status(db: Session, run: AnalysisRun) -> str:
    has_questions = db.query(Question.id).filter(Question.exam_id == run.exam_id).count() > 0
    has_scores = _count_exam_students(db, run.exam_id, run.class_name) > 0
    if has_questions and has_scores:
        return "ready"
    if has_questions or has_scores:
        return "partial"
    return "draft"


def _safe_number(value) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(number):
        return 0.0
    return number
