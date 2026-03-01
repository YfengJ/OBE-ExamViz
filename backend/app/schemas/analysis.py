from pydantic import BaseModel


class ScoreStatsResponse(BaseModel):
    total_students: int
    average_score: float
    max_score: float
    min_score: float
    pass_rate: float
    score_segments: dict[str, int]


class QuestionAnalysisItem(BaseModel):
    question_id: int
    qno: str
    qtype: str
    full_score: float
    avg_score: float
    difficulty: float
    discrimination: float
    pass_rate: float


class OBEAchievementItem(BaseModel):
    co_code: str
    co_name: str
    achievement: float
    threshold: float
