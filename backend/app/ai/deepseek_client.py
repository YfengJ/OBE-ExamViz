from __future__ import annotations

import json
import re

import httpx

from backend.app.core.config import settings


class DeepSeekClient:
    def __init__(self) -> None:
        self._api_key = settings.DEEPSEEK_API_KEY
        self._base = settings.DEEPSEEK_API_BASE.rstrip("/")
        self._model = settings.DEEPSEEK_MODEL

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def generate_warning_summary(self, anonymous_student_id: str, reasons: list[str]) -> str:
        if not self._api_key:
            return f"Student {anonymous_student_id}: monitor learning status. Reasons: {', '.join(reasons)}."

        return await self._chat(
            system_prompt="You are an education analytics assistant. Never output sensitive personal data.",
            user_prompt=(
                f"Student ID: {anonymous_student_id}. "
                f"Warning reasons: {', '.join(reasons)}. "
                "Generate a concise learning-risk analysis and actionable guidance in Chinese."
            ),
        )

    async def generate_paper_improvement(self, meta: dict, warnings: list[dict], fallback_text: str) -> str:
        if not self._api_key:
            return fallback_text

        warning_text = "; ".join(
            [f"{item['student_no']}:{'/'.join(item['reasons'])}" for item in warnings[:10]]
        ) or "无重点预警学生"
        return await self._chat(
            system_prompt="You are an education quality analyst. Write concrete Chinese teaching improvement suggestions without sensitive personal data.",
            user_prompt=(
                f"课程：{meta.get('course_name', '')}；班级：{meta.get('class_name', '')}；"
                f"考试：{meta.get('exam_name', '')}；主要预警：{warning_text}。"
                "请生成一段适合试卷分析表“教师对今后教学持续改进的具体意见”的中文文字，180字到260字。"
                "内容要包含课堂讲评、分层辅导、阶段性检测和后续跟踪四类措施。"
            ),
        )

    async def generate_report_narrative(
        self,
        *,
        meta: dict,
        score_stats: dict,
        score_segments: list[dict],
        question_groups: list[dict],
        course_outcomes: list[dict],
        warnings: list[dict],
        fallback_sections: dict[str, str],
        suggestion_template: str = "free",
    ) -> dict[str, str]:
        if not self._api_key:
            return fallback_sections

        payload_text = {
            "meta": {
                "course_name": meta.get("course_name", ""),
                "class_name": meta.get("class_name", ""),
                "teacher_name": meta.get("teacher_name", ""),
                "department": meta.get("department", ""),
                "academic_year": meta.get("academic_year", ""),
                "exam_name": meta.get("exam_name", ""),
                "exam_date": meta.get("exam_date", ""),
            },
            "score_stats": score_stats,
            "score_segments": score_segments,
            "question_groups": question_groups,
            "course_outcomes": course_outcomes,
            "warnings": warnings[:10],
        }
        if suggestion_template == "per_outcome":
            improvement_requirement = (
                "2. improvement_actions 必须按每个课程目标逐项生成建议，格式用 1）2）3）...；"
                "每一项都要明确写出对应 CO 编号、课程目标说明或能力要求、达成度/阈值、关联题型，"
                "并给出与本课程内容直接相关的课堂讲评、练习、辅导和复测措施；"
                "不得只写通用的课堂管理建议。"
            )
        else:
            improvement_requirement = (
                "2. improvement_actions 写 180-280 字，按 1）2）3）4）组织，措施要具体；"
            )

        response = await self._chat(
            system_prompt=(
                "你是一名高校试卷分析专家。"
                "请基于给定的结构化教学数据，撰写符合高校试卷分析表语气的中文文字。"
                "不要编造不存在的数据，不要输出无关前言，不要泄露敏感个人隐私。"
                "必须只返回 JSON 对象。"
            ),
            user_prompt=(
                "请根据以下 JSON 数据，生成试卷分析表中的 4 段中文内容，"
                "字段必须严格是 score_summary、support_analysis、attainment_analysis、improvement_actions。"
                "要求："
                "1. score_summary、support_analysis、attainment_analysis 每段 80-180 字；"
                f"{improvement_requirement}"
                "3. 语言正式，适合学校试卷分析报告；"
                "4. 要明确引用成绩统计、课程目标、题型表现与改进建议；"
                "5. improvement_actions 至少包含课堂讲评、分层辅导、阶段性检测和闭环跟踪；"
                "6. 只输出 JSON，不要 markdown。"
                f"\n\n结构化数据：{json.dumps(payload_text, ensure_ascii=False)}"
            ),
        )
        parsed = self._extract_json_object(response)
        if not parsed:
            return fallback_sections
        normalized = {
            "score_summary": str(parsed.get("score_summary") or "").strip(),
            "support_analysis": str(parsed.get("support_analysis") or "").strip(),
            "attainment_analysis": str(parsed.get("attainment_analysis") or "").strip(),
            "improvement_actions": str(parsed.get("improvement_actions") or "").strip(),
        }
        if any(not value for value in normalized.values()):
            return fallback_sections
        return normalized

    async def _chat(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0.3,
        }

        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self._base}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    def _extract_json_object(self, text: str) -> dict:
        content = text.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
        try:
            data = json.loads(content)
            return data if isinstance(data, dict) else {}
        except Exception:
            pass
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return {}
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
