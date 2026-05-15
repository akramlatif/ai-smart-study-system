"""
Pydantic schemas for the Interactive Tutor Mode.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TutorStartRequest(BaseModel):
    difficulty: str = "medium"  # easy, medium, hard


class SubtopicPlan(BaseModel):
    name: str
    description: str
    prerequisite: Optional[str] = None


class TutorStartResponse(BaseModel):
    tutor_session_id: str
    topic: str
    subtopics: list[SubtopicPlan]
    current_subtopic: str
    current_index: int
    total_subtopics: int
    explanation: str
    question: str
    difficulty: str


class TutorAnswerRequest(BaseModel):
    tutor_session_id: str
    answer: str


class TutorEvaluation(BaseModel):
    is_correct: bool
    score: float  # 0.0 to 1.0
    feedback: str
    hint: Optional[str] = None
    simplified_explanation: Optional[str] = None
    should_retry: bool = False


class TutorAnswerResponse(BaseModel):
    evaluation: TutorEvaluation
    # Next step (if advancing)
    advanced: bool = False
    is_session_complete: bool = False
    next_subtopic: Optional[str] = None
    next_explanation: Optional[str] = None
    next_question: Optional[str] = None
    current_index: int = 0
    total_subtopics: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    difficulty: str = "medium"


class TutorStepDetail(BaseModel):
    subtopic_name: str
    subtopic_index: int
    explanation: str
    question_text: str
    student_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    attempts: int = 0
    is_skipped: bool = False


class TutorProgress(BaseModel):
    tutor_session_id: str
    topic: str
    subtopics: list[str]
    current_index: int
    total_subtopics: int
    correct_count: int
    incorrect_count: int
    difficulty: str
    is_complete: bool
    weak_areas: list[str]
    steps: list[TutorStepDetail]


class TutorSkipRequest(BaseModel):
    tutor_session_id: str
