"""Certifications routes."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session, joinedload

from src.core.auth import validate_session
from src.db.session import get_db
from src.db.models.learning_platform import (
    User,
    Course,
    Enrollment,
    EnrollmentStatus,
    CourseCertification,
    UserCertification,
    CertificationRequestStatus,
    UserCourseGrant,
)
from src.schemas.certifications import (
    CourseCertificationRead,
    CertificationCatalogRead,
    UserCertificationRead,
)

router = APIRouter(tags=["certifications"])


def get_current_user_required(
    session_id: str | None = Cookie(None),
    db: Session = Depends(get_db),
) -> User:
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session = validate_session(session_id, db)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    user = db.query(User).filter(User.id == session["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _user_has_grant(db: Session, user_id: str, course_id: str) -> bool:
    return (
        db.query(UserCourseGrant)
        .filter(UserCourseGrant.user_id == user_id, UserCourseGrant.course_id == course_id)
        .first()
    ) is not None


@router.get("/courses/{course_id}/certification", response_model=CourseCertificationRead)
def get_course_certification(
    course_id: str,
    user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get certification info for a course, including whether it's free for this user."""
    certification = (
        db.query(CourseCertification)
        .filter(CourseCertification.course_id == course_id)
        .first()
    )
    if not certification:
        raise HTTPException(status_code=404, detail="This course has no certification")

    is_free = certification.cost is None or _user_has_grant(db, user.id, course_id)

    return CourseCertificationRead(
        id=certification.id,
        course_id=certification.course_id,
        title=certification.title,
        description=certification.description,
        cost=float(certification.cost) if certification.cost is not None else None,
        validity_days=certification.validity_days,
        is_free_for_user=is_free,
    )


@router.post(
    "/courses/{course_id}/certification/request",
    response_model=UserCertificationRead,
    status_code=201,
)
def request_certification(
    course_id: str,
    user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Request certification after completing a course."""
    certification = (
        db.query(CourseCertification)
        .filter(CourseCertification.course_id == course_id)
        .first()
    )
    if not certification:
        raise HTTPException(status_code=404, detail="This course has no certification")

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == user.id,
            Enrollment.course_id == course_id,
            Enrollment.status == EnrollmentStatus.completed,
        )
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=400, detail="You must complete the course before requesting certification")

    existing = (
        db.query(UserCertification)
        .filter(UserCertification.user_id == user.id, UserCertification.course_certification_id == certification.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="You have already requested this certification")

    user_cert = UserCertification(
        id=str(uuid.uuid4()),
        user_id=user.id,
        course_certification_id=certification.id,
        enrollment_id=enrollment.id,
        status=CertificationRequestStatus.REQUESTED,
        requested_at=datetime.utcnow(),
    )
    db.add(user_cert)
    db.commit()
    db.refresh(user_cert, attribute_names=["course_certification"])

    course = db.query(Course).filter(Course.id == course_id).first()
    return UserCertificationRead(
        id=user_cert.id,
        course_certification=CourseCertificationRead(
            id=certification.id,
            course_id=certification.course_id,
            title=certification.title,
            description=certification.description,
            cost=float(certification.cost) if certification.cost is not None else None,
            validity_days=certification.validity_days,
            is_free_for_user=_user_has_grant(db, user.id, course_id) or certification.cost is None,
        ),
        status=user_cert.status.value,
        requested_at=user_cert.requested_at,
        course_title=course.title if course else None,
    )


@router.get("/certifications/my", response_model=list[UserCertificationRead])
def get_my_certifications(
    user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get all certification requests for the current user."""
    user_certs = (
        db.query(UserCertification)
        .options(
            joinedload(UserCertification.course_certification)
            .joinedload(CourseCertification.course)
        )
        .filter(UserCertification.user_id == user.id)
        .order_by(UserCertification.requested_at.desc())
        .all()
    )

    results = []
    for uc in user_certs:
        cert = uc.course_certification
        course = cert.course if cert else None
        is_free = (cert.cost is None or _user_has_grant(db, user.id, cert.course_id)) if cert else False
        results.append(UserCertificationRead(
            id=uc.id,
            course_certification=CourseCertificationRead(
                id=cert.id, course_id=cert.course_id, title=cert.title,
                description=cert.description,
                cost=float(cert.cost) if cert.cost is not None else None,
                validity_days=cert.validity_days, is_free_for_user=is_free,
            ),
            status=uc.status.value,
            requested_at=uc.requested_at,
            approved_at=uc.approved_at,
            issued_at=uc.issued_at,
            rejected_at=uc.rejected_at,
            rejection_reason=uc.rejection_reason,
            expiration_date=uc.expiration_date,
            certificate_code=uc.certificate_code,
            certificate_url=uc.certificate_url,
            course_title=course.title if course else None,
        ))
    return results


@router.get("/certifications/catalog", response_model=list[CertificationCatalogRead])
def get_certifications_catalog(
    user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get all available certifications with course info and user status."""
    certs = (
        db.query(CourseCertification)
        .options(joinedload(CourseCertification.course).joinedload(Course.area))
        .all()
    )

    # Batch check user state
    user_cert_map = {}
    user_certs = (
        db.query(UserCertification)
        .filter(UserCertification.user_id == user.id)
        .all()
    )
    for uc in user_certs:
        user_cert_map[uc.course_certification_id] = uc.status.value

    completed_course_ids = set(
        row[0] for row in db.query(Enrollment.course_id)
        .filter(Enrollment.user_id == user.id, Enrollment.status == EnrollmentStatus.completed)
        .all()
    )

    grant_course_ids = set(
        row[0] for row in db.query(UserCourseGrant.course_id)
        .filter(UserCourseGrant.user_id == user.id)
        .all()
    )

    results = []
    for cert in certs:
        course = cert.course
        if not course:
            continue
        is_free = cert.cost is None or course.id in grant_course_ids
        results.append(CertificationCatalogRead(
            id=cert.id,
            course_id=course.id,
            title=cert.title,
            description=cert.description,
            cost=float(cert.cost) if cert.cost is not None else None,
            validity_days=cert.validity_days,
            is_free_for_user=is_free,
            course_title=course.title,
            course_cover_url=course.cover_url,
            course_area=course.area.name if course.area else None,
            course_completed=course.id in completed_course_ids,
            user_certification_status=user_cert_map.get(cert.id),
        ))

    return results
