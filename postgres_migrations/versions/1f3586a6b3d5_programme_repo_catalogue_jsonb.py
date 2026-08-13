"""programme repo_catalogue jsonb

Revision ID: 1f3586a6b3d5
Revises: 5e85268f844f
Create Date: 2026-08-13 08:48:03.721477

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1f3586a6b3d5"
down_revision: Union[str, Sequence[str], None] = "5e85268f844f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "programmes",
        sa.Column(
            "repo_catalogue",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.alter_column("programmes", "repo_catalogue", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("programmes", "repo_catalogue")
