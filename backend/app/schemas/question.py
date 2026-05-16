from pydantic import BaseModel, ConfigDict


class QuestionBase(BaseModel):
    exam_id: int
    qno: str
    qtype: str
    qgroup_name: str | None = None
    sub_qno: str | None = None
    score: float
    section: str | None = None
    knowledge_point: str | None = None
    co_code: str | None = None
    indicator_code: str | None = None
    co_weight: float | None = None
    expected_threshold: float | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    qno: str | None = None
    qtype: str | None = None
    qgroup_name: str | None = None
    sub_qno: str | None = None
    score: float | None = None
    section: str | None = None
    knowledge_point: str | None = None
    co_code: str | None = None
    indicator_code: str | None = None
    co_weight: float | None = None
    expected_threshold: float | None = None


class QuestionResponse(QuestionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
