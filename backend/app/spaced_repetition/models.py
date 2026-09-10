"""
Spaced repetition models
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database.base import Base

class SpacedRepetitionLog(Base):
    """Spaced repetition review schedule and progress"""
    __tablename__ = "spaced_repetition_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Review tracking
    review_number = Column(Integer, nullable=False)  # 1st, 2nd, 3rd review, etc.
    interval_days = Column(Integer, default=0)  # Days since last review
    
    # Scheduling
    scheduled_date = Column(DateTime, nullable=False, index=True)
    completed_date = Column(DateTime, nullable=True)
    
    # Performance
    retention_score = Column(Float, default=0.0)  # 0-100
    questions_correct = Column(Integer, default=0)
    questions_total = Column(Integer, default=0)
    time_spent_minutes = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assignment = relationship("Assignment", back_populates="spaced_repetition_logs")

    def __repr__(self):
        return f"<SpacedRepetitionLog Review#{self.review_number}>"
