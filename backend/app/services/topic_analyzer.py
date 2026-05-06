"""
TopicAnalyzer service — identifies topics from text using GPT-4o.
"""
import os
import json
from tenacity import retry, stop_after_attempt, wait_exponential

from app.schemas.topic import TopicAnalysis

_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../../prompts/topic_analysis.txt")


def _load_system_prompt() -> str:
    try:
        with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "You are an expert educational topic extractor. "
            "Analyze the provided text and return a JSON object with "
            "main_topic, subtopics (list, max 5), and confidence (0.0-1.0)."
        )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
async def analyze(
    text: str,
    session_context: str,
    openai_client,
) -> TopicAnalysis:
    """
    Analyze text to identify the main topic and subtopics.

    Returns TopicAnalysis with confidence score.
    If confidence < 0.70, sets needs_clarification=True.
    """
    system_prompt = _load_system_prompt()

    user_content = text
    if session_context:
        user_content = f"[Session Context]\n{session_context}\n\n[New Input]\n{text}"

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
        max_tokens=500,
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)

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
