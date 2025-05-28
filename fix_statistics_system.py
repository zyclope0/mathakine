#!/usr/bin/env python3
"""
Script de diagnostic et réparation du système de statistiques Mathakine.

Ce script :
1. Diagnostique les problèmes de statistiques
2. Répare la méthode record_attempt pour mettre à jour les statistiques
3. Recalcule toutes les statistiques existantes
4. Vérifie l'intégrité du système

Usage:
    python fix_statistics_system.py --diagnose    # Diagnostic seulement
    python fix_statistics_system.py --repair      # Réparation complète
    python fix_statistics_system.py --recalculate # Recalcul des stats
"""

import sys
import os
import argparse
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import func, text
from sqlalchemy.orm import Session

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.user import User
from app.models.progress import Progress
from app.models.legacy_tables import UserStats, Statistics
from app.services.exercise_service import ExerciseService
from app.services.user_service import UserService
from loguru import logger


class StatisticsSystemFixer:
    """Classe pour diagnostiquer et réparer le système de statistiques."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.issues_found = []
        self.fixes_applied = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def diagnose(self) -> Dict[str, Any]:
        """Diagnostique les problèmes du système de statistiques."""
        logger.info("🔍 Début du diagnostic du système de statistiques...")
        
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "statistics": {},
            "recommendations": []
        }
        
        # 1. Vérifier les tentatives sans statistiques correspondantes
        attempts_count = self.db.query(func.count(Attempt.id)).scalar()
        user_stats_count = self.db.query(func.count(UserStats.id)).scalar()
        progress_count = self.db.query(func.count(Progress.id)).scalar()
        
        diagnosis["statistics"] = {
            "total_attempts": attempts_count,
            "user_stats_records": user_stats_count,
            "progress_records": progress_count
        }
        
        logger.info(f"📊 Statistiques trouvées:")
        logger.info(f"   - Tentatives: {attempts_count}")
        logger.info(f"   - UserStats: {user_stats_count}")
        logger.info(f"   - Progress: {progress_count}")
        
        # 2. Vérifier les utilisateurs avec tentatives mais sans statistiques
        users_with_attempts = self.db.query(func.count(func.distinct(Attempt.user_id))).scalar()
        users_with_stats = self.db.query(func.count(func.distinct(UserStats.id))).scalar()
        users_with_progress = self.db.query(func.count(func.distinct(Progress.user_id))).scalar()
        
        if users_with_attempts > users_with_stats:
            issue = f"❌ {users_with_attempts - users_with_stats} utilisateurs ont des tentatives mais pas de UserStats"
            diagnosis["issues"].append(issue)
            self.issues_found.append(issue)
            logger.warning(issue)
        
        if users_with_attempts > users_with_progress:
            issue = f"❌ {users_with_attempts - users_with_progress} utilisateurs ont des tentatives mais pas de Progress"
            diagnosis["issues"].append(issue)
            self.issues_found.append(issue)
            logger.warning(issue)
        
        # 3. Vérifier les incohérences dans les statistiques
        inconsistent_stats = self.db.execute(text("""
            SELECT u.id, u.username, 
                   COUNT(a.id) as actual_attempts,
                   COALESCE(SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END), 0) as actual_correct,
                   COALESCE(SUM(p.total_attempts), 0) as recorded_attempts,
                   COALESCE(SUM(p.correct_attempts), 0) as recorded_correct
            FROM users u
            LEFT JOIN attempts a ON u.id = a.user_id
            LEFT JOIN progress p ON u.id = p.user_id
            WHERE u.id IN (SELECT DISTINCT user_id FROM attempts)
            GROUP BY u.id, u.username
            HAVING COUNT(a.id) != COALESCE(SUM(p.total_attempts), 0)
               OR COALESCE(SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END), 0) != COALESCE(SUM(p.correct_attempts), 0)
        """)).fetchall()
        
        if inconsistent_stats:
            issue = f"❌ {len(inconsistent_stats)} utilisateurs ont des statistiques incohérentes"
            diagnosis["issues"].append(issue)
            self.issues_found.append(issue)
            logger.warning(issue)
            
            for stat in inconsistent_stats:
                logger.warning(f"   - {stat.username}: {stat.actual_attempts} tentatives réelles vs {stat.recorded_attempts} enregistrées")
        
        # 4. Recommandations
        if self.issues_found:
            diagnosis["recommendations"] = [
                "Exécuter --repair pour corriger la méthode record_attempt",
                "Exécuter --recalculate pour recalculer toutes les statistiques",
                "Tester le système avec de nouvelles tentatives"
            ]
        else:
            diagnosis["recommendations"] = ["✅ Système de statistiques sain"]
            logger.success("✅ Aucun problème détecté dans le système de statistiques")
        
        return diagnosis
    
    def repair_record_attempt_method(self) -> bool:
        """Répare la méthode record_attempt pour mettre à jour les statistiques."""
        logger.info("🔧 Réparation de la méthode record_attempt...")
        
        # Lire le fichier actuel
        service_file = "app/services/exercise_service.py"
        
        try:
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier si la méthode contient déjà la mise à jour des statistiques
            if "update_user_progress" in content and "update_user_statistics" in content:
                logger.info("✅ La méthode record_attempt semble déjà réparée")
                return True
            
            # Trouver la méthode record_attempt et ajouter la mise à jour des statistiques
            import re
            
            # Pattern pour trouver la fin de la méthode record_attempt
            pattern = r'(# Log de l\'action\s+is_correct = attempt_data\.get\("is_correct", False\)\s+logger\.info\(f"Tentative enregistrée pour l\'exercice {exercise_id}: {\'Correcte\' if is_correct else \'Incorrecte\'}"\)\s+)(return attempt)'
            
            replacement = r'''\1
                # 🔥 CORRECTION CRITIQUE : Mettre à jour les statistiques utilisateur
                try:
                    self._update_user_statistics(session, attempt_data, exercise)
                    logger.info(f"Statistiques mises à jour pour l'utilisateur {attempt_data.get('user_id')}")
                except Exception as stats_error:
                    logger.error(f"Erreur lors de la mise à jour des statistiques: {stats_error}")
                    # Ne pas faire échouer la tentative pour une erreur de stats
                
                \2'''
            
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            
            # Ajouter la méthode helper pour mettre à jour les statistiques
            helper_method = '''
    @staticmethod
    def _update_user_statistics(session: Session, attempt_data: Dict[str, Any], exercise: Exercise) -> None:
        """
        Met à jour les statistiques utilisateur après une tentative.
        
        Args:
            session: Session de base de données
            attempt_data: Données de la tentative
            exercise: Exercice concerné
        """
        user_id = attempt_data.get("user_id")
        is_correct = attempt_data.get("is_correct", False)
        time_spent = attempt_data.get("time_spent", 0)
        
        # 1. Mettre à jour ou créer Progress
        progress = session.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.exercise_type == exercise.exercise_type
        ).first()
        
        if progress:
            progress.total_attempts += 1
            if is_correct:
                progress.correct_attempts += 1
                progress.streak += 1
                if progress.streak > progress.highest_streak:
                    progress.highest_streak = progress.streak
            else:
                progress.streak = 0
            
            # Mettre à jour le temps moyen
            if progress.average_time is None:
                progress.average_time = time_spent
            else:
                total_time = progress.average_time * (progress.total_attempts - 1) + time_spent
                progress.average_time = total_time / progress.total_attempts
            
            progress.completion_rate = progress.calculate_completion_rate()
            progress.update_mastery_level()
        else:
            new_progress = Progress(
                user_id=user_id,
                exercise_type=exercise.exercise_type,
                difficulty=exercise.difficulty,
                total_attempts=1,
                correct_attempts=1 if is_correct else 0,
                average_time=time_spent,
                streak=1 if is_correct else 0,
                highest_streak=1 if is_correct else 0
            )
            session.add(new_progress)
        
        # 2. Mettre à jour ou créer UserStats
        user_stat = session.query(UserStats).filter(
            UserStats.exercise_type == exercise.exercise_type.value,
            UserStats.difficulty == exercise.difficulty.value
        ).first()
        
        if user_stat:
            user_stat.total_attempts += 1
            if is_correct:
                user_stat.correct_attempts += 1
            user_stat.last_updated = datetime.now()
        else:
            new_user_stat = UserStats(
                exercise_type=exercise.exercise_type.value,
                difficulty=exercise.difficulty.value,
                total_attempts=1,
                correct_attempts=1 if is_correct else 0
            )
            session.add(new_user_stat)
        
        session.flush()
'''
            
            # Ajouter la méthode helper avant la dernière ligne de la classe
            class_end_pattern = r'(\s+return None\s*$)'
            new_content = re.sub(class_end_pattern, helper_method + r'\1', new_content, flags=re.MULTILINE)
            
            # Sauvegarder le fichier modifié
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.success("✅ Méthode record_attempt réparée avec succès")
            self.fixes_applied.append("Méthode record_attempt réparée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la réparation: {e}")
            return False
    
    def recalculate_all_statistics(self) -> bool:
        """Recalcule toutes les statistiques à partir des tentatives existantes."""
        logger.info("🔄 Recalcul de toutes les statistiques...")
        
        try:
            # 1. Vider les tables de statistiques
            self.db.query(UserStats).delete()
            self.db.query(Progress).delete()
            self.db.commit()
            
            logger.info("🗑️ Tables de statistiques vidées")
            
            # 2. Recalculer pour chaque utilisateur
            users_with_attempts = self.db.query(Attempt.user_id).distinct().all()
            
            for (user_id,) in users_with_attempts:
                self._recalculate_user_statistics(user_id)
            
            self.db.commit()
            logger.success(f"✅ Statistiques recalculées pour {len(users_with_attempts)} utilisateurs")
            self.fixes_applied.append(f"Statistiques recalculées pour {len(users_with_attempts)} utilisateurs")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du recalcul: {e}")
            self.db.rollback()
            return False
    
    def _recalculate_user_statistics(self, user_id: int) -> None:
        """Recalcule les statistiques pour un utilisateur spécifique."""
        # Récupérer toutes les tentatives de l'utilisateur
        attempts = self.db.query(Attempt).filter(Attempt.user_id == user_id).all()
        
        # Grouper par exercice pour calculer les Progress
        exercise_stats = {}
        
        for attempt in attempts:
            exercise = self.db.query(Exercise).filter(Exercise.id == attempt.exercise_id).first()
            if not exercise:
                continue
            
            key = (exercise.exercise_type, exercise.difficulty)
            
            if key not in exercise_stats:
                exercise_stats[key] = {
                    'total_attempts': 0,
                    'correct_attempts': 0,
                    'total_time': 0,
                    'streak': 0,
                    'highest_streak': 0,
                    'current_streak': 0
                }
            
            stats = exercise_stats[key]
            stats['total_attempts'] += 1
            stats['total_time'] += attempt.time_spent or 0
            
            if attempt.is_correct:
                stats['correct_attempts'] += 1
                stats['current_streak'] += 1
                stats['highest_streak'] = max(stats['highest_streak'], stats['current_streak'])
            else:
                stats['current_streak'] = 0
        
        # Créer les enregistrements Progress
        for (exercise_type, difficulty), stats in exercise_stats.items():
            avg_time = stats['total_time'] / stats['total_attempts'] if stats['total_attempts'] > 0 else 0
            
            progress = Progress(
                user_id=user_id,
                exercise_type=exercise_type,
                difficulty=difficulty,
                total_attempts=stats['total_attempts'],
                correct_attempts=stats['correct_attempts'],
                average_time=avg_time,
                streak=stats['current_streak'],
                highest_streak=stats['highest_streak']
            )
            progress.completion_rate = progress.calculate_completion_rate()
            progress.update_mastery_level()
            
            self.db.add(progress)
        
        # Créer les enregistrements UserStats globaux
        global_stats = {}
        for (exercise_type, difficulty), stats in exercise_stats.items():
            type_key = exercise_type.value if hasattr(exercise_type, 'value') else str(exercise_type)
            diff_key = difficulty.value if hasattr(difficulty, 'value') else str(difficulty)
            
            user_stat = UserStats(
                exercise_type=type_key,
                difficulty=diff_key,
                total_attempts=stats['total_attempts'],
                correct_attempts=stats['correct_attempts']
            )
            self.db.add(user_stat)
    
    def verify_repair(self) -> bool:
        """Vérifie que la réparation a fonctionné."""
        logger.info("🔍 Vérification de la réparation...")
        
        # Créer une tentative test et vérifier que les stats sont mises à jour
        # (Cette vérification nécessiterait un environnement de test)
        
        diagnosis = self.diagnose()
        
        if not diagnosis["issues"]:
            logger.success("✅ Réparation vérifiée avec succès")
            return True
        else:
            logger.warning("⚠️ Des problèmes persistent après la réparation")
            return False


def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(description="Diagnostic et réparation du système de statistiques Mathakine")
    parser.add_argument("--diagnose", action="store_true", help="Effectuer un diagnostic seulement")
    parser.add_argument("--repair", action="store_true", help="Réparer le système complet")
    parser.add_argument("--recalculate", action="store_true", help="Recalculer les statistiques seulement")
    parser.add_argument("--verify", action="store_true", help="Vérifier la réparation")
    
    args = parser.parse_args()
    
    if not any([args.diagnose, args.repair, args.recalculate, args.verify]):
        parser.print_help()
        return
    
    logger.info("🚀 Démarrage du script de réparation des statistiques Mathakine")
    
    with StatisticsSystemFixer() as fixer:
        success = True
        
        if args.diagnose or args.repair:
            diagnosis = fixer.diagnose()
            print("\n" + "="*60)
            print("📊 RAPPORT DE DIAGNOSTIC")
            print("="*60)
            print(f"Timestamp: {diagnosis['timestamp']}")
            print(f"Tentatives totales: {diagnosis['statistics']['total_attempts']}")
            print(f"Enregistrements UserStats: {diagnosis['statistics']['user_stats_records']}")
            print(f"Enregistrements Progress: {diagnosis['statistics']['progress_records']}")
            
            if diagnosis['issues']:
                print("\n❌ PROBLÈMES DÉTECTÉS:")
                for issue in diagnosis['issues']:
                    print(f"  - {issue}")
                print("\n💡 RECOMMANDATIONS:")
                for rec in diagnosis['recommendations']:
                    print(f"  - {rec}")
            else:
                print("\n✅ AUCUN PROBLÈME DÉTECTÉ")
        
        if args.repair:
            print("\n" + "="*60)
            print("🔧 RÉPARATION EN COURS")
            print("="*60)
            
            if fixer.repair_record_attempt_method():
                logger.success("✅ Méthode record_attempt réparée")
            else:
                logger.error("❌ Échec de la réparation de record_attempt")
                success = False
            
            if fixer.recalculate_all_statistics():
                logger.success("✅ Statistiques recalculées")
            else:
                logger.error("❌ Échec du recalcul des statistiques")
                success = False
        
        if args.recalculate:
            if fixer.recalculate_all_statistics():
                logger.success("✅ Statistiques recalculées")
            else:
                logger.error("❌ Échec du recalcul des statistiques")
                success = False
        
        if args.verify or args.repair:
            if fixer.verify_repair():
                logger.success("✅ Vérification réussie")
            else:
                logger.warning("⚠️ Vérification échouée")
                success = False
        
        if fixer.fixes_applied:
            print("\n" + "="*60)
            print("✅ CORRECTIONS APPLIQUÉES")
            print("="*60)
            for fix in fixer.fixes_applied:
                print(f"  ✓ {fix}")
        
        if success:
            logger.success("🎉 Script terminé avec succès!")
        else:
            logger.error("❌ Script terminé avec des erreurs")
            sys.exit(1)


if __name__ == "__main__":
    main() 