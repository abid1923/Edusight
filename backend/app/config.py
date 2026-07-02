"""
Application configuration.
Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Application ───────────────────────────────────────────────
APP_TITLE = "Edusight API"
APP_DESCRIPTION = "Backend API untuk platform pembelajaran berbasis AI"
APP_VERSION = "1.0.0"

# ─── Database ──────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./learning_insight.db")

# ─── JWT Authentication ───────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set! Application cannot start without a secure secret key.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ─── CORS ──────────────────────────────────────────────────────
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    if origin.strip()
]

# ─── AI Insight Thresholds ─────────────────────────────────────
# Minimum activity required before generating AI insights
INSIGHT_MIN_LOGINS = int(os.getenv("INSIGHT_MIN_LOGINS", "5"))
INSIGHT_MIN_QUIZ_ATTEMPTS = int(os.getenv("INSIGHT_MIN_QUIZ_ATTEMPTS", "3"))
INSIGHT_MIN_COMPLETIONS = int(os.getenv("INSIGHT_MIN_COMPLETIONS", "2"))

# ─── Quiz Settings ─────────────────────────────────────────────
MAX_QUIZ_ATTEMPTS = int(os.getenv("MAX_QUIZ_ATTEMPTS", "3"))
QUESTIONS_PER_QUIZ = int(os.getenv("QUESTIONS_PER_QUIZ", "10"))

# ─── LLM Integration (Groq) ───────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "512"))
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))

# Multi API Key Fallback
GROQ_API_KEYS = []
for i in range(1, 6):
    key = os.getenv(f"GROQ_API_KEY_{i}", "")
    if key:
        GROQ_API_KEYS.append((i, key))

# Fallback to default GROQ_API_KEY if no indexed keys are found
if not GROQ_API_KEYS and GROQ_API_KEY:
    GROQ_API_KEYS.append((1, GROQ_API_KEY))

