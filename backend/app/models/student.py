from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_no = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    class_name = Column(String, nullable=False)
    major = Column(String, nullable=False)
    grade_year = Column(String, nullable=False)

    exam_scores = relationship("StudentExamScore", back_populates="student")
    component_scores = relationship("StudentComponentScore", back_populates="student")
    question_scores = relationship("StudentQuestionScore", back_populates="student")
    warnings = relationship("WarningResult", back_populates="student")
