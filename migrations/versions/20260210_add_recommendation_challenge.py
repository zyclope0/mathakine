"""Add challenge_id to recommendations for challenge recommendations

Revision ID: 20260210_rec_challenge
Revises: 20260209_password_reset
Create Date: 2026-02-10 12:00:00.000000

Permet de recommander des défis logiques en plus des exercices.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260210_rec_challenge'
down_revision: Union[str, None] = '20260209_password_reset'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c['name'] for c in insp.get_columns('recommendations')}
    if 'challenge_id' not in cols:
        op.add_column(
            'recommendations',
            sa.Column('challenge_id', sa.Integer(), sa.ForeignKey('logic_challenges.id', ondelete='SET NULL'), nullable=True)
        )
    if 'recommendation_type' not in cols:
        op.add_column(
            'recommendations',
            sa.Column('recommendation_type', sa.String(20), nullable=False, server_default='exercise')
        )
    indexes = {idx['name'] for idx in insp.get_indexes('recommendations')}
    if 'ix_recommendations_challenge_id' not in indexes:
        op.create_index('ix_recommendations_challenge_id', 'recommendations', ['challenge_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_recommendations_challenge_id', table_name='recommendations')
    op.drop_column('recommendations', 'recommendation_type')
    op.drop_column('recommendations', 'challenge_id')
