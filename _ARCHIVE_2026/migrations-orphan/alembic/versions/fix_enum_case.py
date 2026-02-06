"""Fix enum values to match PostgreSQL case sensitivity

Revision ID: fix_enum_case_2025
Revises: 
Create Date: 2025-11-16 23:00:00

This migration fixes the enum values in PostgreSQL to accept UPPERCASE values
as expected by SQLAlchemy's default behavior.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fix_enum_case_2025'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Drop and recreate the enum types with UPPERCASE values
    to match SQLAlchemy's automatic conversion.
    
    SAFE because the database is currently empty (0 exercises, 0 challenges).
    """
    
    # Temporairement changer le type de la colonne en text
    op.execute("ALTER TABLE exercises ALTER COLUMN exercise_type TYPE text USING exercise_type::text")
    op.execute("ALTER TABLE exercises ALTER COLUMN difficulty TYPE text USING difficulty::text")
    
    # Supprimer les anciens enums
    op.execute("DROP TYPE IF EXISTS exercisetype CASCADE")
    op.execute("DROP TYPE IF EXISTS difficultylevel CASCADE")
    
    # Recréer les enums avec valeurs en MAJUSCULES
    op.execute("""
        CREATE TYPE exercisetype AS ENUM (
            'ADDITION',
            'SOUSTRACTION', 
            'MULTIPLICATION',
            'DIVISION',
            'FRACTIONS',
            'GEOMETRIE',
            'TEXTE',
            'MIXTE',
            'DIVERS'
        )
    """)
    
    op.execute("""
        CREATE TYPE difficultylevel AS ENUM (
            'INITIE',
            'PADAWAN',
            'CHEVALIER',
            'MAITRE'
        )
    """)
    
    # Réappliquer les types enum aux colonnes
    op.execute("ALTER TABLE exercises ALTER COLUMN exercise_type TYPE exercisetype USING exercise_type::exercisetype")
    op.execute("ALTER TABLE exercises ALTER COLUMN difficulty TYPE difficultylevel USING difficulty::difficultylevel")
    
    print("✅ Migration réussie : enums corrigés pour accepter les MAJUSCULES")


def downgrade():
    """
    Revert to lowercase enum values.
    
    WARNING: This will break the application if data exists with uppercase values.
    Only use if rolling back immediately after upgrade.
    """
    
    # Temporairement changer en text
    op.execute("ALTER TABLE exercises ALTER COLUMN exercise_type TYPE text USING exercise_type::text")
    op.execute("ALTER TABLE exercises ALTER COLUMN difficulty TYPE text USING difficulty::text")
    
    # Supprimer les enums MAJUSCULES
    op.execute("DROP TYPE IF EXISTS exercisetype CASCADE")
    op.execute("DROP TYPE IF EXISTS difficultylevel CASCADE")
    
    # Recréer avec minuscules (état original)
    op.execute("""
        CREATE TYPE exercisetype AS ENUM (
            'addition',
            'soustraction', 
            'multiplication',
            'division',
            'fractions',
            'geometrie',
            'texte',
            'mixte',
            'divers'
        )
    """)
    
    op.execute("""
        CREATE TYPE difficultylevel AS ENUM (
            'initie',
            'padawan',
            'chevalier',
            'maitre'
        )
    """)
    
    # Réappliquer les types
    op.execute("ALTER TABLE exercises ALTER COLUMN exercise_type TYPE exercisetype USING LOWER(exercise_type)::exercisetype")
    op.execute("ALTER TABLE exercises ALTER COLUMN difficulty TYPE difficultylevel USING LOWER(difficulty)::difficultylevel")
    
    print("⚠️ Downgrade effectué : retour aux minuscules")


