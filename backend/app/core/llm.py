"""
AI client — Uses OpenAI (gpt-4o) by default.
On quota / rate-limit failures automatically retries with:
  1. models/gemini-2.0-flash
  2. models/gemini-2.0-flash-lite   (cheaper quota bucket)
  3. models/gemini-2.5-flash        (newest free-tier model)
All models share the same GEMINI_API_KEY from settings.
"""
import json
import re
import logging
from openai import AsyncOpenAI
import google.generativeai as genai
from app.core.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

_gemini_configured = False

# Ordered list of Gemini models to try, cheapest / most available first
_GEMINI_FALLBACK_MODELS = [
    "models/gemini-2.0-flash",
    "models/gemini-2.0-flash-lite",
    "models/gemini-2.5-flash",
]


def _ensure_gemini_configured() -> None:
    global _gemini_configured
    if not _gemini_configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_configured = True


def _is_quota_error(exc: Exception) -> bool:
    """Return True if the exception is a quota / rate-limit error."""
    msg = str(exc).lower()
    return any(k in msg for k in ("quota", "429", "rate limit", "insufficient_quota", "resource_exhausted"))


async def _try_gemini(system_prompt: str, user_message: str, temperature: float, max_tokens: int) -> str:
    """Try each Gemini fallback model in order, return raw text."""
    _ensure_gemini_configured()
    full_prompt = f"{system_prompt}\n\n---\n\n{user_message}"
    last_error: Exception | None = None

    for model_name in _GEMINI_FALLBACK_MODELS:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    response_mime_type="application/json",
                ),
            )
            response = await model.generate_content_async(full_prompt)
            logger.info(f"Gemini model succeeded: {model_name}")
            return response.text.strip()
        except Exception as exc:
            last_error = exc
            logger.warning(f"Gemini model {model_name} failed: {exc}")
            continue  # try next model

    # All models exhausted
    raise HTTPException(
        status_code=503,
        detail=(
            "All AI services are currently unavailable (quota exhausted on OpenAI and all Gemini models). "
            "Please add a valid OpenAI API key in your .env file or wait for your Gemini quota to reset."
        ),
    )


async def generate_json(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> dict:
    """
    Call OpenAI GPT-4o and return a parsed JSON dict.
    On any failure (quota, network, etc.) falls back through all configured Gemini models.
    """
    text: str = ""

    # --- Primary: OpenAI ---
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        text = response.choices[0].message.content.strip()
    except Exception as openai_exc:
        logger.warning(f"OpenAI failed ({type(openai_exc).__name__}): {openai_exc}. Trying Gemini fallbacks...")
        text = await _try_gemini(system_prompt, user_message, temperature, max_tokens)

    # --- Clean response & parse ---
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as parse_exc:
        logger.error(f"JSON parse error: {parse_exc}. Raw text: {text[:300]}")
        raise HTTPException(status_code=500, detail="AI service returned an invalid response. Please try again.")
