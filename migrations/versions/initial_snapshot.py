"""Initial schema snapshot

Revision ID: initial_snapshot
Revises:
Create Date: 2025-05-12 00:35:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "initial_snapshot"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cette migration représente l'état initial de la base de données.
    Étant donné que la base de données existe déjà avec toutes les tables,
    ce script ne fait que documenter la structure actuelle mais n'exécute
    aucune modification.
    """
    # Note: les tables et colonnes sont déjà créées dans la base de données
    # Ce code est donc uniquement documentaire et n'est pas exécuté
    pass


def downgrade() -> None:
    """
    On ne supporte pas la redescente depuis l'état initial
    """
    raise NotImplementedError("Downgrade not supported from initial state")
