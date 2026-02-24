from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class StudentComponentScore(Base):
    __tablename__ = "student_component_scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("assessment_components.id"), nullable=False)
    score = Column(Float, default=0.0)

    # 关系
    student = relationship("Student", back_populates="component_scores")
    component = relationship("AssessmentComponent", back_populates="student_scores")