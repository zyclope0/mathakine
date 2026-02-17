"""
Service de gestion des badges et achievements pour Mathakine
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.achievement import Achievement, UserAchievement
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.user import User

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
            
        except Exception as badge_check_error:
            logger.error(f"Erreur lors de la vérification des badges pour l'utilisateur {user_id}: {badge_check_error}")
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
                requirements.get('consecutive_correct', 20)
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
        
        # BADGE: Maître Jedi (100 tentatives)
        elif badge.code == 'jedi_master':
            attempts_count = self.db.query(func.count(Attempt.id)).filter(
                Attempt.user_id == user_id
            ).scalar()
            return attempts_count >= requirements.get('attempts_count', 100)
        
        # BADGE: Grand Maître (200 tentatives)
        elif badge.code == 'grand_master':
            attempts_count = self.db.query(func.count(Attempt.id)).filter(
                Attempt.user_id == user_id
            ).scalar()
            return attempts_count >= requirements.get('attempts_count', 200)
        
        # BADGE: Maître des Soustractions (15 soustractions consécutives)
        elif badge.code == 'subtraction_master':
            return self._check_consecutive_success(
                user_id,
                requirements.get('exercise_type', 'soustraction'),
                requirements.get('consecutive_correct', 15)
            )
        
        # BADGE: Maître des Multiplications (15 multiplications consécutives)
        elif badge.code == 'multiplication_master':
            return self._check_consecutive_success(
                user_id,
                requirements.get('exercise_type', 'multiplication'),
                requirements.get('consecutive_correct', 15)
            )
        
        # BADGE: Maître des Divisions (15 divisions consécutives)
        elif badge.code == 'division_master':
            return self._check_consecutive_success(
                user_id,
                requirements.get('exercise_type', 'division'),
                requirements.get('consecutive_correct', 15)
            )
        
        # BADGE: Expert (taux de réussite ≥ 80% sur 50 tentatives)
        elif badge.code == 'expert':
            return self._check_success_rate(
                user_id,
                requirements.get('success_rate', 80),
                requirements.get('min_attempts', 50)
            )
        
        # BADGE: Perfectionniste (taux de réussite ≥ 95% sur 30 tentatives)
        elif badge.code == 'perfectionist':
            return self._check_success_rate(
                user_id,
                requirements.get('success_rate', 95),
                requirements.get('min_attempts', 30)
            )
        
        # BADGE: Semaine Parfaite (7 jours consécutifs)
        elif badge.code == 'perfect_week':
            return self._check_consecutive_days(
                user_id,
                requirements.get('consecutive_days', 7)
            )
        
        # BADGE: Mois Parfait (30 jours consécutifs)
        elif badge.code == 'perfect_month':
            return self._check_consecutive_days(
                user_id,
                requirements.get('consecutive_days', 30)
            )
        
        # BADGE: Explorateur (essayer tous les types d'exercices)
        elif badge.code == 'explorer':
            return self._check_all_exercise_types(user_id)
        
        # BADGE: Polyvalent (réussir au moins 5 exercices de chaque type)
        elif badge.code == 'versatile':
            return self._check_min_per_type(
                user_id,
                requirements.get('min_per_type', 5)
            )
        
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
    
    def _check_success_rate(self, user_id: int, min_success_rate: float, min_attempts: int) -> bool:
        """Vérifier si l'utilisateur atteint un taux de réussite minimum sur un nombre minimum de tentatives"""
        
        stats = self.db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN is_correct THEN 1 END) as correct
            FROM attempts
            WHERE user_id = :user_id
        """), {
            "user_id": user_id
        }).fetchone()
        
        if not stats or stats.total < min_attempts:
            return False
        
        success_rate = (stats.correct / stats.total) * 100
        return success_rate >= min_success_rate
    
    def _check_consecutive_days(self, user_id: int, required_days: int) -> bool:
        """Vérifier si l'utilisateur a fait des exercices pendant X jours consécutifs"""
        
        # Récupérer les jours uniques avec des tentatives, triés par date décroissante
        days = self.db.execute(text("""
            SELECT DISTINCT DATE(created_at) as day
            FROM attempts
            WHERE user_id = :user_id
            ORDER BY day DESC
            LIMIT :limit
        """), {
            "user_id": user_id,
            "limit": required_days + 1  # Prendre un jour de plus pour vérifier la continuité
        }).fetchall()
        
        if len(days) < required_days:
            return False
        
        # Vérifier que les jours sont consécutifs
        today = datetime.now(timezone.utc).date()
        consecutive_count = 0
        
        for i, day_row in enumerate(days):
            day = day_row.day if hasattr(day_row, 'day') else day_row[0]
            expected_date = today - timedelta(days=i)
            
            if day == expected_date:
                consecutive_count += 1
            else:
                break
        
        return consecutive_count >= required_days
    
    def _check_all_exercise_types(self, user_id: int) -> bool:
        """Vérifier si l'utilisateur a essayé tous les types d'exercices disponibles"""
        
        # Récupérer tous les types d'exercices disponibles
        all_types = self.db.execute(text("""
            SELECT DISTINCT exercise_type
            FROM exercises
            WHERE is_active = true AND is_archived = false
        """)).fetchall()
        
        if not all_types:
            return False
        
        all_types_set = {row.exercise_type if hasattr(row, 'exercise_type') else row[0] for row in all_types}
        
        # Récupérer les types d'exercices que l'utilisateur a essayés
        user_types = self.db.execute(text("""
            SELECT DISTINCT e.exercise_type
            FROM attempts a
            JOIN exercises e ON a.exercise_id = e.id
            WHERE a.user_id = :user_id
        """), {
            "user_id": user_id
        }).fetchall()
        
        user_types_set = {row.exercise_type if hasattr(row, 'exercise_type') else row[0] for row in user_types}
        
        # Normaliser les types (lowercase pour comparaison)
        all_types_normalized = {str(t).lower() for t in all_types_set}
        user_types_normalized = {str(t).lower() for t in user_types_set}
        
        return all_types_normalized.issubset(user_types_normalized)
    
    def _check_min_per_type(self, user_id: int, min_count: int) -> bool:
        """Vérifier si l'utilisateur a réussi au moins X exercices de chaque type"""
        
        # Récupérer tous les types d'exercices disponibles
        all_types = self.db.execute(text("""
            SELECT DISTINCT exercise_type
            FROM exercises
            WHERE is_active = true AND is_archived = false
        """)).fetchall()
        
        if not all_types:
            return False
        
        all_types_set = {row.exercise_type if hasattr(row, 'exercise_type') else row[0] for row in all_types}
        
        # Pour chaque type, vérifier si l'utilisateur a réussi au moins min_count exercices
        for ex_type in all_types_set:
            success_count = self.db.execute(text("""
                SELECT COUNT(*) as count
                FROM attempts a
                JOIN exercises e ON a.exercise_id = e.id
                WHERE a.user_id = :user_id
                AND LOWER(e.exercise_type::text) = LOWER(:exercise_type)
                AND a.is_correct = true
            """), {
                "user_id": user_id,
                "exercise_type": str(ex_type)
            }).fetchone()
            
            count = success_count.count if hasattr(success_count, 'count') else success_count[0]
            if count < min_count:
                return False
        
        return True
    
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
            
        except Exception as badge_award_error:
            self.db.rollback()
            logger.error(f"Erreur lors de l'attribution du badge {badge.code}: {badge_award_error}")
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
                
        except Exception as gamification_update_error:
            self.db.rollback()
            logger.error(f"Erreur mise à jour gamification pour l'utilisateur {user_id}: {gamification_update_error}")
    
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

            pinned: List[int] = []
            try:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user and hasattr(user, "pinned_badge_ids") and user.pinned_badge_ids:
                    pinned = [int(x) for x in user.pinned_badge_ids if isinstance(x, (int, float))]
            except Exception:
                pass
            
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
                    'jedi_rank': user_stats[3] if user_stats else 'youngling',
                    'pinned_badge_ids': pinned,
                } if user_stats else {
                    'total_points': 0,
                    'current_level': 1,
                    'experience_points': 0,
                    'jedi_rank': 'youngling',
                    'pinned_badge_ids': [],
                }
            }
            
        except Exception as user_badges_error:
            logger.error(f"Erreur récupération badges utilisateur {user_id}: {user_badges_error}")
            return {'earned_badges': [], 'user_stats': {}}
    
    def _format_requirements_to_text(self, badge: Achievement) -> Optional[str]:
        """Convertit le JSON requirements en texte lisible (critères d'obtention)."""
        if not badge.requirements:
            return None
        try:
            req = json.loads(badge.requirements) if isinstance(badge.requirements, str) else badge.requirements
        except (json.JSONDecodeError, TypeError):
            return None
        if not isinstance(req, dict):
            return None
        # attempts_count
        target = req.get("attempts_count")
        if target is not None:
            return f"Résoudre {target} exercices"
        # min_attempts + success_rate
        target = req.get("min_attempts")
        rate = req.get("success_rate")
        if target is not None and rate is not None:
            return f"{target} tentatives avec {rate}% de réussite"
        # exercise_type + consecutive_correct
        ex_type = req.get("exercise_type", "").lower()
        consec = req.get("consecutive_correct")
        if consec is not None:
            labels = {"addition": "additions", "soustraction": "soustractions", "multiplication": "multiplications", "division": "divisions"}
            label = labels.get(ex_type, ex_type)
            return f"{consec} {label} consécutives correctes"
        # max_time
        max_t = req.get("max_time")
        if max_t is not None:
            return f"Résoudre un exercice en moins de {max_t} secondes"
        # consecutive_days
        days = req.get("consecutive_days")
        if days is not None:
            return f"{days} jours consécutifs d'activité"
        return None

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
                    'criteria_text': self._format_requirements_to_text(badge),
                    'star_wars_title': badge.star_wars_title,
                    'difficulty': badge.difficulty,
                    'points_reward': badge.points_reward,
                    'category': badge.category,
                    'is_secret': badge.is_secret
                }
                for badge in badges
            ]
            
        except Exception as available_badges_error:
            logger.error(f"Erreur récupération badges disponibles: {available_badges_error}")
            return []

    def _get_badge_progress(self, user_id: int, badge: Achievement) -> tuple[float, int, int]:
        """
        Calcule la progression vers un badge non débloqué.
        Returns: (progress 0.0-1.0, current_value, target_value)
        """
        if not badge.requirements:
            return (0.0, 0, 0)
        try:
            req = json.loads(badge.requirements) if isinstance(badge.requirements, str) else badge.requirements
        except (json.JSONDecodeError, TypeError):
            return (0.0, 0, 0)

        target = req.get("attempts_count")
        if target is not None:
            attempts = self.db.query(func.count(Attempt.id)).filter(Attempt.user_id == user_id).scalar() or 0
            progress = min(1.0, attempts / max(1, target))
            return (round(progress, 2), attempts, target)

        target = req.get("min_attempts")
        if target is not None and "success_rate" in req:
            stats = self.db.execute(text("""
                SELECT COUNT(*), COUNT(CASE WHEN is_correct THEN 1 END)
                FROM attempts WHERE user_id = :user_id
            """), {"user_id": user_id}).fetchone()
            total = stats[0] if stats else 0
            correct = stats[1] if stats else 0
            rate_ok = (correct / total * 100 >= req["success_rate"]) if total else False
            progress = min(1.0, total / max(1, target)) if total else 0.0
            if rate_ok and total >= target:
                progress = 1.0
            return (round(progress, 2), total, target)

        return (0.0, 0, 0)

    def get_badges_progress(self, user_id: int) -> Dict[str, Any]:
        """
        Progression vers les badges (unlocked + in_progress).
        """
        earned_ids = {
            r[0] for r in self.db.query(UserAchievement.achievement_id)
            .filter(UserAchievement.user_id == user_id)
            .all()
        }
        all_badges = self.db.query(Achievement).filter(Achievement.is_active == True).all()
        unlocked = []
        in_progress = []
        for b in all_badges:
            if b.id in earned_ids:
                unlocked.append({"id": b.id, "code": b.code, "name": b.name})
            else:
                prog, cur, tgt = self._get_badge_progress(user_id, b)
                in_progress.append({
                    "id": b.id,
                    "code": b.code,
                    "name": b.name,
                    "progress": prog,
                    "current": cur,
                    "target": tgt,
                    "criteria_text": self._format_requirements_to_text(b),
                })
        return {"unlocked": unlocked, "in_progress": in_progress}

    def get_badges_rarity_stats(self) -> Dict[str, Any]:
        """
        Stats rareté par badge : unlock_count, unlock_percent, rarity_label.
        A-4 : preuve sociale (« X% ont débloqué »), indicateur rareté.
        """
        try:
            total_users = self.db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 1
            rows = self.db.execute(text("""
                SELECT ua.achievement_id, COUNT(DISTINCT ua.user_id) as unlock_count
                FROM user_achievements ua
                JOIN achievements a ON a.id = ua.achievement_id
                WHERE a.is_active = true
                GROUP BY ua.achievement_id
            """)).fetchall()
            by_badge = {}
            for row in rows:
                aid = row[0]
                count = row[1]
                pct = round((count / total_users) * 100, 1) if total_users else 0
                if pct < 5:
                    rarity = "rare"
                elif pct < 20:
                    rarity = "uncommon"
                else:
                    rarity = "common"
                by_badge[str(aid)] = {
                    "unlock_count": count,
                    "unlock_percent": pct,
                    "rarity": rarity,
                }
            return {"total_users": total_users, "by_badge": by_badge}
        except Exception as e:
            logger.error(f"Erreur get_badges_rarity_stats: {e}")
            return {"total_users": 0, "by_badge": {}}

    def set_pinned_badges(self, user_id: int, badge_ids: List[int]) -> List[int]:
        """
        A-4 : Épingler 1-3 badges. Seuls les badges obtenus peuvent être épinglés.
        Returns: liste finale des IDs épinglés (max 3).
        """
        MAX_PINNED = 3
        earned_ids = {
            r[0]
            for r in self.db.query(UserAchievement.achievement_id)
            .filter(UserAchievement.user_id == user_id)
            .all()
        }
        valid = [bid for bid in badge_ids[:MAX_PINNED] if bid in earned_ids]
        valid = list(dict.fromkeys(valid))[:MAX_PINNED]
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.pinned_badge_ids = valid
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur set_pinned_badges: {e}")
            return []
        return valid 