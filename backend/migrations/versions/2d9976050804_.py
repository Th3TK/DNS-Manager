"""Initiate base schema

Revision ID: 2d9976050804
Revises: 
Create Date: 2026-08-13 15:26:49.363554

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2d9976050804'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('action_log',
        sa.Column('entry_uuid', sa.UUID(), nullable=False),
        sa.Column('action_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('actor_type', sa.Enum('USER', 'WATCHER', name='actortype'), nullable=False),
        sa.Column('actor', sa.String(), nullable=False),
        sa.Column('action', sa.Enum('CREATED', 'CHANGED', 'DELETED', 'RESTORED', 'PERMANENTLY_DELETED', name='changeaction'), nullable=False),
        sa.Column('affected_object', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('object_before', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('object_after', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('entry_uuid')
    )
    op.create_index(op.f('ix_action_log_action'), 'action_log', ['action'], unique=False)
    op.create_index(op.f('ix_action_log_actor'), 'action_log', ['actor'], unique=False)
    op.create_table('users',
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password', sa.String(length=60), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False, server_default=''),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default="false"),
        sa.Column('disabled', sa.Boolean(), nullable=False, server_default="false"),
        sa.PrimaryKeyConstraint('username')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_table('dns_records_metadata',
        sa.Column('zone_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('comment', sa.String(), nullable=True),
        sa.Column('checks_enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('origin', sa.Enum('MANUAL', 'AUTOMATIC', name='internal_record_origin'), nullable=False),
        sa.ForeignKeyConstraint(['author'], ['users.username'], ),
        sa.PrimaryKeyConstraint('zone_id', 'name', 'type', 'content')
    )
    op.create_index('ix_dns_records_metadata_zone_name', 'dns_records_metadata', ['zone_id'], unique=False)
    op.create_table('dns_zones_metadata',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('comment', sa.String(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['author'], ['users.username'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('dns_zones_metadata')
    op.drop_index('ix_dns_records_metadata_zone_name', table_name='dns_records_metadata')
    op.drop_table('dns_records_metadata')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_action_log_actor'), table_name='action_log')
    op.drop_index(op.f('ix_action_log_action'), table_name='action_log')
    op.drop_table('action_log')
    op.execute("DROP TYPE IF EXISTS internal_record_origin")
    op.execute("DROP TYPE IF EXISTS changeaction")
    op.execute("DROP TYPE IF EXISTS actortype")
