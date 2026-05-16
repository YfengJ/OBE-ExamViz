from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class GeneratedContent(Base):
    __tablename__ = "generated_contents"
    __table_args__ = (UniqueConstraint("run_id", "content_type", name="uq_generated_contents_run_type"),)

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    content_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    ai_enabled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    run = relationship("AnalysisRun", back_populates="generated_contents")
