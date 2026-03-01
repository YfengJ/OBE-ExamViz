from __future__ import annotations

from io import BytesIO

import pandas as pd


def build_score_report_excel(
    stats: dict,
    question_rows: list[dict],
    obe_rows: list[dict],
    warning_rows: list[dict] | None = None,
    trend_rows: list[dict] | None = None,
    meta: dict | None = None,
    sheet_name: str = "final_exam_analysis",
) -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        stats_df = pd.DataFrame([stats])
        question_df = pd.DataFrame(question_rows)
        obe_df = pd.DataFrame(obe_rows)
        warning_df = pd.DataFrame(warning_rows or [])
        trend_df = pd.DataFrame(trend_rows or [])
        meta_df = pd.DataFrame([meta or {}])

        meta_df = meta_df.rename(columns={
            "course_id": "课程ID", "exam_id": "考试ID", "class_name": "班级", "generated_at": "生成时间"
        })
        stats_df = stats_df.rename(columns={
            "total_students": "总人数", "average_score": "平均分", "max_score": "最高分",
            "min_score": "最低分", "pass_rate": "及格率", "score_segments": "分数段"
        })
        trend_df = trend_df.rename(columns={
            "exam_id": "考试ID", "exam_name": "考试名称", "exam_date": "考试日期", "avg_score": "平均分"
        })
        question_df = question_df.rename(columns={
            "question_id": "题目ID", "qno": "题号", "qtype": "题型", "full_score": "满分",
            "avg_score": "平均分", "difficulty": "难度", "discrimination": "区分度", "pass_rate": "得分率"
        })
        obe_df = obe_df.rename(columns={
            "co_code": "目标代码", "co_name": "课程目标", "threshold": "期望阈值",
            "full_sum": "满分总和", "actual_sum": "实际平均分", "achievement": "最终达成度"
        })
        if not warning_df.empty:
            warning_df = warning_df.rename(columns={
                "id": "记录ID", "student_id": "数据库中学生ID", "student_no": "学号", "class_name": "班级",
                "course_id": "课程ID", "course_name": "课程名称", "term": "学期", "level": "预警级别",
                "status": "处理状态", "reasons": "预警原因", "ai_summary": "AI诊断报告", "created_at": "生成时间"
            })

        meta_df.to_excel(writer, index=False, sheet_name="基础信息", startrow=0)
        stats_df.to_excel(writer, index=False, sheet_name="基础信息", startrow=3)
        trend_df.to_excel(writer, index=False, sheet_name="成绩分布")
        question_df.to_excel(writer, index=False, sheet_name="题目分析")
        obe_df.to_excel(writer, index=False, sheet_name="达成度分析")
        warning_df.to_excel(writer, index=False, sheet_name="预警记录")

    output.seek(0)
    return output.read()
