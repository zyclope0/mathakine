"""
Modèle SQLAlchemy pour les résultats du diagnostic initial (F03).

Un DiagnosticResult représente une session de diagnostic complétée par un
utilisateur. Les scores par type d'exercice sont stockés en JSONB pour rester
flexibles si de nouveaux types sont ajoutés sans migration.

Structure de `scores` :
{
  "addition":       {"level": 2, "correct": 4, "total": 5},
  "soustraction":   {"level": 1, "correct": 2, "total": 4},
  "multiplication": {"level": 3, "correct": 5, "total": 5},
  "division":       {"level": 2, "correct": 3, "total": 5}
}

`level` correspond aux niveaux de difficulté ordinaux :
  0 = INITIE, 1 = PADAWAN, 2 = CHEVALIER, 3 = MAITRE, 4 = GRAND_MAITRE
"""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class DiagnosticResult(Base):
    """Résultat d'une session de diagnostic adaptatif pour un utilisateur."""

    __tablename__ = "diagnostic_results"

    __table_args__ = (
        Index("ix_diagnostic_results_user_id", "user_id"),
        Index("ix_diagnostic_results_completed_at", "completed_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user = relationship("User", back_populates="diagnostic_results")

    # Source du déclenchement : "onboarding" | "settings"
    triggered_from = Column(String(20), nullable=False, default="onboarding")

    # Scores par type d'exercice (JSONB pour extensibilité future)
    scores = Column(JSONB, nullable=False, default=dict)

    # Nombre total de questions posées lors de cette session
    questions_asked = Column(Integer, nullable=False, default=0)

    # Durée de la session en secondes (nullable si non mesuré)
    duration_seconds = Column(Integer, nullable=True)

    completed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<DiagnosticResult id={self.id} user={self.user_id} "
            f"from={self.triggered_from} scores={self.scores}>"
        )
