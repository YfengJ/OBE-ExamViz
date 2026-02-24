from pydantic import BaseModel
from typing import Optional
from datetime import date

class ExamBase(BaseModel):
    course_id: int
    exam_type: str  # usual/mid/final
    name: str
    date: date
    total_score: float = 100.0

class ExamCreate(ExamBase):
    pass

class ExamResponse(ExamBase):
    id: int

    class Config:
        from_attributes = True