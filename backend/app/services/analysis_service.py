from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.models.exam import Exam
from backend.app.models.obe_outcome import OBEOutcome
from backend.app.models.question import Question
from backend.app.models.student import Student
from backend.app.models.student_exam_score import StudentExamScore
from backend.app.models.student_question_score import StudentQuestionScore

ROOT_DIR = Path(__file__).resolve().parents[3]
SAMPLE_DIR = ROOT_DIR / "sample_data"


def _safe_float(value: float | int | None) -> float:
    if value is None:
        return 0.0
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(number):
        return 0.0
    return number


def _load_sample_exam_scores(course_id: int) -> pd.DataFrame:
    path = SAMPLE_DIR / "exam_scores.csv"
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    return df[df["course_id"] == course_id].copy()


def get_course_score_dataframe(db: Session, course_id: int) -> pd.DataFrame:
    rows = (
        db.query(Student.student_no, Student.class_name, StudentExamScore.total_score)
        .join(StudentExamScore, Student.id == StudentExamScore.student_id)
        .join(Exam, Exam.id == StudentExamScore.exam_id)
        .filter(Exam.course_id == course_id, Exam.exam_type == "final")
        .all()
    )

    if rows:
        return pd.DataFrame(
            [
                {
                    "student_no": row.student_no,
                    "class_name": row.class_name,
                    "total_score": _safe_float(row.total_score),
                }
                for row in rows
            ]
        )

    fallback = _load_sample_exam_scores(course_id)
    if fallback.empty:
        return fallback

    students = db.query(Student.student_no, Student.class_name).all()
    mapping = {item.student_no: item.class_name for item in students}
    fallback["class_name"] = fallback["student_no"].map(mapping).fillna("Unknown")
    fallback["total_score"] = fallback["total_score"].astype(float)
    return fallback


def score_statistics(db: Session, course_id: int, class_name: str | None = None) -> dict:
    df = get_course_score_dataframe(db, course_id)
    if class_name:
        df = df[df["class_name"] == class_name]

    if df.empty:
        return {
            "total_students": 0,
            "average_score": 0,
            "max_score": 0,
            "min_score": 0,
            "pass_rate": 0,
            "score_segments": {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "0-59": 0},
        }

    scores = df["total_score"]
    total = len(scores)
    segments = {
        "90-100": int(((scores >= 90) & (scores <= 100)).sum()),
        "80-89": int(((scores >= 80) & (scores < 90)).sum()),
        "70-79": int(((scores >= 70) & (scores < 80)).sum()),
        "60-69": int(((scores >= 60) & (scores < 70)).sum()),
        "0-59": int((scores < 60).sum()),
    }
    return {
        "total_students": total,
        "average_score": round(float(scores.mean()), 2),
        "max_score": round(float(scores.max()), 2),
        "min_score": round(float(scores.min()), 2),
        "pass_rate": round(float((scores >= 60).sum()) / total if total else 0.0, 4),
        "score_segments": segments,
    }


def score_trend(db: Session, course_id: int) -> list[dict]:
    rows = (
        db.query(Exam.id, Exam.name, Exam.date, StudentExamScore.total_score)
        .join(StudentExamScore, StudentExamScore.exam_id == Exam.id)
        .filter(Exam.course_id == course_id)
        .all()
    )
    if not rows:
        return []

    df = pd.DataFrame(
        [
            {"exam_id": row.id, "exam_name": row.name, "exam_date": row.date, "score": _safe_float(row.total_score)}
            for row in rows
        ]
    )
    grouped = (
        df.groupby(["exam_id", "exam_name", "exam_date"], as_index=False)["score"]
        .mean()
        .sort_values("exam_date")
    )
    return [
        {
            "exam_id": int(row["exam_id"]),
            "exam_name": str(row["exam_name"]),
            "exam_date": str(row["exam_date"]),
            "avg_score": round(float(row["score"]), 2),
        }
        for _, row in grouped.iterrows()
    ]


def question_analysis(db: Session, exam_id: int) -> list[dict]:
    questions = db.query(Question).filter(Question.exam_id == exam_id).order_by(Question.qno.asc()).all()
    if not questions:
        return []

    question_ids = [q.id for q in questions]
    score_rows = (
        db.query(StudentQuestionScore.student_id, StudentQuestionScore.question_id, StudentQuestionScore.score)
        .filter(StudentQuestionScore.question_id.in_(question_ids))
        .all()
    )

    if not score_rows:
        return [
            {
                "question_id": q.id,
                "qno": q.qno,
                "qtype": q.qtype,
                "full_score": _safe_float(q.score),
                "avg_score": 0.0,
                "difficulty": 1.0,
                "discrimination": 0.0,
                "pass_rate": 0.0,
            }
            for q in questions
        ]

    df = pd.DataFrame(
        [
            {
                "student_id": row.student_id,
                "question_id": row.question_id,
                "score": _safe_float(row.score),
            }
            for row in score_rows
        ]
    )

    pivot = df.pivot_table(index="student_id", columns="question_id", values="score", aggfunc="mean").fillna(0)
    total_scores = pivot.sum(axis=1)
    n = len(total_scores)
    high_n = max(1, int(np.ceil(n * 0.27)))
    low_n = max(1, int(np.ceil(n * 0.27)))
    high_idx = total_scores.sort_values(ascending=False).head(high_n).index
    low_idx = total_scores.sort_values(ascending=True).head(low_n).index

    result: list[dict] = []
    for q in questions:
        q_df = df[df["question_id"] == q.id]
        full = max(_safe_float(q.score), 1.0)
        avg = float(q_df["score"].mean()) if not q_df.empty else 0.0
        pass_rate = float((q_df["score"] >= full * 0.6).sum()) / len(q_df) if len(q_df) else 0.0
        difficulty = max(0.0, min(1.0, 1 - (avg / full)))

        high_avg = float(pivot.loc[high_idx, q.id].mean()) if q.id in pivot.columns else 0.0
        low_avg = float(pivot.loc[low_idx, q.id].mean()) if q.id in pivot.columns else 0.0
        discrimination = max(0.0, min(1.0, (high_avg - low_avg) / full))

        result.append(
            {
                "question_id": q.id,
                "qno": q.qno,
                "qtype": q.qtype,
                "full_score": round(full, 2),
                "avg_score": round(avg, 2),
                "difficulty": round(difficulty, 4),
                "discrimination": round(discrimination, 4),
                "pass_rate": round(pass_rate, 4),
            }
        )

    return result


def obe_achievement(db: Session, course_id: int, exam_id: int | None = None) -> list[dict]:
    question_query = db.query(Question).join(Exam, Exam.id == Question.exam_id).filter(Exam.course_id == course_id)
    if exam_id is not None:
        question_query = question_query.filter(Question.exam_id == exam_id)
    questions = question_query.all()

    if not questions:
        return []

    scores = (
        db.query(StudentQuestionScore.question_id, StudentQuestionScore.score)
        .filter(StudentQuestionScore.question_id.in_([q.id for q in questions]))
        .all()
    )
    score_df = pd.DataFrame([{"question_id": s.question_id, "score": _safe_float(s.score)} for s in scores])

    outcomes = db.query(OBEOutcome).filter(OBEOutcome.course_id == course_id).all()
    outcome_map = {item.co_code: item for item in outcomes}
    default_threshold = 0.6

    by_co: dict[str, dict] = {}
    for q in questions:
        code = (q.co_code or "UNMAPPED").strip()
        if code not in by_co:
            outcome = outcome_map.get(code)
            by_co[code] = {
                "co_code": code,
                "co_name": outcome.co_name if outcome else f"Course Outcome {code}",
                "threshold": float(outcome.threshold) if outcome else default_threshold,
                "full_sum": 0.0,
                "actual_sum": 0.0,
            }

        by_co[code]["full_sum"] += _safe_float(q.score)
        if not score_df.empty:
            mean_score = score_df[score_df["question_id"] == q.id]["score"].mean()
            by_co[code]["actual_sum"] += _safe_float(mean_score)

    result = []
    for value in by_co.values():
        full = value.pop("full_sum")
        actual = value.pop("actual_sum")
        achievement = round(_safe_float(actual / full), 4) if full else 0.0
        value["achievement"] = achievement
        result.append(value)

    return sorted(result, key=lambda item: item["co_code"])


def ensure_seed_data_for_demo(db: Session) -> None:
    students_file = SAMPLE_DIR / "students.csv"
    courses_file = SAMPLE_DIR / "courses.csv"
    exams_file = SAMPLE_DIR / "exams.csv"
    questions_file = SAMPLE_DIR / "questions.csv"

    if not students_file.exists() or not courses_file.exists() or not exams_file.exists():
        return

    students_df = pd.read_csv(students_file)
    for row in students_df.to_dict(orient="records"):
        student_no = str(row["student_no"]).strip()
        if not student_no:
            continue
        exists = db.query(Student.id).filter(Student.student_no == student_no).first()
        if exists:
            continue
        db.add(
            Student(
                student_no=student_no,
                name=row.get("name") if pd.notna(row.get("name")) else None,
                class_name=str(row["class_name"]).strip(),
                major=str(row["major"]).strip(),
                grade_year=str(row["grade_year"]).strip(),
            )
        )
    db.commit()

    courses_df = pd.read_csv(courses_file)
    for row in courses_df.to_dict(orient="records"):
        course_code = str(row["course_code"]).strip()
        if not course_code:
            continue
        exists = db.query(Course.id).filter(Course.course_code == course_code).first()
        if exists:
            continue
        db.add(
            Course(
                course_code=course_code,
                course_name=str(row["course_name"]).strip(),
                term=str(row["term"]).strip(),
                department=str(row["department"]).strip(),
                major=str(row["major"]).strip(),
                credit=float(row.get("credit", 0.0) or 0.0),
                description=(str(row["description"]).strip() if pd.notna(row.get("description")) else None),
            )
        )
    db.commit()

    exams_df = pd.read_csv(exams_file)
    for row in exams_df.to_dict(orient="records"):
        course_id = int(row["course_id"])
        name = str(row["name"]).strip()
        if not name:
            continue
        exists = db.query(Exam.id).filter(Exam.course_id == course_id, Exam.name == name).first()
        if exists:
            continue
        db.add(
            Exam(
                course_id=course_id,
                exam_type=str(row["exam_type"]).strip(),
                name=name,
                date=pd.to_datetime(row["date"]).date(),
                total_score=float(row.get("total_score", 100)),
            )
        )
    db.commit()

    if questions_file.exists():
        questions_df = pd.read_csv(questions_file)
        for row in questions_df.to_dict(orient="records"):
            exam_id = int(row["exam_id"])
            qno = str(row["qno"]).strip()
            if not qno:
                continue
            exists = db.query(Question.id).filter(Question.exam_id == exam_id, Question.qno == qno).first()
            if exists:
                continue
            db.add(
                Question(
                    exam_id=exam_id,
                    qno=qno,
                    qtype=str(row["qtype"]).strip(),
                    score=float(row.get("score", 0)),
                    section=(str(row["section"]).strip() if pd.notna(row.get("section")) else None),
                    knowledge_point=(str(row["knowledge_point"]).strip() if pd.notna(row.get("knowledge_point")) else None),
                    co_code=(str(row["co_code"]).strip() if pd.notna(row.get("co_code")) else None),
                    indicator_code=(str(row["indicator_code"]).strip() if pd.notna(row.get("indicator_code")) else None),
                )
            )
        db.commit()

    scores_df = _load_sample_exam_scores(course_id=1)
    if not scores_df.empty:
        student_id_map = {s.student_no: s.id for s in db.query(Student).all()}
        exams = db.query(Exam).filter(Exam.course_id == 1, Exam.exam_type == "final").all()
        if exams:
            exam_id = exams[0].id
            for row in scores_df.to_dict(orient="records"):
                sid = student_id_map.get(str(row["student_no"]).strip())
                if sid is None:
                    continue
                exists = (
                    db.query(StudentExamScore.id)
                    .filter(StudentExamScore.student_id == sid, StudentExamScore.exam_id == exam_id)
                    .first()
                )
                if exists:
                    continue
                db.add(StudentExamScore(student_id=sid, exam_id=exam_id, total_score=float(row["total_score"])))
            db.commit()
