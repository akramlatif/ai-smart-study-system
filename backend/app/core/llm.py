"""
AI client — Uses OpenAI by default, falls back to Gemini if quota/rate limits are hit.
"""
import json
import re
import logging
from openai import AsyncOpenAI
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

_gemini_configured = False

def _ensure_gemini_configured():
    global _gemini_configured
    if not _gemini_configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_configured = True

async def generate_json(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> dict:
    """
    Call OpenAI and return parsed JSON dict.
    If it fails, fall back to Gemini.
    """
    text = ""
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        text = response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"OpenAI failed: {e}. Falling back to Gemini.")
        
        try:
            _ensure_gemini_configured()
            model = genai.GenerativeModel(
                model_name="models/gemini-2.0-flash",
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    response_mime_type="application/json",
                ),
            )
            full_prompt = f"{system_prompt}\n\n---\n\n{user_message}"
            response = await model.generate_content_async(full_prompt)
            text = response.text.strip()
        except Exception as gemini_e:
            logger.error(f"Gemini fallback also failed: {gemini_e}")
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="AI Services are currently unavailable. Please check quotas or try again later.")

    # Strip markdown code fences if present just in case
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="AI Service returned invalid response format.")
