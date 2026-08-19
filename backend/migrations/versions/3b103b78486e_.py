"""Add dns_trash table

Revision ID: 3b103b78486e
Revises: 2ad29c853a09
Create Date: 2026-08-19 15:48:03.901935

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3b103b78486e"
down_revision: Union[str, Sequence[str], None] = "2ad29c853a09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "dns_trash",
        sa.Column("entry_uuid", sa.UUID(), nullable=False),
        sa.Column(
            "deletion_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("actor", sa.String(), nullable=False),
        sa.Column(
            "object_type",
            sa.Enum("ZONE", "RECORD", name="dns_trash_object_type"),
            nullable=False,
        ),
        sa.Column(
            "object_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("entry_uuid"),
    )

    op.create_index(
        op.f("ix_dns_trash_actor"),
        "dns_trash",
        ["actor"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dns_trash_object_type"),
        "dns_trash",
        ["object_type"],
        unique=False,
    )

    op.execute("ALTER TYPE actionobjecttype RENAME TO action_log_object_type")


def downgrade() -> None:
    """Downgrade schema."""

    op.execute("ALTER TYPE action_log_object_type RENAME TO actionobjecttype")

    op.drop_index(
        op.f("ix_dns_trash_object_type"),
        table_name="dns_trash",
    )
    op.drop_index(
        op.f("ix_dns_trash_actor"),
        table_name="dns_trash",
    )
    op.drop_table("dns_trash")

    op.execute("DROP TYPE IF EXISTS dns_trash_object_type")
