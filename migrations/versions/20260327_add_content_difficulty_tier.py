"""F42 phase 2 — difficulty_tier sur exercises et logic_challenges

Revision ID: 20260327_content_difficulty_tier
Revises: 20260326_users_age_group
Create Date: 2026-03-27

Colonne nullable puis backfill Python (âge × difficulté → 1..12).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session, sessionmaker

revision: str = "20260327_content_difficulty_tier"
down_revision: Union[str, None] = "20260326_users_age_group"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    ex_cols = {c["name"] for c in insp.get_columns("exercises")}
    if "difficulty_tier" not in ex_cols:
        op.add_column(
            "exercises",
            sa.Column("difficulty_tier", sa.Integer(), nullable=True),
        )
    lc_cols = {c["name"] for c in insp.get_columns("logic_challenges")}
    if "difficulty_tier" not in lc_cols:
        op.add_column(
            "logic_challenges",
            sa.Column("difficulty_tier", sa.Integer(), nullable=True),
        )

    # Index (idempotent) — requis par le modèle ORM (index=True) et les requêtes reco
    existing_indexes_ex = {idx["name"] for idx in insp.get_indexes("exercises")}
    if "ix_exercises_difficulty_tier" not in existing_indexes_ex:
        op.create_index(
            "ix_exercises_difficulty_tier", "exercises", ["difficulty_tier"]
        )
    existing_indexes_lc = {idx["name"] for idx in insp.get_indexes("logic_challenges")}
    if "ix_logic_challenges_difficulty_tier" not in existing_indexes_lc:
        op.create_index(
            "ix_logic_challenges_difficulty_tier",
            "logic_challenges",
            ["difficulty_tier"],
        )

    SessionCls = sessionmaker(bind=conn, class_=Session, expire_on_commit=False)
    s = SessionCls()
    try:
        from app.core.difficulty_tier import (
            assign_exercise_difficulty_tier,
            assign_logic_challenge_difficulty_tier,
        )
        from app.models.exercise import Exercise
        from app.models.logic_challenge import LogicChallenge

        for ex in s.query(Exercise).yield_per(300):
            assign_exercise_difficulty_tier(ex)
        for ch in s.query(LogicChallenge).yield_per(300):
            assign_logic_challenge_difficulty_tier(ch)
        s.commit()
    finally:
        s.close()


def downgrade() -> None:
    op.drop_index("ix_logic_challenges_difficulty_tier", table_name="logic_challenges")
    op.drop_index("ix_exercises_difficulty_tier", table_name="exercises")
    op.drop_column("logic_challenges", "difficulty_tier")
    op.drop_column("exercises", "difficulty_tier")
