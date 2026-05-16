from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    qno = Column(String, nullable=False)
    qtype = Column(String, nullable=False)
    qgroup_name = Column(String, nullable=True)
    sub_qno = Column(String, nullable=True)
    score = Column(Float, default=0.0)
    section = Column(String, nullable=True)
    knowledge_point = Column(String, nullable=True)
    co_code = Column(String, nullable=True)
    indicator_code = Column(String, nullable=True)
    co_weight = Column(Float, default=0.0)
    expected_threshold = Column(Float, default=0.65)

    exam = relationship("Exam", back_populates="questions")
    student_scores = relationship("StudentQuestionScore", back_populates="question")
