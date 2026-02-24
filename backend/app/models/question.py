from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    qno = Column(String, nullable=False)  # 题号，如"1", "2-1"等
    qtype = Column(String, nullable=False)  # 题型：单选/多选/填空/简答/论述
    score = Column(Float, default=0.0)  # 该题满分
    section = Column(String, nullable=True)  # 所属章节
    knowledge_point = Column(String, nullable=True)  # 知识点
    co_code = Column(String, nullable=True)  # 课程目标代码
    indicator_code = Column(String, nullable=True)  # 指标点代码

    # 关系
    exam = relationship("Exam", back_populates="questions")
    student_scores = relationship("StudentQuestionScore", back_populates="question")