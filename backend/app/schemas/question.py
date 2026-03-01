from pydantic import BaseModel


class QuestionBase(BaseModel):
    exam_id: int
    qno: str
    qtype: str
    score: float
    section: str | None = None
    knowledge_point: str | None = None
    co_code: str | None = None
    indicator_code: str | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    qno: str | None = None
    qtype: str | None = None
    score: float | None = None
    section: str | None = None
    knowledge_point: str | None = None
    co_code: str | None = None
    indicator_code: str | None = None


class QuestionResponse(QuestionBase):
    id: int

    class Config:
        from_attributes = True
