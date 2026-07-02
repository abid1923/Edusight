"""
User database model.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships — Logging tables (AI dataset compatible)
    login_logs = relationship("LoginLog", back_populates="user", order_by="LoginLog.timestamp")
    learning_activities = relationship("LearningActivity", back_populates="user", order_by="LearningActivity.start_time")
    quiz_logs = relationship("QuizLog", back_populates="user", order_by="QuizLog.timestamp")
    completion_logs = relationship("CompletionLog", back_populates="user", order_by="CompletionLog.completed_at")
    insights = relationship("Insight", back_populates="user", order_by="Insight.generated_at")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
