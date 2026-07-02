"""
Export service.
Exports AI-compatible logging data to CSV (.csv) files.
Supports: login_log, learning_activity, quiz_log, completion_log.
"""

import csv
import io
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.logging_model import CompletionLog, LearningActivity, LoginLog, QuizLog


def _create_csv_from_rows(headers: list[str], rows: list[list]) -> io.BytesIO:
    """Create a CSV from headers and row data."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=",", lineterminator="\n")

    # Write headers
    writer.writerow(headers)

    # Write data rows
    writer.writerows(rows)

    # Convert string stream to bytes stream
    bytes_output = io.BytesIO(output.getvalue().encode("utf-8"))
    bytes_output.seek(0)
    return bytes_output


def export_login_log(db: Session) -> io.BytesIO:
    """Export login_log table to CSV."""
    logs = db.query(LoginLog).order_by(LoginLog.timestamp).all()

    headers = ["id", "user_id", "timestamp"]
    rows = [
        [log.id, log.user_id, log.timestamp.isoformat() if log.timestamp else None]
        for log in logs
    ]

    return _create_csv_from_rows(headers, rows)


def export_learning_activity(db: Session) -> io.BytesIO:
    """Export learning_activity table to CSV."""
    activities = db.query(LearningActivity).order_by(LearningActivity.start_time).all()

    headers = ["id", "user_id", "material_id", "path", "start_time", "end_time"]
    rows = [
        [
            a.id, a.user_id, a.material_id, a.path,
            a.start_time.isoformat() if a.start_time else None,
            a.end_time.isoformat() if a.end_time else None,
        ]
        for a in activities
    ]

    return _create_csv_from_rows(headers, rows)


def export_quiz_log(db: Session) -> io.BytesIO:
    """Export quiz_log table to CSV."""
    logs = db.query(QuizLog).order_by(QuizLog.timestamp).all()

    headers = ["id", "user_id", "material_id", "path", "score", "attempt", "timestamp"]
    rows = [
        [
            log.id, log.user_id, log.material_id, log.path,
            log.score, log.attempt,
            log.timestamp.isoformat() if log.timestamp else None,
        ]
        for log in logs
    ]

    return _create_csv_from_rows(headers, rows)


def export_completion_log(db: Session) -> io.BytesIO:
    """Export completion_log table to CSV."""
    logs = db.query(CompletionLog).order_by(CompletionLog.completed_at).all()

    headers = ["id", "user_id", "material_id", "path", "completed_at"]
    rows = [
        [
            log.id, log.user_id, log.material_id, log.path,
            log.completed_at.isoformat() if log.completed_at else None,
        ]
        for log in logs
    ]

    return _create_csv_from_rows(headers, rows)


def export_insights(db: Session) -> io.BytesIO:
    """Export insights table combined with user features to CSV."""
    from app.models.insight_model import Insight
    from app.models.user_model import User
    from app.ai.feature_engineering import extract_features

    insights = db.query(Insight).order_by(Insight.generated_at).all()

    headers = [
        "id", "user_id", "username", "cluster_id", "learning_type",
        "total_login", "total_study_minutes", "completion_rate",
        "avg_quiz_score", "avg_attempts_per_material", "generated_at"
    ]
    
    rows = []
    for insight in insights:
        user = db.query(User).filter(User.id == insight.user_id).first()
        username = user.username if user else f"user_{insight.user_id}"
        
        # Extract features for this user
        features = extract_features(insight.user_id, db)
        
        rows.append([
            insight.id,
            insight.user_id,
            username,
            insight.cluster_id,
            insight.learning_type,
            features.get("total_login", 0),
            features.get("total_study_minutes", 0.0),
            features.get("completion_rate", 0.0),
            features.get("avg_quiz_score", 0.0),
            features.get("avg_attempts_per_material", 1.0),
            insight.generated_at.isoformat() if insight.generated_at else None
        ])

    return _create_csv_from_rows(headers, rows)
