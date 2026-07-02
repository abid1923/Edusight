"""
Recommendation routes: get personalized learning recommendations.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser
from app.schemas.insight_schema import RecommendationItem
from app.models.insight_model import Insight, Recommendation
from app.services import recommendation_service

router = APIRouter(prefix="/api/recommendation", tags=["Recommendations"])


@router.get("/me", response_model=list[RecommendationItem])
def get_my_recommendations(current_user: CurrentUser, db: Session = Depends(get_db)):
    """
    Get personalized recommendations (internal materials & external resources).
    Loads from saved recommendations if an AI Insight has been generated,
    otherwise calculates recommendations on-the-fly with fallback profile.
    """
    user_id = current_user.id

    # Try to get recommendations from latest generated insight
    latest_insight = db.query(Insight).filter(Insight.user_id == user_id).order_by(Insight.generated_at.desc()).first()

    if latest_insight:
        # Load from DB
        recs = db.query(Recommendation).filter(
            Recommendation.insight_id == latest_insight.id
        ).order_by(Recommendation.score.desc()).all()
        
        return [
            RecommendationItem(
                title=r.title,
                description=r.description,
                url=r.url,
                resource_type=r.resource_type,
                reason=r.reason,
                priority=r.priority,
                path_name=r.path_name,
                score=r.score,
            )
            for r in recs
        ]

    # If no insight has been generated, generate on-the-fly with fallback/empty statistics
    try:
        from app.ai.inference import predict_learning_type
        prediction = predict_learning_type(user_id, db)
        learning_type = prediction["learning_type"]
        features = prediction["features"]
    except Exception:
        learning_type = "Moderate Learner"
        features = {"avg_quiz_score": 0, "completion_rate": 0}

    # Fetch stats
    from app.services.insight_service import _get_user_stats
    stats = _get_user_stats(user_id, db)

    # Generate recommendations on the fly
    recs = recommendation_service.generate_recommendations(
        user_id, learning_type, features, stats, db
    )

    return [RecommendationItem(**rec) for rec in recs]
