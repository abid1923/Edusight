"""
Dynamic Learning Type Reasoning.
Hybrid dynamic template system — BUKAN full LLM realtime.

Menghasilkan alasan kenapa user mendapatkan learning type tertentu
berdasarkan actual activity data.

Why hybrid template (bukan LLM)?
- Lebih hemat token
- Lebih cepat
- Tetap personal
- Lebih stabil

Reasoning input:
- total_login
- total_study_minutes
- completion_rate
- avg_quiz_score
- avg_attempts_per_material
"""


def _classify_level(value: float, low: float, high: float) -> str:
    """Classify numeric value into 'rendah', 'cukup', or 'tinggi'."""
    if value < low:
        return "rendah"
    elif value < high:
        return "cukup"
    else:
        return "tinggi"


def _login_description(total_login: int) -> str:
    """Generate dynamic description for login activity."""
    if total_login < 5:
        return "frekuensi login yang masih rendah"
    elif total_login < 15:
        return "frekuensi login yang cukup rutin"
    else:
        return "frekuensi login yang sangat aktif"


def _study_time_description(total_study_minutes: float) -> str:
    """Generate dynamic description for study duration."""
    if total_study_minutes < 30:
        return "durasi belajar yang masih sedikit"
    elif total_study_minutes < 120:
        return "durasi belajar yang cukup aktif"
    else:
        return "durasi belajar yang sangat tinggi dan tekun"


def _completion_description(completion_rate: float) -> str:
    """Generate dynamic description for completion rate."""
    if completion_rate < 30:
        return "tingkat penyelesaian materi yang masih rendah"
    elif completion_rate < 70:
        return "tingkat penyelesaian materi yang cukup baik"
    else:
        return "tingkat penyelesaian materi yang sangat baik"


def _quiz_description(avg_quiz_score: float, avg_attempts_per_material: float) -> str:
    """Generate dynamic description for quiz performance."""
    if avg_quiz_score == 0.0 and avg_attempts_per_material == 1.0:
        return "belum aktif mengerjakan kuis"

    score_level = _classify_level(avg_quiz_score, 50, 75)
    if avg_attempts_per_material < 1.5:
        attempt_desc = "rata-rata percobaan yang minimal"
    elif avg_attempts_per_material < 2.5:
        attempt_desc = "rata-rata percobaan yang wajar"
    else:
        attempt_desc = "rata-rata percobaan yang cukup banyak"

    if score_level == "rendah":
        return f"performa kuis yang perlu ditingkatkan dengan {attempt_desc}"
    elif score_level == "cukup":
        return f"performa kuis yang cukup baik dengan {attempt_desc}"
    else:
        return f"performa kuis yang sangat baik dengan {attempt_desc}"


def generate_reason(learning_type: str, features: dict) -> str:
    """
    Generate dynamic reasoning kenapa user mendapatkan learning type tertentu.

    Reasoning berbeda per user berdasarkan actual activity data.
    Menggunakan hybrid dynamic template — BUKAN static hardcoded text.

    Args:
        learning_type: Tipe belajar dari clustering.
        features: Dictionary dari feature_engineering.extract_features():
            - total_login
            - total_study_minutes
            - completion_rate
            - avg_quiz_score
            - avg_attempts_per_material

    Returns:
        Dynamic reasoning string yang personal untuk user.
    """
    total_login = features.get("total_login", 0)
    total_study_minutes = features.get("total_study_minutes", 0.0)
    completion_rate = features.get("completion_rate", 0)
    avg_quiz_score = features.get("avg_quiz_score", 0)
    avg_attempts_per_material = features.get("avg_attempts_per_material", 1.0)

    # Build dynamic fragments
    login_desc = _login_description(total_login)
    study_desc = _study_time_description(total_study_minutes)
    completion_desc = _completion_description(completion_rate)
    quiz_desc = _quiz_description(avg_quiz_score, avg_attempts_per_material)

    # Compose reason based on learning type + actual data
    if learning_type == "Active Learner":
        reason = (
            f"Tipe belajar ini muncul karena kamu memiliki {login_desc}, "
            f"{study_desc}, {completion_desc}, dan {quiz_desc}. "
            f"Pola ini menunjukkan konsistensi dan komitmen belajar yang kuat."
        )
    elif learning_type == "Moderate Learner":
        # Identify strengths and weaknesses for moderate learners
        strengths = []
        areas_to_improve = []

        if total_login >= 10:
            strengths.append(login_desc)
        else:
            areas_to_improve.append(login_desc)

        if completion_rate >= 50:
            strengths.append(completion_desc)
        else:
            areas_to_improve.append(completion_desc)

        if avg_quiz_score >= 60:
            strengths.append(quiz_desc)
        else:
            areas_to_improve.append(quiz_desc)

        if strengths and areas_to_improve:
            reason = (
                f"Tipe belajar ini muncul karena kamu memiliki {', '.join(strengths)}, "
                f"namun masih memiliki {', '.join(areas_to_improve)}. "
                f"Ada potensi besar untuk berkembang lebih jauh."
            )
        else:
            reason = (
                f"Tipe belajar ini muncul karena kamu memiliki {login_desc}, "
                f"{study_desc}, dan {quiz_desc}. "
                f"Konsistensi yang lebih tinggi akan membantu peningkatan signifikan."
            )
    elif learning_type == "Passive Learner":
        reason = (
            f"Tipe belajar ini muncul karena kamu memiliki {login_desc}, "
            f"{study_desc}, dan {quiz_desc}. "
            f"Dengan meningkatkan frekuensi belajar dan latihan, kamu bisa naik ke level berikutnya."
        )
    else:
        reason = (
            f"Tipe belajar kamu ditentukan berdasarkan {login_desc}, "
            f"{study_desc}, {completion_desc}, dan {quiz_desc}."
        )

    return reason
