"""Add password reset columns to users table

Revision ID: 20260209_password_reset
Revises: 20260206_exercises_missing_idx
Create Date: 2026-02-09 12:00:00.000000

Ajoute les colonnes pour la réinitialisation de mot de passe :
- password_reset_token
- password_reset_expires_at
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260209_password_reset'
down_revision: Union[str, None] = '20260206_exercises_missing_idx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c['name'] for c in insp.get_columns('users')}
    if 'password_reset_token' not in cols:
        op.add_column('users', sa.Column('password_reset_token', sa.String(255), nullable=True))
    if 'password_reset_expires_at' not in cols:
        op.add_column('users', sa.Column('password_reset_expires_at', sa.DateTime(timezone=True), nullable=True))
    indexes = {idx['name'] for idx in insp.get_indexes('users')}
    if 'ix_users_password_reset_token' not in indexes:
        op.create_index('ix_users_password_reset_token', 'users', ['password_reset_token'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_users_password_reset_token', table_name='users')
    op.drop_column('users', 'password_reset_expires_at')
    op.drop_column('users', 'password_reset_token')
