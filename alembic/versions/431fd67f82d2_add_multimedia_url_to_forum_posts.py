"""add_multimedia_url_to_forum_posts

Revision ID: 431fd67f82d2
Revises: b0efe930db00
Create Date: 2026-03-12 02:34:48.609531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = '431fd67f82d2'
down_revision: Union[str, Sequence[str], None] = 'b0efe930db00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add multimedia_url column to forum_posts table
    op.add_column('forum_posts', sa.Column('multimedia_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove multimedia_url column from forum_posts table
    op.drop_column('forum_posts', 'multimedia_url')
