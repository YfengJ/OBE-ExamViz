from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class OBEOutcome(Base):
    __tablename__ = "obe_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    co_code = Column(String, nullable=False)  # 课程目标代码
    co_name = Column(String, nullable=False)  # 课程目标名称
    threshold = Column(Float, default=0.6)  # 达成度阈值

    # 关系
    course = relationship("Course", back_populates="obe_outcomes")