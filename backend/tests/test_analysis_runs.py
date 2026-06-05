from __future__ import annotations

import asyncio
import json
from datetime import date
from io import BytesIO

import openpyxl
from docx import Document
from fastapi.testclient import TestClient

from backend.app.ai.deepseek_client import DeepSeekClient
from backend.app.core.database import SessionLocal
from backend.app.core.config import settings
from backend.app.main import app
from backend.app.models.analysis_run import AnalysisRun
from backend.app.models.course import Course
from backend.app.models.exam import Exam
from backend.app.models.generated_content import GeneratedContent
from backend.app.models.obe_outcome import OBEOutcome
from backend.app.models.question import Question
from backend.app.models.student import Student
from backend.app.models.student_exam_score import StudentExamScore
from backend.app.models.student_question_score import StudentQuestionScore
from backend.app.reports.teacher_template_report import _student_outcome_rows_for_target
from backend.app.services.analysis_run_service import (
    AI_SUGGESTION_CONTENT,
    AI_SUGGESTION_MARKER,
    REPORT_CONTEXT_SNAPSHOT_CONTENT,
    _build_rule_based_narrative,
    _sanitize_report_narrative,
    ensure_teacher_demo_data,
    get_run_export_context,
)


def _seed_teacher_data() -> None:
    db = SessionLocal()
    try:
        ensure_teacher_demo_data(db, force=True)
    finally:
        db.close()


def _first_run(client: TestClient) -> dict:
    _seed_teacher_data()
    response = client.get("/api/v1/analysis-runs")
    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert payload["data"]
    return payload["data"][0]


def _clear_generated_content(run_id: int) -> None:
    db = SessionLocal()
    try:
        db.query(GeneratedContent).filter(GeneratedContent.run_id == run_id).delete()
        db.commit()
    finally:
        db.close()


def _create_run_without_question_scores(include_question_scores: bool = False) -> int:
    db = SessionLocal()
    try:
        suffix = db.query(Course).filter(Course.course_code.like("TRUST-NO-QS%")).count() + 1
        course_code = f"TRUST-NO-QS-{suffix}"
        class_name = f"可信测试班{suffix}"
        course = Course(
            course_code=course_code,
            course_name="可信性测试课程",
            term="2025-2026-1",
            department="计算机科学与技术系",
            major="示例专业",
            credit=2,
            owner="示例负责人",
            description="用于验证缺失逐题得分时不合成分析结果。",
        )
        db.add(course)
        db.flush()
        exam = Exam(
            course_id=course.id,
            exam_type="final",
            name="可信性测试课程期末考试",
            date=date(2026, 1, 10),
            total_score=100,
        )
        db.add(exam)
        db.flush()
        db.add_all(
            [
                OBEOutcome(
                    course_id=course.id,
                    co_code="CO1",
                    co_name="课程目标1",
                    indicator="指标点1-1",
                    description="掌握可信性测试课程的基础概念。",
                    threshold=0.65,
                ),
                OBEOutcome(
                    course_id=course.id,
                    co_code="CO2",
                    co_name="课程目标2",
                    indicator="指标点2-1",
                    description="能够完成可信性测试课程的问题分析。",
                    threshold=0.65,
                ),
            ]
        )
        questions = [
            Question(exam_id=exam.id, qno="1", qtype="选择题", qgroup_name="选择题", score=40, co_code="CO1"),
            Question(exam_id=exam.id, qno="2", qtype="综合题", qgroup_name="综合题", score=60, co_code="CO2"),
        ]
        db.add_all(questions)
        students = [
            Student(student_no=f"990{suffix:04d}1", name="学生甲", class_name=class_name, major="示例专业", grade_year="2025"),
            Student(student_no=f"990{suffix:04d}2", name="学生乙", class_name=class_name, major="示例专业", grade_year="2025"),
        ]
        db.add_all(students)
        db.flush()
        db.add_all(
            [
                StudentExamScore(student_id=students[0].id, exam_id=exam.id, total_score=88),
                StudentExamScore(student_id=students[1].id, exam_id=exam.id, total_score=76),
            ]
        )
        if include_question_scores:
            db.add_all(
                [
                    StudentQuestionScore(student_id=students[0].id, question_id=questions[0].id, score=36),
                    StudentQuestionScore(student_id=students[0].id, question_id=questions[1].id, score=52),
                    StudentQuestionScore(student_id=students[1].id, question_id=questions[0].id, score=30),
                    StudentQuestionScore(student_id=students[1].id, question_id=questions[1].id, score=46),
                ]
            )
        run = AnalysisRun(
            course_id=course.id,
            exam_id=exam.id,
            class_name=class_name,
            academic_year="2025-2026学年第一学期",
            term_label="2025-2026-1",
            teacher_name="示例教师",
            department="计算机科学与技术系",
            major="示例专业",
            exam_date=date(2026, 1, 10),
            student_count_expected=2,
            student_count_actual=2,
            status="ready" if include_question_scores else "partial",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run.id
    finally:
        db.close()


def test_analysis_runs_list_and_dashboard() -> None:
    with TestClient(app) as client:
        run = _first_run(client)
        run_id = run["run"]["id"]

        dashboard_response = client.get(f"/api/v1/analysis-runs/{run_id}/dashboard")
        assert dashboard_response.status_code == 200

        dashboard = dashboard_response.json()["data"]
        assert dashboard["score_stats"]["total_students"] >= 0
        assert "course_outcomes" in dashboard
        assert "warnings" in dashboard


def test_analysis_run_does_not_synthesize_missing_question_scores() -> None:
    with TestClient(app) as client:
        run_id = _create_run_without_question_scores()
        response = client.get(f"/api/v1/analysis-runs/{run_id}/dashboard")

    assert response.status_code == 200
    dashboard = response.json()["data"]
    assert dashboard["course_outcomes"] == []
    assert dashboard["student_outcomes"] == []
    assert dashboard["data_quality"]["question_score_rows_actual"] == 0
    assert dashboard["data_quality"]["missing_question_score_rows"] == 4
    assert dashboard["data_quality"]["has_synthesized_question_scores"] is False
    assert any("逐题得分" in issue for issue in dashboard["data_quality"]["issues"])
    assert dashboard["readiness"]["can_generate_report"] is False
    assert "逐题得分" in dashboard["readiness"]["next_action"]["label"]
    assert dashboard["readiness"]["next_action"]["path"] == "/exams"


def test_analysis_run_dashboard_readiness_allows_complete_report_generation() -> None:
    with TestClient(app) as client:
        run_id = _create_run_without_question_scores(include_question_scores=True)
        response = client.get(f"/api/v1/analysis-runs/{run_id}/dashboard")

    assert response.status_code == 200
    readiness = response.json()["data"]["readiness"]
    assert readiness["can_generate_report"] is True
    assert readiness["blocking_errors"] == []
    assert readiness["next_action"]["path"] == "/report-preview"
    assert any(item["key"] == "question_scores" and item["status"] == "ready" for item in readiness["items"])


def test_docx_export_blocks_when_required_data_is_missing() -> None:
    with TestClient(app) as client:
        run_id = _create_run_without_question_scores()
        response = client.get(f"/api/v1/analysis-runs/{run_id}/export/docx")

    assert response.status_code == 400
    assert "逐题得分" in response.json()["detail"]


def test_report_export_context_is_snapshotted_after_first_build() -> None:
    with TestClient(app) as client:
        run_id = _create_run_without_question_scores(include_question_scores=True)
    _clear_generated_content(run_id)
    db = SessionLocal()
    try:
        first_context = get_run_export_context(db, run_id)
        course = db.query(Course).filter(Course.id == first_context["run"]["course_id"]).first()
        assert course is not None
        original_name = first_context["meta"]["course_name"]
        course.course_name = "导出后被修改的课程名称"
        db.commit()

        second_context = get_run_export_context(db, run_id)
        snapshot = (
            db.query(GeneratedContent)
            .filter(GeneratedContent.run_id == run_id, GeneratedContent.content_type == REPORT_CONTEXT_SNAPSHOT_CONTENT)
            .first()
        )
    finally:
        db.close()

    assert snapshot is not None
    assert second_context["meta"]["course_name"] == original_name
    assert second_context["meta"]["course_name"] != "导出后被修改的课程名称"


def test_rule_based_paper_suggestion_is_detailed_and_actionable() -> None:
    context = {
        "meta": {"course_name": "示例课程B", "class_name": "示例班级B", "exam_name": "期末考试"},
        "score_stats": {
            "total_students": 2,
            "average_score": 66.5,
            "max_score": 82,
            "min_score": 51,
            "pass_rate": 0.5,
        },
        "score_segments": [{"label": "60-69", "count": 1, "rate": 0.5}, {"label": "<60", "count": 1, "rate": 0.5}],
        "question_groups": [
            {"qgroup_name": "选择题", "full_score": 20, "avg_score": 15, "achievement": 0.75},
            {"qgroup_name": "建模题", "full_score": 20, "avg_score": 9, "achievement": 0.45},
        ],
        "course_outcomes": [
            {
                "co_code": "CO1",
                "co_name": "课程目标1",
                "achievement": 0.75,
                "threshold": 0.65,
                "supporting_groups": ["选择题"],
            },
            {
                "co_code": "CO2",
                "co_name": "课程目标2",
                "achievement": 0.45,
                "threshold": 0.65,
                "supporting_groups": ["建模题"],
            },
        ],
        "warnings": [{"student_no": "2023001", "reasons": ["期末卷面成绩低于60分"]}],
        "difficulty_label": "中等",
    }

    narrative = _build_rule_based_narrative(context)
    suggestion = narrative["improvement_actions"]

    assert len(suggestion) >= 220
    assert "CO2" in suggestion
    assert "建模题" in suggestion
    assert "1）" in suggestion and "4）" in suggestion
    assert "阶段性" in suggestion


def test_deepseek_report_prompt_uses_anonymized_warning_statistics(monkeypatch) -> None:
    captured: dict[str, str] = {}

    async def fake_chat(self, system_prompt: str, user_prompt: str) -> str:
        captured["user_prompt"] = user_prompt
        return json.dumps(
            {
                "score_summary": "AI 成绩统计摘要",
                "support_analysis": "AI 支撑度分析",
                "attainment_analysis": "AI 达成度分析",
                "improvement_actions": "AI 持续改进建议",
            },
            ensure_ascii=False,
        )

    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(DeepSeekClient, "_chat", fake_chat)

    client = DeepSeekClient()
    asyncio.run(
        client.generate_report_narrative(
            meta={"course_name": "示例课程A", "class_name": "示例班级A", "exam_name": "期末考试"},
            score_stats={"total_students": 2, "average_score": 70, "max_score": 90, "min_score": 50, "pass_rate": 0.5},
            score_segments=[],
            question_groups=[],
            course_outcomes=[],
            warnings=[
                {
                    "student_no": "9900001",
                    "student_name": "学生甲",
                    "final_score": 50,
                    "course_total_score": 58,
                    "level": "critical",
                    "reasons": ["期末卷面成绩低于60分"],
                }
            ],
            fallback_sections={
                "score_summary": "fallback",
                "support_analysis": "fallback",
                "attainment_analysis": "fallback",
                "improvement_actions": "fallback",
            },
        )
    )

    prompt = captured["user_prompt"]
    assert "9900001" not in prompt
    assert "学生甲" not in prompt
    assert "warning_count" in prompt
    assert "期末卷面成绩低于60分" in prompt


def test_deepseek_client_redacts_sensitive_prompt_text() -> None:
    client = DeepSeekClient()
    prompt = client._redact_sensitive_text(
        'student_no: 20231103101, student_name: 张三, 学号：20231103102 姓名：李四。课程代码 CS101。'
    )

    assert "20231103101" not in prompt
    assert "20231103102" not in prompt
    assert "张三" not in prompt
    assert "李四" not in prompt
    assert "CS101" in prompt


def test_report_narrative_redacts_student_identifiers_from_cached_text() -> None:
    context = {
        "warnings": [
            {"student_no": "20251106205", "student_name": "俞入洋"},
            {"student_no": "20251106207", "student_name": "郭金鑫"},
        ],
        "student_scores": [
            {"student_no": "20251106209", "name": "刘庆铎"},
        ],
        "student_outcomes": [],
    }
    narrative = {
        "improvement_actions": "对预警学生（如俞入洋、郭金鑫、20251106209等）进行一对一帮扶，并持续跟踪20251106205。",
    }

    sanitized = _sanitize_report_narrative(narrative, context)
    text = sanitized["improvement_actions"]

    assert "俞入洋" not in text
    assert "郭金鑫" not in text
    assert "刘庆铎" not in text
    assert "20251106205" not in text
    assert "20251106209" not in text
    assert "重点关注学生" in text


def test_analysis_run_data_lineage_explains_input_output_sources() -> None:
    with TestClient(app) as client:
        run = _first_run(client)
        run_id = run["run"]["id"]

        response = client.get(f"/api/v1/analysis-runs/{run_id}/data-lineage")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["input_requirements"]
    assert payload["report_sections"]
    assert payload["course_objectives"]
    assert payload["transfer_checklist"]

    methods = {item["source_method"] for item in payload["report_sections"]}
    assert {"direct_read", "computed", "ai_generated", "rendered_chart"}.issubset(methods)
    assert any("课程目标" in field for item in payload["input_requirements"] for field in item["fields"])
    assert all(item["support_source"] == "question_mapping" for item in payload["course_objectives"])


def test_analysis_run_excel_export_contains_template_sheets() -> None:
    with TestClient(app) as client:
        run_id = _first_run(client)["run"]["id"]
        export_response = client.get(f"/api/v1/analysis-runs/{run_id}/export/excel")

    assert export_response.status_code == 200
    workbook = openpyxl.load_workbook(BytesIO(export_response.content))
    assert "期末成绩单" in workbook.sheetnames
    assert "班级分析主表" in workbook.sheetnames
    assert "课程目标平均分和达成度" in workbook.sheetnames
    assert "课程目标分析图" in workbook.sheetnames


def test_analysis_run_docx_export_returns_docx_package() -> None:
    with TestClient(app) as client:
        run_id = _first_run(client)["run"]["id"]
        export_response = client.get(f"/api/v1/analysis-runs/{run_id}/export/docx")

    assert export_response.status_code == 200
    assert export_response.content[:2] == b"PK"
    document = Document(BytesIO(export_response.content))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    table_text = "\n".join(cell.text for table in document.tables for row in table.rows for cell in row.cells)
    assert "试 卷 分 析 表" in text
    assert "可视化补充页" not in text
    assert "1、试题对课程目标的支撑度分析" in table_text
    assert "课程目标达成度表" in table_text


def test_analysis_run_narrative_contains_required_sections() -> None:
    with TestClient(app) as client:
        run_id = _first_run(client)["run"]["id"]
        narrative_response = client.get(f"/api/v1/analysis-runs/{run_id}/export/narrative")

    assert narrative_response.status_code == 200
    narrative = narrative_response.json()["data"]["narrative"]
    assert narrative["score_summary"]
    assert narrative["support_analysis"]
    assert narrative["attainment_analysis"]
    assert narrative["improvement_actions"]


def test_analysis_run_narrative_is_cached(monkeypatch) -> None:
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "")
    with TestClient(app) as client:
        run_id = _first_run(client)["run"]["id"]
        _clear_generated_content(run_id)

        empty_cache_response = client.get(f"/api/v1/analysis-runs/{run_id}/export/narrative/cache")
        assert empty_cache_response.status_code == 200
        assert empty_cache_response.json()["data"]["narrative"] is None

        generated_response = client.get(f"/api/v1/analysis-runs/{run_id}/export/narrative")
        assert generated_response.status_code == 200
        generated = generated_response.json()["data"]["narrative"]

        cached_response = client.get(f"/api/v1/analysis-runs/{run_id}/export/narrative/cache")
        assert cached_response.status_code == 200
        cached = cached_response.json()["data"]
        assert cached["cached"] is True
        assert cached["narrative"] == generated


def test_analysis_run_ai_suggestion_waits_for_real_generation(monkeypatch) -> None:
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "")
    with TestClient(app) as client:
        run_id = _first_run(client)["run"]["id"]
        _clear_generated_content(run_id)

        empty_cache_response = client.get(f"/api/v1/analysis-runs/{run_id}/paper-summary/cache")
        assert empty_cache_response.status_code == 200
        assert empty_cache_response.json()["data"]["narrative"] is None

        generated_response = client.get(f"/api/v1/analysis-runs/{run_id}/paper-summary")
        assert generated_response.status_code == 200
        assert generated_response.json()["data"]["ai_enabled"] is False

        cached_response = client.get(f"/api/v1/analysis-runs/{run_id}/paper-summary/cache")
        assert cached_response.status_code == 200
        cached = cached_response.json()["data"]
        assert cached["cached"] is False
        assert cached["narrative"] is None


def test_analysis_run_ai_suggestion_ignores_legacy_cached_text() -> None:
    with TestClient(app) as client:
        run_id = _first_run(client)["run"]["id"]
        _clear_generated_content(run_id)
        db = SessionLocal()
        try:
            db.add(
                GeneratedContent(
                    run_id=run_id,
                    content_type="ai_suggestion",
                    ai_enabled=True,
                    payload={
                        "score_summary": "旧缓存摘要",
                        "support_analysis": "旧缓存支撑分析",
                        "attainment_analysis": "旧缓存达成分析",
                        "improvement_actions": "旧缓存持续改进建议",
                    },
                )
            )
            db.commit()
        finally:
            db.close()

        cached_response = client.get(f"/api/v1/analysis-runs/{run_id}/paper-summary/cache")

        assert cached_response.status_code == 200
        cached = cached_response.json()["data"]
        assert cached["cached"] is False
        assert cached["narrative"] is None


def test_analysis_run_ai_suggestion_is_cached_after_ai_generation(monkeypatch) -> None:
    async def fake_generate_report_narrative(self, **kwargs):
        return {
            "score_summary": "AI 成绩统计摘要",
            "support_analysis": "AI 支撑度分析",
            "attainment_analysis": "AI 达成度分析",
            "improvement_actions": "AI 持续改进建议",
        }

    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(DeepSeekClient, "generate_report_narrative", fake_generate_report_narrative)
    with TestClient(app) as client:
        run_id = _first_run(client)["run"]["id"]
        _clear_generated_content(run_id)

        generated_response = client.get(f"/api/v1/analysis-runs/{run_id}/paper-summary")
        assert generated_response.status_code == 200
        generated_data = generated_response.json()["data"]
        assert generated_data["ai_enabled"] is True
        generated = generated_data["narrative"]

        cached_response = client.get(f"/api/v1/analysis-runs/{run_id}/paper-summary/cache")
        assert cached_response.status_code == 200
        cached = cached_response.json()["data"]
        assert cached["cached"] is True
        assert cached["narrative"] == generated


def test_analysis_run_ai_suggestion_supports_per_outcome_template(monkeypatch) -> None:
    captured: dict = {}

    async def fake_generate_report_narrative(self, **kwargs):
        captured.update(kwargs)
        outcome_text = "；".join(
            f"{item['co_code']}：围绕{item.get('description') or item.get('co_name')}开展专项训练"
            for item in kwargs["course_outcomes"]
        )
        return {
            "score_summary": "AI 成绩统计摘要",
            "support_analysis": "AI 支撑度分析",
            "attainment_analysis": "AI 达成度分析",
            "improvement_actions": outcome_text,
        }

    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(DeepSeekClient, "generate_report_narrative", fake_generate_report_narrative)
    with TestClient(app) as client:
        run_id = _first_run(client)["run"]["id"]
        _clear_generated_content(run_id)

        response = client.get(
            f"/api/v1/analysis-runs/{run_id}/paper-summary",
            params={"template": "per_outcome", "force": "true"},
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["ai_enabled"] is True
    assert data["suggestion_template"] == "per_outcome"
    assert captured["suggestion_template"] == "per_outcome"
    for outcome in captured["course_outcomes"]:
        assert outcome["co_code"] in data["narrative"]["improvement_actions"]


def test_analysis_run_ai_suggestion_force_replaces_existing_cache(monkeypatch) -> None:
    async def fake_generate_report_narrative(self, **kwargs):
        return {
            "score_summary": "新 AI 成绩统计摘要",
            "support_analysis": "新 AI 支撑度分析",
            "attainment_analysis": "新 AI 达成度分析",
            "improvement_actions": "新 AI 持续改进建议：按课程目标重新安排训练。",
        }

    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(DeepSeekClient, "generate_report_narrative", fake_generate_report_narrative)
    with TestClient(app) as client:
        run_id = _first_run(client)["run"]["id"]
        _clear_generated_content(run_id)
        db = SessionLocal()
        try:
            db.add(
                GeneratedContent(
                    run_id=run_id,
                    content_type=AI_SUGGESTION_CONTENT,
                    ai_enabled=True,
                    payload={
                        "score_summary": "旧 AI 成绩统计摘要",
                        "support_analysis": "旧 AI 支撑度分析",
                        "attainment_analysis": "旧 AI 达成度分析",
                        "improvement_actions": "旧 AI 持续改进建议",
                        "_generation_source": AI_SUGGESTION_MARKER,
                    },
                )
            )
            db.commit()
        finally:
            db.close()

        response = client.get(
            f"/api/v1/analysis-runs/{run_id}/paper-summary",
            params={"template": "free", "force": "true"},
        )
        cache_response = client.get(f"/api/v1/analysis-runs/{run_id}/paper-summary/cache")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["narrative"]["improvement_actions"].startswith("新 AI")
    assert cache_response.status_code == 200
    cached = cache_response.json()["data"]
    assert cached["cached"] is True
    assert cached["narrative"]["improvement_actions"].startswith("新 AI")


def test_analysis_run_docx_export_uses_cached_ai_suggestion() -> None:
    with TestClient(app) as client:
        run_id = _first_run(client)["run"]["id"]
        _clear_generated_content(run_id)
        unique_suggestion = "这是AI建议独有内容：把低于70分学生纳入三周跟踪清单，并安排一次针对性错题复盘。"
        db = SessionLocal()
        try:
            db.add(
                GeneratedContent(
                    run_id=run_id,
                    content_type=AI_SUGGESTION_CONTENT,
                    ai_enabled=True,
                    payload={
                        "score_summary": "AI 成绩统计摘要",
                        "support_analysis": "AI 支撑度分析",
                        "attainment_analysis": "AI 达成度分析",
                        "improvement_actions": unique_suggestion,
                        "_generation_source": AI_SUGGESTION_MARKER,
                    },
                )
            )
            db.commit()
        finally:
            db.close()

        export_response = client.get(f"/api/v1/analysis-runs/{run_id}/export/docx")

    assert export_response.status_code == 200
    document = Document(BytesIO(export_response.content))
    table_text = "\n".join(cell.text for table in document.tables for row in table.rows for cell in row.cells)
    assert unique_suggestion in table_text


def test_analysis_runs_list_keeps_seed_runs_after_teacher_imported_run_exists() -> None:
    _seed_teacher_data()
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.course_code == "TCHR-REGRESSION").first()
        if not course:
            course = Course(
                course_code="TCHR-REGRESSION",
                course_name="测试导入课",
                term="演示学期",
                department="示例学院",
                major="示例专业",
                credit=2,
                description="回归测试课程",
            )
            db.add(course)
            db.flush()
        exam = db.query(Exam).filter(Exam.course_id == course.id, Exam.name == "测试导入课期末考试").first()
        if not exam:
            exam = Exam(course_id=course.id, exam_type="final", name="测试导入课期末考试", date=date(2026, 1, 10), total_score=100)
            db.add(exam)
            db.flush()
        run = db.query(AnalysisRun).filter(AnalysisRun.course_id == course.id, AnalysisRun.exam_id == exam.id).first()
        if not run:
            db.add(
                AnalysisRun(
                    course_id=course.id,
                    exam_id=exam.id,
                    class_name="示例测试班级",
                    academic_year="演示学期",
                    term_label="演示学期",
                    teacher_name="测试教师",
                    department="示例学院",
                    major="示例专业",
                    status="draft",
                )
            )
        db.commit()
    finally:
        db.close()

    with TestClient(app) as client:
        response = client.get("/api/v1/analysis-runs")

    assert response.status_code == 200
    course_names = {item["course_name"] for item in response.json()["data"]}
    assert "测试导入课" in course_names
    assert {"示例课程A", "示例课程B", "示例课程F"}.issubset(course_names)

    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.course_code == "TCHR-REGRESSION").first()
        if course:
            exam_ids = [item[0] for item in db.query(Exam.id).filter(Exam.course_id == course.id).all()]
            if exam_ids:
                db.query(AnalysisRun).filter(AnalysisRun.exam_id.in_(exam_ids)).delete(synchronize_session=False)
                db.query(Exam).filter(Exam.id.in_(exam_ids)).delete(synchronize_session=False)
            db.delete(course)
            db.commit()
    finally:
        db.close()


def test_create_course_from_syllabus_extracts_basic_info_and_outcomes() -> None:
    document = Document()
    document.add_paragraph("课程代码：DEMO-204")
    document.add_paragraph("课程名称：示例课程D")
    document.add_paragraph("开课单位：示例学院")
    document.add_paragraph("适用专业：示例专业")
    document.add_paragraph("开设学期：演示学期")
    document.add_paragraph("学时/学分：64/3.5")
    document.add_paragraph("课程负责人：示例负责人")
    document.add_paragraph("二、课程简介")
    document.add_paragraph("本课程用于演示课程简介的自动提取能力。")
    document.add_paragraph("三、课程目标")
    document.add_paragraph("课程目标1：理解示例课程D的基本概念和方法。")
    document.add_paragraph("课程目标2：能够分析示例问题并选择合适方案。")
    document.add_paragraph("（二）课程目标对毕业要求指标点的支撑关系")
    document.add_paragraph("课程目标10：这行属于后续支撑关系说明，不应被识别为新的课程目标。")
    stream = BytesIO()
    document.save(stream)
    stream.seek(0)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/analysis/courses/from-syllabus",
            files={
                "file": (
                    "示例课程D教学大纲.docx",
                    stream.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 200
    payload = response.json()["data"]
    course = payload["course"]
    assert course["course_code"] == "DEMO-204"
    assert course["course_name"] == "示例课程D"
    assert course["owner"] == "示例负责人"
    assert course["credit"] == 3.5
    assert "演示课程简介" in course["description"]
    assert len(payload["outcomes"]) == 2
    assert payload["outcomes"][0]["co_code"] == "CO1"

    db = SessionLocal()
    try:
        created = db.query(Course).filter(Course.course_code == "DEMO-204").first()
        outcomes = db.query(OBEOutcome).filter(OBEOutcome.course_id == created.id).order_by(OBEOutcome.co_code.asc()).all()
    finally:
        db.close()

    assert created is not None
    assert [item.co_code for item in outcomes] == ["CO1", "CO2"]


def test_report_chart_matches_course_goal_label_to_co_code() -> None:
    rows = [
        {"student_no": "9000001", "co_code": "CO1", "achievement": 0.8, "threshold": 0.65},
        {"student_no": "9000002", "co_code": "CO2", "achievement": 0.6, "threshold": 0.65},
    ]

    matched = _student_outcome_rows_for_target(rows, "课程目标1", "CO1")

    assert len(matched) == 1
    assert matched[0]["student_no"] == "9000001"


def test_teacher_import_endpoints_refresh_run_snapshot() -> None:
    with TestClient(app) as client:
        run = _first_run(client)
        run_id = run["run"]["id"]
        exam_id = run["run"]["exam_id"]

        final_scores = "student_no,total_score\n9000001,88\n9000002,76\n"
        paper_structure = (
            "qno,qtype,qgroup_name,score,co_code,indicator_code,co_weight,expected_threshold\n"
            "1,单选题,选择题,10,CO1,IND1,0.1,0.65\n"
        )
        question_scores = f"student_no,exam_id,qno,score\n9000001,{exam_id},1,8\n"

        final_response = client.post(
            "/api/v1/import/final-scores",
            files={"file": ("final_scores.csv", final_scores.encode("utf-8"), "text/csv")},
            data={"run_id": str(run_id)},
        )
        assert final_response.status_code == 200
        assert final_response.json()["data"]["inserted"] + final_response.json()["data"]["updated"] >= 1

        structure_response = client.post(
            "/api/v1/import/paper-structure",
            files={"file": ("paper_structure.csv", paper_structure.encode("utf-8"), "text/csv")},
            data={"run_id": str(run_id)},
        )
        assert structure_response.status_code == 200
        assert structure_response.json()["data"]["inserted"] + structure_response.json()["data"]["updated"] >= 1

        question_response = client.post(
            "/api/v1/import/question-scores",
            files={"file": ("question_scores.csv", question_scores.encode("utf-8"), "text/csv")},
            data={"run_id": str(run_id)},
        )
        assert question_response.status_code == 200
        assert question_response.json()["data"]["inserted"] + question_response.json()["data"]["updated"] >= 1

        dashboard_response = client.get(f"/api/v1/analysis-runs/{run_id}/dashboard")
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()["data"]
        assert dashboard["run"]["student_count_actual"] >= 1


def test_question_scores_import_uses_run_context_without_exam_id() -> None:
    with TestClient(app) as client:
        run = _first_run(client)
        run_id = run["run"]["id"]

        paper_structure = (
            "qno,qtype,qgroup_name,score,co_code,indicator_code,co_weight,expected_threshold\n"
            "9,单选题,选择题,10,CO1,IND1,0.1,0.65\n"
        )
        structure_response = client.post(
            "/api/v1/import/paper-structure",
            files={"file": ("paper_structure.csv", paper_structure.encode("utf-8"), "text/csv")},
            data={"run_id": str(run_id)},
        )
        assert structure_response.status_code == 200

        question_scores = "student_no,qno,score\n9000001,9,8\n"
        question_response = client.post(
            "/api/v1/import/question-scores",
            files={"file": ("question_scores.csv", question_scores.encode("utf-8"), "text/csv")},
            data={"run_id": str(run_id)},
        )
        assert question_response.status_code == 200
        payload = question_response.json()["data"]
        assert payload["inserted"] + payload["updated"] >= 1
