"""
FeynmanEvaluator service — evaluates student explanations using Gemini.
"""
from pathlib import Path
from app.schemas.feynman import FeynmanFeedback
from app.schemas.topic import TopicAnalysis
from app.core.gemini import generate_json

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "feynman_evaluation.txt"


async def evaluate(
    student_explanation: str,
    topic: TopicAnalysis,
    session_context: str,
    openai_client=None,  # kept for signature compatibility
) -> FeynmanFeedback:
    """Evaluate student explanation using Feynman Technique rubric."""
    system_prompt = PROMPT_PATH.read_text()
    user_message = f"""Topic: {topic.main_topic}
Subtopics: {', '.join(topic.subtopics) if topic.subtopics else 'None'}

Session Context:
{session_context}

Student's Explanation:
{student_explanation}"""

    data = await generate_json(
        system_prompt=system_prompt,
        user_message=user_message,
        temperature=0.3,
        max_tokens=1500,
    )
    return FeynmanFeedback(**data)
