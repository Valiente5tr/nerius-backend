"""Quiz schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# Read schemas (learner-facing, no correct answers)
# ============================================================


class QuizQuestionOptionRead(BaseModel):
    """Option without is_correct — learners must not see correct answers."""

    id: str
    option_text: str
    sort_order: int
    match_target: str | None

    model_config = ConfigDict(from_attributes=True)


class QuizQuestionRead(BaseModel):
    """Question with options (no correct answer info)."""

    id: str
    question_type: str
    question_text: str
    points: float
    sort_order: int
    options: list[QuizQuestionOptionRead]

    model_config = ConfigDict(from_attributes=True)


class QuizRead(BaseModel):
    """Full quiz with questions and options."""

    id: str
    lesson_id: str
    title: str
    description: str | None
    passing_score: float
    max_attempts: int | None
    time_limit_seconds: int | None
    is_required: bool
    questions: list[QuizQuestionRead]

    model_config = ConfigDict(from_attributes=True)


class QuizSummaryRead(BaseModel):
    """Lightweight quiz info for lesson listings."""

    id: str
    lesson_id: str
    title: str
    passing_score: float
    is_required: bool
    questions_count: int

    model_config = ConfigDict(from_attributes=True)


class QuizAttemptSummaryRead(BaseModel):
    """Attempt summary without detailed responses."""

    id: str
    quiz_id: str
    attempt_number: int
    status: str
    score: float | None
    passed: bool | None
    started_at: datetime
    completed_at: datetime | None
    time_spent_seconds: int | None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Graded schemas (correct answers revealed after completion)
# ============================================================


class QuizQuestionOptionGradedRead(BaseModel):
    """Option with is_correct revealed for graded results."""

    id: str
    option_text: str
    sort_order: int
    match_target: str | None
    is_correct: bool

    model_config = ConfigDict(from_attributes=True)


class QuizQuestionGradedRead(BaseModel):
    """Question with explanation and correct answers revealed."""

    id: str
    question_type: str
    question_text: str
    explanation: str | None
    points: float
    sort_order: int
    options: list[QuizQuestionOptionGradedRead]

    model_config = ConfigDict(from_attributes=True)


class QuizResponseRead(BaseModel):
    """A single response within a graded attempt."""

    id: str
    question_id: str
    selected_option_id: str | None
    text_response: str | None
    ordering_response: list[str] | None
    matching_response: dict[str, str] | None
    is_correct: bool | None
    points_earned: float | None

    model_config = ConfigDict(from_attributes=True)


class QuizAttemptDetailRead(QuizAttemptSummaryRead):
    """Detailed attempt with graded questions and responses."""

    responses: list[QuizResponseRead]
    questions: list[QuizQuestionGradedRead]


# ============================================================
# Input schemas for quiz submission
# ============================================================


class QuizResponseSubmit(BaseModel):
    """A single response submitted by the learner."""

    question_id: str
    selected_option_id: str | None = None
    text_response: str | None = None
    ordering_response: list[str] | None = None
    matching_response: dict[str, str] | None = None


class QuizSubmitRequest(BaseModel):
    """Request body for submitting a quiz attempt."""

    responses: list[QuizResponseSubmit]


class QuizSubmitResult(BaseModel):
    """Result returned after grading a quiz submission."""

    attempt: QuizAttemptSummaryRead
    total_points: float
    earned_points: float
    passed: bool

    model_config = ConfigDict(from_attributes=True)
