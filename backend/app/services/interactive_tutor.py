"""
InteractiveTutor service — step-by-step teaching with evaluation.
The MOST IMPORTANT new feature: teaches one subtopic at a time,
asks questions, evaluates answers, adapts difficulty.
"""
import os
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.llm import generate_json

_PLAN_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../../prompts/tutor_plan_subtopics.txt")
_TEACH_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../../prompts/tutor_teach_subtopic.txt")
_EVAL_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../../prompts/tutor_evaluate_answer.txt")


def _load_prompt(path: str, fallback: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return fallback


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
async def plan_subtopics(
    topic: str,
    source_text: str = "",
    session_context: str = "",
) -> list[dict]:
    """Break a topic into ordered subtopics with prerequisites."""
    system_prompt = _load_prompt(
        _PLAN_PROMPT_PATH,
        "Break the topic into 4-8 ordered subtopics. Return JSON with subtopics array."
    )

    user_parts = [f"Topic: {topic}"]
    if source_text:
        user_parts.append(f"\n[Source Material]\n{source_text[:3000]}")
    if session_context:
        user_parts.append(f"\n[Session Context]\n{session_context}")

    data = await generate_json(
        system_prompt=system_prompt,
        user_message="\n".join(user_parts),
        temperature=0.3,
        max_tokens=1500,
    )

    subtopics = data.get("subtopics", [])
    if not isinstance(subtopics, list) or len(subtopics) == 0:
        # Fallback: return the topic itself as a single subtopic
        subtopics = [{"name": topic, "description": "Full topic overview", "prerequisite": None}]

    return subtopics


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
async def teach_subtopic(
    subtopic: str,
    main_topic: str,
    difficulty_level: str = "medium",
    source_text: str = "",
    session_context: str = "",
    previous_subtopics: list[str] | None = None,
) -> dict:
    """Generate explanation and comprehension question for ONE subtopic."""
    system_prompt = _load_prompt(
        _TEACH_PROMPT_PATH,
        "Explain the subtopic and ask one comprehension question. Return JSON."
    )

    user_parts = [
        f"Main Topic: {main_topic}",
        f"Subtopic to teach: {subtopic}",
        f"Difficulty Level: {difficulty_level}",
    ]
    if previous_subtopics:
        user_parts.append(f"Already taught subtopics: {', '.join(previous_subtopics)}")
    if source_text:
        user_parts.append(f"\n[Source Material]\n{source_text[:3000]}")
    if session_context:
        user_parts.append(f"\n[Session Context]\n{session_context}")

    data = await generate_json(
        system_prompt=system_prompt,
        user_message="\n".join(user_parts),
        temperature=0.4,
        max_tokens=1500,
    )

    return {
        "explanation": data.get("explanation", f"Let's learn about {subtopic}."),
        "question": data.get("question", f"What is the key idea behind {subtopic}?"),
        "key_concept": data.get("key_concept", subtopic),
    }


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
async def evaluate_answer(
    question: str,
    student_answer: str,
    subtopic: str,
    main_topic: str,
    explanation: str,
    difficulty_level: str = "medium",
    session_context: str = "",
) -> dict:
    """Evaluate student's answer with adaptive feedback."""
    system_prompt = _load_prompt(
        _EVAL_PROMPT_PATH,
        "Evaluate the student's answer. Return JSON with is_correct, score, feedback, hint, should_retry."
    )

    user_parts = [
        f"Main Topic: {main_topic}",
        f"Subtopic: {subtopic}",
        f"Difficulty: {difficulty_level}",
        f"\nExplanation given:\n{explanation}",
        f"\nQuestion asked:\n{question}",
        f"\nStudent's answer:\n{student_answer}",
    ]
    if session_context:
        user_parts.append(f"\n[Session Context]\n{session_context}")

    data = await generate_json(
        system_prompt=system_prompt,
        user_message="\n".join(user_parts),
        temperature=0.3,
        max_tokens=1000,
    )

    return {
        "is_correct": bool(data.get("is_correct", False)),
        "score": float(data.get("score", 0.0)),
        "feedback": data.get("feedback", "Thank you for your answer."),
        "hint": data.get("hint"),
        "simplified_explanation": data.get("simplified_explanation"),
        "should_retry": bool(data.get("should_retry", False)),
    }


def adapt_difficulty(correct_count: int, incorrect_count: int, current: str) -> str:
    """Adjust difficulty based on student performance."""
    total = correct_count + incorrect_count
    if total < 3:
        return current  # Not enough data yet

    accuracy = correct_count / total if total > 0 else 0.5

    levels = ["easy", "medium", "hard"]
    current_idx = levels.index(current) if current in levels else 1

    if accuracy >= 0.8 and current_idx < 2:
        return levels[current_idx + 1]  # Increase difficulty
    elif accuracy < 0.4 and current_idx > 0:
        return levels[current_idx - 1]  # Decrease difficulty

    return current
