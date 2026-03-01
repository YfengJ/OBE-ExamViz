from pydantic import BaseModel


class StudentBase(BaseModel):
    student_no: str
    name: str | None = None
    class_name: str
    major: str
    grade_year: str


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    student_no: str | None = None
    name: str | None = None
    class_name: str | None = None
    major: str | None = None
    grade_year: str | None = None


class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True
