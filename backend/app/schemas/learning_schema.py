"""
Learning path, material, quiz, and progress schemas.
"""

from datetime import datetime

from pydantic import BaseModel, Field


# ─── Learning Path ─────────────────────────────────────────────
class LearningPathResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    order: int
    total_materials: int = 0
    completed_materials: int = 0

    class Config:
        from_attributes = True


# ─── Material ──────────────────────────────────────────────────
class MaterialResponse(BaseModel):
    id: int
    learning_path_id: int
    title: str
    description: str | None = None
    order: int
    is_completed: bool = False
    is_unlocked: bool = False
    has_quiz: bool = False
    last_score: float | None = None
    best_score: float | None = None
    attempts_count: int = 0

    class Config:
        from_attributes = True


class MaterialDetailResponse(BaseModel):
    id: int
    learning_path_id: int
    title: str
    description: str | None = None
    order: int
    is_completed: bool = False
    time_spent_seconds: int = 0
    quiz_id: int | None = None

    class Config:
        from_attributes = True


# ─── Start Learning ───────────────────────────────────────────
class StartLearningResponse(BaseModel):
    activity_id: int
    material_id: int
    path: str
    start_time: datetime
    message: str


# ─── Progress ─────────────────────────────────────────────────
class MarkCompleteRequest(BaseModel):
    time_spent_seconds: int = Field(0, ge=0, description="Waktu yang dihabiskan (detik)")


class ProgressResponse(BaseModel):
    material_id: int
    is_completed: bool
    completed_at: datetime | None = None
    time_spent_seconds: int = 0

    class Config:
        from_attributes = True


class OverallProgressResponse(BaseModel):
    total_paths: int
    total_materials: int
    completed_materials: int
    overall_percent: float
    paths: list[LearningPathResponse]


# ─── Quiz ──────────────────────────────────────────────────────
class QuizQuestionResponse(BaseModel):
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    class Config:
        from_attributes = True


class QuizResponse(BaseModel):
    quiz_id: int
    title: str
    material_id: int
    questions: list[QuizQuestionResponse]
    attempts_used: int
    max_attempts: int


class AnswerItem(BaseModel):
    question_id: int
    answer: str = Field(..., pattern="^[abcdABCD]$", description="Jawaban: a, b, c, atau d")


class QuizSubmitRequest(BaseModel):
    answers: list[AnswerItem]


class QuizResultResponse(BaseModel):
    quiz_id: int
    attempt_number: int
    score: float
    correct_answers: int
    total_questions: int
    passed: bool
    attempts_remaining: int
