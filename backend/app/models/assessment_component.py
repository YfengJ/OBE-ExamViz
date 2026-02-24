from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class AssessmentComponent(Base):
    __tablename__ = "assessment_components"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String, nullable=False)  # 作业/实验/出勤等
    weight = Column(Float, default=0.0)  # 权重，如0.3表示30%

    # 关系
    course = relationship("Course", back_populates="assessment_components")
    student_scores = relationship("StudentComponentScore", back_populates="component")