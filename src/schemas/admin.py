"""Admin panel schemas for course management CRUD."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Course admin schemas
# ============================================================


class CourseAdminCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=180)
    description: str | None = None
    area_id: str | None = None
    cover_url: str | None = None
    estimated_minutes: int | None = Field(None, ge=0)
    access_type: str = "free"  # free | restricted
    status: str = "draft"  # draft | published | archived


class CourseAdminUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=180)
    description: str | None = None
    area_id: str | None = None
    cover_url: str | None = None
    estimated_minutes: int | None = Field(None, ge=0)
    access_type: str | None = None
    status: str | None = None


class CourseAreaMini(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class CourseCreatorMini(BaseModel):
    id: str
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class CourseAdminRead(BaseModel):
    """Course summary for admin listing — includes counts and all statuses."""
    id: str
    title: str
    description: str | None = None
    status: str
    access_type: str
    estimated_minutes: int | None = None
    cover_url: str | None = None
    created_at: datetime
    updated_at: datetime
    area: CourseAreaMini | None = None
    created_by_user: CourseCreatorMini
    modules_count: int = 0
    lessons_count: int = 0
    total_enrolled: int = 0
    total_completed: int = 0


# ============================================================
# Module admin schemas
# ============================================================


class ModuleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=180)


class ModuleUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=180)


class ModuleReorder(BaseModel):
    module_ids: list[str]


class ModuleAdminRead(BaseModel):
    id: str
    course_id: str
    title: str
    sort_order: int
    lessons_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Lesson admin schemas
# ============================================================


class LessonAdminCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=180)
    description: str | None = None
    estimated_minutes: int | None = Field(None, ge=0)


class LessonAdminUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=180)
    description: str | None = None
    estimated_minutes: int | None = Field(None, ge=0)


class LessonReorder(BaseModel):
    lesson_ids: list[str]


class LessonAdminRead(BaseModel):
    id: str
    module_id: str
    title: str
    description: str | None = None
    sort_order: int
    estimated_minutes: int | None = None
    has_quiz: bool = False
    resources_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Resource admin schemas
# ============================================================


class ResourceAdminCreate(BaseModel):
    resource_type: str  # video | pdf | slide | podcast
    title: str = Field(..., min_length=1, max_length=180)
    external_url: str = Field(..., min_length=1)
    thumbnail_url: str | None = None
    duration_seconds: int | None = Field(None, ge=0)
    resource_metadata: dict | None = None


class ResourceAdminUpdate(BaseModel):
    resource_type: str | None = None
    title: str | None = Field(None, min_length=1, max_length=180)
    external_url: str | None = Field(None, min_length=1)
    thumbnail_url: str | None = None
    duration_seconds: int | None = Field(None, ge=0)
    resource_metadata: dict | None = None


class ResourceAdminRead(BaseModel):
    id: str
    lesson_id: str
    resource_type: str
    title: str
    external_url: str
    thumbnail_url: str | None = None
    duration_seconds: int | None = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Quiz admin schemas
# ============================================================


class QuizAdminCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=180)
    description: str | None = None
    passing_score: float = Field(70.0, ge=0, le=100)
    max_attempts: int | None = Field(None, ge=1)
    time_limit_seconds: int | None = Field(None, ge=1)
    is_required: bool = True


class QuizAdminUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=180)
    description: str | None = None
    passing_score: float | None = Field(None, ge=0, le=100)
    max_attempts: int | None = Field(None, ge=1)
    time_limit_seconds: int | None = Field(None, ge=1)
    is_required: bool | None = None


class QuestionAdminCreate(BaseModel):
    question_type: str  # multiple_choice, true_false, short_answer, ordering, matching
    question_text: str = Field(..., min_length=1)
    explanation: str | None = None
    points: float = Field(1.0, ge=0)


class QuestionAdminUpdate(BaseModel):
    question_type: str | None = None
    question_text: str | None = Field(None, min_length=1)
    explanation: str | None = None
    points: float | None = Field(None, ge=0)


class OptionInput(BaseModel):
    option_text: str
    is_correct: bool = False
    sort_order: int
    match_target: str | None = None


class OptionsBulkReplace(BaseModel):
    options: list[OptionInput]


class QuestionReorder(BaseModel):
    question_ids: list[str]


# ============================================================
# Badge linking schemas
# ============================================================


class BadgeMini(BaseModel):
    id: str
    name: str
    description: str | None = None
    icon_url: str | None = None
    main_color: str
    secondary_color: str

    model_config = ConfigDict(from_attributes=True)


class CourseBadgeLinkCreate(BaseModel):
    badge_id: str
    progress_percentage: float = Field(100.0, ge=0, le=100)


class CourseBadgeLinkUpdate(BaseModel):
    progress_percentage: float = Field(..., ge=0, le=100)


class CourseBadgeLinkRead(BaseModel):
    id: str
    course_id: str
    badge: BadgeMini
    progress_percentage: float


# ============================================================
# Gem linking schemas
# ============================================================


class GemLinkCreate(BaseModel):
    gem_id: str
    sort_order: int = 0


class GemMini(BaseModel):
    id: str
    title: str
    description: str | None = None
    icon_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CourseGemLinkRead(BaseModel):
    id: str
    course_id: str
    gem: GemMini
    sort_order: int


class LessonGemLinkRead(BaseModel):
    id: str
    lesson_id: str
    gem: GemMini
    sort_order: int


# ============================================================
# Certification schemas
# ============================================================


class CertificationAdminCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    cost: float | None = Field(None, ge=0)
    validity_days: int | None = Field(None, ge=1)


class CertificationAdminUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    cost: float | None = Field(None, ge=0)
    validity_days: int | None = Field(None, ge=1)


class CertificationAdminRead(BaseModel):
    id: str
    course_id: str
    title: str
    description: str | None = None
    cost: float | None = None
    validity_days: int | None = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Access grants schemas
# ============================================================


class GrantUserMini(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class GrantCreate(BaseModel):
    user_ids: list[str]


class GrantAdminRead(BaseModel):
    id: str
    course_id: str
    user: GrantUserMini
    granted_at: datetime


# ============================================================
# User role management (super admin only)
# ============================================================


class UserWithRolesRead(BaseModel):
    """User listing for role management."""
    id: str
    first_name: str
    last_name: str
    email: str
    status: str
    area_name: str | None = None
    roles: list[str] = []       # All role names
    admin_role: str | None = None  # The admin role (if any): super_admin, content_admin, content_editor, content_viewer
    is_learner: bool = False
    created_at: datetime


class SetAdminRoleRequest(BaseModel):
    """Body for setting a user's admin role. Use null to remove admin access."""
    role: str | None = None  # "content_admin" | "content_editor" | "content_viewer" | null
