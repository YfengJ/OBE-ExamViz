from pydantic import BaseModel
from typing import Optional

class CourseBase(BaseModel):
    course_code: str
    course_name: str
    term: str
    department: str
    major: str
    credit: float = 0.0
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int

    class Config:
        from_attributes = True