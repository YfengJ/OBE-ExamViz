from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalysisRunCreate(BaseModel):
    course_id: int
    exam_id: int
    class_name: str
    academic_year: str
    term_label: str
    teacher_name: str | None = None
    department: str | None = None
    major: str | None = None
    exam_date: date | None = None
    student_count_expected: int | None = None
    student_count_actual: int | None = None
    outcome_threshold: float = 0.65
    usual_weight: float = Field(default=0.2, ge=0, le=1)
    midterm_weight: float = Field(default=0.2, ge=0, le=1)
    final_weight: float = Field(default=0.6, ge=0, le=1)


class AnalysisRunResponse(AnalysisRunCreate):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisRunOverview(BaseModel):
    run: AnalysisRunResponse
    course_name: str
    exam_name: str
    progress: dict[str, int | bool]


class AnalysisRunNarrative(BaseModel):
    score_summary: str
    support_analysis: str
    attainment_analysis: str
    improvement_actions: str
