"""Learning service for handling learning paths, materials, progress tracking, and quizzes."""

import random
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import MAX_QUIZ_ATTEMPTS
from app.models.activity_model import (
    LearningPath,
    Material,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    UserProgress,
)
from app.models.logging_model import CompletionLog, LearningActivity, QuizLog
from app.models.user_model import User
from app.schemas.learning_schema import (
    AnswerItem,
    LearningPathResponse,
    MaterialDetailResponse,
    MaterialResponse,
    OverallProgressResponse,
    QuizQuestionResponse,
    QuizResponse,
    QuizResultResponse,
    StartLearningResponse,
)


# ─── Learning Paths ───────────────────────────────────────────

def get_learning_paths(user_id: int, db: Session) -> list[LearningPathResponse]:
    """Get all learning paths with user's progress stats."""
    paths = db.query(LearningPath).order_by(LearningPath.order).all()
    result = []

    for path in paths:
        total = len(path.materials)
        completed = (
            db.query(UserProgress)
            .filter(
                UserProgress.user_id == user_id,
                UserProgress.material_id.in_([m.id for m in path.materials]),
                UserProgress.is_completed == True,
            )
            .count()
        )
        result.append(
            LearningPathResponse(
                id=path.id,
                name=path.name,
                description=path.description,
                order=path.order,
                total_materials=total,
                completed_materials=completed,
            )
        )

    return result


# ─── Materials ─────────────────────────────────────────────────

def get_materials(path_id: int, user_id: int, db: Session) -> list[MaterialResponse]:
    """Get all materials in a path with sequential unlock and quiz attempt stats."""
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path tidak ditemukan")

    materials = (
        db.query(Material)
        .filter(Material.learning_path_id == path_id)
        .order_by(Material.order)
        .all()
    )

    result = []
    previous_completed = True  # First material is always unlocked

    for mat in materials:
        progress = (
            db.query(UserProgress)
            .filter(UserProgress.user_id == user_id, UserProgress.material_id == mat.id)
            .first()
        )
        is_completed = progress.is_completed if progress else False
        is_unlocked = previous_completed

        attempts_count = 0
        last_score = None
        best_score = None
        if mat.quiz:
            attempts = (
                db.query(QuizAttempt)
                .filter(QuizAttempt.user_id == user_id, QuizAttempt.quiz_id == mat.quiz.id)
                .order_by(QuizAttempt.attempt_number.asc())
                .all()
            )
            attempts_count = len(attempts)
            if attempts_count > 0:
                last_score = round(attempts[-1].score, 2)
                best_score = round(max(att.score for att in attempts), 2)

        result.append(
            MaterialResponse(
                id=mat.id,
                learning_path_id=mat.learning_path_id,
                title=mat.title,
                description=mat.description,
                order=mat.order,
                is_completed=is_completed,
                is_unlocked=is_unlocked,
                has_quiz=mat.quiz is not None,
                last_score=last_score,
                best_score=best_score,
                attempts_count=attempts_count,
            )
        )
        previous_completed = is_completed

    return result


def get_material_detail(material_id: int, user_id: int, db: Session) -> MaterialDetailResponse:
    """Get detailed info for a single material."""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materi tidak ditemukan")

    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.material_id == material_id)
        .first()
    )

    return MaterialDetailResponse(
        id=material.id,
        learning_path_id=material.learning_path_id,
        title=material.title,
        description=material.description,
        order=material.order,
        is_completed=progress.is_completed if progress else False,
        time_spent_seconds=progress.time_spent_seconds if progress else 0,
        quiz_id=material.quiz.id if material.quiz else None,
    )


# ─── Start Learning (Activity Logging) ────────────────────────

def start_learning(material_id: int, user_id: int, db: Session) -> StartLearningResponse:
    """
    Record the start of a learning session.
    Writes to learning_activity table with start_time.
    """
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materi tidak ditemukan")

    # Get learning path name for the 'path' field
    path = db.query(LearningPath).filter(LearningPath.id == material.learning_path_id).first()

    now = datetime.now(timezone.utc)

    activity = LearningActivity(
        user_id=user_id,
        material_id=material_id,
        path=path.name,
        start_time=now,
        end_time=None,  # Will be filled when material is completed
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    return StartLearningResponse(
        activity_id=activity.id,
        material_id=material_id,
        path=path.name,
        start_time=now,
        message=f"Sesi belajar '{material.title}' dimulai",
    )


# ─── Complete Material ────────────────────────────────────────

def mark_material_complete(material_id: int, user_id: int, time_spent: int, db: Session) -> dict:
    """Mark a learning material as completed and record the duration."""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materi tidak ditemukan")

    # Check sequential unlock: all previous materials must be completed
    previous_materials = (
        db.query(Material)
        .filter(
            Material.learning_path_id == material.learning_path_id,
            Material.order < material.order,
        )
        .all()
    )

    for prev_mat in previous_materials:
        prev_progress = (
            db.query(UserProgress)
            .filter(UserProgress.user_id == user_id, UserProgress.material_id == prev_mat.id)
            .first()
        )
        if not prev_progress or not prev_progress.is_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Materi sebelumnya '{prev_mat.title}' belum diselesaikan",
            )

    # Get learning path name
    path = db.query(LearningPath).filter(LearningPath.id == material.learning_path_id).first()
    now = datetime.now(timezone.utc)

    # Create or update UserProgress (for unlock logic)
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.material_id == material_id)
        .first()
    )

    if progress:
        progress.is_completed = True
        progress.completed_at = now
        progress.time_spent_seconds += time_spent
    else:
        progress = UserProgress(
            user_id=user_id,
            material_id=material_id,
            is_completed=True,
            completed_at=now,
            time_spent_seconds=time_spent,
        )
        db.add(progress)

    # Log to completion_log (AI dataset compatible) if it doesn't already exist
    existing_completion = db.query(CompletionLog).filter(
        CompletionLog.user_id == user_id,
        CompletionLog.material_id == material_id
    ).first()
    if not existing_completion:
        completion = CompletionLog(
            user_id=user_id,
            material_id=material_id,
            path=path.name,
            completed_at=now,
        )
        db.add(completion)

    # Update learning_activity end_time (find the latest open session)
    open_activity = (
        db.query(LearningActivity)
        .filter(
            LearningActivity.user_id == user_id,
            LearningActivity.material_id == material_id,
            LearningActivity.end_time == None,
        )
        .order_by(LearningActivity.start_time.desc())
        .first()
    )

    if open_activity:
        open_activity.end_time = now
    else:
        # If no open session, create a complete activity record
        activity = LearningActivity(
            user_id=user_id,
            material_id=material_id,
            path=path.name,
            start_time=now,
            end_time=now,
        )
        db.add(activity)

    db.commit()

    return {"message": f"Materi '{material.title}' berhasil diselesaikan"}


# ─── Quiz ──────────────────────────────────────────────────────

def get_quiz(material_id: int, user_id: int, db: Session) -> QuizResponse:
    """Get quiz for a material with shuffled questions."""
    quiz = db.query(Quiz).filter(Quiz.material_id == material_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz tidak ditemukan untuk materi ini")

    # Check attempt count
    attempts_used = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id, QuizAttempt.quiz_id == quiz.id)
        .count()
    )

    # Get questions and shuffle
    questions = list(quiz.questions)
    random.shuffle(questions)

    question_responses = [
        QuizQuestionResponse(
            id=q.id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
        )
        for q in questions
    ]

    return QuizResponse(
        quiz_id=quiz.id,
        title=quiz.title,
        material_id=material_id,
        questions=question_responses,
        attempts_used=attempts_used,
        max_attempts=MAX_QUIZ_ATTEMPTS,
    )


def submit_quiz(quiz_id: int, user_id: int, answers: list[AnswerItem], db: Session) -> QuizResultResponse:
    """Submit quiz answers, calculate score, and log the attempt details."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz tidak ditemukan")

    # Check attempt limit
    attempts_used = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id, QuizAttempt.quiz_id == quiz_id)
        .count()
    )

    if attempts_used >= MAX_QUIZ_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sudah mencapai batas maksimal {MAX_QUIZ_ATTEMPTS} attempt",
        )

    # Calculate score
    correct_count = 0
    total_questions = len(quiz.questions)

    # Build lookup for correct answers
    correct_map = {q.id: q.correct_answer.lower() for q in quiz.questions}

    for answer in answers:
        if answer.question_id in correct_map:
            if answer.answer.lower() == correct_map[answer.question_id]:
                correct_count += 1

    score = (correct_count / total_questions * 100) if total_questions > 0 else 0
    attempt_number = attempts_used + 1
    now = datetime.now(timezone.utc)

    # Save to QuizAttempt (app logic, retained for backward compatibility)
    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        score=score,
        total_questions=total_questions,
        correct_answers=correct_count,
        attempt_number=attempt_number,
        completed_at=now,
    )
    db.add(attempt)

    # Get material and path info for quiz_log
    material = db.query(Material).filter(Material.id == quiz.material_id).first()
    path = db.query(LearningPath).filter(LearningPath.id == material.learning_path_id).first()

    # Log to quiz_log (AI dataset compatible)
    quiz_log = QuizLog(
        user_id=user_id,
        material_id=quiz.material_id,
        path=path.name,
        score=score,
        attempt=attempt_number,
        timestamp=now,
    )
    db.add(quiz_log)

    # Automatically mark the material as completed when user submits quiz
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.material_id == quiz.material_id)
        .first()
    )
    if progress:
        progress.is_completed = True
        progress.completed_at = now
    else:
        progress = UserProgress(
            user_id=user_id,
            material_id=quiz.material_id,
            is_completed=True,
            completed_at=now,
            time_spent_seconds=60,  # fallback duration
        )
        db.add(progress)

    existing_completion = db.query(CompletionLog).filter(
        CompletionLog.user_id == user_id,
        CompletionLog.material_id == quiz.material_id
    ).first()
    if not existing_completion:
        completion = CompletionLog(
            user_id=user_id,
            material_id=quiz.material_id,
            path=path.name,
            completed_at=now,
        )
        db.add(completion)

    db.commit()

    return QuizResultResponse(
        quiz_id=quiz_id,
        attempt_number=attempt_number,
        score=round(score, 2),
        correct_answers=correct_count,
        total_questions=total_questions,
        passed=score >= 70,
        attempts_remaining=MAX_QUIZ_ATTEMPTS - attempt_number,
    )


# ─── Overall Progress ─────────────────────────────────────────

def get_overall_progress(user_id: int, db: Session) -> OverallProgressResponse:
    """Get overall progress across all learning paths."""
    paths = get_learning_paths(user_id, db)
    total_materials = sum(p.total_materials for p in paths)
    completed_materials = sum(p.completed_materials for p in paths)

    overall_percent = (completed_materials / total_materials * 100) if total_materials > 0 else 0

    return OverallProgressResponse(
        total_paths=len(paths),
        total_materials=total_materials,
        completed_materials=completed_materials,
        overall_percent=round(overall_percent, 2),
        paths=paths,
    )
