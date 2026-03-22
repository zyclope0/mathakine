"""IA8 — persistance structurée des runs du harness d'évaluation génération IA.

Revision ID: 20260322_ai_eval_harness
Revises: 20260321_point_events
Create Date: 2026-03-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "20260322_ai_eval_harness"
down_revision: Union[str, None] = "20260321_point_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "ai_eval_harness_runs" not in tables:
        op.create_table(
            "ai_eval_harness_runs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("run_uuid", sa.String(length=36), nullable=False),
            sa.Column("mode", sa.String(length=16), nullable=False),
            sa.Column("target", sa.String(length=64), nullable=False),
            sa.Column("corpus_path", sa.Text(), nullable=False),
            sa.Column("corpus_version", sa.Integer(), nullable=False),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("cases_total", sa.Integer(), nullable=False),
            sa.Column("cases_run", sa.Integer(), nullable=False),
            sa.Column("cases_passed", sa.Integer(), nullable=False),
            sa.Column("cases_failed", sa.Integer(), nullable=False),
            sa.Column("cases_skipped", sa.Integer(), nullable=False),
            sa.Column("limitations_note", sa.Text(), nullable=False),
            sa.Column("json_artifact_path", sa.Text(), nullable=True),
            sa.Column("markdown_artifact_path", sa.Text(), nullable=True),
            sa.Column("token_tracker_snapshot", JSONB, nullable=True),
            sa.Column("report_snapshot_json", JSONB, nullable=True),
            sa.Column("git_revision", sa.String(length=64), nullable=True),
            sa.Column("app_version", sa.String(length=64), nullable=True),
            sa.Column(
                "live_opt_in",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
        op.create_index(
            "ix_ai_eval_harness_runs_run_uuid",
            "ai_eval_harness_runs",
            ["run_uuid"],
            unique=True,
        )
        op.create_index(
            "ix_ai_eval_harness_runs_completed_at",
            "ai_eval_harness_runs",
            ["completed_at"],
            unique=False,
        )

    if "ai_eval_harness_case_results" not in tables:
        op.create_table(
            "ai_eval_harness_case_results",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "run_id",
                sa.Integer(),
                sa.ForeignKey("ai_eval_harness_runs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("case_id", sa.String(length=256), nullable=False),
            sa.Column("pipeline", sa.String(length=128), nullable=False),
            sa.Column("success", sa.Boolean(), nullable=False),
            sa.Column(
                "expected_success",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
            sa.Column("failure_reason", sa.Text(), nullable=True),
            sa.Column("structural_ok", sa.Boolean(), nullable=True),
            sa.Column("business_ok", sa.Boolean(), nullable=True),
            sa.Column("latency_ms", sa.Float(), nullable=True),
            sa.Column(
                "live_skipped",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column("skip_reason", sa.Text(), nullable=True),
            sa.Column("tokens_prompt", sa.Integer(), nullable=True),
            sa.Column("tokens_completion", sa.Integer(), nullable=True),
            sa.Column("cost_usd_estimate", sa.Numeric(14, 8), nullable=True),
            sa.Column("structural_errors", JSONB, nullable=True),
            sa.Column("business_errors", JSONB, nullable=True),
            sa.Column("difficulty_flags", JSONB, nullable=True),
            sa.Column("choices_flags", JSONB, nullable=True),
            sa.Column("rationale", sa.Text(), nullable=True),
            sa.Column("pedagogical_note", sa.Text(), nullable=True),
        )
        op.create_index(
            "ix_ai_eval_harness_case_results_run_id",
            "ai_eval_harness_case_results",
            ["run_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "ai_eval_harness_case_results" in tables:
        op.drop_index(
            "ix_ai_eval_harness_case_results_run_id",
            table_name="ai_eval_harness_case_results",
        )
        op.drop_table("ai_eval_harness_case_results")

    if "ai_eval_harness_runs" in tables:
        op.drop_index(
            "ix_ai_eval_harness_runs_completed_at",
            table_name="ai_eval_harness_runs",
        )
        op.drop_index(
            "ix_ai_eval_harness_runs_run_uuid",
            table_name="ai_eval_harness_runs",
        )
        op.drop_table("ai_eval_harness_runs")
