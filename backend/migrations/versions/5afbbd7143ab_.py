"""Updated the action log table

Revision ID: 5afbbd7143ab
Revises: 2d9976050804
Create Date: 2026-08-17 08:59:45.648011

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5afbbd7143ab"
down_revision: Union[str, Sequence[str], None] = "2d9976050804"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    action_object_type = sa.Enum(
        "ZONE",
        "RECORD",
        name="actionobjecttype",
    )

    action_object_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "action_log",
        sa.Column(
            "affected_object_type",
            action_object_type,
            nullable=False,
        ),
    )

    op.drop_column("action_log", "affected_object")

    op.create_index(
        op.f("ix_action_log_affected_object_type"),
        "action_log",
        ["affected_object_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_action_log_affected_object_type"), table_name="action_log")
    op.drop_column("action_log", "affected_object_type")
    op.execute("DROP TYPE IF EXISTS actionobjecttype")
