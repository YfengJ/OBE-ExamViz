from sqlalchemy import Column, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class WarningRule(Base):
    __tablename__ = "warning_rules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    name = Column(String, nullable=False)
    level = Column(String, nullable=False)
    config_json = Column(JSON, nullable=False)

    course = relationship("Course", back_populates="warning_rules")
