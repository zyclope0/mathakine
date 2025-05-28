"""
Service de gestion des badges et achievements pour Mathakine
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timezone, timedelta
import logging

from app.models.user import User
from app.models.achievement import Achievement, UserAchievement
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class BadgeService:
    """Service pour la gestion des badges et achievements"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_and_award_badges(self, user_id: int, attempt_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Vérifier et attribuer les badges mérités par un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            attempt_data: Données de la dernière tentative (optionnel)
            
        Returns:
            Liste des nouveaux badges obtenus
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"Utilisateur {user_id} non trouvé")
                return []
            
            # Récupérer tous les badges disponibles
            available_badges = self.db.query(Achievement).filter(
                Achievement.is_active == True
            ).all()
            
            # Récupérer les badges déjà obtenus - CORRECTION
            earned_badge_ids = set(
                badge_id[0] for badge_id in self.db.query(UserAchievement.achievement_id)
                .filter(UserAchievement.user_id == user_id)
                .all()
            )
            
            new_badges = []
            
            for badge in available_badges:
                if badge.id not in earned_badge_ids:
                    if self._check_badge_requirements(user_id, badge, attempt_data):
                        new_badge = self._award_badge(user_id, badge)
                        if new_badge:
                            new_badges.append(new_badge)
                            logger.info(f"🎖️ Badge '{badge.name}' attribué à l'utilisateur {user_id}")
            
            # Mettre à jour les points et le niveau
            if new_badges:
                self._update_user_gamification(user_id, new_badges)
            
            return new_badges
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des badges pour l'utilisateur {user_id}: {e}")
            return []
    
    def _check_badge_requirements(self, user_id: int, badge: Achievement, attempt_data: Dict[str, Any] = None) -> bool:
        """Vérifier si un utilisateur remplit les conditions pour un badge"""
        
        if not badge.requirements:
            return False
        
        try:
            requirements = json.loads(badge.requirements) if isinstance(badge.requirements, str) else badge.requirements
        except (json.JSONDecodeError, TypeError):
            logger.error(f"Requirements invalides pour le badge {badge.code}")
            return False
        
        # BADGE: Premiers Pas (1 tentative)
        if badge.code == 'first_steps':
            attempts_count = self.db.query(func.count(Attempt.id)).filter(
                Attempt.user_id == user_id
            ).scalar()
            return attempts_count >= requirements.get('attempts_count', 1)
        
        # BADGE: Voie du Padawan (10 tentatives)
        elif badge.code == 'padawan_path':
            attempts_count = self.db.query(func.count(Attempt.id)).filter(
                Attempt.user_id == user_id
            ).scalar()
            return attempts_count >= requirements.get('attempts_count', 10)
        
        # BADGE: Épreuve du Chevalier (50 tentatives)
        elif badge.code == 'knight_trial':
            attempts_count = self.db.query(func.count(Attempt.id)).filter(
                Attempt.user_id == user_id
            ).scalar()
            return attempts_count >= requirements.get('attempts_count', 50)
        
        # BADGE: Maître des Additions (20 additions consécutives)
        elif badge.code == 'addition_master':
            return self._check_consecutive_success(
                user_id, 
                requirements.get('exercise_type', 'addition'),
                requirements.get('streak', 20)
            )
        
        # BADGE: Éclair de Vitesse (exercice en moins de 5 secondes)
        elif badge.code == 'speed_demon':
            max_time = requirements.get('max_time', 5)
            if attempt_data and attempt_data.get('time_spent', float('inf')) <= max_time:
                return True
            
            # Vérifier dans l'historique
            fast_attempt = self.db.query(Attempt).filter(
                Attempt.user_id == user_id,
                Attempt.is_correct == True,
                Attempt.time_spent <= max_time
            ).first()
            return fast_attempt is not None
        
        # BADGE: Journée Parfaite (tous les exercices d'une journée réussis)
        elif badge.code == 'perfect_day':
            return self._check_perfect_day(user_id)
        
        return False
    
    def _check_consecutive_success(self, user_id: int, exercise_type: str, required_streak: int) -> bool:
        """Vérifier une série consécutive de succès pour un type d'exercice"""
        
        # Récupérer les dernières tentatives pour ce type d'exercice
        attempts = self.db.execute(text("""
            SELECT a.is_correct
            FROM attempts a
            JOIN exercises e ON a.exercise_id = e.id
            WHERE a.user_id = :user_id 
            AND e.exercise_type = :exercise_type
            ORDER BY a.created_at DESC
            LIMIT :limit
        """), {
            "user_id": user_id,
            "exercise_type": exercise_type,
            "limit": required_streak * 2  # Prendre plus pour être sûr
        }).fetchall()
        
        if len(attempts) < required_streak:
            return False
        
        # Compter la série actuelle de succès
        current_streak = 0
        for attempt in attempts:
            if attempt.is_correct:  # Accès direct à l'attribut au lieu de [0]
                current_streak += 1
                if current_streak >= required_streak:
                    return True
            else:
                break  # Série interrompue
        
        return False
    
    def _check_perfect_day(self, user_id: int) -> bool:
        """Vérifier si l'utilisateur a eu une journée parfaite"""
        
        today = datetime.now(timezone.utc).date()
        
        # Récupérer toutes les tentatives d'aujourd'hui
        today_attempts = self.db.execute(text("""
            SELECT COUNT(*) as total, 
                   COUNT(CASE WHEN is_correct THEN 1 END) as correct
            FROM attempts
            WHERE user_id = :user_id 
            AND DATE(created_at) = :today
        """), {
            "user_id": user_id,
            "today": today
        }).fetchone()
        
        if not today_attempts or today_attempts.total == 0:
            return False
        
        # Tous les exercices doivent être réussis ET au moins 3 exercices
        return today_attempts.correct == today_attempts.total and today_attempts.total >= 3
    
    def _award_badge(self, user_id: int, badge: Achievement) -> Optional[Dict[str, Any]]:
        """Attribuer un badge à un utilisateur"""
        
        try:
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=badge.id,
                earned_at=datetime.now(timezone.utc),
                is_displayed=True
            )
            
            self.db.add(user_achievement)
            self.db.commit()
            
            return {
                'id': badge.id,
                'code': badge.code,
                'name': badge.name,
                'description': badge.description,
                'star_wars_title': badge.star_wars_title,
                'difficulty': badge.difficulty,
                'points_reward': badge.points_reward,
                'earned_at': user_achievement.earned_at.isoformat()
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur lors de l'attribution du badge {badge.code}: {e}")
            return None
    
    def _update_user_gamification(self, user_id: int, new_badges: List[Dict[str, Any]]):
        """Mettre à jour les points et le niveau de l'utilisateur"""
        
        try:
            # Calculer les points gagnés
            total_points_gained = sum(badge['points_reward'] for badge in new_badges)
            
            # Mettre à jour l'utilisateur
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                # Ajouter les points
                current_points = getattr(user, 'total_points', 0) or 0
                new_total_points = current_points + total_points_gained
                
                # Calculer le nouveau niveau (100 points par niveau)
                new_level = max(1, new_total_points // 100 + 1)
                
                # Calculer le rang Jedi basé sur le niveau
                jedi_rank = self._calculate_jedi_rank(new_level)
                
                # Mettre à jour via SQL brut pour éviter les problèmes de modèle
                self.db.execute(text("""
                    UPDATE users 
                    SET total_points = :total_points,
                        current_level = :current_level,
                        experience_points = :experience_points,
                        jedi_rank = :jedi_rank
                    WHERE id = :user_id
                """), {
                    "total_points": new_total_points,
                    "current_level": new_level,
                    "experience_points": new_total_points % 100,
                    "jedi_rank": jedi_rank,
                    "user_id": user_id
                })
                
                self.db.commit()
                logger.info(f"Gamification mise à jour pour l'utilisateur {user_id}: {total_points_gained} points, niveau {new_level}, rang {jedi_rank}")
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur mise à jour gamification pour l'utilisateur {user_id}: {e}")
    
    def _calculate_jedi_rank(self, level: int) -> str:
        """Calculer le rang Jedi basé sur le niveau"""
        
        if level < 5:
            return 'youngling'
        elif level < 15:
            return 'padawan'
        elif level < 30:
            return 'knight'
        elif level < 50:
            return 'master'
        else:
            return 'grand_master'
    
    def get_user_badges(self, user_id: int) -> Dict[str, Any]:
        """Récupérer tous les badges d'un utilisateur"""
        
        try:
            # Badges obtenus
            earned_badges = self.db.execute(text("""
                SELECT a.id, a.code, a.name, a.description, a.star_wars_title,
                       a.difficulty, a.points_reward, a.category,
                       ua.earned_at, ua.is_displayed
                FROM achievements a
                JOIN user_achievements ua ON a.id = ua.achievement_id
                WHERE ua.user_id = :user_id
                ORDER BY ua.earned_at DESC
            """), {"user_id": user_id}).fetchall()
            
            # Statistiques utilisateur
            user_stats = self.db.execute(text("""
                SELECT total_points, current_level, experience_points, jedi_rank
                FROM users
                WHERE id = :user_id
            """), {"user_id": user_id}).fetchone()
            
            return {
                'earned_badges': [
                    {
                        'id': badge[0],
                        'code': badge[1],
                        'name': badge[2],
                        'description': badge[3],
                        'star_wars_title': badge[4],
                        'difficulty': badge[5],
                        'points_reward': badge[6],
                        'category': badge[7],
                        'earned_at': badge[8].isoformat() if badge[8] else None,
                        'is_displayed': badge[9]
                    }
                    for badge in earned_badges
                ],
                'user_stats': {
                    'total_points': user_stats[0] if user_stats else 0,
                    'current_level': user_stats[1] if user_stats else 1,
                    'experience_points': user_stats[2] if user_stats else 0,
                    'jedi_rank': user_stats[3] if user_stats else 'youngling'
                } if user_stats else {
                    'total_points': 0,
                    'current_level': 1,
                    'experience_points': 0,
                    'jedi_rank': 'youngling'
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération badges utilisateur {user_id}: {e}")
            return {'earned_badges': [], 'user_stats': {}}
    
    def get_available_badges(self) -> List[Dict[str, Any]]:
        """Récupérer tous les badges disponibles"""
        
        try:
            badges = self.db.query(Achievement).filter(
                Achievement.is_active == True
            ).order_by(Achievement.category, Achievement.difficulty).all()
            
            return [
                {
                    'id': badge.id,
                    'code': badge.code,
                    'name': badge.name,
                    'description': badge.description,
                    'star_wars_title': badge.star_wars_title,
                    'difficulty': badge.difficulty,
                    'points_reward': badge.points_reward,
                    'category': badge.category,
                    'is_secret': badge.is_secret
                }
                for badge in badges
            ]
            
        except Exception as e:
            logger.error(f"Erreur récupération badges disponibles: {e}")
            return [] 