"""
Modèles SQLAlchemy — persistance des exécutions du harness d'évaluation IA (IA8).

Un run agrège les métadonnées d'une exécution (corpus, mode, compteurs, chemins
d'artefacts) et des lignes de résultat par cas pour l'historique / comparaisons
sans reparser les fichiers Markdown.
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class AiEvalHarnessRun(Base):
    """Une exécution complète du harness (offline ou live)."""

    __tablename__ = "ai_eval_harness_runs"

    __table_args__ = (
        Index("ix_ai_eval_harness_runs_run_uuid", "run_uuid", unique=True),
        Index("ix_ai_eval_harness_runs_completed_at", "completed_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_uuid = Column(String(36), nullable=False, unique=True)

    mode = Column(String(16), nullable=False)
    target = Column(String(64), nullable=False)
    corpus_path = Column(Text, nullable=False)
    corpus_version = Column(Integer, nullable=False)

    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False)

    cases_total = Column(Integer, nullable=False)
    cases_run = Column(Integer, nullable=False)
    cases_passed = Column(Integer, nullable=False)
    cases_failed = Column(Integer, nullable=False)
    cases_skipped = Column(Integer, nullable=False)

    limitations_note = Column(Text, nullable=False, default="")

    json_artifact_path = Column(Text, nullable=True)
    markdown_artifact_path = Column(Text, nullable=True)

    token_tracker_snapshot = Column(JSONB, nullable=True)
    report_snapshot_json = Column(JSONB, nullable=True)

    git_revision = Column(String(64), nullable=True)
    app_version = Column(String(64), nullable=True)
    live_opt_in = Column(Boolean, nullable=False, default=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    case_results = relationship(
        "AiEvalHarnessCaseResult",
        back_populates="run",
        cascade="all, delete-orphan",
    )


class AiEvalHarnessCaseResult(Base):
    """Résultat structuré d'un cas du corpus pour un run donné."""

    __tablename__ = "ai_eval_harness_case_results"

    __table_args__ = (Index("ix_ai_eval_harness_case_results_run_id", "run_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(
        Integer,
        ForeignKey("ai_eval_harness_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    run = relationship("AiEvalHarnessRun", back_populates="case_results")

    case_id = Column(String(256), nullable=False)
    pipeline = Column(String(128), nullable=False)

    success = Column(Boolean, nullable=False)
    expected_success = Column(Boolean, nullable=False, default=True)
    failure_reason = Column(Text, nullable=True)

    structural_ok = Column(Boolean, nullable=True)
    business_ok = Column(Boolean, nullable=True)

    latency_ms = Column(Float, nullable=True)

    live_skipped = Column(Boolean, nullable=False, server_default="false")
    skip_reason = Column(Text, nullable=True)

    tokens_prompt = Column(Integer, nullable=True)
    tokens_completion = Column(Integer, nullable=True)
    cost_usd_estimate = Column(Numeric(14, 8), nullable=True)

    structural_errors = Column(JSONB, nullable=True)
    business_errors = Column(JSONB, nullable=True)
    difficulty_flags = Column(JSONB, nullable=True)
    choices_flags = Column(JSONB, nullable=True)

    rationale = Column(Text, nullable=True)
    pedagogical_note = Column(Text, nullable=True)
