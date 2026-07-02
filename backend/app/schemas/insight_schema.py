"""
AI Insight request/response schemas.
Includes dashboard, insight, recommendation, and threshold schemas.
"""

from datetime import datetime

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    """Single recommendation item — supports internal and external resources."""
    title: str
    description: str | None = None
    url: str | None = None  # External link (YouTube, article, tutorial)
    resource_type: str = "internal"  # "internal", "youtube", "article", "tutorial", "external"
    reason: str | None = None
    priority: str = "medium"  # "high", "medium", "low"
    path_name: str | None = None
    score: int | None = None

    class Config:
        from_attributes = True


class InsightResponse(BaseModel):
    """Full insight response with LLM-generated fields."""
    learning_type: str
    reason: str | None = None
    strength: str | None = None
    weakness: str | None = None
    motivation: str | None = None
    insight_text: str
    recommendations: list[RecommendationItem] = []
    cluster_id: int | None = None
    generated_at: datetime
    features: dict[str, float] | None = None

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    """
    Final dashboard output sesuai master plan.
    Learning Type → Reason → Insight → Recommendation
    """
    learning_type: str
    reason: str
    strength: str
    weakness: str
    motivation: str
    recommendations: list[RecommendationItem] = []
    cluster_id: int | None = None
    generated_at: datetime
    insight_source: str | None = None  # "llm" or "fallback"
    features: dict[str, float] | None = None


class ThresholdStatus(BaseModel):
    metric: str
    current: int
    required: int
    met: bool


class ActivityThresholdResponse(BaseModel):
    meets_threshold: bool
    message: str
    details: list[ThresholdStatus]


class GenerateInsightResponse(BaseModel):
    success: bool
    message: str
    insight: InsightResponse | None = None
