from typing import Literal
from pydantic import BaseModel


class AnswerOption(BaseModel):
    label: Literal["A", "B", "C", "D"]
    text: str
    is_correct: bool


class QuizQuestion(BaseModel):
    id: str
    question_type: Literal["multiple_choice", "short_answer"]
    difficulty: Literal["easy", "medium", "hard"]
    question_text: str
    options: list[AnswerOption] | None = None  # MCQ only
    correct_answer: str
    explanation: str | None = None
    saved_for_review: bool = False

    model_config = {"from_attributes": True}


class QuizFilter(BaseModel):
    difficulty: Literal["easy", "medium", "hard"] | None = None
    question_type: Literal["multiple_choice", "short_answer"] | None = None
