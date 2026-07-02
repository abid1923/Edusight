"""Personalized recommendation system combining internal materials and external resources."""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.activity_model import LearningPath, Material, UserProgress
from app.models.insight_model import Recommendation
from app.models.logging_model import QuizLog

logger = logging.getLogger(__name__)


# ─── External Resource Catalog ────────────────────────────────
# Loaded dynamically from JSON, with fallback
EXTERNAL_RESOURCES = [
    {
        "title": "Python untuk Pemula - Tutorial Lengkap",
        "url": "https://youtube.com/placeholder-python-beginner",
        "resource_type": "youtube",
        "path_name": "Python Basics",
        "level": "beginner",
        "tags": ["python", "beginner", "fundamental"],
    },
    {
        "title": "Memahami REST API dari Nol",
        "url": "https://youtube.com/placeholder-rest-api",
        "resource_type": "youtube",
        "path_name": "Backend Development",
        "level": "beginner",
        "tags": ["api", "rest", "backend"],
    },
    {
        "title": "FastAPI Crash Course",
        "url": "https://youtube.com/placeholder-fastapi",
        "resource_type": "youtube",
        "path_name": "Backend Development",
        "level": "intermediate",
        "tags": ["fastapi", "python", "backend"],
    },
    {
        "title": "Panduan Lengkap Machine Learning untuk Pemula",
        "url": "https://example.com/placeholder-ml-guide",
        "resource_type": "article",
        "path_name": "Machine Learning",
        "level": "beginner",
        "tags": ["machine-learning", "ai", "beginner"],
    },
    {
        "title": "Database Design Best Practices",
        "url": "https://example.com/placeholder-db-design",
        "resource_type": "article",
        "path_name": "Database",
        "level": "intermediate",
        "tags": ["database", "sql", "design"],
    },
    {
        "title": "Authentication & Authorization Tutorial",
        "url": "https://youtube.com/placeholder-auth",
        "resource_type": "tutorial",
        "path_name": "Backend Development",
        "level": "intermediate",
        "tags": ["auth", "jwt", "security"],
    },
    {
        "title": "Git & Version Control Essentials",
        "url": "https://youtube.com/placeholder-git",
        "resource_type": "youtube",
        "path_name": "Development Tools",
        "level": "beginner",
        "tags": ["git", "version-control", "tools"],
    },
    {
        "title": "Advanced Python: Decorators & Generators",
        "url": "https://example.com/placeholder-advanced-python",
        "resource_type": "tutorial",
        "path_name": "Python Advanced",
        "level": "advanced",
        "tags": ["python", "advanced", "decorators"],
    },
]

try:
    import os
    import json
    _base_dir = os.path.dirname(os.path.abspath(__file__))
    _rekomendasi_dir = os.path.abspath(os.path.join(_base_dir, "../../../frontend/public/content/rekomendasi"))
    
    _files_map = {
        "Machine Learning": "ml_rekomendasi_link.json",
        "Frontend Development": "frontend_rekomendasi_link.json",
        "Backend Development": "backend_rekomendasi_link.json"
    }
    
    _loaded_resources = []
    for _path_name, _filename in _files_map.items():
        _filepath = os.path.join(_rekomendasi_dir, _filename)
        if os.path.exists(_filepath):
            with open(_filepath, "r", encoding="utf-8") as _f:
                _data = json.load(_f)
            _recs = _data.get("rekomendasi", {})
            for _level in ["beginner", "intermediate", "advanced"]:
                _level_data = _recs.get(_level, {})
                _links = _level_data.get("link", [])
                for _link in _links:
                    _loaded_resources.append({
                        "title": _link.get("judul"),
                        "url": _link.get("url"),
                        "resource_type": _link.get("tipe", "website"),
                        "path_name": _path_name,
                        "level": _level,
                        "tags": _link.get("bab_relevan", []),
                        "description": _link.get("deskripsi"),
                    })
    if _loaded_resources:
        EXTERNAL_RESOURCES = _loaded_resources
except Exception as _e:
    pass


def _calculate_path_progress(user_id: int, db: Session) -> list[dict]:
    """Calculate progress per learning path for a user."""
    paths = db.query(LearningPath).order_by(LearningPath.order).all()
    result = []

    for path in paths:
        mat_ids = [m.id for m in path.materials]
        total = len(mat_ids)
        if total == 0:
            continue

        completed = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.material_id.in_(mat_ids),
            UserProgress.is_completed == True,
        ).count()

        progress_pct = (completed / total * 100) if total > 0 else 0

        # Get uncompleted materials
        completed_ids = [
            p.material_id for p in db.query(UserProgress).filter(
                UserProgress.user_id == user_id,
                UserProgress.material_id.in_(mat_ids),
                UserProgress.is_completed == True,
            ).all()
        ]
        uncompleted = [m for m in path.materials if m.id not in completed_ids]

        result.append({
            "path_id": path.id,
            "path_name": path.name,
            "total": total,
            "completed": completed,
            "progress_pct": progress_pct,
            "uncompleted_materials": uncompleted,
        })

    return result


def _score_internal_material(
    material, path_info: dict, learning_type: str, features: dict
) -> dict:
    """Score an internal material for recommendation ranking."""
    score = 0
    reasons = []

    progress_pct = path_info["progress_pct"]
    avg_quiz_score = features.get("avg_quiz_score", 0)
    completion_rate = features.get("completion_rate", 0)

    # Factor 1: Uncompleted material gets higher score
    score += 30
    reasons.append("materi belum diselesaikan")

    # Factor 2: Learning type weighting
    if learning_type == "Passive Learner":
        # Prioritize beginner/early materials
        if material.order <= 2:
            score += 25
            reasons.append("cocok untuk membangun dasar")
    elif learning_type == "Moderate Learner":
        # Prioritize materials in-progress paths
        if 30 < progress_pct < 80:
            score += 20
            reasons.append("melanjutkan path yang sedang berjalan")
    elif learning_type == "Active Learner":
        # Prioritize advanced/unstarted paths
        if progress_pct < 30:
            score += 20
            reasons.append("eksplorasi path baru")

    # Factor 3: Quiz performance based
    if avg_quiz_score < 60:
        # Low score → prioritize earlier materials (review)
        if material.order <= 2:
            score += 15
            reasons.append("review dasar untuk meningkatkan pemahaman")
    elif avg_quiz_score >= 80:
        # High score → advance to later materials
        if material.order >= 3:
            score += 15
            reasons.append("siap untuk materi lanjutan")

    # Factor 4: Completion rate based priority
    if completion_rate < 30:
        score += 10  # Boost for low completion users
        reasons.append("meningkatkan progress belajar")

    # Priority assignment
    if score >= 50:
        priority = "high"
    elif score >= 30:
        priority = "medium"
    else:
        priority = "low"

    return {
        "title": material.title,
        "description": material.description or f"Materi dari path {path_info['path_name']}",
        "url": None,
        "resource_type": "internal",
        "reason": ". ".join(reasons[:2]).capitalize() if reasons else "Materi yang direkomendasikan",
        "priority": priority,
        "path_name": path_info["path_name"],
        "score": score,
    }


def _score_external_resource(
    resource: dict, learning_type: str, features: dict, path_progress: list[dict]
) -> dict:
    """Score an external resource for recommendation ranking."""
    score = 0
    reasons = []

    avg_quiz_score = features.get("avg_quiz_score", 0)
    completion_rate = features.get("completion_rate", 0)
    level = resource.get("level", "beginner")

    # Factor 1: Level matching based on learning type
    if learning_type == "Passive Learner" and level == "beginner":
        score += 25
        reasons.append("resource level cocok untuk memulai")
    elif learning_type == "Moderate Learner" and level in ("beginner", "intermediate"):
        score += 20
        reasons.append("level sesuai untuk pengembangan")
    elif learning_type == "Active Learner" and level in ("intermediate", "advanced"):
        score += 25
        reasons.append("tantangan level yang sesuai")

    # Factor 2: Path relevance
    for pp in path_progress:
        if pp["path_name"].lower() in resource.get("path_name", "").lower():
            if pp["progress_pct"] < 100:
                score += 15
                reasons.append(f"mendukung path {pp['path_name']}")
            break

    # Factor 3: Quiz score alignment
    if avg_quiz_score < 50 and level == "beginner":
        score += 10
        reasons.append("membantu memperkuat fundamental")
    elif avg_quiz_score >= 75 and level in ("intermediate", "advanced"):
        score += 10
        reasons.append("siap untuk tingkat yang lebih tinggi")

    # Factor 4: Resource type variety
    if resource["resource_type"] == "youtube":
        score += 5  # Slight boost for video content (more engaging)

    # Priority assignment
    if score >= 40:
        priority = "high"
    elif score >= 20:
        priority = "medium"
    else:
        priority = "low"

    return {
        "title": resource["title"],
        "description": resource.get("description"),
        "url": resource["url"],
        "resource_type": resource["resource_type"],
        "reason": ". ".join(reasons[:2]).capitalize() if reasons else "Resource yang relevan",
        "priority": priority,
        "path_name": resource.get("path_name"),
        "score": score,
    }


def generate_recommendations(
    user_id: int,
    learning_type: str,
    features: dict,
    stats: dict,
    db: Session,
    max_recommendations: int = 6,
) -> list[dict]:
    """Generate and rank personalized internal and external recommendations."""
    all_scored = []

    # ─── Internal Material Recommendations ─────────────────────
    path_progress = _calculate_path_progress(user_id, db)

    for pp in path_progress:
        for material in pp["uncompleted_materials"]:
            scored = _score_internal_material(material, pp, learning_type, features)
            all_scored.append(scored)

    # ─── External Resource Recommendations ─────────────────────
    for resource in EXTERNAL_RESOURCES:
        scored = _score_external_resource(resource, learning_type, features, path_progress)
        all_scored.append(scored)

    # ─── Rank & Select Top N ───────────────────────────────────
    all_scored.sort(key=lambda x: x["score"], reverse=True)

    # Balance internal and external — aim for a mix
    internal = [r for r in all_scored if r["resource_type"] == "internal"]
    external = [r for r in all_scored if r["resource_type"] != "internal"]

    # Take top from each, then fill remaining
    half = max_recommendations // 2
    selected = internal[:half] + external[:half]

    # Fill remaining slots from highest scored overall
    remaining = max_recommendations - len(selected)
    if remaining > 0:
        already_titles = {r["title"] for r in selected}
        for r in all_scored:
            if r["title"] not in already_titles:
                selected.append(r)
                already_titles.add(r["title"])
                if len(selected) >= max_recommendations:
                    break

    # Final sort by score
    selected.sort(key=lambda x: x["score"], reverse=True)

    logger.info(
        f"Generated {len(selected)} recommendations for user {user_id} "
        f"(type={learning_type}, internal={len(internal)}, external={len(external)})"
    )

    return selected


def save_recommendations(
    insight_id: int, user_id: int, recommendations: list[dict], db: Session
) -> list[Recommendation]:
    """Save the generated recommendations to the database."""
    saved = []
    for rec in recommendations:
        db_rec = Recommendation(
            insight_id=insight_id,
            user_id=user_id,
            title=rec["title"],
            description=rec.get("description"),
            url=rec.get("url"),
            resource_type=rec.get("resource_type", "internal"),
            reason=rec.get("reason"),
            priority=rec.get("priority", "medium"),
            path_name=rec.get("path_name"),
            score=rec.get("score"),
        )
        db.add(db_rec)
        saved.append(db_rec)

    db.commit()
    return saved
