from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    class_name = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    term_label = Column(String, nullable=False)
    teacher_name = Column(String, nullable=True)
    department = Column(String, nullable=True)
    major = Column(String, nullable=True)
    exam_date = Column(Date, nullable=True)
    student_count_expected = Column(Integer, default=0)
    student_count_actual = Column(Integer, default=0)
    outcome_threshold = Column(Float, default=0.65)
    usual_weight = Column(Float, default=0.2)
    midterm_weight = Column(Float, default=0.2)
    final_weight = Column(Float, default=0.6)
    status = Column(String, default="draft", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    course = relationship("Course")
    exam = relationship("Exam")
    generated_contents = relationship("GeneratedContent", back_populates="run", cascade="all, delete-orphan")
