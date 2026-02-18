"""Add missing tables (user_sessions, notifications) and missing indexes

Revision ID: 20260205_missing_tables_idx
Revises: 20250107_add_enum_values
Create Date: 2026-02-05 12:00:00.000000

Cette migration :
- Crée la table 'user_sessions' (sessions utilisateur)
- Crée la table 'notifications' (notifications utilisateur)
- Ajoute l'index manquant idx_users_avatar_url sur la table 'users'
- Les index idx_users_jedi_rank, idx_users_total_points et idx_achievements_category
  existent déjà en BDD et ne sont pas recréés.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '20260205_missing_tables_idx'
down_revision: Union[str, None] = '20250107_add_enum_values'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing = set(insp.get_table_names())

    # ── Table user_sessions ─────────────────────────────────────────────
    if 'user_sessions' not in existing:
        op.create_table(
            'user_sessions',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('session_token', sa.String(255), unique=True, nullable=False),
            sa.Column('device_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('ip_address', postgresql.INET(), nullable=True),
            sa.Column('user_agent', sa.Text(), nullable=True),
            sa.Column('location_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true')),
            sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        )
        existing.add('user_sessions')

    # Index sur user_sessions (IF NOT EXISTS pour idempotence)
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_user_sessions_id ON user_sessions (id)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions (user_id)"))
    op.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_user_sessions_session_token ON user_sessions (session_token)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_user_sessions_is_active ON user_sessions (is_active)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_user_sessions_expires_at ON user_sessions (expires_at)"))

    # ── Table notifications ─────────────────────────────────────────────
    if 'notifications' not in existing:
        op.create_table(
            'notifications',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('type', sa.String(50), nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('message', sa.Text(), nullable=True),
            sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('action_url', sa.String(255), nullable=True),
            sa.Column('is_read', sa.Boolean(), server_default=sa.text('false')),
            sa.Column('is_email_sent', sa.Boolean(), server_default=sa.text('false')),
            sa.Column('priority', sa.Integer(), server_default=sa.text('5')),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        existing.add('notifications')

    # Index sur notifications (IF NOT EXISTS pour idempotence)
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_notifications_id ON notifications (id)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications (user_id)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_notifications_type ON notifications (type)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications (is_read)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_notifications_created_at ON notifications (created_at)"))

    # ── Index manquant sur users ────────────────────────────────────────
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_users_avatar_url ON users (avatar_url)"))


def downgrade() -> None:
    # Supprimer l'index sur users
    op.drop_index('idx_users_avatar_url', table_name='users')

    # Supprimer les index sur notifications
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_type', table_name='notifications')
    op.drop_index('idx_notifications_user', table_name='notifications')
    op.drop_index('ix_notifications_id', table_name='notifications')

    # Supprimer la table notifications
    op.drop_table('notifications')

    # Supprimer les index sur user_sessions
    op.drop_index('ix_user_sessions_expires_at', table_name='user_sessions')
    op.drop_index('ix_user_sessions_is_active', table_name='user_sessions')
    op.drop_index('ix_user_sessions_session_token', table_name='user_sessions')
    op.drop_index('idx_user_sessions_user_id', table_name='user_sessions')
    op.drop_index('ix_user_sessions_id', table_name='user_sessions')

    # Supprimer la table user_sessions
    op.drop_table('user_sessions')
