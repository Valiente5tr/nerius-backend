"""Role-based permission helpers.

Admin role hierarchy (within admin scope):
- super_admin       — Can do everything across all panels
- content_admin     — Rol 1: Full admin within admin panel (create/publish/edit/delete)
- content_editor    — Rol 2: Can edit existing courses but NOT create/publish
- content_viewer    — Rol 3: Cannot access course management (no "Cursos" tab)
"""

from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.orm import Session

from src.core.auth import validate_session
from src.db.session import get_db
from src.db.models.learning_platform import User, UserRole, Role, RoleName


# Role groups
ADMIN_ROLES_ALL = [
    RoleName.SUPER_ADMIN,
    RoleName.CONTENT_ADMIN,
    RoleName.CONTENT_EDITOR,
    RoleName.CONTENT_VIEWER,
]

# Roles that can CREATE or PUBLISH courses
COURSE_PUBLISHER_ROLES = [RoleName.SUPER_ADMIN, RoleName.CONTENT_ADMIN]

# Roles that can EDIT existing courses (mutate modules, lessons, resources, etc.)
COURSE_EDITOR_ROLES = [
    RoleName.SUPER_ADMIN,
    RoleName.CONTENT_ADMIN,
    RoleName.CONTENT_EDITOR,
]

# Roles that can READ the admin course list (not viewers)
COURSE_READER_ROLES = [
    RoleName.SUPER_ADMIN,
    RoleName.CONTENT_ADMIN,
    RoleName.CONTENT_EDITOR,
]


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


def get_user_role_names(db: Session, user_id: str) -> list[str]:
    """Return the list of role names for a user."""
    rows = (
        db.query(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    return [r[0].value for r in rows]


def _user_has_any_role(db: Session, user_id: str, role_names: list[RoleName]) -> bool:
    return (
        db.query(UserRole)
        .join(Role, Role.id == UserRole.role_id)
        .filter(UserRole.user_id == user_id, Role.name.in_(role_names))
        .first()
    ) is not None


def require_admin(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
) -> User:
    """Allow any admin role (super, admin, editor, viewer)."""
    if not _user_has_any_role(db, current_user.id, ADMIN_ROLES_ALL):
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
    return current_user


def require_course_reader(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
) -> User:
    """Allow super_admin, content_admin, content_editor (NOT viewer)."""
    if not _user_has_any_role(db, current_user.id, COURSE_READER_ROLES):
        raise HTTPException(status_code=403, detail="No tienes permiso para ver cursos")
    return current_user


def require_course_editor(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
) -> User:
    """Allow super_admin, content_admin, content_editor — can edit existing courses."""
    if not _user_has_any_role(db, current_user.id, COURSE_EDITOR_ROLES):
        raise HTTPException(status_code=403, detail="No tienes permiso para editar cursos")
    return current_user


def require_course_publisher(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
) -> User:
    """Allow only super_admin and content_admin — can create, delete, publish."""
    if not _user_has_any_role(db, current_user.id, COURSE_PUBLISHER_ROLES):
        raise HTTPException(
            status_code=403,
            detail="Solo administradores de contenido pueden crear o publicar cursos",
        )
    return current_user


def require_super_admin(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
) -> User:
    """Allow only super_admin."""
    if not _user_has_any_role(db, current_user.id, [RoleName.SUPER_ADMIN]):
        raise HTTPException(status_code=403, detail="Se requiere rol de super administrador")
    return current_user
