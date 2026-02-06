#!/usr/bin/env python3
"""
Script pour nettoyer la table exercises et générer 2-3 exercices cohérents
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.database import get_db_connection
from app.services.exercise_service_translations import create_exercise_with_translations
from loguru import logger

def clean_exercises_table():
    """Nettoie la table exercises en archivant tous les exercices existants"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Compter les exercices avant archivage
        cursor.execute("SELECT COUNT(*) FROM exercises WHERE is_archived = false")
        count_before = cursor.fetchone()[0]
        
        # Archiver tous les exercices (au lieu de les supprimer pour respecter les contraintes FK)
        cursor.execute("UPDATE exercises SET is_archived = true, is_active = false WHERE is_archived = false")
        conn.commit()
        
        logger.info(f"[OK] {count_before} exercices archives (is_archived = true, is_active = false)")
        return True
    except Exception as e:
        logger.error(f"[ERREUR] Erreur lors du nettoyage: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def generate_coherent_exercises():
    """Génère 2-3 exercices cohérents avec tous les champs remplis"""
    
    exercises_to_create = [
        {
            'title': 'Addition spatiale - Niveau Initie',
            'exercise_type': 'addition',
            'difficulty': 'initie',
            'question': 'Tu as trouvé 5 cristaux d\'énergie et ton ami en a trouvé 3. Combien avez-vous de cristaux au total?',
            'correct_answer': '8',
            'choices': ['6', '8', '9', '7'],
            'explanation': 'Pour trouver la réponse, tu dois additionner 5 et 3, ce qui donne 8.',
            'hint': 'Pense à additionner les deux nombres ensemble.',
            'tags': 'algorithmique,simple,spatial',
            'age_group': '6-8',
            'context_theme': 'spatial',
            'complexity': 1,
            'is_active': True,
            'is_archived': False,
            'view_count': 0,
            'ai_generated': False,
        },
        {
            'title': 'Soustraction galactique - Niveau Padawan',
            'exercise_type': 'soustraction',
            'difficulty': 'padawan',
            'question': 'La flotte rebelle comptait 15 vaisseaux, mais 7 ont été détruits dans la bataille. Combien de vaisseaux reste-t-il?',
            'correct_answer': '8',
            'choices': ['7', '8', '9', '6'],
            'explanation': 'Pour calculer ce qui reste, on soustrait: 15 - 7 = 8.',
            'hint': 'Soustrais le nombre de vaisseaux détruits du total initial.',
            'tags': 'algorithmique,spatial',
            'age_group': '8-10',
            'context_theme': 'spatial',
            'complexity': 2,
            'is_active': True,
            'is_archived': False,
            'view_count': 0,
            'ai_generated': False,
        },
        {
            'title': 'Multiplication stellaire - Niveau Chevalier',
            'exercise_type': 'multiplication',
            'difficulty': 'chevalier',
            'question': 'Chaque escadron contient 6 vaisseaux. Si tu as 4 escadrons, combien de vaisseaux as-tu au total?',
            'correct_answer': '24',
            'choices': ['20', '22', '24', '26'],
            'explanation': 'Pour multiplier, on calcule: 6 × 4 = 24. Chaque escadron a 6 vaisseaux, et il y a 4 escadrons.',
            'hint': 'Multiplie le nombre de vaisseaux par escadron par le nombre d\'escadrons.',
            'tags': 'algorithmique,spatial',
            'age_group': '10-12',
            'context_theme': 'spatial',
            'complexity': 3,
            'is_active': True,
            'is_archived': False,
            'view_count': 0,
            'ai_generated': False,
        },
    ]
    
    created_exercises = []
    
    for exercise_data in exercises_to_create:
        try:
            logger.info(f"[CREATION] Creation de l'exercice: {exercise_data['title']}")
            created_exercise = create_exercise_with_translations(exercise_data, locale='fr')
            
            if created_exercise:
                logger.info(f"[OK] Exercice cree avec succes - ID: {created_exercise.get('id')}, Titre: {created_exercise.get('title')}")
                logger.info(f"   Type: {created_exercise.get('exercise_type')}, Difficulte: {created_exercise.get('difficulty')}")
                logger.info(f"   Created_at: {created_exercise.get('created_at')}")
                created_exercises.append(created_exercise)
            else:
                logger.error(f"[ERREUR] Echec de la creation de l'exercice: {exercise_data['title']}")
        except Exception as e:
            logger.error(f"[ERREUR] Erreur lors de la creation de l'exercice {exercise_data['title']}: {e}")
            import traceback
            traceback.print_exc()
    
    return created_exercises

def verify_exercises():
    """Vérifie que les exercices créés ont tous les champs correctement remplis"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                id, title, exercise_type, difficulty, 
                is_active, is_archived, view_count, ai_generated,
                created_at, updated_at,
                creator_id, age_group, context_theme, complexity,
                answer_type, text_metadata
            FROM exercises 
            ORDER BY id DESC
        """)
        
        rows = cursor.fetchall()
        
        print("\n" + "=" * 80)
        print("VÉRIFICATION DES EXERCICES CRÉÉS")
        print("=" * 80)
        
        for row in rows:
            exercise_id, title, exercise_type, difficulty, is_active, is_archived, view_count, ai_generated, created_at, updated_at, creator_id, age_group, context_theme, complexity, answer_type, text_metadata = row
            
            print(f"\nExercice ID: {exercise_id}")
            print(f"   Titre: {title}")
            print(f"   Type: {exercise_type}, Difficulte: {difficulty}")
            print(f"   is_active: {is_active}, is_archived: {is_archived}, view_count: {view_count}")
            print(f"   ai_generated: {ai_generated}")
            print(f"   created_at: {created_at}")
            print(f"   updated_at: {updated_at}")
            print(f"   creator_id: {creator_id}")
            print(f"   age_group: {age_group}, context_theme: {context_theme}, complexity: {complexity}")
            print(f"   answer_type: {answer_type}, text_metadata: {text_metadata}")
            
            # Vérifier les champs critiques
            issues = []
            if created_at is None:
                issues.append("[ATTENTION] created_at est NULL")
            if updated_at is None:
                issues.append("[ATTENTION] updated_at est NULL")
            if is_archived is None:
                issues.append("[ATTENTION] is_archived est NULL")
            if view_count is None:
                issues.append("[ATTENTION] view_count est NULL")
            
            if issues:
                print(f"   PROBLEMES DETECTES:")
                for issue in issues:
                    print(f"      {issue}")
            else:
                print(f"   [OK] Tous les champs critiques sont correctement remplis")
        
        print("\n" + "=" * 80)
        print(f"Total: {len(rows)} exercices vérifiés")
        
    finally:
        cursor.close()
        conn.close()

def main():
    """Fonction principale"""
    print("=" * 80)
    print("NETTOYAGE ET GENERATION D'EXERCICES")
    print("=" * 80)
    
    # Étape 1: Nettoyer la table
    print("\nEtape 1: Nettoyage de la table exercises...")
    if not clean_exercises_table():
        print("[ERREUR] Echec du nettoyage, arret du script")
        return
    
    # Étape 2: Générer les exercices
    print("\nEtape 2: Generation de 3 exercices coherents...")
    created_exercises = generate_coherent_exercises()
    
    print(f"\n[OK] {len(created_exercises)} exercices crees avec succes")
    
    # Étape 3: Vérification
    print("\nEtape 3: Verification des exercices crees...")
    verify_exercises()
    
    print("\n" + "=" * 80)
    print("[OK] PROCESSUS TERMINE")
    print("=" * 80)

if __name__ == "__main__":
    main()

