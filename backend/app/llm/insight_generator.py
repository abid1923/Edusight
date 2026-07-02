"""Generates personalized insights (strengths, weaknesses, motivations) using Groq LLM."""

import json
import logging

from app.llm.client import call_llm, is_llm_configured
from app.llm.prompts import SYSTEM_PROMPT, build_insight_prompt

logger = logging.getLogger(__name__)

# ─── Fallback Insight Templates ───────────────────────────────
# Digunakan jika LLM tidak tersedia atau gagal
FALLBACK_INSIGHTS = {
    "Active Learner": {
        "why_this_type": "Kamu dikelompokkan sebagai Active Learner karena tingkat aktivitas login dan penyelesaian materimu sangat tinggi serta konsisten.",
        "strength": "Kamu memiliki konsistensi belajar yang sangat baik dan aktif menyelesaikan materi secara teratur.",
        "weakness": "Cobalah untuk lebih fokus pada materi yang belum dikuasai agar pemahaman lebih merata.",
        "motivation": "Pertahankan momentum belajarmu, konsistensi adalah kunci keberhasilan jangka panjang.",
    },
    "Moderate Learner": {
        "why_this_type": "Kamu dikelompokkan sebagai Moderate Learner karena aktivitas belajarmu stabil dan konsisten, meskipun frekuensi penyelesaian materi dan pengerjaan kuis berada di tingkat menengah.",
        "strength": "Kamu menunjukkan pola belajar yang cukup stabil dan memiliki pemahaman dasar yang baik.",
        "weakness": "Tingkatkan frekuensi latihan quiz dan penyelesaian materi untuk hasil yang lebih optimal.",
        "motivation": "Setiap langkah kecil yang konsisten akan membawamu lebih dekat ke tujuan belajarmu.",
    },
    "Passive Learner": {
        "why_this_type": "Kamu dikelompokkan sebagai Passive Learner karena kamu baru memulai perjalanan belajarmu dan frekuensi aktivitas belajarmu di platform masih perlu ditingkatkan.",
        "strength": "Kamu sudah memulai perjalanan belajar dan menunjukkan ketertarikan pada materi yang tersedia.",
        "weakness": "Cobalah untuk lebih rutin membuka materi dan menyelesaikan quiz agar pemahaman semakin berkembang.",
        "motivation": "Mulailah dari langkah kecil setiap hari, potensi belajarmu masih sangat besar untuk dikembangkan.",
    },
}

DEFAULT_FALLBACK = {
    "why_this_type": "Kamu dikelompokkan pada tipe belajar ini berdasarkan pola aktivitas belajarmu saat ini.",
    "strength": "Kamu sudah memulai perjalanan belajar dengan baik.",
    "weakness": "Terus tingkatkan konsistensi dan frekuensi belajarmu.",
    "motivation": "Setiap usaha belajar akan membawa hasil yang positif.",
}


def _parse_llm_response(response: str) -> dict | None:
    """Parse JSON response from LLM, stripping markdown markers if needed."""
    # Strip markdown code block markers if present
    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
        # Parse fields with backward compatibility
        why_this_type = data.get("why_this_type") or data.get("reason")
        strength = data.get("strength")
        weakness = data.get("weakness")
        motivation = data.get("motivation")

        if why_this_type and strength and weakness and motivation:
            return {
                "why_this_type": str(why_this_type),
                "strength": str(strength),
                "weakness": str(weakness),
                "motivation": str(motivation),
            }
        logger.warning(f"LLM response missing required fields: {list(data.keys())}")
        return None
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse LLM response as JSON: {e}")
        logger.debug(f"Raw response: {response}")
        return None


def generate_llm_insight(learning_type: str, features: dict) -> dict:
    """Generate personalized learning insights using Groq API with fallback templates."""
    # Check if LLM is configured
    if not is_llm_configured():
        logger.warning("LLM belum dikonfigurasi, menggunakan fallback insight")
        fallback = FALLBACK_INSIGHTS.get(learning_type, DEFAULT_FALLBACK)
        return {**fallback, "source": "fallback"}

    # Build prompt
    user_prompt = build_insight_prompt(learning_type, features)

    # Call LLM
    try:
        response = call_llm(SYSTEM_PROMPT, user_prompt)
        parsed = _parse_llm_response(response)

        if parsed:
            logger.info(f"LLM insight berhasil di-generate untuk {learning_type}")
            return {**parsed, "source": "llm"}
        else:
            logger.warning("Gagal parse LLM response, menggunakan fallback")
            fallback = FALLBACK_INSIGHTS.get(learning_type, DEFAULT_FALLBACK)
            return {**fallback, "source": "fallback"}

    except Exception as e:
        logger.error(f"LLM call gagal: {e}")
        fallback = FALLBACK_INSIGHTS.get(learning_type, DEFAULT_FALLBACK)
        return {**fallback, "source": "fallback"}
