"""
Learning routes: paths, materials, progress, quizzes, activity logging.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser
from app.schemas.learning_schema import (
    MarkCompleteRequest, MaterialDetailResponse, MaterialResponse,
    LearningPathResponse, OverallProgressResponse, QuizResponse,
    QuizResultResponse, QuizSubmitRequest, StartLearningResponse,
)
from app.services import learning_service

router = APIRouter(prefix="/api/learning", tags=["Learning"])


@router.get("/paths", response_model=list[LearningPathResponse])
def list_learning_paths(current_user: CurrentUser, db: Session = Depends(get_db)):
    """List all learning paths with user progress."""
    return learning_service.get_learning_paths(current_user.id, db)


@router.get("/paths/{path_id}/materials", response_model=list[MaterialResponse])
def list_materials(path_id: int, current_user: CurrentUser, db: Session = Depends(get_db)):
    """List materials for a learning path with unlock/completion status."""
    return learning_service.get_materials(path_id, current_user.id, db)


@router.get("/materials/{material_id}", response_model=MaterialDetailResponse)
def get_material(material_id: int, current_user: CurrentUser, db: Session = Depends(get_db)):
    """Get detailed information for a single material."""
    return learning_service.get_material_detail(material_id, current_user.id, db)


@router.post("/materials/{material_id}/start", response_model=StartLearningResponse)
def start_learning(
    material_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Start a learning session. Records start_time to learning_activity table."""
    return learning_service.start_learning(material_id, current_user.id, db)


@router.post("/materials/{material_id}/complete")
def complete_material(
    material_id: int,
    request: MarkCompleteRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Mark a material as completed. Validates sequential unlock. Logs to completion_log."""
    return learning_service.mark_material_complete(material_id, current_user.id, request.time_spent_seconds, db)


@router.get("/materials/{material_id}/quiz", response_model=QuizResponse)
def get_quiz(material_id: int, current_user: CurrentUser, db: Session = Depends(get_db)):
    """Get quiz for a material with shuffled questions."""
    return learning_service.get_quiz(material_id, current_user.id, db)


@router.post("/quiz/{quiz_id}/submit", response_model=QuizResultResponse)
def submit_quiz(
    quiz_id: int,
    request: QuizSubmitRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Submit quiz answers. Max 3 attempts per quiz. Logs to quiz_log."""
    return learning_service.submit_quiz(quiz_id, current_user.id, request.answers, db)


@router.get("/progress", response_model=OverallProgressResponse)
def get_progress(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Get overall learning progress across all paths."""
    return learning_service.get_overall_progress(current_user.id, db)
