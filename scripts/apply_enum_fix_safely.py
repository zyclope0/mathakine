#!/usr/bin/env python3
"""
Script sécurisé pour appliquer la correction d'enum PostgreSQL
Avec vérifications et rollback automatique en cas d'erreur
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.base import SessionLocal, engine
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge

def check_database_state(db):
    """Vérifie l'état de la base de données"""
    ex_count = db.query(Exercise).count()
    ch_count = db.query(LogicChallenge).count()
    return ex_count, ch_count

def apply_enum_fix():
    """Applique la correction d'enum avec vérifications de sécurité"""
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("CORRECTION DES ENUMS POSTGRESQL - SCRIPT SÉCURISÉ")
        print("=" * 70)
        
        # Étape 1 : Vérifier l'état actuel
        print("\n[1/5] Vérification de l'état de la base de données...")
        ex_count, ch_count = check_database_state(db)
        print(f"   [OK] Exercices : {ex_count}")
        print(f"   [OK] Challenges : {ch_count}")
        
        if ex_count > 0 or ch_count > 0:
            print("\n[WARNING] ATTENTION : La base contient des donnees !")
            response = input("Voulez-vous continuer ? (oui/non) : ")
            if response.lower() != 'oui':
                print("[ANNULE] Operation annulee par l'utilisateur")
                return False
        
        # Étape 2 : Tester la connexion
        print("\n[2/5] Test de la connexion PostgreSQL...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"   [OK] Connecte a : {version[:50]}...")
        
        # Étape 3 : Appliquer la migration
        print("\n[3/5] Application de la migration...")
        
        with engine.connect() as conn:
            # Commencer une transaction
            trans = conn.begin()
            
            try:
                # Convertir en text temporairement
                print("   [->] Conversion des colonnes en TEXT...")
                conn.execute(text("ALTER TABLE exercises ALTER COLUMN exercise_type TYPE text USING exercise_type::text"))
                conn.execute(text("ALTER TABLE exercises ALTER COLUMN difficulty TYPE text USING difficulty::text"))
                
                # Supprimer les anciens enums
                print("   [->] Suppression des anciens types ENUM...")
                conn.execute(text("DROP TYPE IF EXISTS exercisetype CASCADE"))
                conn.execute(text("DROP TYPE IF EXISTS difficultylevel CASCADE"))
                
                # Recréer avec MAJUSCULES
                print("   [->] Creation des nouveaux types ENUM (MAJUSCULES)...")
                conn.execute(text("""
                    CREATE TYPE exercisetype AS ENUM (
                        'ADDITION', 'SOUSTRACTION', 'MULTIPLICATION', 'DIVISION',
                        'FRACTIONS', 'GEOMETRIE', 'TEXTE', 'MIXTE', 'DIVERS'
                    )
                """))
                
                conn.execute(text("""
                    CREATE TYPE difficultylevel AS ENUM (
                        'INITIE', 'PADAWAN', 'CHEVALIER', 'MAITRE'
                    )
                """))
                
                # Réappliquer les types
                print("   [->] Reapplication des types ENUM aux colonnes...")
                conn.execute(text("ALTER TABLE exercises ALTER COLUMN exercise_type TYPE exercisetype USING UPPER(exercise_type)::exercisetype"))
                conn.execute(text("ALTER TABLE exercises ALTER COLUMN difficulty TYPE difficultylevel USING UPPER(difficulty)::difficultylevel"))
                
                # Commit la transaction
                trans.commit()
                print("   [OK] Migration appliquee avec succes !")
                
            except Exception as e:
                # Rollback en cas d'erreur
                trans.rollback()
                print(f"\n[ERREUR] ERREUR lors de la migration : {e}")
                print("   [->] Rollback effectue, base de donnees inchangee")
                return False
        
        # Étape 4 : Vérification post-migration
        print("\n[4/5] Vérification post-migration...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = 'exercisetype'::regtype 
                ORDER BY enumsortorder
            """))
            enum_values = [row[0] for row in result]
            print(f"   [OK] Valeurs de exercisetype : {enum_values}")
        
        # Étape 5 : Test final
        print("\n[5/5] Test final avec SQLAlchemy...")
        # Recharger la session pour prendre en compte les changements
        db.close()
        db = SessionLocal()
        
        # Tester en créant un exercice fictif
        from app.models.exercise import ExerciseType, DifficultyLevel
        test_ex = Exercise(
            title="Test Migration",
            question="Test",
            correct_answer="42",
            explanation="Test",
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.INITIE,
            complexity=1
        )
        db.add(test_ex)
        db.flush()  # Flush sans commit
        
        print(f"   [OK] Test insertion : exercise_type = {test_ex.exercise_type}")
        print(f"   [OK] Test insertion : difficulty = {test_ex.difficulty}")
        
        # Rollback du test (on ne garde pas l'exercice de test)
        db.rollback()
        
        print("\n" + "=" * 70)
        print("[SUCCES] MIGRATION REUSSIE !")
        print("=" * 70)
        print("\nLe script seed_quality_exercises_challenges.py peut maintenant être lancé.")
        
        return True
        
    except Exception as e:
        print(f"\n[ERREUR] ERREUR CRITIQUE : {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = apply_enum_fix()
    sys.exit(0 if success else 1)

