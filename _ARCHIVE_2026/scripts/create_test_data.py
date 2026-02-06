#!/usr/bin/env python3
"""
Script pour créer des données de test pour les utilisateurs
Utile pour tester le tableau de bord et les fonctionnalités
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import get_db
from app.models.user import User
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.services.auth_service import get_user_by_username
from app.utils.db_helpers import get_enum_value
from datetime import datetime, timezone, timedelta
import json
import random
import argparse

def create_test_data(username="test_user", num_exercises=4, num_attempts_per_exercise=3):
    """
    Crée des données de test pour un utilisateur
    
    Args:
        username: Nom d'utilisateur pour lequel créer les données
        num_exercises: Nombre d'exercices à créer
        num_attempts_per_exercise: Nombre de tentatives par exercice
    """
    # Obtenir une session de base de données
    db_generator = get_db()
    db = next(db_generator)

    try:
        # Récupérer l'utilisateur
        user = get_user_by_username(db, username)
        if not user:
            print(f"❌ Erreur: L'utilisateur '{username}' n'existe pas")
            print(f"💡 Conseil: Créez d'abord l'utilisateur ou utilisez 'test_user'")
            return False
        
        print(f"✅ Utilisateur trouvé: {user.username} (ID: {user.id})")
        
        # Types d'exercices disponibles
        exercise_types = [
            (ExerciseType.ADDITION, DifficultyLevel.INITIE, "Addition simple", "Combien font {} + {} ?"),
            (ExerciseType.SOUSTRACTION, DifficultyLevel.INITIE, "Soustraction simple", "Combien font {} - {} ?"),
            (ExerciseType.MULTIPLICATION, DifficultyLevel.PADAWAN, "Multiplication simple", "Combien font {} × {} ?"),
            (ExerciseType.DIVISION, DifficultyLevel.PADAWAN, "Division simple", "Combien font {} ÷ {} ?")
        ]
        
        created_exercises = []
        
        # Créer les exercices
        for i in range(min(num_exercises, len(exercise_types))):
            ex_type, difficulty, title_template, question_template = exercise_types[i]
            
            # Générer des nombres selon le type
            if ex_type == ExerciseType.ADDITION:
                a, b = random.randint(1, 10), random.randint(1, 10)
                correct_answer = str(a + b)
                question = question_template.format(a, b)
                choices = [str(correct_answer), str(a + b - 1), str(a + b + 1), str(a + b + 2)]
            elif ex_type == ExerciseType.SOUSTRACTION:
                a, b = random.randint(5, 15), random.randint(1, 5)
                correct_answer = str(a - b)
                question = question_template.format(a, b)
                choices = [str(correct_answer), str(a - b - 1), str(a - b + 1), str(a - b + 2)]
            elif ex_type == ExerciseType.MULTIPLICATION:
                a, b = random.randint(2, 5), random.randint(2, 5)
                correct_answer = str(a * b)
                question = question_template.format(a, b)
                choices = [str(correct_answer), str(a * b - 1), str(a * b + 1), str(a * b + 2)]
            elif ex_type == ExerciseType.DIVISION:
                b = random.randint(2, 5)
                result = random.randint(2, 8)
                a = b * result
                correct_answer = str(result)
                question = question_template.format(a, b)
                choices = [str(correct_answer), str(result - 1), str(result + 1), str(result + 2)]
            
            # Mélanger les choix
            random.shuffle(choices)
            
            exercise_data = {
                "title": f"{title_template} {i+1}",
                "exercise_type": get_enum_value(ex_type, ex_type.value, db),
                "difficulty": get_enum_value(difficulty, difficulty.value, db),
                "question": question,
                "correct_answer": correct_answer,
                "choices": json.dumps(choices),
                "explanation": f"La réponse est {correct_answer}",
                "hint": "Prenez votre temps pour calculer",
                "is_active": True,
                "is_archived": False,
                "creator_id": user.id
            }
            
            # Vérifier si l'exercice existe déjà
            existing = db.query(Exercise).filter(
                Exercise.title == exercise_data["title"],
                Exercise.creator_id == user.id
            ).first()
            
            if not existing:
                exercise = Exercise(**exercise_data)
                db.add(exercise)
                db.flush()  # Pour obtenir l'ID
                created_exercises.append(exercise)
                print(f"📝 Exercice créé: {exercise.title} (ID: {exercise.id})")
            else:
                created_exercises.append(existing)
                print(f"♻️  Exercice existant: {existing.title} (ID: {existing.id})")
        
        # Créer des tentatives de test
        attempt_data = []
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        
        for i, exercise in enumerate(created_exercises):
            # Créer plusieurs tentatives pour chaque exercice
            for j in range(random.randint(num_attempts_per_exercise, num_attempts_per_exercise + 2)):
                # 75% de réussite en moyenne
                is_correct = random.choice([True, True, True, False])
                attempt_time = base_time + timedelta(days=i, hours=j*2)
                
                attempt = Attempt(
                    user_id=user.id,
                    exercise_id=exercise.id,
                    user_answer=exercise.correct_answer if is_correct else "mauvaise_réponse",
                    is_correct=is_correct,
                    time_spent=random.uniform(30.0, 120.0),  # Entre 30s et 2min
                    attempt_number=j + 1,
                    hints_used=random.randint(0, 2),
                    device_info="Test Device",
                    created_at=attempt_time
                )
                
                db.add(attempt)
                attempt_data.append(attempt)
        
        # Sauvegarder toutes les données
        db.commit()
        
        print(f"\n🎉 Données de test créées avec succès !")
        print(f"   📚 {len(created_exercises)} exercices")
        print(f"   🎯 {len(attempt_data)} tentatives")
        print(f"   👤 Utilisateur: {user.username} (ID: {user.id})")
        
        # Afficher un résumé des statistiques
        total_attempts = len(attempt_data)
        correct_attempts = sum(1 for a in attempt_data if a.is_correct)
        success_rate = round((correct_attempts / total_attempts) * 100) if total_attempts > 0 else 0
        
        print(f"\n📊 Statistiques générées :")
        print(f"   📈 Total tentatives: {total_attempts}")
        print(f"   ✅ Tentatives correctes: {correct_attempts}")
        print(f"   🎯 Taux de réussite: {success_rate}%")
        
        # Statistiques par type
        type_stats = {}
        for attempt in attempt_data:
            exercise = next(ex for ex in created_exercises if ex.id == attempt.exercise_id)
            ex_type = exercise.exercise_type
            if ex_type not in type_stats:
                type_stats[ex_type] = {"total": 0, "correct": 0}
            type_stats[ex_type]["total"] += 1
            if attempt.is_correct:
                type_stats[ex_type]["correct"] += 1
        
        print(f"\n📋 Répartition par type :")
        for ex_type, stats in type_stats.items():
            rate = round((stats["correct"] / stats["total"]) * 100) if stats["total"] > 0 else 0
            print(f"   {ex_type}: {stats['correct']}/{stats['total']} ({rate}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données de test: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Fonction principale avec gestion des arguments"""
    parser = argparse.ArgumentParser(description="Créer des données de test pour les utilisateurs")
    parser.add_argument("--username", "-u", default="test_user", 
                       help="Nom d'utilisateur pour lequel créer les données (défaut: test_user)")
    parser.add_argument("--exercises", "-e", type=int, default=4,
                       help="Nombre d'exercices à créer (défaut: 4)")
    parser.add_argument("--attempts", "-a", type=int, default=3,
                       help="Nombre de tentatives par exercice (défaut: 3)")
    
    args = parser.parse_args()
    
    print(f"🚀 Création de données de test pour l'utilisateur '{args.username}'...")
    print(f"   📝 {args.exercises} exercices")
    print(f"   🎯 ~{args.attempts} tentatives par exercice")
    print()
    
    success = create_test_data(args.username, args.exercises, args.attempts)
    
    if success:
        print(f"\n✨ Données de test créées ! Vous pouvez maintenant :")
        print(f"   🌐 Tester le tableau de bord sur http://localhost:8000/dashboard")
        print(f"   📊 Voir les statistiques via l'API /api/users/stats")
        print(f"   🔍 Vous connecter avec: {args.username} / padawan123")
    else:
        print(f"\n💥 Échec de la création des données de test.")
        print(f"   💡 Vérifiez que l'utilisateur '{args.username}' existe")

if __name__ == "__main__":
    main() 