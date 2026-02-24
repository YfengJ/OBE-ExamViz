from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_no = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)  # 姓名脱敏，可为空
    class_name = Column(String, nullable=False)
    major = Column(String, nullable=False)
    grade_year = Column(String, nullable=False)

    # 关系
    exam_scores = relationship("StudentExamScore", back_populates="student")
    component_scores = relationship("StudentComponentScore", back_populates="student")
    question_scores = relationship("StudentQuestionScore", back_populates="student")
    warnings = relationship("WarningResult", back_populates="student")