"""Gem bank routes."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Cookie, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from src.core.auth import validate_session
from src.db.session import get_db
from src.db.models.learning_platform import (
    Area,
    User,
    UserRole,
    RoleName,
    PublicationStatus,
    GemVisibility,
    Gem,
    GemCategory,
    GemTag,
    GemTagLink,
    GemAreaLink,
    UserGemCollection,
    CourseGem,
    LessonGem,
)
from src.schemas.gems import (
    GemCardRead,
    GemDetailRead,
    GemCategoryRead,
    GemTagRead,
    GemCreatorRead,
    AreaRead,
    GemCreate,
    GemUpdate,
    GemSaveRequest,
    UserGemCollectionRead,
)

router = APIRouter(tags=["gems"], prefix="/gems")


# ============================================================
# Auth helpers
# ============================================================


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


def get_current_user_optional(
    session_id: str | None = Cookie(None),
    db: Session = Depends(get_db),
) -> User | None:
    if not session_id:
        return None
    session = validate_session(session_id, db)
    if not session:
        return None
    return db.query(User).filter(User.id == session["user_id"]).first()


def require_admin(user: User, db: Session) -> None:
    role_link = (
        db.query(UserRole)
        .join(UserRole.role)
        .filter(
            UserRole.user_id == user.id,
            UserRole.role.has(
                or_(
                    UserRole.role.has(name=RoleName.SUPER_ADMIN),
                    UserRole.role.has(name=RoleName.CONTENT_ADMIN),
                )
            ),
        )
        .first()
    )
    if not role_link:
        raise HTTPException(status_code=403, detail="Admin access required")


# ============================================================
# Helper to build GemCardRead from a Gem ORM instance
# ============================================================


def _get_saves_counts(gem_ids: list[str], db: Session) -> dict[str, int]:
    """Compute saves_count for a list of gem IDs from user_gem_collection."""
    if not gem_ids:
        return {}
    rows = (
        db.query(UserGemCollection.gem_id, func.count(UserGemCollection.id))
        .filter(UserGemCollection.gem_id.in_(gem_ids))
        .group_by(UserGemCollection.gem_id)
        .all()
    )
    return {gem_id: cnt for gem_id, cnt in rows}


def _gem_to_card(
    gem: Gem,
    saved_gem_ids: set[str] | None = None,
    saves_counts: dict[str, int] | None = None,
) -> GemCardRead:
    tags = [GemTagRead(id=link.tag.id, name=link.tag.name) for link in gem.tag_links]
    return GemCardRead(
        id=gem.id,
        title=gem.title,
        description=gem.description,
        icon_url=gem.icon_url,
        gemini_url=gem.gemini_url,
        visibility=gem.visibility.value,
        is_featured=gem.is_featured,
        status=gem.status.value,
        saves_count=saves_counts.get(gem.id, 0) if saves_counts else 0,
        created_at=gem.created_at,
        category=GemCategoryRead(
            id=gem.category.id,
            name=gem.category.name,
            description=gem.category.description,
            icon=gem.category.icon,
            sort_order=gem.category.sort_order,
        ) if gem.category else None,
        area=AreaRead(id=gem.area.id, name=gem.area.name) if gem.area else None,
        created_by_user=GemCreatorRead(
            id=gem.created_by_user.id,
            first_name=gem.created_by_user.first_name,
            last_name=gem.created_by_user.last_name,
        ),
        tags=tags,
        is_saved=gem.id in saved_gem_ids if saved_gem_ids else False,
    )


def _gems_to_cards(
    gems: list[Gem],
    saved_gem_ids: set[str],
    db: Session,
) -> list[GemCardRead]:
    """Convert a list of Gem ORM instances to GemCardRead with saves_count."""
    gem_ids = [g.id for g in gems]
    saves_counts = _get_saves_counts(gem_ids, db)
    return [_gem_to_card(g, saved_gem_ids, saves_counts) for g in gems]


def _get_saved_gem_ids(user: User | None, db: Session) -> set[str]:
    if not user:
        return set()
    rows = (
        db.query(UserGemCollection.gem_id)
        .filter(UserGemCollection.user_id == user.id)
        .all()
    )
    return {r[0] for r in rows}


def _base_gem_query(db: Session):
    return (
        db.query(Gem)
        .options(
            joinedload(Gem.category),
            joinedload(Gem.area),
            joinedload(Gem.created_by_user),
            joinedload(Gem.tag_links).joinedload(GemTagLink.tag),
        )
        .filter(Gem.status == PublicationStatus.PUBLISHED)
    )


# Subquery for ordering by saves_count
def _saves_count_subquery(db: Session):
    return (
        db.query(
            UserGemCollection.gem_id,
            func.count(UserGemCollection.id).label("saves_count"),
        )
        .group_by(UserGemCollection.gem_id)
        .subquery()
    )


# ============================================================
# Public endpoints
# ============================================================


@router.get("/categories", response_model=list[GemCategoryRead])
def get_gem_categories(db: Session = Depends(get_db)):
    """List all gem categories ordered by sort_order."""
    categories = (
        db.query(GemCategory)
        .order_by(GemCategory.sort_order, GemCategory.name)
        .all()
    )
    return [
        GemCategoryRead(
            id=c.id, name=c.name, description=c.description,
            icon=c.icon, sort_order=c.sort_order,
        )
        for c in categories
    ]


@router.get("/tags", response_model=list[GemTagRead])
def get_gem_tags(db: Session = Depends(get_db)):
    """List tags ordered by usage count (most popular first)."""
    tags = (
        db.query(GemTag, func.count(GemTagLink.gem_id).label("cnt"))
        .outerjoin(GemTagLink, GemTag.id == GemTagLink.tag_id)
        .group_by(GemTag.id)
        .order_by(func.count(GemTagLink.gem_id).desc())
        .limit(50)
        .all()
    )
    return [GemTagRead(id=t.id, name=t.name) for t, _ in tags]


@router.get("/featured", response_model=list[GemCardRead])
def get_featured_gems(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
    limit: int = Query(default=10, le=20),
):
    """Get featured/highlighted gems."""
    saved_ids = _get_saved_gem_ids(current_user, db)
    gems = (
        _base_gem_query(db)
        .filter(Gem.is_featured.is_(True))
        .order_by(Gem.created_at.desc())
        .limit(limit)
        .all()
    )
    return _gems_to_cards(gems, saved_ids, db)


@router.get("/search", response_model=list[GemCardRead])
def search_gems(
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(default=20, le=50),
    skip: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Search gems by title, description, or tag names."""
    saved_ids = _get_saved_gem_ids(current_user, db)
    search_term = f"%{q}%"

    # Get gem IDs that match via tags
    tag_gem_ids = (
        db.query(GemTagLink.gem_id)
        .join(GemTag, GemTagLink.tag_id == GemTag.id)
        .filter(GemTag.name.ilike(search_term))
        .subquery()
    )

    gems = (
        _base_gem_query(db)
        .filter(
            or_(
                Gem.title.ilike(search_term),
                Gem.description.ilike(search_term),
                Gem.id.in_(tag_gem_ids),
            )
        )
        .order_by(Gem.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return _gems_to_cards(gems, saved_ids, db)


@router.get("/recommended", response_model=list[GemCardRead])
def get_recommended_gems(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
    limit: int = Query(default=10, le=20),
):
    """Get gems recommended for the current user based on their area."""
    saved_ids = _get_saved_gem_ids(current_user, db)

    if current_user.area_id:
        # Primary: gems whose main area matches or that have an area_link to user's area
        area_link_gem_ids = (
            db.query(GemAreaLink.gem_id)
            .filter(GemAreaLink.area_id == current_user.area_id)
            .subquery()
        )
        gems = (
            _base_gem_query(db)
            .filter(
                or_(
                    Gem.area_id == current_user.area_id,
                    Gem.id.in_(area_link_gem_ids),
                )
            )
            .order_by(Gem.created_at.desc())
            .limit(limit)
            .all()
        )
        if len(gems) >= limit:
            return _gems_to_cards(gems, saved_ids, db)

        # Fill with other popular gems
        existing_ids = {g.id for g in gems}
        remaining = limit - len(gems)
        extra = (
            _base_gem_query(db)
            .filter(Gem.id.notin_(existing_ids))
            .order_by(Gem.created_at.desc())
            .limit(remaining)
            .all()
        )
        gems.extend(extra)
    else:
        gems = (
            _base_gem_query(db)
            .order_by(Gem.created_at.desc())
            .limit(limit)
            .all()
        )

    return _gems_to_cards(gems, saved_ids, db)


@router.get("/collection", response_model=list[UserGemCollectionRead])
def get_user_gem_collection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get the current user's saved gem collection."""
    saved_ids = _get_saved_gem_ids(current_user, db)
    entries = (
        db.query(UserGemCollection)
        .options(
            joinedload(UserGemCollection.gem)
            .joinedload(Gem.category),
            joinedload(UserGemCollection.gem)
            .joinedload(Gem.area),
            joinedload(UserGemCollection.gem)
            .joinedload(Gem.created_by_user),
            joinedload(UserGemCollection.gem)
            .joinedload(Gem.tag_links)
            .joinedload(GemTagLink.tag),
        )
        .filter(UserGemCollection.user_id == current_user.id)
        .order_by(UserGemCollection.saved_at.desc())
        .all()
    )
    gem_ids = [e.gem.id for e in entries]
    saves_counts = _get_saves_counts(gem_ids, db)
    return [
        UserGemCollectionRead(
            id=e.id,
            gem=_gem_to_card(e.gem, saved_ids, saves_counts),
            saved_at=e.saved_at,
            notes=e.notes,
        )
        for e in entries
    ]


# ============================================================
# List and detail (must come after /categories, /tags, etc.)
# ============================================================


@router.get("", response_model=list[GemCardRead])
def get_gems(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
    limit: int = Query(default=20, le=50),
    skip: int = Query(default=0, ge=0),
    category_id: str | None = Query(default=None),
    area_id: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    featured: bool | None = Query(default=None),
):
    """List published gems with optional filters."""
    saved_ids = _get_saved_gem_ids(current_user, db)
    query = _base_gem_query(db)

    if category_id:
        query = query.filter(Gem.category_id == category_id)
    if area_id:
        area_link_ids = (
            db.query(GemAreaLink.gem_id)
            .filter(GemAreaLink.area_id == area_id)
            .subquery()
        )
        query = query.filter(or_(Gem.area_id == area_id, Gem.id.in_(area_link_ids)))
    if tag:
        tag_gem_ids = (
            db.query(GemTagLink.gem_id)
            .join(GemTag, GemTagLink.tag_id == GemTag.id)
            .filter(GemTag.name == tag)
            .subquery()
        )
        query = query.filter(Gem.id.in_(tag_gem_ids))
    if featured is not None:
        query = query.filter(Gem.is_featured.is_(featured))

    gems = query.order_by(Gem.created_at.desc()).offset(skip).limit(limit).all()
    return _gems_to_cards(gems, saved_ids, db)


@router.get("/{gem_id}", response_model=GemDetailRead)
def get_gem_detail(
    gem_id: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Get full detail of a gem."""
    gem = (
        _base_gem_query(db)
        .options(joinedload(Gem.area_links).joinedload(GemAreaLink.area))
        .filter(Gem.id == gem_id)
        .first()
    )
    if not gem:
        raise HTTPException(status_code=404, detail="Gem not found")

    saved_ids = _get_saved_gem_ids(current_user, db)
    tags = [GemTagRead(id=link.tag.id, name=link.tag.name) for link in gem.tag_links]
    areas = [AreaRead(id=link.area.id, name=link.area.name) for link in gem.area_links]

    saves_counts = _get_saves_counts([gem.id], db)

    return GemDetailRead(
        id=gem.id,
        title=gem.title,
        description=gem.description,
        instructions=gem.instructions,
        icon_url=gem.icon_url,
        gemini_url=gem.gemini_url,
        conversation_starters=gem.conversation_starters,
        visibility=gem.visibility.value,
        is_featured=gem.is_featured,
        status=gem.status.value,
        saves_count=saves_counts.get(gem.id, 0),
        created_at=gem.created_at,
        updated_at=gem.updated_at,
        category=GemCategoryRead(
            id=gem.category.id, name=gem.category.name,
            description=gem.category.description, icon=gem.category.icon,
            sort_order=gem.category.sort_order,
        ) if gem.category else None,
        area=AreaRead(id=gem.area.id, name=gem.area.name) if gem.area else None,
        areas=areas,
        created_by_user=GemCreatorRead(
            id=gem.created_by_user.id,
            first_name=gem.created_by_user.first_name,
            last_name=gem.created_by_user.last_name,
        ),
        tags=tags,
        is_saved=gem.id in saved_ids,
    )


# ============================================================
# Save / unsave (user collection)
# ============================================================


@router.post("/{gem_id}/save", status_code=201)
def save_gem_to_collection(
    gem_id: str,
    body: GemSaveRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Save a gem to the current user's collection."""
    gem = db.query(Gem).filter(Gem.id == gem_id, Gem.status == PublicationStatus.PUBLISHED).first()
    if not gem:
        raise HTTPException(status_code=404, detail="Gem not found")

    existing = (
        db.query(UserGemCollection)
        .filter(UserGemCollection.user_id == current_user.id, UserGemCollection.gem_id == gem_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Gem already saved")

    entry = UserGemCollection(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        gem_id=gem_id,
        notes=body.notes if body else None,
    )
    db.add(entry)
    db.commit()
    return {"message": "Gem saved to collection"}


@router.delete("/{gem_id}/save", status_code=204)
def remove_gem_from_collection(
    gem_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Remove a gem from the current user's collection."""
    entry = (
        db.query(UserGemCollection)
        .filter(UserGemCollection.user_id == current_user.id, UserGemCollection.gem_id == gem_id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Gem not in collection")
    db.delete(entry)
    db.commit()
    return None


# ============================================================
# Admin CRUD
# ============================================================


def _get_or_create_tags(tag_names: list[str], db: Session) -> list[GemTag]:
    tags = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        tag = db.query(GemTag).filter(GemTag.name == name).first()
        if not tag:
            tag = GemTag(id=str(uuid.uuid4()), name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


@router.post("", response_model=GemCardRead, status_code=201)
def create_gem(
    body: GemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Create a new gem (admin only)."""
    require_admin(current_user, db)

    gem_id = str(uuid.uuid4())
    gem = Gem(
        id=gem_id,
        category_id=body.category_id,
        area_id=body.area_id,
        created_by_user_id=current_user.id,
        title=body.title,
        description=body.description,
        instructions=body.instructions,
        icon_url=body.icon_url,
        gemini_url=body.gemini_url,
        conversation_starters=body.conversation_starters,
        visibility=GemVisibility(body.visibility),
        is_featured=body.is_featured,
        status=PublicationStatus(body.status),
    )
    db.add(gem)
    db.flush()

    # Tags
    tags = _get_or_create_tags(body.tag_names, db)
    for tag in tags:
        db.add(GemTagLink(gem_id=gem_id, tag_id=tag.id))

    # Additional area links
    for aid in body.additional_area_ids:
        db.add(GemAreaLink(gem_id=gem_id, area_id=aid))

    db.commit()

    # Reload with relationships
    gem = (
        _base_gem_query(db)
        .filter(Gem.id == gem_id)
        .first()
    )
    saves_counts = _get_saves_counts([gem_id], db)
    return _gem_to_card(gem, saves_counts=saves_counts)


@router.put("/{gem_id}", response_model=GemCardRead)
def update_gem(
    gem_id: str,
    body: GemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Update an existing gem (admin only)."""
    require_admin(current_user, db)

    gem = db.query(Gem).filter(Gem.id == gem_id).first()
    if not gem:
        raise HTTPException(status_code=404, detail="Gem not found")

    if body.title is not None:
        gem.title = body.title
    if body.description is not None:
        gem.description = body.description
    if body.instructions is not None:
        gem.instructions = body.instructions
    if body.icon_url is not None:
        gem.icon_url = body.icon_url
    if body.gemini_url is not None:
        gem.gemini_url = body.gemini_url
    if body.conversation_starters is not None:
        gem.conversation_starters = body.conversation_starters
    if body.category_id is not None:
        gem.category_id = body.category_id
    if body.area_id is not None:
        gem.area_id = body.area_id
    if body.visibility is not None:
        gem.visibility = GemVisibility(body.visibility)
    if body.is_featured is not None:
        gem.is_featured = body.is_featured
    if body.status is not None:
        gem.status = PublicationStatus(body.status)

    # Update tags
    if body.tag_names is not None:
        db.query(GemTagLink).filter(GemTagLink.gem_id == gem_id).delete()
        tags = _get_or_create_tags(body.tag_names, db)
        for tag in tags:
            db.add(GemTagLink(gem_id=gem_id, tag_id=tag.id))

    # Update additional areas
    if body.additional_area_ids is not None:
        db.query(GemAreaLink).filter(GemAreaLink.gem_id == gem_id).delete()
        for aid in body.additional_area_ids:
            db.add(GemAreaLink(gem_id=gem_id, area_id=aid))

    db.commit()

    gem = _base_gem_query(db).filter(Gem.id == gem_id).first()
    saves_counts = _get_saves_counts([gem_id], db)
    return _gem_to_card(gem, saves_counts=saves_counts)


@router.delete("/{gem_id}", status_code=204)
def archive_gem(
    gem_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Archive a gem (soft delete, admin only)."""
    require_admin(current_user, db)

    gem = db.query(Gem).filter(Gem.id == gem_id).first()
    if not gem:
        raise HTTPException(status_code=404, detail="Gem not found")

    gem.status = PublicationStatus.ARCHIVED
    db.commit()
    return None
