"""
ExplanationGenerator service — generates multi-level explanations using Gemini.

Supports adaptive mode: when the user has struggled with the topic (it appears
in their weak_topics list), a specialised prompt is loaded that spends more
time on foundational concepts.
"""
import os
from tenacity import retry, stop_after_attempt, wait_exponential

from app.schemas.topic import TopicAnalysis
from app.schemas.explanation import ExplanationContent, ExplanationSet
from app.core.llm import generate_json

_PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), "../../prompts/explanation_generation.txt"
)
_ADAPTIVE_PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), "../../prompts/explanation_generation_adaptive.txt"
)


def _load_system_prompt(adaptive: bool = False) -> str:
    path = _ADAPTIVE_PROMPT_PATH if adaptive else _PROMPT_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
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
    openai_client=None,  # kept for signature compatibility
    topic_id: str = "",
    weak_topics: list[str] | None = None,
) -> ExplanationSet:
    """Generate all three explanation levels in a single Gemini call.

    Args:
        weak_topics: optional list of topic_ids the user struggles with.
            If the current topic_id is in this list, an adaptive prompt is
            used that emphasises foundational concepts. When ``None`` or
            empty, the default prompt is used (backward-compatible).
    """
    # Determine whether to use the adaptive prompt
    use_adaptive = bool(weak_topics and topic_id and topic_id in weak_topics)
    system_prompt = _load_system_prompt(adaptive=use_adaptive)

    user_content_parts = [f"Topic: {topic.main_topic}"]
    if topic.subtopics:
        user_content_parts.append(f"Subtopics: {', '.join(topic.subtopics)}")
    if session_context:
        user_content_parts.append(f"\n[Session Context]\n{session_context}")
    if source_text:
        user_content_parts.append(f"\n[Source Material]\n{source_text}")

    user_content = "\n".join(user_content_parts)

    data = await generate_json(
        system_prompt=system_prompt,
        user_message=user_content,
        temperature=0.3,
        max_tokens=8192,
    )

    def _parse_level(level_key: str, level_name: str) -> ExplanationContent:
        level_data = data.get(level_key, {})
        if isinstance(level_data, str):
            content = level_data
            refs = []
        else:
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

    return ExplanationSet(
        topic_id=topic_id,
        basic=_parse_level("basic", "basic"),
        intermediate=_parse_level("intermediate", "intermediate"),
        advanced=_parse_level("advanced", "advanced"),
    )

