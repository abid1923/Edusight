"""
AI Insight database model.
Stores clustering results, LLM-generated insights, and recommendations.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Insight(Base):
    """
    Menyimpan hasil AI insight termasuk LLM-generated content.
    Fields:
    - cluster_id, learning_type: dari AI clustering
    - reason: dynamic reasoning (hybrid template)
    - strength, weakness, motivation: dari LLM (Groq)
    - insight_text: backward compatible text
    - recommendation: JSON recommendations
    """
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    cluster_id = Column(Integer, nullable=True)  # From clustering model
    learning_type = Column(String(100), nullable=False)  # e.g. "Active Learner"
    reason = Column(Text, nullable=True)  # Dynamic reasoning text
    strength = Column(Text, nullable=True)  # LLM: strength insight
    weakness = Column(Text, nullable=True)  # LLM: weakness insight
    motivation = Column(Text, nullable=True)  # LLM: motivation insight
    insight_text = Column(Text, nullable=False)  # Backward compatible full text
    recommendation = Column(Text, nullable=True)  # JSON recommendations
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="insights")

    def __repr__(self):
        return f"<Insight(user_id={self.user_id}, type='{self.learning_type}')>"


class Recommendation(Base):
    """
    Menyimpan recommendation resources (internal dan external).
    Mendukung:
    - Internal material recommendations
    - External resources: YouTube links, artikel, tutorial
    """
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    insight_id = Column(Integer, ForeignKey("insights.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)  # External link (YouTube, artikel, etc.)
    resource_type = Column(String(50), nullable=False, default="internal")
    # resource_type: "internal", "youtube", "article", "tutorial", "external"
    reason = Column(Text, nullable=True)  # Why this is recommended
    priority = Column(String(20), nullable=False, default="medium")
    # priority: "high", "medium", "low"
    path_name = Column(String(100), nullable=True)  # Learning path name
    score = Column(Integer, nullable=True)  # Ranking score for ordering
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    insight = relationship("Insight")
    user = relationship("User")

    def __repr__(self):
        return f"<Recommendation(user_id={self.user_id}, title='{self.title}', type='{self.resource_type}')>"
