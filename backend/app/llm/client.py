"""
Groq LLM Client.
Handles API initialization and chat completion calls.

Groq digunakan karena:
- Lebih cepat (low latency)
- Cocok untuk short insight generation
- Free tier cukup baik
"""

import logging

from groq import Groq

from app.config import GROQ_API_KEYS, GROQ_MAX_TOKENS, GROQ_MODEL, GROQ_TEMPERATURE

logger = logging.getLogger(__name__)


def is_llm_configured() -> bool:
    """Check apakah LLM API key sudah dikonfigurasi."""
    return len(GROQ_API_KEYS) > 0


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Memanggil Groq API untuk chat completion dengan fallback otomatis.

    Args:
        system_prompt: System message yang mengatur perilaku AI.
        user_prompt: User message berisi data/pertanyaan.

    Returns:
        Response text dari LLM.

    Raises:
        RuntimeError: Jika API key belum dikonfigurasi atau semua key gagal.
    """
    if not is_llm_configured():
        raise RuntimeError(
            "GROQ_API_KEY belum dikonfigurasi. "
            "Set environment variable GROQ_API_KEY_1 s/d GROQ_API_KEY_5 di file .env"
        )

    last_error = None
    for index, api_key in GROQ_API_KEYS:
        try:
            logger.info(f"Using Groq API Key #{index}")
            client = Groq(api_key=api_key)

            logger.info(f"Calling Groq API (model={GROQ_MODEL})...")
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=GROQ_MAX_TOKENS,
                temperature=GROQ_TEMPERATURE,
            )

            result = response.choices[0].message.content.strip()
            logger.info(f"Groq API response received ({len(result)} chars)")
            return result
        except Exception as e:
            logger.warning(f"Groq API Key #{index} gagal: {e}")
            last_error = e

    raise RuntimeError(f"Semua Groq API Keys gagal. Error terakhir: {last_error}")
