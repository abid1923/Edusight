"""Feature extraction from activity log tables for clustering prediction."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.activity_model import Material, UserProgress
from app.models.logging_model import CompletionLog, LearningActivity, LoginLog, QuizLog


# Feature order HARUS sama dengan notebook modelling (feature_columns.pkl)
FEATURE_COLUMNS = [
    "total_login",
    "total_study_minutes",
    "completion_rate",
    "avg_quiz_score",
    "avg_attempts_per_material",
]

# Total materi sesuai aturan bisnis web: 3 path × 5 materi
TOTAL_MATERIAL = 15


def extract_features(user_id: int, db: Session) -> dict:
    """Extract user kognitif features from activity log tables."""

    # ─── total_login ───────────────────────────────────────────
    # Jumlah login unik per hari (deduplikasi sama seperti notebook)
    # fillna(1): user pasti login minimal sekali
    total_login = (
        db.query(func.count(func.distinct(
            func.date(LoginLog.timestamp)
        )))
        .filter(LoginLog.user_id == user_id)
        .scalar() or 1
    )

    # ─── total_study_minutes ───────────────────────────────────
    # Total durasi belajar dalam menit
    # Dihitung di sisi Python karena SQLite tidak support timestampdiff
    # Filter end_time > start_time untuk menghindari durasi negatif
    study_logs = (
        db.query(LearningActivity.start_time, LearningActivity.end_time)
        .filter(LearningActivity.user_id == user_id)
        .all()
    )
    total_study_minutes = round(
        sum(
            (row.end_time - row.start_time).total_seconds() / 60
            for row in study_logs
            if row.end_time and row.start_time and row.end_time > row.start_time
        ),
        1
    ) if study_logs else 0.0

    # ─── completion_rate ───────────────────────────────────────
    # Persentase materi selesai dari total 15 materi
    # Rumus: (materi_selesai / 15) × 100
    # Nilai selalu kelipatan 6.67 karena berbasis integer materi
    # fillna(0.0): belum ada materi yang selesai
    completed_materials = (
        db.query(CompletionLog)
        .filter(CompletionLog.user_id == user_id)
        .count()
    )
    completion_rate = round(
        completed_materials / TOTAL_MATERIAL * 100, 2
    ) if completed_materials > 0 else 0.0

    # ─── avg_quiz_score ────────────────────────────────────────
    # Rata-rata skor TERTINGGI per materi (bukan rata-rata semua attempt)
    # Langkah:
    #   1. Untuk setiap (user, material): ambil skor tertinggi
    #   2. Rata-rata skor tertinggi tersebut across semua materi
    # Konsisten dengan notebook:
    #   quiz_per_mat.groupby('user_id')['highest_score'].mean()
    # fillna(0.0): belum ada data kuis
    highest_scores_subquery = (
        db.query(
            QuizLog.material_id,
            func.max(QuizLog.score).label("highest_score")
        )
        .filter(QuizLog.user_id == user_id)
        .group_by(QuizLog.material_id)
        .subquery()
    )
    avg_quiz_result = (
        db.query(func.avg(highest_scores_subquery.c.highest_score))
        .scalar()
    )
    avg_quiz_score = round(float(avg_quiz_result), 2) if avg_quiz_result else 0.0

    # ─── avg_attempts_per_material ─────────────────────────────
    # Rata-rata jumlah percobaan kuis per materi
    # Langkah:
    #   1. Untuk setiap (user, material): ambil attempt maksimal
    #   2. Rata-rata attempt maksimal tersebut across semua materi
    # Konsisten dengan notebook:
    #   quiz_per_mat.groupby('user_id')['max_attempt'].mean()
    # fillna(1.0): default minimal 1 attempt jika belum ada data kuis
    max_attempts_subquery = (
        db.query(
            QuizLog.material_id,
            func.max(QuizLog.attempt).label("max_attempt")
        )
        .filter(QuizLog.user_id == user_id)
        .group_by(QuizLog.material_id)
        .subquery()
    )
    avg_attempts_result = (
        db.query(func.avg(max_attempts_subquery.c.max_attempt))
        .scalar()
    )
    avg_attempts_per_material = (
        round(float(avg_attempts_result), 2)
        if avg_attempts_result
        else 1.0
    )

    return {
        "total_login"              : total_login,
        "total_study_minutes"      : total_study_minutes,
        "completion_rate"          : completion_rate,
        "avg_quiz_score"           : avg_quiz_score,
        "avg_attempts_per_material": avg_attempts_per_material,
    }