"""R5 — reason_code / reason_params on recommendations (i18n-ready, API backward compatible)

Revision ID: 20260320_rec_reason_i18n
Revises: 20260309_password_changed_at
Create Date: 2026-03-20

Colonnes optionnelles : la vérité produit pour l’affichage des raisons passe par reason_code +
reason_params côté front ; ``reason`` reste un fallback texte (ex. anglais court ou legacy).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260320_rec_reason_i18n"
down_revision: Union[str, None] = "20260309_password_changed_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("recommendations")}
    if "reason_code" not in cols:
        op.add_column(
            "recommendations",
            sa.Column("reason_code", sa.String(length=80), nullable=True),
        )
    if "reason_params" not in cols:
        op.add_column(
            "recommendations",
            sa.Column("reason_params", sa.JSON(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("recommendations", "reason_params")
    op.drop_column("recommendations", "reason_code")
