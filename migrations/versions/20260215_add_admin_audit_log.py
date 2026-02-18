"""Add admin_audit_logs table for audit trail

Revision ID: 20260215_audit_log
Revises: 20260216_userrole_uppercase
Create Date: 2026-02-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260216_audit_log"
down_revision: Union[str, None] = "20260216_userrole"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing = set(insp.get_table_names())
    if "admin_audit_logs" not in existing:
        op.create_table(
            "admin_audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("admin_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("action", sa.String(50), nullable=False),
            sa.Column("resource_type", sa.String(30), nullable=True),
            sa.Column("resource_id", sa.Integer(), nullable=True),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_admin_audit_logs_id ON admin_audit_logs (id)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_admin_audit_logs_admin_user_id ON admin_audit_logs (admin_user_id)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_admin_audit_logs_action ON admin_audit_logs (action)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_admin_audit_logs_resource_type ON admin_audit_logs (resource_type)"))
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_admin_audit_logs_created_at ON admin_audit_logs (created_at)"))


def downgrade() -> None:
    op.drop_index("ix_admin_audit_logs_created_at", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_resource_type", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_action", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_admin_user_id", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_id", table_name="admin_audit_logs")
    op.drop_table("admin_audit_logs")
