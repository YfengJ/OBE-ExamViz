from datetime import date as DateType

from pydantic import BaseModel


class ExamBase(BaseModel):
    course_id: int
    exam_type: str
    name: str
    date: DateType
    total_score: float = 100.0


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    course_id: int | None = None
    exam_type: str | None = None
    name: str | None = None
    date: DateType | None = None
    total_score: float | None = None


class ExamResponse(ExamBase):
    id: int

    class Config:
        from_attributes = True
