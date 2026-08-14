"""identity membership and session epoch

Revision ID: 9713e795e01c
Revises: 1f3586a6b3d5
Create Date: 2026-08-14 12:50:29.978179

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9713e795e01c"
down_revision: Union[str, Sequence[str], None] = "1f3586a6b3d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "programme_memberships",
        sa.Column("identity_id", sa.UUID(), nullable=False),
        sa.Column("programme_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False, comment="Unique identifier for the record"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            comment="Timestamp (UTC) when record was created",
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
            comment="Timestamp (UTC) when record was last updated",
        ),
        sa.ForeignKeyConstraint(["identity_id"], ["user_identities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["programme_id"], ["programmes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "identity_id", "programme_id", name="uq_programme_memberships_identity_programme"
        ),
    )
    op.create_index(
        op.f("ix_programme_memberships_identity_id"),
        "programme_memberships",
        ["identity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_programme_memberships_programme_id"),
        "programme_memberships",
        ["programme_id"],
        unique=False,
    )
    op.add_column(
        "user_identities", sa.Column("display_name", sa.String(length=255), nullable=True)
    )
    op.execute("UPDATE user_identities SET display_name = credential_identifier")
    op.alter_column("user_identities", "display_name", nullable=False)
    op.add_column(
        "user_identities",
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
    )
    op.add_column(
        "user_identities",
        sa.Column("session_epoch", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("user_identities", "status", server_default=None)
    op.alter_column("user_identities", "session_epoch", server_default=None)
    op.drop_column("user_identities", "tenant_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "user_identities", sa.Column("tenant_id", sa.UUID(), autoincrement=False, nullable=True)
    )
    op.drop_column("user_identities", "session_epoch")
    op.drop_column("user_identities", "status")
    op.drop_column("user_identities", "display_name")
    op.drop_index(op.f("ix_programme_memberships_programme_id"), table_name="programme_memberships")
    op.drop_index(op.f("ix_programme_memberships_identity_id"), table_name="programme_memberships")
    op.drop_table("programme_memberships")
