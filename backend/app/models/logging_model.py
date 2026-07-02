"""
Dedicated AI-compatible logging models.
These tables mirror the AI dataset modelling structure for direct export.

Tables:
- LoginLog: histori login user → total_login
- LearningActivity: aktivitas belajar → avg_study_time, total_material_view
- QuizLog: hasil quiz → avg_quiz_score, quiz_attempts
- CompletionLog: penyelesaian materi → completion_rate
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class LoginLog(Base):
    """
    Menyimpan histori login user.
    AI Purpose: menghitung total_login.
    """
    __tablename__ = "login_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="login_logs")

    def __repr__(self):
        return f"<LoginLog(id={self.id}, user_id={self.user_id}, timestamp={self.timestamp})>"


class LearningActivity(Base):
    """
    Menyimpan aktivitas belajar user.
    AI Purpose: menghitung avg_study_time dan total_material_view.
    Study duration = end_time - start_time.
    """
    __tablename__ = "learning_activity"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    path = Column(String(100), nullable=False)  # Learning path name (e.g. "Machine Learning")
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)  # Null saat user masih belajar

    # Relationships
    user = relationship("User", back_populates="learning_activities")

    def __repr__(self):
        return f"<LearningActivity(id={self.id}, user_id={self.user_id}, material_id={self.material_id})>"


class QuizLog(Base):
    """
    Menyimpan hasil quiz user (mirror dataset modelling).
    AI Purpose: menghitung avg_quiz_score dan quiz_attempts.
    """
    __tablename__ = "quiz_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    path = Column(String(100), nullable=False)  # Learning path name
    score = Column(Float, nullable=False, default=0.0)
    attempt = Column(Integer, nullable=False, default=1)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="quiz_logs")

    def __repr__(self):
        return f"<QuizLog(id={self.id}, user_id={self.user_id}, score={self.score}, attempt={self.attempt})>"


class CompletionLog(Base):
    """
    Menyimpan progress penyelesaian materi.
    AI Purpose: menghitung completion_rate.
    """
    __tablename__ = "completion_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    path = Column(String(100), nullable=False)  # Learning path name
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="completion_logs")

    def __repr__(self):
        return f"<CompletionLog(id={self.id}, user_id={self.user_id}, material_id={self.material_id})>"
