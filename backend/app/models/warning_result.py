from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class WarningResult(Base):
    __tablename__ = "warning_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    term = Column(String, nullable=False)
    level = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    reasons_json = Column(JSON, nullable=False)
    ai_summary = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    student = relationship("Student", back_populates="warnings")
    course = relationship("Course")
