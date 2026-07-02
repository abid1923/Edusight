"""
User routes: profile and dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser
from app.models.activity_model import QuizAttempt, UserProgress, LearningPath, Material
from app.models.logging_model import CompletionLog, LearningActivity, LoginLog, QuizLog
from app.schemas.user_schema import DashboardResponse, UserResponse, UserUpdateRequest

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: CurrentUser):
    """Get current user's profile."""
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    request: UserUpdateRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.email is not None:
        # Check email uniqueness
        from app.models.user_model import User
        existing = db.query(User).filter(User.email == request.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email sudah digunakan")
        current_user.email = request.email
    if request.username is not None:
        # Check username uniqueness
        from app.models.user_model import User
        existing = db.query(User).filter(User.username == request.username, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username sudah digunakan")
        current_user.username = request.username
    if request.password is not None:
        from app.utils.hashing import hash_password
        current_user.hashed_password = hash_password(request.password)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Get dashboard statistics for current user."""
    user_id = current_user.id

    completed = db.query(UserProgress).filter(
        UserProgress.user_id == user_id, UserProgress.is_completed == True
    ).count()

    quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).count()

    total_paths = db.query(LearningPath).count()

    # Calculate overall progress
    total_materials = db.query(Material).count()
    overall_pct = (completed / total_materials * 100) if total_materials > 0 else 0

    # Recent activities from dedicated logging tables (last 10)
    recent_list = []

    # Recent logins
    recent_logins = db.query(LoginLog).filter(
        LoginLog.user_id == user_id
    ).order_by(LoginLog.timestamp.desc()).limit(5).all()
    for log in recent_logins:
        recent_list.append({
            "type": "login",
            "metadata": {"timestamp": log.timestamp.isoformat() if log.timestamp else None},
            "created_at": log.timestamp.isoformat() if log.timestamp else None,
        })

    # Recent completions
    recent_completions = db.query(CompletionLog).filter(
        CompletionLog.user_id == user_id
    ).order_by(CompletionLog.completed_at.desc()).limit(5).all()
    for log in recent_completions:
        recent_list.append({
            "type": "material_complete",
            "metadata": {"material_id": log.material_id, "path": log.path},
            "created_at": log.completed_at.isoformat() if log.completed_at else None,
        })

    # Recent quiz logs
    recent_quizzes = db.query(QuizLog).filter(
        QuizLog.user_id == user_id
    ).order_by(QuizLog.timestamp.desc()).limit(5).all()
    for log in recent_quizzes:
        recent_list.append({
            "type": "quiz_attempt",
            "metadata": {"material_id": log.material_id, "path": log.path, "score": log.score, "attempt": log.attempt},
            "created_at": log.timestamp.isoformat() if log.timestamp else None,
        })

    # Sort recent activities by created_at desc and take last 10
    recent_list.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    recent_list = recent_list[:10]

    # Path progress
    paths = db.query(LearningPath).order_by(LearningPath.order).all()
    path_progress = []
    for p in paths:
        mat_ids = [m.id for m in p.materials]
        p_completed = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.material_id.in_(mat_ids),
            UserProgress.is_completed == True,
        ).count() if mat_ids else 0
        path_progress.append({
            "path_id": p.id, "path_name": p.name,
            "total": len(mat_ids), "completed": p_completed,
            "percent": round(p_completed / len(mat_ids) * 100, 2) if mat_ids else 0,
        })

    # Fetch latest AI Insight
    from app.models.insight_model import Insight, Recommendation
    from app.ai.feature_engineering import extract_features
    latest_insight = db.query(Insight).filter(Insight.user_id == user_id).order_by(Insight.generated_at.desc()).first()

    features = extract_features(user_id, db)

    if latest_insight:
        learning_type = latest_insight.learning_type
        reason = latest_insight.reason or ""
        strength = latest_insight.strength or ""
        weakness = latest_insight.weakness or ""
        motivation = latest_insight.motivation or ""

        # Fetch recommendations from DB
        recs = db.query(Recommendation).filter(
            Recommendation.insight_id == latest_insight.id
        ).order_by(Recommendation.score.desc()).all()

        recommendation_summary = [
            {
                "title": r.title,
                "description": r.description,
                "url": r.url,
                "resource_type": r.resource_type,
                "reason": r.reason,
                "priority": r.priority,
                "path_name": r.path_name,
                "score": r.score,
            }
            for r in recs
        ]
    else:
        # Fallback fields for users without an active AI Insight
        learning_type = "Undetermined"
        reason = "Belum cukup aktivitas untuk menghasilkan insight. Teruslah belajar untuk membuka analisis tipe belajarmu!"
        strength = "Mulai pelajari materi baru untuk menganalisis kekuatan belajarmu."
        weakness = "Performa belajarmu akan dianalisis setelah kamu mencoba beberapa kuis."
        motivation = "Langkah kecil setiap hari akan membantumu mencapai pemahaman yang luar biasa. Semangat belajar!"

        # Fallback intelligent recommendations based on uncompleted basic materials
        recommendation_summary = []
        for p in paths:
            if p.materials:
                first_mat = p.materials[0]
                # Check if completed
                is_comp = db.query(UserProgress).filter(
                    UserProgress.user_id == user_id,
                    UserProgress.material_id == first_mat.id,
                    UserProgress.is_completed == True,
                ).first()
                if not is_comp:
                    recommendation_summary.append({
                        "title": first_mat.title,
                        "description": f"Materi dasar dari path {p.name}",
                        "url": None,
                        "resource_type": "internal",
                        "reason": "Mulai dari materi dasar untuk membangun fondasi.",
                        "priority": "high",
                        "path_name": p.name,
                        "score": 100,
                    })

    # Find next uncompleted material
    all_materials = db.query(Material).join(LearningPath).order_by(
        LearningPath.order.asc(), Material.order.asc()
    ).all()

    next_material_data = None
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
            next_material_data = {
                "pathId": mat.learning_path_id,
                "pathName": mat.learning_path.name,
                "materialId": mat.id,
                "chapterName": f"Bab {mat.order}: {mat.title}",
                "slideIndex": 0
            }
            break

    return DashboardResponse(
        username=current_user.username,
        learning_type=learning_type,
        reason=reason,
        strength=strength,
        weakness=weakness,
        motivation=motivation,
        progress_summary={
            "total_materials_completed": completed,
            "total_quiz_attempts": quiz_attempts,
            "total_learning_paths": total_paths,
            "overall_progress_percent": round(overall_pct, 2),
            "recent_activities": recent_list,
            "path_progress": path_progress,
            "next_material": next_material_data,
        },
        recommendation_summary=recommendation_summary,
        features=features,
    )

