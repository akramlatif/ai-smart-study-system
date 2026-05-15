"""
Pydantic schemas for the Revision System.
"""
from pydantic import BaseModel


class Flashcard(BaseModel):
    front: str
    back: str


class Formula(BaseModel):
    formula: str
    description: str


class KeyDefinition(BaseModel):
    term: str
    definition: str


class ExamQuestion(BaseModel):
    question: str
    expected_answer: str
    difficulty: str = "medium"


class RevisionMaterial(BaseModel):
    session_id: str
    topic: str
    summary_notes: str
    flashcards: list[Flashcard]
    formulas: list[Formula]
    key_definitions: list[KeyDefinition]
    exam_questions: list[ExamQuestion]
