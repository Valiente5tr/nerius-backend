"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Request
from sqlalchemy.orm import Session

from src.core.auth import authenticate_user, create_session, validate_session, invalidate_session
from src.db.session import get_db
from src.schemas.user import LoginRequest, LoginResponse, UserRead

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    http_request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Login with email and password. Sets a session cookie."""
    user = authenticate_user(request.email, request.password, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # Get user agent and IP from request
    user_agent = http_request.headers.get("user-agent")
    ip_address = http_request.client.host if http_request.client else None

    # Create session and set cookie
    session_id = create_session(
        user_id=user.id,
        db=db,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=30 * 24 * 60 * 60,  # 30 days (matches settings.session_expire_days)
    )

    return LoginResponse(
        message="Login successful",
        user=UserRead(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status.value,
        ),
    )


@router.post("/logout")
def logout(
    response: Response,
    session_id: str | None = Cookie(None),
    db: Session = Depends(get_db),
):
    """Logout and invalidate session."""
    if session_id:
        invalidate_session(session_id, db)
    
    response.delete_cookie("session_id")
    
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserRead)
def get_current_user(
    session_id: str | None = Cookie(None),
    db: Session = Depends(get_db),
):
    """Get current logged-in user information."""
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

    # Get user from database
    from src.db.models.learning_platform import User
    user = db.query(User).filter(User.id == session["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return UserRead(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        status=user.status.value,
    )


@router.get("/sessions")
def get_active_sessions(
    session_id: str | None = Cookie(None),
    db: Session = Depends(get_db),
):
    """Get all active sessions for the current user."""
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    session_data = validate_session(session_id, db)
    if not session_data:
        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid",
        )

    # Get all sessions for this user
    from src.db.models.learning_platform import Session as SessionModel
    from datetime import datetime
    
    sessions = (
        db.query(SessionModel)
        .filter(
            SessionModel.user_id == session_data["user_id"],
            SessionModel.expires_at > datetime.utcnow()
        )
        .order_by(SessionModel.last_activity_at.desc())
        .all()
    )

    return {
        "total": len(sessions),
        "sessions": [
            {
                "id": s.id,
                "created_at": s.created_at.isoformat(),
                "expires_at": s.expires_at.isoformat(),
                "last_activity_at": s.last_activity_at.isoformat(),
                "user_agent": s.user_agent,
                "ip_address": s.ip_address,
                "is_current": s.id == session_id,
            }
            for s in sessions
        ],
    }


@router.delete("/sessions/{session_id}")
def revoke_session(
    session_id: str,  # Path parameter: the session to revoke
    current_session_id: str | None = Cookie(None, alias="session_id"),  # Cookie: current user's session
    db: Session = Depends(get_db),
):
    """Revoke a specific session. Users can only revoke their own sessions."""
    if not current_session_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    current_session = validate_session(current_session_id, db)
    if not current_session:
        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid",
        )

    # Get the session to revoke
    from src.db.models.learning_platform import Session as SessionModel
    
    target_session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id)
        .first()
    )

    if not target_session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    # Check if the session belongs to the current user
    if target_session.user_id != current_session["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="Cannot revoke another user's session",
        )

    # Revoke the session
    invalidate_session(session_id, db)

    return {"message": "Session revoked successfully"}
