"""
SocraticTutor service — generates Socratic questions using Gemini.
"""
from pathlib import Path
from app.schemas.socratic import SocraticQuestion, SocraticResponse, QuestionAnswerPair
from app.schemas.topic import TopicAnalysis
from app.core.llm import generate_json

START_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "socratic_start.txt"
RESPOND_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "socratic_respond.txt"


async def start(
    topic: TopicAnalysis,
    session_context: str,
    openai_client=None,  # kept for signature compatibility
) -> SocraticQuestion:
    """Generate opening Socratic question."""
    system_prompt = START_PROMPT_PATH.read_text()
    user_message = f"""Topic: {topic.main_topic}
Subtopics: {', '.join(topic.subtopics) if topic.subtopics else 'None'}

Session Context:
{session_context}

Generate an opening Socratic question for this topic."""

    data = await generate_json(
        system_prompt=system_prompt,
        user_message=user_message,
        temperature=0.7,
        max_tokens=300,
    )
    data["depth_level"] = 1  # always depth 1 for opening question
    return SocraticQuestion(**data)


async def respond(
    student_answer: str,
    question_chain: list[QuestionAnswerPair],
    current_depth: int,
    session_context: str,
    openai_client=None,  # kept for signature compatibility
) -> SocraticResponse:
    """Generate next question or complete the session."""
    system_prompt = RESPOND_PROMPT_PATH.read_text()

    chain_text = ""
    for pair in question_chain:
        chain_text += (
            f"\nQ{pair.question_index} "
            f"(depth={pair.question.depth_level}, type={pair.question.question_type}):\n"
            f"  Question: {pair.question.question_text}\n"
        )
        if pair.student_answer:
            chain_text += f"  Student Answer: {pair.student_answer}\n"

    user_message = f"""Session Context:
{session_context}

Question-Answer Chain So Far:
{chain_text}

Student's Latest Answer:
{student_answer}

Current Depth Level: {current_depth}

Generate the next question or conclude the session."""

    data = await generate_json(
        system_prompt=system_prompt,
        user_message=user_message,
        temperature=0.7,
        max_tokens=800,
    )

    # Enforce depth monotonicity
    if not data.get("is_complete") and data.get("question"):
        next_depth = data["question"].get("depth_level", current_depth)
        data["question"]["depth_level"] = max(current_depth, min(5, next_depth))

    return SocraticResponse(**data)
