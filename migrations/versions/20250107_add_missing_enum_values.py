"""Add missing enum values for LogicChallengeType

Revision ID: 20250107_add_enum_values
Revises: 20250513_baseline
Create Date: 2025-01-07 13:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250107_add_enum_values"
down_revision: Union[str, None] = "20250513_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Ajoute les valeurs manquantes aux enums PostgreSQL.

    Pour LogicChallengeType, ajoute :
    - VISUAL (défis visuels et spatiaux)
    - RIDDLE (énigmes et puzzles)
    """
    # Vérifier si les valeurs existent déjà avant de les ajouter
    # Note: PostgreSQL ne permet pas d'ajouter une valeur si elle existe déjà

    # Ajouter VISUAL à logicchallengetype
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'VISUAL' 
                AND enumtypid = 'logicchallengetype'::regtype
            ) THEN
                ALTER TYPE logicchallengetype ADD VALUE 'VISUAL';
            END IF;
        END $$;
    """)

    # Ajouter RIDDLE à logicchallengetype
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'RIDDLE' 
                AND enumtypid = 'logicchallengetype'::regtype
            ) THEN
                ALTER TYPE logicchallengetype ADD VALUE 'RIDDLE';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """
    Note: PostgreSQL ne permet pas de supprimer des valeurs d'enum directement.
    Pour revenir en arrière, il faudrait :
    1. Créer un nouveau type enum sans ces valeurs
    2. Migrer les données
    3. Supprimer l'ancien type
    4. Renommer le nouveau type

    Cette opération est complexe et risquée, donc on laisse les valeurs en place.
    """
    # PostgreSQL ne permet pas de supprimer des valeurs d'enum directement
    # Les valeurs resteront dans la base de données mais ne seront plus utilisées
    pass
