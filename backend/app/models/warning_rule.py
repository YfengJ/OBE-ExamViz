from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class WarningRule(Base):
    __tablename__ = "warning_rules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)  # 为空表示全局规则
    name = Column(String, nullable=False)
    level = Column(String, nullable=False)  # warning/critical
    config_json = Column(JSON, nullable=False)  # 规则配置JSON

    # 关系
    course = relationship("Course", back_populates="warning_rules")