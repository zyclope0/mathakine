from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, JSON\
    , ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base



class LogicChallengeType(str, enum.Enum):
    """Types de défis logiques"""
    SEQUENCE = "sequence"          # Suites logiques (nombres, formes, etc.)
    PATTERN = "pattern"            # Reconnaissance de motifs
    PUZZLE = "puzzle"              # Énigmes et puzzles
    DEDUCTION = "deduction"        # Raisonnement déductif
    SPATIAL = "spatial"            # Raisonnement spatial
    PROBABILITY = "probability"    # Probabilités simples
    GRAPH = "graph"                # Problèmes de graphes
    CODING = "coding"              # Codage et décryptage
    CHESS = "chess"                # Problèmes d'échecs
    CUSTOM = "custom"              # Défis personnalisés



class AgeGroup(str, enum.Enum):
    """Groupes d'âge pour les défis logiques"""
    GROUP_10_12 = "10-12"  # Pour les 10-12 ans (niveau débutant)
    GROUP_13_15 = "13-15"  # Pour les 13-15 ans (niveau intermédiaire)
    ALL_AGES = "all"       # Tous âges (avec indices adaptables)



class LogicChallenge(Base):
    """Modèle pour les défis de logique mathématique (Épreuves du Conseil Jedi)"""
    __tablename__ = "logic_challenges"

    id = Column(Integer, primary_key=True, index=True)

    # Métadonnées
    title = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", back_populates="created_logic_challenges")
    challenge_type = Column(Enum(LogicChallengeType), nullable=False)
    age_group = Column(Enum(AgeGroup), nullable=False)

    # Contenu du défi
    description = Column(Text, nullable=False)  # Énoncé du problème
    visual_data = Column(JSON, nullable=True)   # Données pour visualisation (graphes, formes, etc.)
    correct_answer = Column(String, nullable=False)
    solution_explanation = Column(Text, nullable=False)  # Explication détaillée

    # Indices progressifs
    hint_level1 = Column(Text, nullable=True)  # Indice de base
    hint_level2 = Column(Text, nullable=True)  # Indice intermédiaire
    hint_level3 = Column(Text, nullable=True)  # Indice avancé

    # Métadonnées d'évaluation
    difficulty_rating = Column(Float, default=3.0)  # Échelle 1-5
    estimated_time_minutes = Column(Integer, default=15)  # Temps estimé en minutes
    success_rate = Column(Float, default=0.0)  # Pourcentage de réussite

    # Métadonnées du contenu
    image_url = Column(String, nullable=True)  # URL de l'image associée
    source_reference = Column(String, nullable=True)  # Source (concours, livre, etc.)
    tags = Column(String, nullable=True)  # Tags séparés par des virgules

    # Métadonnées pour la génération
    is_template = Column(Boolean, default=False)  # S'il s'agit d'un template pour génération
    generation_parameters = Column(JSON, nullable=True)  # Paramètres pour la génération

    # États
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)

    # Horodatage
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relations
    attempts = relationship("LogicChallengeAttempt", back_populates="challenge")



    def __repr__(self):
        return f"<LogicChallenge {self.id}: {self.title} (Age: {self.age_group}, Type: {self.challenge_type})>"



class LogicChallengeAttempt(Base):
    """Modèle pour les tentatives de résolution de défis logiques"""
    __tablename__ = "logic_challenge_attempts"

    id = Column(Integer, primary_key=True, index=True)

    # Relations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="logic_challenge_attempts")
    challenge_id = Column(Integer, ForeignKey("logic_challenges.id"), nullable=False)
    challenge = relationship("LogicChallenge", back_populates="attempts")

    # Données de tentative
    user_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Float, nullable=True)  # Temps passé en secondes

    # Indices utilisés
    hint_level1_used = Column(Boolean, default=False)
    hint_level2_used = Column(Boolean, default=False)
    hint_level3_used = Column(Boolean, default=False)

    # Métadonnées
    attempt_number = Column(Integer, default=1)  # Numéro de tentative pour ce défi et cet utilisateur
    notes = Column(Text, nullable=True)  # Notes de l'utilisateur

    # Horodatage
    created_at = Column(DateTime(timezone=True), default=func.now())



    def __repr__(self):
        status = "réussie" if self.is_correct else "échouée"
        return f"<Tentative Logique {self.id}: Utilisateur {self.user_id}, Défi {self.challenge_id}\
            , {status}>"
