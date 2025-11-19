"""add_email_verification_fields

Revision ID: add_email_verification
Revises: fix_enum_case
Create Date: 2025-11-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_email_verification'
down_revision = 'fix_enum_case_2025'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter les colonnes de vérification email
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('email_verification_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('email_verification_sent_at', sa.DateTime(timezone=True), nullable=True))
    
    # Créer un index sur email_verification_token pour les recherches rapides
    op.create_index('ix_users_email_verification_token', 'users', ['email_verification_token'], unique=False)


def downgrade():
    # Supprimer l'index
    op.drop_index('ix_users_email_verification_token', table_name='users')
    
    # Supprimer les colonnes
    op.drop_column('users', 'email_verification_sent_at')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'is_email_verified')

