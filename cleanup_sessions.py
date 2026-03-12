"""Cleanup expired sessions from the database."""

from src.db.session import SessionLocal
from src.core.auth import cleanup_expired_sessions


def main():
    """Remove expired sessions from database."""
    db = SessionLocal()
    try:
        count = cleanup_expired_sessions(db)
        print(f"✓ Cleaned up {count} expired session(s)")
    except Exception as e:
        print(f"✗ Error cleaning up sessions: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
