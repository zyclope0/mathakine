"""
Modèle SQLAlchemy pour les utilisateurs - Version étendue pour futures fonctionnalités
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator
import json
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.db.base import Base


class UserRole(PyEnum):
    """Énumération des rôles d'utilisateur"""
    PADAWAN = "padawan"     # Apprenti, niveau standard
    MAITRE = "maitre"       # Enseignant, créateur d'exercices
    GARDIEN = "gardien"     # Modérateur, gestion des utilisateurs
    ARCHIVISTE = "archiviste"  # Administrateur, accès complet


class LearningStyle(PyEnum):
    """Styles d'apprentissage"""
    VISUAL = "visual"       # Apprenant visuel
    AUDITORY = "auditory"   # Apprenant auditif
    KINESTHETIC = "kinesthetic"  # Apprenant kinesthésique
    MIXED = "mixed"         # Apprentissage mixte


class JediRank(PyEnum):
    """Rangs Jedi pour la gamification"""
    YOUNGLING = "youngling"     # Débutant
    INITIATE = "initiate"       # Initié
    PADAWAN = "padawan"         # Padawan
    KNIGHT = "knight"           # Chevalier
    MASTER = "master"           # Maître
    GRAND_MASTER = "grand_master"  # Grand Maître


class JSONEncodedDict(TypeDecorator):
    """Représente un dictionnaire mappé vers une colonne TEXT"""
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class User(Base):
    """Modèle de données pour les utilisateurs de Mathakine - Version étendue"""
    __tablename__ = "users"

    # Champs de base existants
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole, name="userrole", create_type=False), default=UserRole.PADAWAN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Informations pédagogiques existantes
    grade_level = Column(Integer)
    learning_style = Column(Enum(LearningStyle, name="learningstyle", create_type=False))
    preferred_difficulty = Column(String(50))

    # Préférences d'interface existantes
    preferred_theme = Column(String(50))
    accessibility_settings = Column(JSONEncodedDict)

    # === NOUVELLES EXTENSIONS ===
    
    # Profil enrichi
    avatar_url = Column(String(255), nullable=True, index=True)
    bio = Column(Text, nullable=True)
    birth_date = Column(Date, nullable=True)
    timezone = Column(String(50), default='UTC')
    language_preference = Column(String(10), default='fr')

    # Sécurité et sessions
    last_password_change = Column(DateTime(timezone=True), nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Préférences d'apprentissage étendues
    cognitive_profile = Column(JSON, nullable=True)  # Profil cognitif détaillé
    special_needs = Column(JSON, nullable=True)      # Besoins spéciaux (autisme, dyslexie, etc.)

    # Gamification
    total_points = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    experience_points = Column(Integer, default=0)
    jedi_rank = Column(Enum(JediRank, name="jedirank", create_type=False), default=JediRank.YOUNGLING, index=True)

    # Métadonnées sociales
    is_public_profile = Column(Boolean, default=False, index=True)
    allow_friend_requests = Column(Boolean, default=True)
    show_in_leaderboards = Column(Boolean, default=True)

    # Conformité et données
    data_retention_consent = Column(Boolean, default=True)
    marketing_consent = Column(Boolean, default=False)
    deletion_requested_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)

    # Relations existantes
    created_exercises = relationship("Exercise", back_populates="creator", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")

    # Relations avec les défis logiques
    created_logic_challenges = relationship("LogicChallenge", back_populates="creator", cascade="all, delete-orphan")
    logic_challenge_attempts = relationship("LogicChallengeAttempt", back_populates="user", cascade="all, delete-orphan")

    # Nouvelles relations
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    user_achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}, Role: {self.role}, Rank: {self.jedi_rank}>"

    # Méthodes utilitaires pour la gamification
    def add_experience(self, points: int):
        """Ajouter des points d'expérience et gérer la montée de niveau"""
        self.experience_points += points
        self.total_points += points
        
        # Logique de montée de niveau (exemple)
        level_thresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500, 5500]
        new_level = 1
        for i, threshold in enumerate(level_thresholds):
            if self.experience_points >= threshold:
                new_level = i + 1
        
        if new_level > self.current_level:
            self.current_level = new_level
            self.update_jedi_rank()

    def update_jedi_rank(self):
        """Mettre à jour le rang Jedi selon le niveau"""
        if self.current_level >= 10:
            self.jedi_rank = JediRank.GRAND_MASTER
        elif self.current_level >= 8:
            self.jedi_rank = JediRank.MASTER
        elif self.current_level >= 6:
            self.jedi_rank = JediRank.KNIGHT
        elif self.current_level >= 3:
            self.jedi_rank = JediRank.PADAWAN
        elif self.current_level >= 2:
            self.jedi_rank = JediRank.INITIATE
        else:
            self.jedi_rank = JediRank.YOUNGLING

    def is_account_locked(self) -> bool:
        """Vérifier si le compte est verrouillé"""
        if self.locked_until is None:
            return False
        return datetime.now(timezone.utc) < self.locked_until

    def can_attempt_login(self) -> bool:
        """Vérifier si l'utilisateur peut tenter de se connecter"""
        return not self.is_account_locked() and self.failed_login_attempts < 5

    def reset_failed_attempts(self):
        """Réinitialiser les tentatives de connexion échouées"""
        self.failed_login_attempts = 0
        self.locked_until = None

    def increment_failed_attempts(self):
        """Incrémenter les tentatives échouées et verrouiller si nécessaire"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Verrouiller pour 30 minutes
            self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)

    def get_accessibility_preference(self, key: str, default=None):
        """Récupérer une préférence d'accessibilité"""
        if not self.accessibility_settings:
            return default
        return self.accessibility_settings.get(key, default)

    def set_accessibility_preference(self, key: str, value):
        """Définir une préférence d'accessibilité"""
        if not self.accessibility_settings:
            self.accessibility_settings = {}
        self.accessibility_settings[key] = value

    def get_cognitive_profile_trait(self, trait: str, default=None):
        """Récupérer un trait du profil cognitif"""
        if not self.cognitive_profile:
            return default
        return self.cognitive_profile.get(trait, default)

    def has_special_need(self, need: str) -> bool:
        """Vérifier si l'utilisateur a un besoin spécial"""
        if not self.special_needs:
            return False
        return need in self.special_needs.get('conditions', [])
