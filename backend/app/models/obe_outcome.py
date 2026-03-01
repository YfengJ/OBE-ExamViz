from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class OBEOutcome(Base):
    __tablename__ = "obe_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    co_code = Column(String, nullable=False)
    co_name = Column(String, nullable=False)
    threshold = Column(Float, default=0.6)

    course = relationship("Course", back_populates="obe_outcomes")
