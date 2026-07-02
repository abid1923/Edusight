"""
Export routes: download AI dataset logs as CSV files.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import CurrentAdmin
from app.services import export_service

router = APIRouter(prefix="/api/export", tags=["Export Dataset"])


@router.get("/login-log")
def download_login_log(current_admin: CurrentAdmin, db: Session = Depends(get_db)):
    """Export login_log table as .csv file."""
    output = export_service.export_login_log(db)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=login_log.csv"},
    )


@router.get("/learning-activity")
def download_learning_activity(current_admin: CurrentAdmin, db: Session = Depends(get_db)):
    """Export learning_activity table as .csv file."""
    output = export_service.export_learning_activity(db)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=learning_activity.csv"},
    )


@router.get("/quiz-log")
def download_quiz_log(current_admin: CurrentAdmin, db: Session = Depends(get_db)):
    """Export quiz_log table as .csv file."""
    output = export_service.export_quiz_log(db)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=quiz_log.csv"},
    )


@router.get("/completion-log")
def download_completion_log(current_admin: CurrentAdmin, db: Session = Depends(get_db)):
    """Export completion_log table as .csv file."""
    output = export_service.export_completion_log(db)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=completion_log.csv"},
    )


@router.get("/insights")
def download_insights(current_admin: CurrentAdmin, db: Session = Depends(get_db)):
    """Export insights table combined with user features as .csv file."""
    output = export_service.export_insights(db)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=insights.csv"},
    )
