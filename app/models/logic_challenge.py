from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, JSON\
    , ForeignKey, Float, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from typing import List, Optional, Dict, Any
from app.db.base import Base



class LogicChallengeType(str, PyEnum):
    """Types de défis logiques"""
    SEQUENCE = "sequence"          # Suites logiques (nombres, formes, etc.)
    PATTERN = "pattern"            # Reconnaissance de motifs
    VISUAL = "visual"              # Défis visuels et spatiaux  
    PUZZLE = "puzzle"              # Énigmes et puzzles
    RIDDLE = "riddle"              # Énigmes et puzzles
    DEDUCTION = "deduction"        # Raisonnement déductif
    SPATIAL = "spatial"            # Raisonnement spatial
    PROBABILITY = "probability"    # Probabilités simples
    GRAPH = "graph"                # Problèmes de graphes
    CODING = "coding"              # Codage et décryptage
    CHESS = "chess"                # Problèmes d'échecs
    CUSTOM = "custom"              # Défis personnalisés



class AgeGroup(str, PyEnum):
    """Groupes d'âge pour les défis logiques"""
    ENFANT = "enfant"
    ADOLESCENT = "adolescent"
    ADULTE = "adulte"
    AGE_9_12 = "9-12"      # Pour les 9-12 ans (niveau débutant)
    AGE_12_13 = "12-13"    # Pour les 12-13 ans (niveau intermédiaire)
    AGE_13_PLUS = "13+"    # Pour les 13 ans et plus (niveau avancé)
    GROUP_10_12 = "10-12"  # Pour les 10-12 ans (niveau débutant, alias)
    GROUP_13_15 = "13-15"  # Pour les 13-15 ans (niveau intermédiaire, alias)
    ALL_AGES = "all"       # Tous âges (avec indices adaptables)



class LogicChallenge(Base):
    """Modèle pour les défis logiques"""
    __tablename__ = "logic_challenges"

    id = Column(Integer, primary_key=True, index=True)

    # Métadonnées
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    challenge_type = Column(Enum(LogicChallengeType, name="logicchallengetype", create_type=False), nullable=False, index=True)
    age_group = Column(Enum(AgeGroup, name="agegroup", create_type=False), nullable=False, index=True)
    difficulty = Column(String(50), nullable=True, index=True)  # Optionnel pour compatibilité
    
    # Contenu du défi
    content = Column(Text, nullable=True)  # Contenu formaté du défi
    question = Column(Text, nullable=True)  # Question spécifique (pour compatibilité)
    solution = Column(Text, nullable=True)  # Solution technique
    correct_answer = Column(String(255), nullable=True)  # Réponse courte (pour compatibilité)
    choices = Column(JSON, nullable=True)  # Choix possibles (pour les QCM)
    solution_explanation = Column(Text, nullable=True)  # Explication détaillée (alias pour solution)
    visual_data = Column(JSON, nullable=True)  # Données pour visualisation (graphes, formes, etc.)
    
    hints = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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
    is_archived = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)

    # Relations
    attempts = relationship("LogicChallengeAttempt", back_populates="challenge", cascade="all, delete-orphan")
    creator = relationship("User", back_populates="created_logic_challenges")

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire avec conversion des énumérations."""
        from app.utils.db_helpers import get_python_enum_value
        from datetime import datetime, timezone
        
        # Créer le dictionnaire de base
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
        # Convertir les énumérations PostgreSQL vers les valeurs Python
        if result.get('challenge_type'):
            result['challenge_type'] = get_python_enum_value(LogicChallengeType, result['challenge_type'])
        
        if result.get('age_group'):
            result['age_group'] = get_python_enum_value(AgeGroup, result['age_group'])
        
        # Gérer le champ hints (conversion JSON si nécessaire)
        if result.get('hints'):
            if isinstance(result['hints'], str):
                # Si c'est une chaîne, essayer de la parser en JSON
                try:
                    import json
                    result['hints'] = json.loads(result['hints'])
                except (json.JSONDecodeError, TypeError):
                    # Si ça échoue, transformer en liste simple
                    result['hints'] = [result['hints']]
            elif not isinstance(result['hints'], list):
                result['hints'] = []
        else:
            result['hints'] = []
        
        # Gérer les dates (s'assurer qu'elles existent comme objets datetime)
        now = datetime.now(timezone.utc)
        if not result.get('created_at'):
            result['created_at'] = now
        if not result.get('updated_at'):
            result['updated_at'] = now
            
        return result

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
    user_solution = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Float, nullable=True)  # Temps passé en secondes

    # Indices utilisés
    hints_used = Column(Integer, default=0)

    # Métadonnées
    attempt_number = Column(Integer, default=1)  # Numéro de tentative pour ce défi et cet utilisateur
    notes = Column(Text, nullable=True)  # Notes de l'utilisateur

    # Horodatage
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        status = "réussie" if self.is_correct else "échouée"
        return f"<Tentative Logique {self.id}: Utilisateur {self.user_id}, Défi {self.challenge_id}\
            , {status}>"
