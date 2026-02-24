from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class WarningResult(Base):
    __tablename__ = "warning_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    term = Column(String, nullable=False)
    level = Column(String, nullable=False)  # warning/critical
    reasons_json = Column(JSON, nullable=False)  # 预警原因
    ai_summary = Column(String, nullable=True)  # AI生成的分析摘要
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    student = relationship("Student", back_populates="warnings")
    course = relationship("Course")