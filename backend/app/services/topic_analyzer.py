"""
TopicAnalyzer service — identifies topics from text using Gemini.
"""
import os
from tenacity import retry, stop_after_attempt, wait_exponential

from app.schemas.topic import TopicAnalysis
from app.core.gemini import generate_json

_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../../prompts/topic_analysis.txt")


def _load_system_prompt() -> str:
    try:
        with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "You are an expert educational topic extractor. "
            "Analyze the provided text and return a JSON object with "
            "main_topic (string), subtopics (list of strings, max 5), "
            "and confidence (float 0.0-1.0)."
        )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
async def analyze(
    text: str,
    session_context: str,
    openai_client=None,  # kept for signature compatibility
) -> TopicAnalysis:
    """Analyze text to identify the main topic and subtopics."""
    system_prompt = _load_system_prompt()

    user_content = text
    if session_context:
        user_content = f"[Session Context]\n{session_context}\n\n[New Input]\n{text}"

    data = await generate_json(
        system_prompt=system_prompt,
        user_message=user_content,
        temperature=0.2,
        max_tokens=500,
    )

    confidence = float(data.get("confidence", 0.5))
    needs_clarification = confidence < 0.70

    subtopics = data.get("subtopics", [])
    if not isinstance(subtopics, list):
        subtopics = []

    return TopicAnalysis(
        main_topic=data.get("main_topic", "Unknown Topic"),
        subtopics=subtopics[:5],
        confidence=confidence,
        needs_clarification=needs_clarification,
    )
