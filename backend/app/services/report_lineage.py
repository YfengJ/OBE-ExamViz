from __future__ import annotations

from typing import Any


def build_input_requirements(context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    stats = (context or {}).get("score_stats") or {}
    question_items = (context or {}).get("question_items") or []
    course_outcomes = (context or {}).get("course_outcomes") or []
    students = (context or {}).get("students") or (context or {}).get("student_scores") or []
    return [
        {
            "name": "课程与考试基本信息",
            "required": True,
            "source": "输入模板的基本信息表或分析任务信息",
            "fields": ["课程名称", "教学班级", "院系", "任课教师", "学年学期", "考试日期"],
            "used_for": ["报告首页基本信息", "导出文件命名", "任务列表筛选"],
            "current_status": "ready" if (context or {}).get("meta") else "pending",
        },
        {
            "name": "学生名单与期末卷面成绩",
            "required": True,
            "source": "输入模板的学生成绩表",
            "fields": ["学号", "姓名", "期末总分"],
            "used_for": ["应考人数", "实考人数", "平均分", "最高分", "最低分", "及格率", "分数段统计"],
            "current_status": "ready" if students or stats.get("total_students") else "pending",
        },
        {
            "name": "题型、题号与逐题得分",
            "required": True,
            "source": "输入模板的试卷结构表和学生成绩表",
            "fields": ["题型", "题号", "题目满分", "学生逐题得分"],
            "used_for": ["题型得分率", "逐题分析", "课程目标达成度", "达成度分布图"],
            "current_status": "ready" if question_items else "pending",
        },
        {
            "name": "课程目标与试题支撑关系",
            "required": True,
            "source": "输入模板的课程目标表和试卷结构表",
            "fields": ["课程目标编号", "课程目标说明", "题目对应课程目标", "目标阈值"],
            "used_for": ["试题支撑度分析", "学生作答达成度分析", "持续改进建议"],
            "current_status": "ready" if course_outcomes else "pending",
        },
    ]


def build_data_source_overview(context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    meta = (context or {}).get("meta") or {}
    score_stats = (context or {}).get("score_stats") or {}
    question_groups = (context or {}).get("question_groups") or []
    course_outcomes = (context or {}).get("course_outcomes") or []
    warnings = (context or {}).get("warnings") or []
    return [
        {
            "title": "基础信息",
            "source_method": "direct_read",
            "source_label": "读取信息",
            "source": "从输入模板基本信息表和分析任务记录读取",
            "fields": ["课程名称", "教学班级", "院系", "教师", "考试日期"],
            "evidence": f"{meta.get('course_name') or '未识别课程'} / {meta.get('class_name') or '未识别班级'}",
        },
        {
            "title": "成绩统计",
            "source_method": "computed",
            "source_label": "计算得出",
            "source": "由学生逐题得分汇总出的期末卷面总分计算",
            "fields": ["平均分", "最高分", "最低分", "及格率", "分数段人数"],
            "evidence": f"已纳入 {score_stats.get('total_students', 0)} 名学生",
        },
        {
            "title": "题型与课程目标达成度",
            "source_method": "computed",
            "source_label": "计算得出",
            "source": "由试卷结构、逐题得分和课程目标映射计算",
            "fields": ["题型平均分", "题型得分率", "课程目标达成度", "分项权重"],
            "evidence": f"{len(question_groups)} 类题型 / {len(course_outcomes)} 个课程目标",
        },
        {
            "title": "达成度图表",
            "source_method": "rendered_chart",
            "source_label": "图表展示",
            "source": "由本次分析结果绘制",
            "fields": ["课程目标对比图", "学生达成度分布图"],
            "evidence": "导出报告时按已核对的计算结果生成",
        },
        {
            "title": "报告文字与改进建议",
            "source_method": "ai_generated",
            "source_label": "AI生成",
            "source": "基于成绩统计、课程目标和重点预警生成",
            "fields": ["支撑度分析段落", "达成度分析段落", "持续改进建议"],
            "evidence": f"已提供 {len(warnings)} 条重点预警作为生成依据",
        },
    ]


def build_report_section_lineage(context: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "section_key": "basic_info",
            "title": "基本信息表",
            "source_method": "direct_read",
            "source_label": "读取信息",
            "description": "课程、班级、院系、考试时间等字段来自导入文件和本次分析任务。",
        },
        {
            "section_key": "score_statistics",
            "title": "成绩统计",
            "source_method": "computed",
            "source_label": "计算得出",
            "description": "应考人数、实考人数、分数段、平均分、最高分、最低分和试题难度由期末卷面成绩计算。",
        },
        {
            "section_key": "support_analysis",
            "title": "试题对课程目标的支撑度分析",
            "source_method": "ai_generated",
            "source_label": "AI生成",
            "description": "先读取课程目标和支撑题型，再结合各题型满分、得分率和达成度生成说明文字。",
        },
        {
            "section_key": "attainment_table",
            "title": "学生作答情况对课程目标的达成度分析",
            "source_method": "computed",
            "source_label": "计算得出",
            "description": "课程目标达成度表由逐题得分按课程目标汇总，分项达成度和权重按规则计算。",
        },
        {
            "section_key": "attainment_charts",
            "title": "课程目标达成度图表",
            "source_method": "rendered_chart",
            "source_label": "图表展示",
            "description": "对比图和学生分布图使用本次分析中的课程目标达成度与学生逐项目标达成度生成。",
        },
        {
            "section_key": "improvement_actions",
            "title": "教学持续改进意见",
            "source_method": "ai_generated",
            "source_label": "AI生成",
            "description": "结合低得分题型、未达成课程目标和重点学生预警生成。",
        },
    ]


def build_course_objective_lineage(context: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in context.get("course_outcomes") or []:
        rows.append(
            {
                "co_code": item.get("co_code"),
                "co_name": item.get("co_name"),
                "full_score": item.get("full_score"),
                "avg_score": item.get("avg_score"),
                "achievement": item.get("achievement"),
                "threshold": item.get("threshold"),
                "supporting_groups": item.get("supporting_groups") or [],
                "support_source": "question_mapping",
                "source_method": "computed",
                "source_label": "计算得出",
                "source_detail": "按题目所属课程目标汇总学生逐题得分，再除以该课程目标对应满分。",
            }
        )
    return rows


def build_transfer_checklist() -> list[str]:
    return [
        "换一门课时，优先使用系统提供的简洁输入模板，填写基本信息、试卷结构、课程目标和学生逐题得分即可。",
        "题号、题型、满分和题目对应课程目标必须完整，否则课程目标达成度和分布图无法可靠生成。",
        "平均分、达成度、分数段、图表和课程目标分析结果由系统计算，输入模板中不需要手工填写。",
        "导入后先查看结构分析和报告预览，确认统计结果、图表和报告文字都对应本课程，再导出正式文档。",
    ]
