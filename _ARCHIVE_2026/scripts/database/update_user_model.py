#!/usr/bin/env python3
"""
Script pour mettre à jour le modèle User avec les extensions futures.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def update_user_model():
    """Mettre à jour le modèle User avec les nouvelles extensions"""
    
    updated_model = '''"""
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
    ADMIN = "admin"


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
'''

    # Écrire le modèle mis à jour
    user_model_file = project_root / "app" / "models" / "user_extended.py"
    
    with open(user_model_file, 'w', encoding='utf-8') as f:
        f.write(updated_model)
    
    print(f"✅ Modèle User étendu créé : {user_model_file}")
    print("📝 Ce fichier contient le modèle User avec toutes les extensions futures")
    print("   Vous pouvez l'utiliser pour remplacer le modèle actuel après migration")

def create_new_models():
    """Créer les nouveaux modèles pour les tables futures"""
    
    # Modèle UserSession
    user_session_model = '''"""
Modèle SQLAlchemy pour les sessions utilisateur
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INET
from app.db.base import Base


class UserSession(Base):
    """Modèle pour les sessions utilisateur"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    device_info = Column(JSON, nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    location_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    last_activity = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Relations
    user = relationship("User", back_populates="user_sessions")

    def __repr__(self):
        return f"<UserSession {self.id}: User {self.user_id}, Active: {self.is_active}>"

    def is_expired(self) -> bool:
        """Vérifier si la session a expiré"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at

    def extend_session(self, hours: int = 24):
        """Prolonger la session"""
        from datetime import datetime, timezone, timedelta
        self.expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)
        self.last_activity = datetime.now(timezone.utc)
'''

    # Modèle Achievement
    achievement_model = '''"""
Modèles SQLAlchemy pour le système de badges
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Achievement(Base):
    """Modèle pour les badges/achievements"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True, index=True)
    difficulty = Column(String(50), nullable=True)  # bronze, silver, gold, legendary
    points_reward = Column(Integer, default=0)
    is_secret = Column(Boolean, default=False)
    requirements = Column(JSON, nullable=True)
    star_wars_title = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relations
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Achievement {self.code}: {self.name} ({self.difficulty})>"


class UserAchievement(Base):
    """Modèle pour les badges obtenus par les utilisateurs"""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    earned_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    progress_data = Column(JSON, nullable=True)
    is_displayed = Column(Boolean, default=True)

    # Relations
    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    def __repr__(self):
        return f"<UserAchievement: User {self.user_id}, Achievement {self.achievement_id}>"
'''

    # Modèle Notification
    notification_model = '''"""
Modèle SQLAlchemy pour les notifications
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Notification(Base):
    """Modèle pour les notifications utilisateur"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)
    action_url = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    is_email_sent = Column(Boolean, default=False)
    priority = Column(Integer, default=5)  # 1-10
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)

    # Relations
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.id}: {self.type} for User {self.user_id}>"

    def mark_as_read(self):
        """Marquer la notification comme lue"""
        self.is_read = True

    def is_expired(self) -> bool:
        """Vérifier si la notification a expiré"""
        if self.expires_at is None:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
'''

    # Créer les fichiers
    models_dir = project_root / "app" / "models"
    
    files_to_create = [
        ("user_session.py", user_session_model),
        ("achievement.py", achievement_model),
        ("notification.py", notification_model)
    ]
    
    for filename, content in files_to_create:
        file_path = models_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Modèle créé : {file_path}")

def main():
    """Créer tous les modèles étendus"""
    print("🚀 Création des modèles étendus pour Mathakine...")
    print()
    
    try:
        update_user_model()
        print()
        create_new_models()
        print()
        
        print("🎉 Tous les modèles étendus ont été créés !")
        print()
        print("📋 Prochaines étapes :")
        print("   1. Vérifier les modèles créés")
        print("   2. Exécuter les migrations Alembic")
        print("   3. Mettre à jour les imports dans __init__.py")
        print("   4. Adapter les services pour utiliser les nouveaux champs")
        print("   5. Créer les schémas Pydantic correspondants")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des modèles : {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 