from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class StudentExamScore(Base):
    __tablename__ = "student_exam_scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    total_score = Column(Float, default=0.0)

    # 关系
    student = relationship("Student", back_populates="exam_scores")
    exam = relationship("Exam", back_populates="student_scores")