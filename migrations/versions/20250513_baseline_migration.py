"""Baseline migration after schema snapshot

Revision ID: 20250513_baseline
Revises: initial_snapshot
Create Date: 2025-05-13 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250513_baseline'
down_revision: Union[str, None] = 'initial_snapshot'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migration de base à partir de laquelle de nouvelles migrations seront créées.
    Cette migration ne fait aucune modification car elle représente l'état
    actuel de la base de données après l'initialisation.
    """
    pass


def downgrade() -> None:
    """
    Annulation de la migration de base (opération sans effet).
    """
    pass 