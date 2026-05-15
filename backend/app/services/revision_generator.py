"""
RevisionGenerator service — generates flashcards, formulas, definitions,
summary notes, and exam questions using Gemini.
"""
import os
from tenacity import retry, stop_after_attempt, wait_exponential

from app.schemas.topic import TopicAnalysis
from app.schemas.explanation import ExplanationSet
from app.schemas.revision import (
    RevisionMaterial,
    Flashcard,
    Formula,
    KeyDefinition,
    ExamQuestion,
)
from app.core.gemini import generate_json

_PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), "../../prompts/revision_generation.txt"
)


def _load_system_prompt() -> str:
    try:
        with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "Generate revision materials as JSON: summary_notes, flashcards, "
            "formulas, key_definitions, exam_questions."
        )


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
async def generate(
    topic: TopicAnalysis,
    explanations: ExplanationSet | None = None,
    source_text: str = "",
    session_context: str = "",
    session_id: str = "",
) -> RevisionMaterial:
    """Generate comprehensive revision materials for a topic."""
    system_prompt = _load_system_prompt()

    user_parts = [f"Topic: {topic.main_topic}"]
    if topic.subtopics:
        user_parts.append(f"Subtopics: {', '.join(topic.subtopics)}")
    if explanations:
        user_parts.append(f"\n[Basic Explanation]\n{explanations.basic.content}")
        user_parts.append(f"\n[Intermediate Explanation]\n{explanations.intermediate.content}")
        user_parts.append(f"\n[Advanced Explanation]\n{explanations.advanced.content}")
    if source_text:
        user_parts.append(f"\n[Source Material]\n{source_text[:3000]}")
    if session_context:
        user_parts.append(f"\n[Session Context]\n{session_context}")

    data = await generate_json(
        system_prompt=system_prompt,
        user_message="\n".join(user_parts),
        temperature=0.4,
        max_tokens=4000,
    )

    flashcards = []
    for fc in data.get("flashcards", []):
        if isinstance(fc, dict):
            flashcards.append(Flashcard(
                front=fc.get("front", ""),
                back=fc.get("back", ""),
            ))

    formulas = []
    for f in data.get("formulas", []):
        if isinstance(f, dict):
            formulas.append(Formula(
                formula=f.get("formula", ""),
                description=f.get("description", ""),
            ))

    definitions = []
    for d in data.get("key_definitions", []):
        if isinstance(d, dict):
            definitions.append(KeyDefinition(
                term=d.get("term", ""),
                definition=d.get("definition", ""),
            ))

    exam_questions = []
    for eq in data.get("exam_questions", []):
        if isinstance(eq, dict):
            exam_questions.append(ExamQuestion(
                question=eq.get("question", ""),
                expected_answer=eq.get("expected_answer", ""),
                difficulty=eq.get("difficulty", "medium"),
            ))

    return RevisionMaterial(
        session_id=session_id,
        topic=topic.main_topic,
        summary_notes=data.get("summary_notes", ""),
        flashcards=flashcards,
        formulas=formulas,
        key_definitions=definitions,
        exam_questions=exam_questions,
    )
