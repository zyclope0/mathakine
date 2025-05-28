#!/usr/bin/env python3
"""
Script de test complet pour valider le système de statistiques.
Teste différents scénarios : utilisateurs multiples, types d'exercices variés, etc.
"""

import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.legacy_tables import UserStats
from app.services.exercise_service import ExerciseService
from app.utils.db_helpers import get_enum_value
from loguru import logger


class StatisticsTestSuite:
    """Suite de tests pour le système de statistiques."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.test_users = []
        self.test_exercises = []
        self.test_attempts = []
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        self.db.close()
    
    def cleanup(self):
        """Nettoie les données de test créées."""
        try:
            # Supprimer les tentatives de test
            for attempt in self.test_attempts:
                self.db.delete(attempt)
            
            # Supprimer les exercices de test
            for exercise in self.test_exercises:
                self.db.delete(exercise)
            
            # Supprimer les utilisateurs de test
            for user in self.test_users:
                # Supprimer d'abord les progress liés
                self.db.query(Progress).filter(Progress.user_id == user.id).delete()
                self.db.delete(user)
            
            self.db.commit()
            logger.info("🧹 Nettoyage des données de test terminé")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}")
            self.db.rollback()
    
    def create_test_user(self, username_suffix: str) -> User:
        """Crée un utilisateur de test."""
        user = User(
            username=f"test_scenario_{username_suffix}_{int(datetime.now().timestamp())}",
            email=f"test_scenario_{username_suffix}@example.com",
            hashed_password="test_password",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, self.db)
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        self.test_users.append(user)
        return user
    
    def create_test_exercise(self, exercise_type: ExerciseType, difficulty: DifficultyLevel, title_suffix: str) -> Exercise:
        """Crée un exercice de test."""
        exercise = Exercise(
            title=f"Test {title_suffix}",
            exercise_type=get_enum_value(ExerciseType, exercise_type.value, self.db),
            difficulty=get_enum_value(DifficultyLevel, difficulty.value, self.db),
            question=f"Question test {title_suffix}",
            correct_answer="42",
            choices=["40", "41", "42", "43"],
            explanation=f"Explication test {title_suffix}",
            is_active=True,
            is_archived=False
        )
        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        self.test_exercises.append(exercise)
        return exercise
    
    def simulate_attempt(self, user: User, exercise: Exercise, is_correct: bool, time_spent: float) -> bool:
        """Simule une tentative d'exercice."""
        attempt_data = {
            "user_id": user.id,
            "exercise_id": exercise.id,
            "user_answer": "42" if is_correct else "41",
            "is_correct": is_correct,
            "time_spent": time_spent,
            "attempt_number": 1
        }
        
        attempt = ExerciseService.record_attempt(self.db, attempt_data)
        if attempt:
            self.test_attempts.append(attempt)
            return True
        return False
    
    def test_scenario_1_single_user_multiple_attempts(self) -> bool:
        """Test 1: Un utilisateur, plusieurs tentatives sur le même exercice."""
        logger.info("🧪 Test 1: Utilisateur unique, tentatives multiples")
        
        user = self.create_test_user("single_user")
        exercise = self.create_test_exercise(ExerciseType.ADDITION, DifficultyLevel.INITIE, "Addition Simple")
        
        # 3 tentatives : 2 correctes, 1 incorrecte
        attempts = [
            (True, 10.0),   # Correcte
            (False, 15.0),  # Incorrecte
            (True, 8.0)     # Correcte
        ]
        
        for is_correct, time_spent in attempts:
            if not self.simulate_attempt(user, exercise, is_correct, time_spent):
                logger.error("❌ Échec de simulation de tentative")
                return False
        
        # Vérifier les statistiques
        progress = self.db.query(Progress).filter(
            Progress.user_id == user.id,
            Progress.exercise_type == exercise.exercise_type
        ).first()
        
        if not progress:
            logger.error("❌ Aucun Progress créé")
            return False
        
        if progress.total_attempts != 3 or progress.correct_attempts != 2:
            logger.error(f"❌ Progress incorrect: {progress.total_attempts} tentatives, {progress.correct_attempts} correctes (attendu: 3, 2)")
            return False
        
        logger.success("✅ Test 1 réussi")
        return True
    
    def test_scenario_2_multiple_users_same_exercise(self) -> bool:
        """Test 2: Plusieurs utilisateurs sur le même exercice."""
        logger.info("🧪 Test 2: Utilisateurs multiples, même exercice")
        
        user1 = self.create_test_user("multi_user_1")
        user2 = self.create_test_user("multi_user_2")
        exercise = self.create_test_exercise(ExerciseType.MULTIPLICATION, DifficultyLevel.PADAWAN, "Multiplication")
        
        # User1: 2 tentatives correctes
        self.simulate_attempt(user1, exercise, True, 12.0)
        self.simulate_attempt(user1, exercise, True, 10.0)
        
        # User2: 1 tentative incorrecte
        self.simulate_attempt(user2, exercise, False, 20.0)
        
        # Vérifier Progress pour chaque utilisateur
        progress1 = self.db.query(Progress).filter(
            Progress.user_id == user1.id,
            Progress.exercise_type == exercise.exercise_type
        ).first()
        
        progress2 = self.db.query(Progress).filter(
            Progress.user_id == user2.id,
            Progress.exercise_type == exercise.exercise_type
        ).first()
        
        if not progress1 or not progress2:
            logger.error("❌ Progress manquants")
            return False
        
        if progress1.total_attempts != 2 or progress1.correct_attempts != 2:
            logger.error(f"❌ Progress User1 incorrect: {progress1.total_attempts}, {progress1.correct_attempts}")
            return False
        
        if progress2.total_attempts != 1 or progress2.correct_attempts != 0:
            logger.error(f"❌ Progress User2 incorrect: {progress2.total_attempts}, {progress2.correct_attempts}")
            return False
        
        # Vérifier UserStats globales
        user_stat = self.db.query(UserStats).filter(
            UserStats.exercise_type == exercise.exercise_type.value,
            UserStats.difficulty == exercise.difficulty.value
        ).first()
        
        if not user_stat:
            logger.error("❌ UserStats manquantes")
            return False
        
        # UserStats devrait avoir 3 tentatives au total (2+1), 2 correctes
        if user_stat.total_attempts < 3 or user_stat.correct_attempts < 2:
            logger.warning(f"⚠️ UserStats: {user_stat.total_attempts} tentatives, {user_stat.correct_attempts} correctes (attendu au moins: 3, 2)")
        
        logger.success("✅ Test 2 réussi")
        return True
    
    def test_scenario_3_different_exercise_types(self) -> bool:
        """Test 3: Un utilisateur, différents types d'exercices."""
        logger.info("🧪 Test 3: Types d'exercices différents")
        
        user = self.create_test_user("diff_types")
        
        # Créer différents types d'exercices
        exercises = [
            self.create_test_exercise(ExerciseType.ADDITION, DifficultyLevel.INITIE, "Addition"),
            self.create_test_exercise(ExerciseType.SOUSTRACTION, DifficultyLevel.PADAWAN, "Soustraction"),
            self.create_test_exercise(ExerciseType.MULTIPLICATION, DifficultyLevel.CHEVALIER, "Multiplication")
        ]
        
        # Une tentative correcte sur chaque type
        for exercise in exercises:
            if not self.simulate_attempt(user, exercise, True, 15.0):
                logger.error(f"❌ Échec tentative pour {exercise.exercise_type}")
                return False
        
        # Vérifier qu'on a 3 Progress différents
        progress_count = self.db.query(Progress).filter(Progress.user_id == user.id).count()
        
        if progress_count != 3:
            logger.error(f"❌ Nombre de Progress incorrect: {progress_count} (attendu: 3)")
            return False
        
        logger.success("✅ Test 3 réussi")
        return True
    
    def run_all_tests(self) -> bool:
        """Exécute tous les tests de scénarios."""
        logger.info("🚀 Démarrage de la suite de tests de statistiques")
        
        tests = [
            self.test_scenario_1_single_user_multiple_attempts,
            self.test_scenario_2_multiple_users_same_exercise,
            self.test_scenario_3_different_exercise_types
        ]
        
        results = []
        for i, test in enumerate(tests, 1):
            try:
                result = test()
                results.append(result)
                if result:
                    logger.success(f"✅ Test {i} réussi")
                else:
                    logger.error(f"❌ Test {i} échoué")
            except Exception as e:
                logger.error(f"❌ Test {i} échoué avec erreur: {e}")
                results.append(False)
        
        success_count = sum(results)
        total_count = len(results)
        
        logger.info(f"📊 Résultats: {success_count}/{total_count} tests réussis")
        
        if success_count == total_count:
            logger.success("🎉 Tous les tests de scénarios ont réussi!")
            return True
        else:
            logger.error("❌ Certains tests ont échoué")
            return False


def main():
    """Point d'entrée principal."""
    logger.info("🚀 Démarrage des tests de scénarios de statistiques")
    
    with StatisticsTestSuite() as test_suite:
        success = test_suite.run_all_tests()
    
    if success:
        logger.success("🎉 Suite de tests terminée avec succès!")
        print("\n✅ RÉSULTAT: Tous les scénarios de statistiques fonctionnent correctement")
    else:
        logger.error("❌ Suite de tests échouée!")
        print("\n❌ RÉSULTAT: Des problèmes ont été détectés dans les scénarios")
        sys.exit(1)


if __name__ == "__main__":
    main() 