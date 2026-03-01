from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    exam_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    total_score = Column(Float, default=100.0)

    course = relationship("Course", back_populates="exams")
    questions = relationship("Question", back_populates="exam")
    student_scores = relationship("StudentExamScore", back_populates="exam")
