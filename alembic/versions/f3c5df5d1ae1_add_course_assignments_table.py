"""add_course_assignments_table

Revision ID: f3c5df5d1ae1
Revises: b08dc4b458b6
Create Date: 2026-03-12 16:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3c5df5d1ae1"
down_revision: Union[str, Sequence[str], None] = "b08dc4b458b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_assignments",
        sa.Column("course_id", sa.CHAR(length=36), nullable=False),
        sa.Column("assigned_by_user_id", sa.CHAR(length=36), nullable=True),
        sa.Column("assigned_to_user_id", sa.CHAR(length=36), nullable=False),
        sa.Column("due_date", sa.TIMESTAMP(), nullable=False),
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_by_user_id"],
            ["users.id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_to_user_id"],
            ["users.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "assigned_to_user_id",
            "course_id",
            name="uq_course_assignments_user_course",
        ),
    )
    op.create_index(
        "idx_course_assignments_due_date",
        "course_assignments",
        ["due_date"],
        unique=False,
    )
    op.create_index(
        "idx_course_assignments_assigned_by",
        "course_assignments",
        ["assigned_by_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_course_assignments_assigned_by", table_name="course_assignments")
    op.drop_index("idx_course_assignments_due_date", table_name="course_assignments")
    op.drop_table("course_assignments")
