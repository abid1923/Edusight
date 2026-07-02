"""
Learning activity database models.
Covers: LearningPath, Material, UserProgress, Quiz, QuizQuestion, QuizAttempt.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    materials = relationship("Material", back_populates="learning_path", order_by="Material.order")

    def __repr__(self):
        return f"<LearningPath(id={self.id}, name='{self.name}')>"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    learning_path = relationship("LearningPath", back_populates="materials")
    quiz = relationship("Quiz", back_populates="material", uselist=False)
    user_progress = relationship("UserProgress", back_populates="material")

    def __repr__(self):
        return f"<Material(id={self.id}, title='{self.title}')>"


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    material = relationship("Material", back_populates="user_progress")

    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, material_id={self.material_id}, completed={self.is_completed})>"


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    material = relationship("Material", back_populates="quiz")
    questions = relationship("QuizQuestion", back_populates="quiz", order_by="QuizQuestion.id")
    attempts = relationship("QuizAttempt", back_populates="quiz")

    def __repr__(self):
        return f"<Quiz(id={self.id}, title='{self.title}')>"


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)
    correct_answer = Column(String(1), nullable=False)  # 'a', 'b', 'c', or 'd'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")

    def __repr__(self):
        return f"<QuizQuestion(id={self.id}, quiz_id={self.quiz_id})>"


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    total_questions = Column(Integer, nullable=False, default=10)
    correct_answers = Column(Integer, nullable=False, default=0)
    attempt_number = Column(Integer, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")

    def __repr__(self):
        return f"<QuizAttempt(user_id={self.user_id}, quiz_id={self.quiz_id}, attempt={self.attempt_number}, score={self.score})>"
