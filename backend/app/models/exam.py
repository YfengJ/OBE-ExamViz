from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    exam_type = Column(String, nullable=False)  # usual/mid/final
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    total_score = Column(Float, default=100.0)

    # 关系
    course = relationship("Course", back_populates="exams")
    questions = relationship("Question", back_populates="exam")
    student_scores = relationship("StudentExamScore", back_populates="exam")