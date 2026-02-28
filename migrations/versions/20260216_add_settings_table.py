"""Add settings table for global config (paramètres du Temple)

Revision ID: 20260216_settings
Revises: 20260216_audit_log
Create Date: 2026-02-16

Table settings : paramètres globaux modifiables via l'admin (/admin/config).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260216_settings"
down_revision: Union[str, None] = "20260216_audit_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "settings" in insp.get_table_names():
        op.execute(
            sa.text("CREATE INDEX IF NOT EXISTS ix_settings_id ON settings (id)")
        )
        op.execute(
            sa.text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_settings_key ON settings (key)"
            )
        )
        op.execute(
            sa.text(
                "CREATE INDEX IF NOT EXISTS ix_settings_category ON settings (category)"
            )
        )
        return
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(255), unique=True, nullable=False),
        sa.Column("value", sa.String(1024), nullable=True),
        sa.Column("value_json", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("is_system", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("is_public", sa.Boolean(), server_default=sa.text("true")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_settings_id ON settings (id)"))
    op.execute(
        sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_settings_key ON settings (key)")
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS ix_settings_category ON settings (category)"
        )
    )


def downgrade() -> None:
    op.drop_index("ix_settings_category", table_name="settings")
    op.drop_index("ix_settings_key", table_name="settings")
    op.drop_index("ix_settings_id", table_name="settings")
    op.drop_table("settings")
