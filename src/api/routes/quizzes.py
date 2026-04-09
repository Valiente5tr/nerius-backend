"""Quiz routes."""

import uuid
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.core.auth import validate_session
from src.db.session import get_db
from src.db.models.learning_platform import (
    User,
    Enrollment,
    EnrollmentStatus,
    Lesson,
    Quiz,
    QuizQuestion,
    QuizQuestionOption,
    QuizAttempt,
    QuizAttemptResponse,
    QuizAttemptStatus,
)
from src.schemas.quizzes import (
    QuizRead,
    QuizQuestionRead,
    QuizQuestionOptionRead,
    QuizAttemptSummaryRead,
    QuizAttemptDetailRead,
    QuizQuestionGradedRead,
    QuizQuestionOptionGradedRead,
    QuizResponseRead,
    QuizSubmitRequest,
    QuizSubmitResult,
)

router = APIRouter(tags=["quizzes"], prefix="/courses")


def get_current_user_required(
    session_id: str | None = Cookie(None),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user (required)."""
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    session = validate_session(session_id, db)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid",
        )

    user = db.query(User).filter(User.id == session["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


# ============================================================
# Helpers
# ============================================================


def _get_enrollment(db: Session, user_id: str, course_id: str) -> Enrollment:
    """Return the enrollment (active or completed) or raise 403."""
    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
            Enrollment.status.in_([EnrollmentStatus.active, EnrollmentStatus.completed]),
        )
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail="You are not enrolled in this course",
        )
    return enrollment


def _get_quiz_for_lesson(db: Session, lesson_id: str) -> Quiz:
    """Return the quiz for a lesson or raise 404."""
    quiz = (
        db.query(Quiz)
        .options(
            joinedload(Quiz.questions).joinedload(QuizQuestion.options),
        )
        .filter(Quiz.lesson_id == lesson_id)
        .first()
    )
    if not quiz:
        raise HTTPException(
            status_code=404,
            detail="No quiz found for this lesson",
        )
    return quiz


def _build_attempt_summary(attempt: QuizAttempt) -> QuizAttemptSummaryRead:
    return QuizAttemptSummaryRead(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        attempt_number=attempt.attempt_number,
        status=attempt.status.value,
        score=attempt.score,
        passed=attempt.passed,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        time_spent_seconds=attempt.time_spent_seconds,
    )


# ============================================================
# Endpoints
# ============================================================


@router.get(
    "/{course_id}/lessons/{lesson_id}/quiz",
    response_model=QuizRead,
)
def get_quiz(
    course_id: str,
    lesson_id: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get quiz with questions and options (without correct answers).

    - **course_id**: UUID of the course
    - **lesson_id**: UUID of the lesson

    Requires authentication.
    """
    _get_enrollment(db, current_user.id, course_id)
    quiz = _get_quiz_for_lesson(db, lesson_id)

    return QuizRead(
        id=quiz.id,
        lesson_id=quiz.lesson_id,
        title=quiz.title,
        description=quiz.description,
        passing_score=quiz.passing_score,
        max_attempts=quiz.max_attempts,
        time_limit_seconds=quiz.time_limit_seconds,
        is_required=quiz.is_required,
        questions=[
            QuizQuestionRead(
                id=q.id,
                question_type=q.question_type.value,
                question_text=q.question_text,
                points=q.points,
                sort_order=q.sort_order,
                options=[
                    QuizQuestionOptionRead(
                        id=o.id,
                        option_text=o.option_text,
                        sort_order=o.sort_order,
                        match_target=o.match_target,
                    )
                    for o in q.options
                ],
            )
            for q in quiz.questions
        ],
    )


@router.post(
    "/{course_id}/lessons/{lesson_id}/quiz/attempts",
    response_model=QuizAttemptSummaryRead,
    status_code=201,
)
def start_quiz_attempt(
    course_id: str,
    lesson_id: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Start a new quiz attempt.

    - **course_id**: UUID of the course
    - **lesson_id**: UUID of the lesson

    Checks enrollment and max_attempts limit before creating the attempt.
    Requires authentication.
    """
    enrollment = _get_enrollment(db, current_user.id, course_id)
    quiz = _get_quiz_for_lesson(db, lesson_id)

    # Count completed attempts
    completed_count = (
        db.query(func.count(QuizAttempt.id))
        .filter(
            QuizAttempt.quiz_id == quiz.id,
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.status == QuizAttemptStatus.COMPLETED,
        )
        .scalar()
    )

    if quiz.max_attempts is not None and completed_count >= quiz.max_attempts:
        raise HTTPException(
            status_code=400,
            detail="Maximum number of attempts reached",
        )

    # Determine attempt number
    max_attempt_number = (
        db.query(func.max(QuizAttempt.attempt_number))
        .filter(
            QuizAttempt.quiz_id == quiz.id,
            QuizAttempt.user_id == current_user.id,
        )
        .scalar()
    ) or 0

    now = datetime.utcnow()
    attempt = QuizAttempt(
        id=str(uuid.uuid4()),
        quiz_id=quiz.id,
        user_id=current_user.id,
        enrollment_id=enrollment.id,
        attempt_number=max_attempt_number + 1,
        status=QuizAttemptStatus.IN_PROGRESS,
        started_at=now,
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return _build_attempt_summary(attempt)


@router.put(
    "/{course_id}/quiz-attempts/{attempt_id}/responses",
)
def save_quiz_responses(
    course_id: str,
    attempt_id: str,
    body: QuizSubmitRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Save partial responses (auto-save). Does NOT grade or finalize the attempt."""
    attempt = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.id == attempt_id, QuizAttempt.user_id == current_user.id)
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.status != QuizAttemptStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Attempt already completed")

    for resp in body.responses:
        existing = (
            db.query(QuizAttemptResponse)
            .filter(
                QuizAttemptResponse.attempt_id == attempt_id,
                QuizAttemptResponse.question_id == resp.question_id,
            )
            .first()
        )
        if existing:
            existing.selected_option_id = resp.selected_option_id
            existing.text_response = resp.text_response
            existing.ordering_response = resp.ordering_response
            existing.matching_response = resp.matching_response
        else:
            db.add(QuizAttemptResponse(
                id=str(uuid.uuid4()),
                attempt_id=attempt_id,
                question_id=resp.question_id,
                selected_option_id=resp.selected_option_id,
                text_response=resp.text_response,
                ordering_response=resp.ordering_response,
                matching_response=resp.matching_response,
            ))

    db.commit()
    return {"message": "Responses saved", "saved_count": len(body.responses)}


@router.post(
    "/{course_id}/quiz-attempts/{attempt_id}/submit",
    response_model=QuizSubmitResult,
)
def submit_quiz_attempt(
    course_id: str,
    attempt_id: str,
    body: QuizSubmitRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Submit and grade a quiz attempt.

    - **course_id**: UUID of the course
    - **attempt_id**: UUID of the attempt

    Validates ownership, status, and time limit. Grades each response
    and calculates the final score.
    Requires authentication.
    """
    _get_enrollment(db, current_user.id, course_id)

    # Load attempt
    attempt = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.id == attempt_id)
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="This attempt does not belong to you")

    if attempt.status != QuizAttemptStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="This attempt is not in progress")

    # Load quiz with questions and options
    quiz = (
        db.query(Quiz)
        .options(
            joinedload(Quiz.questions).joinedload(QuizQuestion.options),
        )
        .filter(Quiz.id == attempt.quiz_id)
        .first()
    )

    now = datetime.utcnow()

    # Check time limit
    if quiz.time_limit_seconds is not None:
        elapsed = (now - attempt.started_at).total_seconds()
        if elapsed > quiz.time_limit_seconds:
            # Mark as timed out
            attempt.status = QuizAttemptStatus.TIMED_OUT
            attempt.completed_at = now
            attempt.time_spent_seconds = int(elapsed)
            db.commit()
            db.refresh(attempt)
            raise HTTPException(
                status_code=400,
                detail="Time limit exceeded",
            )

    # Build lookup maps
    questions_map: dict[str, QuizQuestion] = {q.id: q for q in quiz.questions}
    responses_map: dict[str, object] = {r.question_id: r for r in body.responses}

    total_points = Decimal("0")
    earned_points = Decimal("0")

    for question in quiz.questions:
        total_points += question.points
        response_data = responses_map.get(question.id)

        is_correct: bool | None = None
        points_earned = Decimal("0")
        selected_option_id = None
        text_response = None
        ordering_response = None
        matching_response = None

        if response_data:
            selected_option_id = response_data.selected_option_id
            text_response = response_data.text_response
            ordering_response = response_data.ordering_response
            matching_response = response_data.matching_response

            if question.question_type.value in ("multiple_choice", "true_false"):
                # Compare selected_option_id with the correct option
                correct_option = next(
                    (o for o in question.options if o.is_correct),
                    None,
                )
                if correct_option and selected_option_id == correct_option.id:
                    is_correct = True
                    points_earned = question.points
                else:
                    is_correct = False

            elif question.question_type.value == "short_answer":
                # Store response; auto-pass for now (manual grading needed)
                is_correct = None
                points_earned = question.points

            elif question.question_type.value == "ordering":
                # Correct order is options sorted by sort_order
                correct_order = [o.id for o in sorted(question.options, key=lambda o: o.sort_order)]
                if ordering_response == correct_order:
                    is_correct = True
                    points_earned = question.points
                else:
                    is_correct = False

            elif question.question_type.value == "matching":
                # For each option, check if matching_response[option_id] == option.match_target
                if matching_response:
                    correct_matches = 0
                    total_matches = len(question.options)
                    for option in question.options:
                        if matching_response.get(option.id) == option.match_target:
                            correct_matches += 1
                    if total_matches > 0:
                        ratio = Decimal(correct_matches) / Decimal(total_matches)
                        points_earned = (question.points * ratio).quantize(Decimal("0.01"))
                    is_correct = correct_matches == total_matches
                else:
                    is_correct = False

        earned_points += points_earned

        # Persist response — update if auto-saved, otherwise insert
        existing_response = (
            db.query(QuizAttemptResponse)
            .filter(
                QuizAttemptResponse.attempt_id == attempt.id,
                QuizAttemptResponse.question_id == question.id,
            )
            .first()
        )
        if existing_response:
            existing_response.selected_option_id = selected_option_id
            existing_response.text_response = text_response
            existing_response.ordering_response = ordering_response
            existing_response.matching_response = matching_response
            existing_response.is_correct = is_correct
            existing_response.points_earned = points_earned
        else:
            db.add(QuizAttemptResponse(
                id=str(uuid.uuid4()),
                attempt_id=attempt.id,
                question_id=question.id,
                selected_option_id=selected_option_id,
                text_response=text_response,
                ordering_response=ordering_response,
                matching_response=matching_response,
                is_correct=is_correct,
                points_earned=points_earned,
            ))

    # Calculate score
    if total_points > 0:
        score = (earned_points / total_points * Decimal("100")).quantize(Decimal("0.01"))
    else:
        score = Decimal("0")

    passed = score >= quiz.passing_score

    # Update attempt
    attempt.status = QuizAttemptStatus.COMPLETED
    attempt.score = score
    attempt.passed = passed
    attempt.completed_at = now
    attempt.time_spent_seconds = int((now - attempt.started_at).total_seconds())

    db.commit()
    db.refresh(attempt)

    return QuizSubmitResult(
        attempt=_build_attempt_summary(attempt),
        total_points=float(total_points),
        earned_points=float(earned_points),
        passed=passed,
    )


@router.get(
    "/{course_id}/quiz-attempts/{attempt_id}",
    response_model=QuizAttemptDetailRead,
)
def get_quiz_attempt_detail(
    course_id: str,
    attempt_id: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get detailed graded results for a completed attempt.

    - **course_id**: UUID of the course
    - **attempt_id**: UUID of the attempt

    Only available for completed attempts (correct answers and explanations
    are revealed). Requires authentication.
    """
    _get_enrollment(db, current_user.id, course_id)

    attempt = (
        db.query(QuizAttempt)
        .options(
            joinedload(QuizAttempt.responses),
        )
        .filter(QuizAttempt.id == attempt_id)
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="This attempt does not belong to you")

    is_completed = attempt.status in (QuizAttemptStatus.COMPLETED, QuizAttemptStatus.TIMED_OUT)

    # Load quiz questions with options
    quiz = (
        db.query(Quiz)
        .options(
            joinedload(Quiz.questions).joinedload(QuizQuestion.options),
        )
        .filter(Quiz.id == attempt.quiz_id)
        .first()
    )

    return QuizAttemptDetailRead(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        attempt_number=attempt.attempt_number,
        status=attempt.status.value,
        score=attempt.score,
        passed=attempt.passed,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        time_spent_seconds=attempt.time_spent_seconds,
        responses=[
            QuizResponseRead(
                id=r.id,
                question_id=r.question_id,
                selected_option_id=r.selected_option_id,
                text_response=r.text_response,
                ordering_response=r.ordering_response,
                matching_response=r.matching_response,
                is_correct=r.is_correct if is_completed else None,
                points_earned=r.points_earned if is_completed else None,
            )
            for r in attempt.responses
        ],
        questions=[
            QuizQuestionGradedRead(
                id=q.id,
                question_type=q.question_type.value,
                question_text=q.question_text,
                explanation=q.explanation if is_completed else None,
                points=q.points,
                sort_order=q.sort_order,
                options=[
                    QuizQuestionOptionGradedRead(
                        id=o.id,
                        option_text=o.option_text,
                        sort_order=o.sort_order,
                        match_target=o.match_target,
                        is_correct=o.is_correct if is_completed else False,
                    )
                    for o in q.options
                ],
            )
            for q in quiz.questions
        ],
    )


@router.get(
    "/{course_id}/lessons/{lesson_id}/quiz/attempts",
    response_model=list[QuizAttemptSummaryRead],
)
def get_quiz_attempts(
    course_id: str,
    lesson_id: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get all of the current user's attempts for a lesson's quiz.

    - **course_id**: UUID of the course
    - **lesson_id**: UUID of the lesson

    Returns attempts ordered by attempt_number.
    Requires authentication.
    """
    _get_enrollment(db, current_user.id, course_id)

    quiz = (
        db.query(Quiz)
        .filter(Quiz.lesson_id == lesson_id)
        .first()
    )
    if not quiz:
        raise HTTPException(
            status_code=404,
            detail="No quiz found for this lesson",
        )

    attempts = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.quiz_id == quiz.id,
            QuizAttempt.user_id == current_user.id,
        )
        .order_by(QuizAttempt.attempt_number.asc())
        .all()
    )

    return [_build_attempt_summary(a) for a in attempts]
