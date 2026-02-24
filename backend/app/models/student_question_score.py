from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class StudentQuestionScore(Base):
    __tablename__ = "student_question_scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    score = Column(Float, default=0.0)

    # 关系
    student = relationship("Student", back_populates="question_scores")
    question = relationship("Question", back_populates="student_scores")