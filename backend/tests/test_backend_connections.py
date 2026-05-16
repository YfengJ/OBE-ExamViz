from __future__ import annotations

from datetime import date
import math
from io import BytesIO

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.core.database import SessionLocal
from backend.app.main import app
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
from backend.app.services.analysis_service import ensure_seed_data_for_demo


def _seed_demo_data(client: TestClient) -> None:
    db = SessionLocal()
    try:
        ensure_seed_data_for_demo(db, force=True)
    finally:
        db.close()


def test_obe_achievement_returns_json_safe_numbers() -> None:
    with TestClient(app) as client:
        _seed_demo_data(client)
        response = client.get("/api/v1/analysis/obe-achievement", params={"course_id": 1, "exam_id": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert isinstance(payload["data"], list)
    for row in payload["data"]:
        value = row.get("achievement")
        assert value is None or math.isfinite(float(value))


def test_upload_csv_handles_missing_values() -> None:
    content = "student_no,name,class_name\n2026001,,A1\n2026002,Alice,A1\n"
    files = {"file": ("sample.csv", content.encode("utf-8"), "text/csv")}

    with TestClient(app) as client:
        response = client.post("/api/v1/analysis/upload-csv", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    rows = payload["data"]["rows"]
    assert len(rows) == 2
    assert rows[0]["name"] is None


def test_upload_excel_handles_missing_values() -> None:
    df = pd.DataFrame([{"student_no": "2026001", "name": None, "score": 78.5}])
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    files = {
        "file": (
            "sample.xlsx",
            buffer.read(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/analysis/upload-excel", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    rows = payload["data"]["rows"]
    assert len(rows) == 1
    assert rows[0]["name"] is None


def test_export_score_report_returns_xlsx_file() -> None:
    with TestClient(app) as client:
        _seed_demo_data(client)
        response = client.get("/api/v1/analysis/export-score-report", params={"course_id": 1, "exam_id": 1})

    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
    assert len(response.content) > 0


def test_students_endpoint_accepts_large_frontend_limit() -> None:
    with TestClient(app) as client:
        _seed_demo_data(client)
        response = client.get("/api/v1/analysis/students", params={"limit": 2000})

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200


def test_delete_course_cascades_all_related_course_data() -> None:
    with TestClient(app) as client:
        _seed_demo_data(client)
        db = SessionLocal()
        try:
            course = Course(
                course_code="DEL-CASCADE",
                course_name="可删除课程",
                term="2025-2026-1",
                department="计算机科学与技术系",
                major="示例专业",
                credit=3,
                owner="测试教师",
                description="用于验证课程级联删除",
            )
            student = Student(student_no="20990001", name="删除测试学生", class_name="删除测试班", major="示例专业", grade_year="2099")
            db.add_all([course, student])
            db.flush()

            exam = Exam(course_id=course.id, exam_type="final", name="可删除课程期末考试", date=date(2026, 1, 10), total_score=100)
            component = AssessmentComponent(course_id=course.id, name="平时成绩", weight=0.2)
            outcome = OBEOutcome(course_id=course.id, co_code="CO1", co_name="课程目标1", threshold=0.65)
            warning_rule = WarningRule(course_id=course.id, name="低分预警", level="warning", config_json={"score_lt": 60})
            warning_result = WarningResult(
                student_id=student.id,
                course_id=course.id,
                term=course.term,
                level="warning",
                status="pending",
                reasons_json=["低于60分"],
            )
            db.add_all([exam, component, outcome, warning_rule, warning_result])
            db.flush()

            question = Question(
                exam_id=exam.id,
                qno="1",
                qtype="选择题",
                qgroup_name="选择题",
                score=20,
                co_code="CO1",
                indicator_code="指标点1",
                co_weight=1,
                expected_threshold=0.65,
            )
            run = AnalysisRun(
                course_id=course.id,
                exam_id=exam.id,
                class_name="删除测试班",
                academic_year=course.term,
                term_label=course.term,
                teacher_name="测试教师",
                department=course.department,
                major=course.major,
                exam_date=exam.date,
                student_count_expected=1,
                student_count_actual=1,
                status="ready",
            )
            db.add_all([question, run])
            db.flush()

            db.add_all(
                [
                    StudentExamScore(student_id=student.id, exam_id=exam.id, total_score=80),
                    StudentQuestionScore(student_id=student.id, question_id=question.id, score=16),
                    StudentComponentScore(student_id=student.id, component_id=component.id, score=90),
                    GeneratedContent(run_id=run.id, content_type="ai_suggestion", payload={"text": "建议"}, ai_enabled=False),
                ]
            )
            db.commit()
            course_id = course.id
            exam_id = exam.id
            question_id = question.id
            run_id = run.id
            component_id = component.id
        finally:
            db.close()

        response = client.delete(f"/api/v1/analysis/courses/{course_id}")

    assert response.status_code == 200
    assert response.json()["data"] is True

    db = SessionLocal()
    try:
        assert db.query(Course).filter(Course.id == course_id).first() is None
        assert db.query(Exam).filter(Exam.id == exam_id).first() is None
        assert db.query(Question).filter(Question.id == question_id).first() is None
        assert db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first() is None
        assert db.query(AssessmentComponent).filter(AssessmentComponent.id == component_id).first() is None
        assert db.query(OBEOutcome).filter(OBEOutcome.course_id == course_id).count() == 0
        assert db.query(WarningRule).filter(WarningRule.course_id == course_id).count() == 0
        assert db.query(WarningResult).filter(WarningResult.course_id == course_id).count() == 0
        assert db.query(StudentExamScore).filter(StudentExamScore.exam_id == exam_id).count() == 0
        assert db.query(StudentQuestionScore).filter(StudentQuestionScore.question_id == question_id).count() == 0
        assert db.query(StudentComponentScore).filter(StudentComponentScore.component_id == component_id).count() == 0
        assert db.query(GeneratedContent).filter(GeneratedContent.run_id == run_id).count() == 0
    finally:
        db.close()
