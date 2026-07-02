"""
LLM module package.
Provides Groq LLM integration for personalized insight generation.
"""

from app.llm.client import call_llm  # noqa: F401
from app.llm.insight_generator import generate_llm_insight  # noqa: F401
from app.llm.reasoning import generate_reason  # noqa: F401
