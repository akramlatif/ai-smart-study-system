"""
Gemini AI client — drop-in replacement for the OpenAI client.
Uses google-generativeai SDK with gemini-2.0-flash.
"""
import json
import re
import google.generativeai as genai
from app.core.config import settings

_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _configured = True


async def generate_json(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> dict:
    """
    Call Gemini and return parsed JSON dict.
    Combines system + user into a single prompt.
    """
    _ensure_configured()

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

    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)
