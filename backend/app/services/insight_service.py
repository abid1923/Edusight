"""Service for checking thresholds, generating, caching, and retrieving AI insights."""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.feature_engineering import extract_features
from app.ai.inference import predict_learning_type
from app.config import INSIGHT_MIN_COMPLETIONS, INSIGHT_MIN_LOGINS, INSIGHT_MIN_QUIZ_ATTEMPTS
from app.llm.insight_generator import generate_llm_insight
from app.models.user_model import User
from app.models.activity_model import Material, UserProgress, QuizAttempt, LearningPath
from app.models.insight_model import Insight, Recommendation
from app.models.logging_model import CompletionLog, LearningActivity, LoginLog, QuizLog
from app.schemas.insight_schema import (
    ActivityThresholdResponse, DashboardResponse, GenerateInsightResponse,
    InsightResponse, RecommendationItem, ThresholdStatus,
)
from app.services.recommendation_service import generate_recommendations, save_recommendations

logger = logging.getLogger(__name__)


def _get_user_stats(user_id: int, db: Session) -> dict:
    """Calculate user activity statistics from logging tables."""
    # total_login — from login_log
    login_count = db.query(LoginLog).filter(
        LoginLog.user_id == user_id
    ).count()

    # quiz_attempts — from quiz_log
    quiz_count = db.query(QuizLog).filter(
        QuizLog.user_id == user_id
    ).count()

    # completion_count — from completion_log
    comp_count = db.query(CompletionLog).filter(
        CompletionLog.user_id == user_id
    ).count()

    # avg_quiz_score — from quiz_log
    quiz_logs = db.query(QuizLog).filter(QuizLog.user_id == user_id).all()
    avg = sum(q.score for q in quiz_logs) / len(quiz_logs) if quiz_logs else 0

    return {
        "login_count": login_count,
        "quiz_attempt_count": quiz_count,
        "completion_count": comp_count,
        "avg_quiz_score": round(avg, 2),
    }


def check_threshold(user_id: int, db: Session) -> ActivityThresholdResponse:
    """Check if user meets minimum activity thresholds for insight generation."""
    stats = _get_user_stats(user_id, db)
    details = [
        ThresholdStatus(
            metric="Login", current=stats["login_count"],
            required=INSIGHT_MIN_LOGINS, met=stats["login_count"] >= INSIGHT_MIN_LOGINS,
        ),
        ThresholdStatus(
            metric="Quiz Attempts", current=stats["quiz_attempt_count"],
            required=INSIGHT_MIN_QUIZ_ATTEMPTS, met=stats["quiz_attempt_count"] >= INSIGHT_MIN_QUIZ_ATTEMPTS,
        ),
        ThresholdStatus(
            metric="Material Completions", current=stats["completion_count"],
            required=INSIGHT_MIN_COMPLETIONS, met=stats["completion_count"] >= INSIGHT_MIN_COMPLETIONS,
        ),
    ]
    meets = all(d.met for d in details)
    msg = "Aktivitas cukup untuk menghasilkan insight" if meets else "Belum cukup aktivitas untuk menghasilkan insight"
    return ActivityThresholdResponse(meets_threshold=meets, message=msg, details=details)


def _should_regenerate(user_id: int, db: Session) -> bool:
    """Determine if a user's AI insight should be regenerated based on new activity."""
    latest_insight = db.query(Insight).filter(
        Insight.user_id == user_id
    ).order_by(Insight.generated_at.desc()).first()

    if not latest_insight:
        return True

    last_generated = latest_insight.generated_at

    # Check for new completions since last insight
    new_completions = db.query(CompletionLog).filter(
        CompletionLog.user_id == user_id,
        CompletionLog.completed_at > last_generated,
    ).count()

    # Check for new quiz submissions since last insight
    new_quizzes = db.query(QuizLog).filter(
        QuizLog.user_id == user_id,
        QuizLog.timestamp > last_generated,
    ).count()

    # Check for new logins since last insight
    new_logins = db.query(LoginLog).filter(
        LoginLog.user_id == user_id,
        LoginLog.timestamp > last_generated,
    ).count()

    # Check for new learning activities since last insight
    new_activities = db.query(LearningActivity).filter(
        LearningActivity.user_id == user_id,
        (LearningActivity.end_time > last_generated) | (LearningActivity.start_time > last_generated),
    ).count()

    if new_completions > 0 or new_quizzes > 0 or new_logins >= 3 or new_activities > 0:
        logger.info(
            f"Regeneration triggered for user {user_id}: "
            f"new_completions={new_completions}, new_quizzes={new_quizzes}, "
            f"new_logins={new_logins}, new_activities={new_activities}"
        )
        return True

    return False


def _build_recommendation_items(insight_id: int, user_id: int, db: Session) -> list[RecommendationItem]:
    """Load saved recommendations from database and convert to schema."""
    recs = db.query(Recommendation).filter(
        Recommendation.insight_id == insight_id,
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


def get_insight(user_id: int, db: Session) -> InsightResponse | None:
    """Get the latest AI insight for a user, including recommendations."""
    insight = db.query(Insight).filter(
        Insight.user_id == user_id
    ).order_by(Insight.generated_at.desc()).first()

    if not insight:
        return None

    recommendations = _build_recommendation_items(insight.id, user_id, db)
    features = extract_features(user_id, db)

    return InsightResponse(
        learning_type=insight.learning_type,
        reason=insight.reason,
        strength=insight.strength,
        weakness=insight.weakness,
        motivation=insight.motivation,
        insight_text=insight.insight_text,
        recommendations=recommendations,
        cluster_id=insight.cluster_id,
        generated_at=insight.generated_at,
        features=features,
    )


def get_dashboard(user_id: int, db: Session) -> DashboardResponse | None:
    """Retrieve cached AI dashboard data for a user."""
    insight = db.query(Insight).filter(
        Insight.user_id == user_id
    ).order_by(Insight.generated_at.desc()).first()

    if not insight:
        return None

    recommendations = _build_recommendation_items(insight.id, user_id, db)
    features = extract_features(user_id, db)

    return DashboardResponse(
        learning_type=insight.learning_type,
        reason=insight.reason or "",
        strength=insight.strength or "",
        weakness=insight.weakness or "",
        motivation=insight.motivation or "",
        recommendations=recommendations,
        cluster_id=insight.cluster_id,
        generated_at=insight.generated_at,
        features=features,
    )


def _get_best_path(user_id: int, db: Session) -> str:
    """Calculate the user's best performing learning path based on progress and quiz scores."""
    paths = {
        "Machine Learning": [1, 2, 3, 4, 5],
        "Frontend Development": [6, 7, 8, 9, 10],
        "Backend Development": [11, 12, 13, 14, 15]
    }
    
    best_path = "Machine Learning"
    highest_score = -1.0
    highest_progress = -1.0
    
    for path_name, mat_ids in paths.items():
        # Count progress
        completed_mats = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.material_id.in_(mat_ids),
            UserProgress.is_completed == True
        ).all()
        progress = len(completed_mats)
        
        # Calculate avg score
        quiz_logs = db.query(QuizLog).filter(
            QuizLog.user_id == user_id,
            QuizLog.material_id.in_(mat_ids)
        ).all()
        
        avg_score = sum(q.score for q in quiz_logs) / len(quiz_logs) if quiz_logs else 0.0
        
        if progress > highest_progress:
            highest_progress = progress
            highest_score = avg_score
            best_path = path_name
        elif progress == highest_progress:
            if avg_score > highest_score:
                highest_score = avg_score
                best_path = path_name
                
    return best_path


def generate_insight(user_id: int, db: Session, force: bool = False) -> GenerateInsightResponse:
    """Generate, cache, and return a new AI insight and set of recommendations."""
    # Step 1: Check threshold
    threshold = check_threshold(user_id, db)
    if not threshold.meets_threshold:
        return GenerateInsightResponse(success=False, message=threshold.message, insight=None)

    # Step 2: Check if regeneration is needed
    if not force and not _should_regenerate(user_id, db):
        existing = get_insight(user_id, db)
        if existing:
            return GenerateInsightResponse(
                success=True,
                message="Insight masih up-to-date. Tidak perlu regenerate.",
                insight=existing,
            )

    # Step 3: AI Clustering → learning_type
    try:
        prediction = predict_learning_type(user_id, db)
        cluster_id = prediction["cluster_id"]
        learning_type = prediction["learning_type"]
        features = prediction["features"]
        logger.info(
            f"AI Prediction untuk user {user_id}: "
            f"cluster={cluster_id}, type={learning_type}, features={features}"
        )
    except Exception as e:
        logger.error(f"AI prediction gagal untuk user {user_id}: {e}")
        return GenerateInsightResponse(
            success=False,
            message=f"AI prediction gagal: {str(e)}",
            insight=None,
        )

    # Fetch personalization metadata
    user = db.query(User).filter(User.id == user_id).first()
    full_name = user.full_name if user else "Pengguna"

    # Find active path
    all_materials = db.query(Material).join(LearningPath).order_by(
        LearningPath.order.asc(), Material.order.asc()
    ).all()
    current_path = "Machine Learning"
    for mat in all_materials:
        prog = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.material_id == mat.id
        ).first()
        is_completed = prog.is_completed if prog else False
        
        quiz_completed = True
        if mat.quiz:
            attempts_count = db.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == mat.quiz.id
            ).count()
            if attempts_count == 0:
                quiz_completed = False

        if not is_completed or not quiz_completed:
            current_path = mat.learning_path.name
            break

    # Find best path
    best_path = _get_best_path(user_id, db)

    # Find lowest quiz score (hardest chapter)
    quiz_logs = db.query(QuizLog).filter(QuizLog.user_id == user_id).all()
    hardest_chapter = None
    hardest_score = None
    if quiz_logs:
        sorted_logs = sorted(quiz_logs, key=lambda x: (-x.attempt, x.score))
        lowest_log = sorted_logs[0]
        mat = db.query(Material).filter(Material.id == lowest_log.material_id).first()
        if mat:
            hardest_chapter = f"Bab {mat.order}: {mat.title} ({mat.learning_path.name})"
            hardest_score = lowest_log.score

    # Prepare features with personalization context metadata
    features_payload = dict(features)
    features_payload["full_name"] = full_name
    features_payload["current_path"] = current_path
    features_payload["best_path"] = best_path
    features_payload["hardest_chapter"] = hardest_chapter
    features_payload["hardest_score"] = hardest_score

    # Step 5: LLM Insight → why_this_type, strength, weakness, motivation (Groq)
    llm_result = generate_llm_insight(learning_type, features_payload)
    why_this_type = llm_result["why_this_type"]
    strength = llm_result["strength"]
    weakness = llm_result["weakness"]
    motivation = llm_result["motivation"]
    insight_source = llm_result["source"]
    logger.info(f"LLM insight generated (source={insight_source}) for user {user_id}")

    # Build backward-compatible insight_text
    insight_text = f"Why This Type: {why_this_type} Strength: {strength} Weakness: {weakness} Motivation: {motivation}"

    # Step 6: Hybrid Recommendation → ranked list
    stats = _get_user_stats(user_id, db)
    recommendations = generate_recommendations(
        user_id, learning_type, features, stats, db
    )

    # Step 7: Save to database (cache)
    recommendation_json = json.dumps(recommendations, ensure_ascii=False)

    new_insight = Insight(
        user_id=user_id,
        learning_type=learning_type,
        reason=why_this_type,  # saved directly to reason column
        strength=strength,
        weakness=weakness,
        motivation=motivation,
        insight_text=insight_text,
        recommendation=recommendation_json,
        cluster_id=cluster_id,
        generated_at=datetime.now(timezone.utc),
    )
    db.add(new_insight)
    db.commit()
    db.refresh(new_insight)

    # Save recommendations to dedicated table
    save_recommendations(new_insight.id, user_id, recommendations, db)

    # Build response
    recommendation_items = [
        RecommendationItem(**rec) for rec in recommendations
    ]

    return GenerateInsightResponse(
        success=True,
        message=f"Insight berhasil dibuat (AI Cluster {cluster_id}, LLM source: {insight_source})",
        insight=InsightResponse(
            learning_type=new_insight.learning_type,
            reason=new_insight.reason,
            strength=new_insight.strength,
            weakness=new_insight.weakness,
            motivation=new_insight.motivation,
            insight_text=new_insight.insight_text,
            recommendations=recommendation_items,
            cluster_id=new_insight.cluster_id,
            generated_at=new_insight.generated_at,
            features=features,
        ),
    )
