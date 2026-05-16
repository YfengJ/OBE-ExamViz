from pydantic import BaseModel, ConfigDict


class CourseBase(BaseModel):
    course_code: str
    course_name: str
    term: str
    department: str
    major: str
    credit: float = 0.0
    owner: str | None = None
    description: str | None = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    course_code: str | None = None
    course_name: str | None = None
    term: str | None = None
    department: str | None = None
    major: str | None = None
    credit: float | None = None
    owner: str | None = None
    description: str | None = None


class CourseResponse(CourseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
