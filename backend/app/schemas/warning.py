from datetime import datetime

from pydantic import BaseModel


class WarningResultResponse(BaseModel):
    id: int
    student_id: int
    student_no: str
    class_name: str
    course_id: int
    course_name: str
    term: str
    level: str
    status: str
    reasons: list[str]
    ai_summary: str | None = None
    created_at: datetime


class WarningGenerateRequest(BaseModel):
    course_id: int
    term: str


class WarningUpdateRequest(BaseModel):
    status: str


class WarningBatchAIRequest(BaseModel):
    warning_ids: list[int]
