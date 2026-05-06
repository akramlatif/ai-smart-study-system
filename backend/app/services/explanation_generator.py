"""
ExplanationGenerator service — generates multi-level explanations using GPT-4o.
"""
import os
import json
from tenacity import retry, stop_after_attempt, wait_exponential

from app.schemas.topic import TopicAnalysis
from app.schemas.explanation import ExplanationContent, ExplanationSet

_PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), "../../prompts/explanation_generation.txt"
)


def _load_system_prompt() -> str:
    try:
        with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "You are an expert educational tutor. Generate three levels of explanation "
            "(basic, intermediate, advanced) for the given topic as a JSON object."
        )


def _count_words(text: str) -> int:
    return len(text.split())


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
async def generate(
    topic: TopicAnalysis,
    session_context: str,
    source_text: str,
    openai_client,
    topic_id: str = "",
) -> ExplanationSet:
    """
    Generate all three explanation levels in a single GPT-4o call.
    """
    system_prompt = _load_system_prompt()

    user_content_parts = [
        f"Topic: {topic.main_topic}",
    ]
    if topic.subtopics:
        user_content_parts.append(f"Subtopics: {', '.join(topic.subtopics)}")
    if session_context:
        user_content_parts.append(f"\n[Session Context]\n{session_context}")
    if source_text:
        excerpt = source_text[:3000]
        user_content_parts.append(f"\n[Source Material]\n{excerpt}")

    user_content = "\n".join(user_content_parts)

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)

    def _parse_level(level_key: str, level_name: str) -> ExplanationContent:
        level_data = data.get(level_key, {})
        content = level_data.get("content", "")
        refs = level_data.get("source_references", [])
        if not isinstance(refs, list):
            refs = []
        return ExplanationContent(
            level=level_name,
            content=content,
            word_count=_count_words(content),
            source_references=refs,
        )

    basic = _parse_level("basic", "basic")
    intermediate = _parse_level("intermediate", "intermediate")
    advanced = _parse_level("advanced", "advanced")

    return ExplanationSet(
        topic_id=topic_id,
        basic=basic,
        intermediate=intermediate,
        advanced=advanced,
    )
