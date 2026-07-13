"""
Tutor router — Interactive Tutor Mode API endpoints.
"""
import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import get_current_user_id
from app.schemas.tutor import (
    TutorStartRequest,
    TutorStartResponse,
    TutorAnswerRequest,
    TutorAnswerResponse,
    TutorEvaluation,
    TutorProgress,
    TutorStepDetail,
    TutorSkipRequest,
    SubtopicPlan,
)
import app.services.session_manager as session_manager
import app.services.interactive_tutor as interactive_tutor
from app.repositories.tutor import TutorRepository
from app.repositories.attempt import AttemptRepository

router = APIRouter(tags=["tutor"])


@router.post("/sessions/{session_id}/tutor/start", response_model=TutorStartResponse)
async def start_tutor(
    session_id: str,
    body: TutorStartRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    """Start an interactive tutoring session: plan subtopics + teach the first one."""
    study_session = await session_manager.get_session(session_id, db, redis)
    if not study_session or study_session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not study_session.topics:
        raise HTTPException(status_code=422, detail="No active topic. Please analyze content first.")

    current_topic = study_session.topics[-1]
    context = session_manager.build_context_window(study_session)

    # Get source text from first user interaction
    source_text = ""
    user_msgs = [i for i in study_session.interactions if i.role == "user"]
    if user_msgs:
        source_text = user_msgs[0].content

    # Step 1: Plan subtopics
    subtopics_data = await interactive_tutor.plan_subtopics(
        topic=current_topic.main_topic,
        source_text=source_text,
        session_context=context,
    )

    subtopic_names = [s.get("name", f"Subtopic {i+1}") for i, s in enumerate(subtopics_data)]

    # Step 2: Create tutor session in DB
    tutor_repo = TutorRepository(db)
    tutor_session = await tutor_repo.create_session(
        session_id=session_id,
        topic=current_topic.main_topic,
        subtopics=subtopic_names,
        difficulty=body.difficulty,
    )

    # Step 3: Teach first subtopic
    first_subtopic = subtopics_data[0]
    teaching = await interactive_tutor.teach_subtopic(
        subtopic=first_subtopic.get("name", "Introduction"),
        main_topic=current_topic.main_topic,
        difficulty_level=body.difficulty,
        source_text=source_text,
        session_context=context,
    )

    # Save step
    await tutor_repo.add_step(
        tutor_session_id=tutor_session.id,
        subtopic_name=first_subtopic.get("name", "Introduction"),
        subtopic_index=0,
        explanation=teaching["explanation"],
        question_text=teaching["question"],
    )
    await db.commit()

    return TutorStartResponse(
        tutor_session_id=tutor_session.id,
        topic=current_topic.main_topic,
        subtopics=[
            SubtopicPlan(
                name=s.get("name", ""),
                description=s.get("description", ""),
                prerequisite=s.get("prerequisite"),
            )
            for s in subtopics_data
        ],
        current_subtopic=first_subtopic.get("name", "Introduction"),
        current_index=0,
        total_subtopics=len(subtopics_data),
        explanation=teaching["explanation"],
        question=teaching["question"],
        difficulty=body.difficulty,
    )


@router.post("/sessions/{session_id}/tutor/answer", response_model=TutorAnswerResponse)
async def submit_tutor_answer(
    session_id: str,
    body: TutorAnswerRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    """Submit answer, get evaluation. If correct → advance. If wrong → hint + retry."""
    study_session = await session_manager.get_session(session_id, db, redis)
    if not study_session or study_session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    tutor_repo = TutorRepository(db)
    tutor_session = await tutor_repo.get_session(body.tutor_session_id)
    if not tutor_session or tutor_session.session_id != session_id:
        raise HTTPException(status_code=404, detail="Tutor session not found.")

    if tutor_session.is_complete:
        raise HTTPException(status_code=422, detail="Tutor session is already complete.")

    # Get current step
    current_step = await tutor_repo.get_current_step(body.tutor_session_id)
    if not current_step:
        raise HTTPException(status_code=422, detail="No pending question to answer.")

    context = session_manager.build_context_window(study_session)

    # Evaluate the answer
    evaluation = await interactive_tutor.evaluate_answer(
        question=current_step.question_text,
        student_answer=body.answer,
        subtopic=current_step.subtopic_name,
        main_topic=tutor_session.topic,
        explanation=current_step.explanation,
        difficulty_level=tutor_session.difficulty_level,
        session_context=context,
    )

    # Update step
    await tutor_repo.update_step_answer(
        step_id=current_step.id,
        student_answer=body.answer,
        is_correct=evaluation["is_correct"],
        score=evaluation["score"],
        feedback=evaluation["feedback"],
        hint=evaluation.get("hint"),
        attempts=current_step.attempts + 1,
    )

    # Write attempt history
    attempt_repo = AttemptRepository(db)
    topic_id = study_session.topics[-1].id if study_session.topics else None
    await attempt_repo.create(
        user_id=user_id,
        session_id=session_id,
        topic_id=topic_id,
        source_mode="tutor",
        difficulty=tutor_session.difficulty_level,
        is_correct=evaluation["is_correct"],
        score=evaluation["score"],
    )

    # Update counts
    correct = tutor_session.correct_count + (1 if evaluation["is_correct"] else 0)
    incorrect = tutor_session.incorrect_count + (0 if evaluation["is_correct"] else 1)

    # Track weak areas
    weak_areas = json.loads(tutor_session.weak_areas_json or "[]")
    if not evaluation["is_correct"] and current_step.subtopic_name not in weak_areas:
        weak_areas.append(current_step.subtopic_name)

    subtopics = json.loads(tutor_session.subtopics_json)
    current_index = tutor_session.current_subtopic_index

    # Adapt difficulty
    new_difficulty = interactive_tutor.adapt_difficulty(correct, incorrect, tutor_session.difficulty_level)

    response = TutorAnswerResponse(
        evaluation=TutorEvaluation(
            is_correct=evaluation["is_correct"],
            score=evaluation["score"],
            feedback=evaluation["feedback"],
            hint=evaluation.get("hint"),
            simplified_explanation=evaluation.get("simplified_explanation"),
            should_retry=evaluation.get("should_retry", False),
        ),
        current_index=current_index,
        total_subtopics=len(subtopics),
        correct_count=correct,
        incorrect_count=incorrect,
        difficulty=new_difficulty,
    )

    if evaluation["is_correct"] or not evaluation.get("should_retry", False):
        # Advance to next subtopic
        next_index = current_index + 1

        if next_index >= len(subtopics):
            # Session complete!
            await tutor_repo.update_session_progress(
                tutor_session_id=body.tutor_session_id,
                current_index=next_index,
                correct_count=correct,
                incorrect_count=incorrect,
                difficulty=new_difficulty,
                weak_areas=weak_areas,
                is_complete=True,
            )
            response.advanced = True
            response.is_session_complete = True
            response.current_index = next_index
        else:
            # Teach next subtopic
            source_text = ""
            user_msgs = [i for i in study_session.interactions if i.role == "user"]
            if user_msgs:
                source_text = user_msgs[0].content

            previous = subtopics[:next_index]
            teaching = await interactive_tutor.teach_subtopic(
                subtopic=subtopics[next_index],
                main_topic=tutor_session.topic,
                difficulty_level=new_difficulty,
                source_text=source_text,
                session_context=context,
                previous_subtopics=previous,
            )

            await tutor_repo.add_step(
                tutor_session_id=body.tutor_session_id,
                subtopic_name=subtopics[next_index],
                subtopic_index=next_index,
                explanation=teaching["explanation"],
                question_text=teaching["question"],
            )

            await tutor_repo.update_session_progress(
                tutor_session_id=body.tutor_session_id,
                current_index=next_index,
                correct_count=correct,
                incorrect_count=incorrect,
                difficulty=new_difficulty,
                weak_areas=weak_areas,
            )

            response.advanced = True
            response.next_subtopic = subtopics[next_index]
            response.next_explanation = teaching["explanation"]
            response.next_question = teaching["question"]
            response.current_index = next_index
    else:
        # Retry — don't advance
        await tutor_repo.update_session_progress(
            tutor_session_id=body.tutor_session_id,
            current_index=current_index,
            correct_count=correct,
            incorrect_count=incorrect,
            difficulty=new_difficulty,
            weak_areas=weak_areas,
        )

    await db.commit()
    return response


@router.post("/sessions/{session_id}/tutor/skip")
async def skip_subtopic(
    session_id: str,
    body: TutorSkipRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    """Skip current subtopic and move to the next one."""
    study_session = await session_manager.get_session(session_id, db, redis)
    if not study_session or study_session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    tutor_repo = TutorRepository(db)
    tutor_session = await tutor_repo.get_session(body.tutor_session_id)
    if not tutor_session or tutor_session.session_id != session_id:
        raise HTTPException(status_code=404, detail="Tutor session not found.")

    current_step = await tutor_repo.get_current_step(body.tutor_session_id)
    if current_step:
        await tutor_repo.mark_step_skipped(current_step.id)

    subtopics = json.loads(tutor_session.subtopics_json)
    next_index = tutor_session.current_subtopic_index + 1

    if next_index >= len(subtopics):
        await tutor_repo.update_session_progress(
            tutor_session_id=body.tutor_session_id,
            current_index=next_index,
            correct_count=tutor_session.correct_count,
            incorrect_count=tutor_session.incorrect_count,
            is_complete=True,
        )
        await db.commit()
        return {"skipped": True, "is_complete": True}

    # Teach next subtopic
    context = session_manager.build_context_window(study_session)
    source_text = ""
    user_msgs = [i for i in study_session.interactions if i.role == "user"]
    if user_msgs:
        source_text = user_msgs[0].content

    teaching = await interactive_tutor.teach_subtopic(
        subtopic=subtopics[next_index],
        main_topic=tutor_session.topic,
        difficulty_level=tutor_session.difficulty_level,
        source_text=source_text,
        session_context=context,
        previous_subtopics=subtopics[:next_index],
    )

    await tutor_repo.add_step(
        tutor_session_id=body.tutor_session_id,
        subtopic_name=subtopics[next_index],
        subtopic_index=next_index,
        explanation=teaching["explanation"],
        question_text=teaching["question"],
    )

    await tutor_repo.update_session_progress(
        tutor_session_id=body.tutor_session_id,
        current_index=next_index,
        correct_count=tutor_session.correct_count,
        incorrect_count=tutor_session.incorrect_count,
    )
    await db.commit()

    return {
        "skipped": True,
        "is_complete": False,
        "next_subtopic": subtopics[next_index],
        "next_explanation": teaching["explanation"],
        "next_question": teaching["question"],
        "current_index": next_index,
        "total_subtopics": len(subtopics),
    }


@router.get("/sessions/{session_id}/tutor/progress", response_model=TutorProgress)
async def get_tutor_progress(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    """Get current tutor session progress."""
    study_session = await session_manager.get_session(session_id, db, redis)
    if not study_session or study_session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    tutor_repo = TutorRepository(db)
    tutor_session = await tutor_repo.get_session_by_study_session(session_id)
    if not tutor_session:
        raise HTTPException(status_code=404, detail="No active tutor session.")

    subtopics = json.loads(tutor_session.subtopics_json)
    weak_areas = json.loads(tutor_session.weak_areas_json or "[]")

    steps = [
        TutorStepDetail(
            subtopic_name=step.subtopic_name,
            subtopic_index=step.subtopic_index,
            explanation=step.explanation,
            question_text=step.question_text,
            student_answer=step.student_answer,
            is_correct=step.is_correct,
            score=step.score,
            feedback=step.feedback,
            attempts=step.attempts,
            is_skipped=step.is_skipped,
        )
        for step in tutor_session.steps
    ]

    return TutorProgress(
        tutor_session_id=tutor_session.id,
        topic=tutor_session.topic,
        subtopics=subtopics,
        current_index=tutor_session.current_subtopic_index,
        total_subtopics=len(subtopics),
        correct_count=tutor_session.correct_count,
        incorrect_count=tutor_session.incorrect_count,
        difficulty=tutor_session.difficulty_level,
        is_complete=tutor_session.is_complete,
        weak_areas=weak_areas,
        steps=steps,
    )
