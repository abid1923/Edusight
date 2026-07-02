"""
AI Learning Insight API — Main Application Entry Point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_DESCRIPTION, APP_TITLE, APP_VERSION, CORS_ORIGINS, GROQ_API_KEYS
from app.database import Base, engine
from app.routes import auth_routes, insight_routes, learning_routes, user_routes, recommendation_routes
from app.routes import export_routes
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from app.utils.limiter import limiter

# Import all models so SQLAlchemy registers them
from app.models import user_model, activity_model, insight_model, logging_model  # noqa: F401

# AI Model
from app.ai.inference import load_model

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup and load AI model."""
    Base.metadata.create_all(bind=engine)

    # Load AI clustering model & scaler on startup
    try:
        load_model()
        logger.info("✅ AI Model loaded successfully on startup")
    except Exception as e:
        logger.error(f"⚠️ Failed to load AI model: {e}")
        logger.warning("Server will start without AI model. Prediction endpoints will fail.")

    # Validate Groq API keys
    if GROQ_API_KEYS:
        logger.info(f"✅ {len(GROQ_API_KEYS)} Groq API key(s) detected — LLM insight generation enabled")
    else:
        logger.warning(
            "⚠️ No Groq API keys set. LLM insight generation will use fallback templates. "
            "Set GROQ_API_KEY_1 to GROQ_API_KEY_5 in .env to enable Groq LLM integration."
        )

    yield


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

# ─── Rate Limiting ─────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ─── CORS Middleware ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routers ─────────────────────────────────────────
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(learning_routes.router)
app.include_router(insight_routes.router)
app.include_router(recommendation_routes.router)
app.include_router(export_routes.router)


# ─── Root Endpoint ─────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    """Health check / welcome endpoint."""
    return {
        "message": "Edusight API is running",
        "version": APP_VERSION,
        "docs": "/docs",
    }
