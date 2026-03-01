from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, nullable=False)
    course_name = Column(String, nullable=False)
    term = Column(String, nullable=False)
    department = Column(String, nullable=False)
    major = Column(String, nullable=False)
    credit = Column(Float, default=0.0)
    description = Column(Text, nullable=True)

    exams = relationship("Exam", back_populates="course")
    assessment_components = relationship("AssessmentComponent", back_populates="course")
    obe_outcomes = relationship("OBEOutcome", back_populates="course")
    warning_rules = relationship("WarningRule", back_populates="course")
