from pydantic import BaseModel
from typing import Optional

class StudentBase(BaseModel):
    student_no: str
    name: Optional[str] = None
    class_name: str
    major: str
    grade_year: str

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True