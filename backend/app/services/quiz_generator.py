"""
QuizGenerator service — generates quiz questions using GPT-4o.
"""
import os
import json
import uuid
from tenacity import retry, stop_after_attempt, wait_exponential

from app.schemas.topic import TopicAnalysis
from app.schemas.explanation import ExplanationSet
from app.schemas.quiz import AnswerOption, QuizQuestion

_PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), "../../prompts/quiz_generation.txt"
)


def _load_system_prompt() -> str:
    try:
        with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "You are an expert quiz creator. Generate quiz questions as a JSON object "
            "with a 'questions' array."
        )


def _parse_options(raw_options) -> list[AnswerOption] | None:
    if not raw_options or not isinstance(raw_options, list):
        return None
    options = []
    for opt in raw_options:
        if isinstance(opt, dict):
            options.append(
                AnswerOption(
                    label=opt.get("label", "A"),
                    text=opt.get("text", ""),
                    is_correct=bool(opt.get("is_correct", False)),
                )
            )
    return options if options else None


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
async def generate(
    topic: TopicAnalysis,
    explanations: ExplanationSet,
    session_context: str,
    openai_client,
    difficulty_filter: str | None = None,
) -> list[QuizQuestion]:
    """
    Generate quiz questions for a topic.

    Returns at least 5 questions with at least 1 easy, 1 medium, 1 hard.
    """
    system_prompt = _load_system_prompt()

    user_content_parts = [
        f"Topic: {topic.main_topic}",
    ]
    if topic.subtopics:
        user_content_parts.append(f"Subtopics: {', '.join(topic.subtopics)}")

    user_content_parts.append(f"\n[Basic Explanation]\n{explanations.basic.content}")
    user_content_parts.append(
        f"\n[Intermediate Explanation]\n{explanations.intermediate.content}"
    )
    user_content_parts.append(f"\n[Advanced Explanation]\n{explanations.advanced.content}")

    if session_context:
        user_content_parts.append(f"\n[Session Context]\n{session_context}")

    if difficulty_filter:
        user_content_parts.append(
            f"\nGenerate only {difficulty_filter} difficulty questions."
        )

    user_content = "\n".join(user_content_parts)

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.7,
        max_tokens=3000,
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)

    questions_raw = data.get("questions", [])
    questions: list[QuizQuestion] = []

    for q in questions_raw:
        if not isinstance(q, dict):
            continue
        options = _parse_options(q.get("options"))
        questions.append(
            QuizQuestion(
                id=str(uuid.uuid4()),
                question_type=q.get("question_type", "multiple_choice"),
                difficulty=q.get("difficulty", "medium"),
                question_text=q.get("question_text", ""),
                options=options,
                correct_answer=q.get("correct_answer", ""),
                explanation=q.get("explanation"),
                saved_for_review=False,
            )
        )

    return questions
