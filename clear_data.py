"""Clear all data from the database."""

from sqlalchemy import text
from src.db.session import SessionLocal


def clear_database():
    """Clear all data from the database."""
    db = SessionLocal()
    try:
        print("Clearing database...")
        
        # Disable foreign key checks temporarily
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        # Clear tables in reverse order
        tables = [
            "analytics_events",
            "user_badges",
            "course_badges",
            "lesson_progress",
            "lesson_resources",
            "lessons",
            "course_modules",
            "forum_comments",
            "forum_posts",
            "course_assignments",
            "enrollments",
            "courses",
            "badges",
            "user_roles",
            "users",
            "roles",
            "areas",
        ]
        
        for table in tables:
            db.execute(text(f"DELETE FROM {table}"))
            print(f"  ✓ Cleared {table}")
        
        # Re-enable foreign key checks
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        
        db.commit()
        print("\n✓ Database cleared successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error clearing database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    clear_database()
