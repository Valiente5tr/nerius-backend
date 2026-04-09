from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CourseCertificationRead(BaseModel):
    id: str
    course_id: str
    title: str
    description: str | None = None
    cost: float | None = None  # null = free
    validity_days: int | None = None  # null = no expiration
    is_free_for_user: bool = False  # true if user has a grant for this course
    model_config = ConfigDict(from_attributes=True)


class CertificationCatalogRead(BaseModel):
    """Certification with course info for catalog display."""
    id: str
    course_id: str
    title: str
    description: str | None = None
    cost: float | None = None
    validity_days: int | None = None
    is_free_for_user: bool = False
    course_title: str
    course_cover_url: str | None = None
    course_area: str | None = None
    course_completed: bool = False
    user_certification_status: str | None = None  # null if not requested


class UserCertificationRead(BaseModel):
    id: str
    course_certification: CourseCertificationRead
    status: str  # requested, approved, issued, rejected
    requested_at: datetime
    approved_at: datetime | None = None
    issued_at: datetime | None = None
    rejected_at: datetime | None = None
    rejection_reason: str | None = None
    expiration_date: datetime | None = None
    certificate_code: str | None = None
    certificate_url: str | None = None
    course_title: str | None = None
    model_config = ConfigDict(from_attributes=True)
