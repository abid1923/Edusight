"""
AI Insight routes: threshold check, get insight, generate insight, dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser
from app.schemas.insight_schema import (
    ActivityThresholdResponse, DashboardResponse, GenerateInsightResponse, InsightResponse,
)
from app.services import insight_service
from app.utils.limiter import limiter

router = APIRouter(prefix="/api/insight", tags=["AI Insight"])


@router.get("/me", response_model=InsightResponse)
def get_my_insight(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Get the latest AI insight for the current user."""
    insight = insight_service.get_insight(current_user.id, db)
    if not insight:
        raise HTTPException(status_code=404, detail="Belum ada insight. Silakan generate insight terlebih dahulu.")
    return insight


@router.post("/generate", response_model=GenerateInsightResponse)
@limiter.limit("3/minute")
def generate_insight(
    request: Request,
    current_user: CurrentUser,
    force: bool = Query(False, description="Force regenerate meskipun insight masih up-to-date"),
    db: Session = Depends(get_db),
):
    """
    Generate a new AI insight using full pipeline:
    Clustering → Reasoning → LLM Insight → Hybrid Recommendation
    """
    return insight_service.generate_insight(current_user.id, db, force=force)


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(current_user: CurrentUser, db: Session = Depends(get_db)):
    """
    Get full AI dashboard output:
    Learning Type → Reason → Strength/Weakness/Motivation → Recommendations
    """
    dashboard = insight_service.get_dashboard(current_user.id, db)
    if not dashboard:
        raise HTTPException(
            status_code=404,
            detail="Belum ada data dashboard. Silakan generate insight terlebih dahulu.",
        )
    return dashboard


@router.get("/threshold", response_model=ActivityThresholdResponse)
def check_threshold(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Check if user meets the minimum activity threshold for insights."""
    return insight_service.check_threshold(current_user.id, db)
