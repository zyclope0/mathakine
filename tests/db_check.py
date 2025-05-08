"""Script de validation de la base de données pour le projet Mathakine"""
import sys
import os
from pathlib import Path
from datetime import datetime
import importlib
import time
import sqlite3

def main():
    """Fonction principale qui exécute la validation de la base de données"""
    print("=== VÉRIFICATION DE LA BASE DE DONNÉES MATHAKINE ===")
    print(f"Date: {datetime.now()}")
    print(f"Répertoire: {os.getcwd()}\n")
    
    # 1. Vérifier les paramètres de la base de données
    check_db_config()
    
    # 2. Tester la connexion à la base de données
    test_db_connection()
    
    # 3. Vérifier les modèles de données
    check_data_models()
    
    # 4. Vérifier la normalisation des types d'exercices et difficultés
    check_data_normalization()
    
    print("\n=== VÉRIFICATION TERMINÉE ===")

def check_db_config():
    """Vérifie la configuration de la base de données dans .env"""
    print("1. Vérification de la configuration de la base de données:")
    
    if not Path(".env").exists():
        print("  ❌ Fichier .env introuvable")
        return False
    
    try:
        # Charger les variables d'environnement depuis .env
        with open(".env", "r") as f:
            env_vars = {}
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                except ValueError:
                    continue
        
        # Vérifier la présence de DATABASE_URL
        if "DATABASE_URL" in env_vars:
            db_url = env_vars["DATABASE_URL"]
            print(f"  ✅ DATABASE_URL: {db_url[:15]}***[masqué]")
            
            # Vérifier le type de base de données
            if "sqlite" in db_url.lower():
                print("  ℹ️ Type de base de données: SQLite (local)")
            elif "postgresql" in db_url.lower():
                print("  ℹ️ Type de base de données: PostgreSQL")
            elif "mysql" in db_url.lower():
                print("  ℹ️ Type de base de données: MySQL")
            else:
                print(f"  ℹ️ Type de base de données: {db_url.split(':')[0]}")
                
            return True
        else:
            print("  ❌ DATABASE_URL non trouvé dans .env")
            
            # Vérifier si d'autres paramètres de base de données sont définis
            db_params = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"]
            found_params = [param for param in db_params if param in env_vars]
            
            if found_params:
                print(f"  ℹ️ Paramètres trouvés: {', '.join(found_params)}")
                return True
            else:
                print("  ❌ Aucun paramètre de base de données trouvé")
                return False
    
    except Exception as e:
        print(f"  ❌ Erreur lors de la lecture du fichier .env: {e}")
        return False

def test_db_connection():
    """Teste la connexion à la base de données"""
    print("\n2. Test de connexion à la base de données:")
    
    try:
        # Ajouter le répertoire courant au sys.path pour permettre l'import
        sys.path.insert(0, os.getcwd())
        
        # Essayer d'importer le module de base de données
        try:
            from app.db.base import Base, engine
            print("  ✅ Import des modules de base de données réussi")
        except ImportError as e:
            print(f"  ❌ Erreur lors de l'import des modules de base de données: {e}")
            return False
        
        # Tester la connexion
        try:
            # Créer une connexion
            conn = engine.connect()
            conn.close()
            print("  ✅ Connexion à la base de données réussie")
            
            # Vérifier si les tables sont créées
            insp = __import__('sqlalchemy.inspection').inspection.inspect(engine)
            tables = insp.get_table_names()
            
            if tables:
                print(f"  ✅ Tables trouvées dans la base de données: {len(tables)} tables")
                if len(tables) <= 10:  # Si peu de tables, on les affiche
                    print(f"  ℹ️ Tables: {', '.join(tables)}")
            else:
                print("  ⚠️ Aucune table trouvée dans la base de données")
                
            return True
        except Exception as e:
            print(f"  ❌ Erreur de connexion à la base de données: {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur lors du test de connexion: {e}")
        return False

def check_data_models():
    """Vérifie les modèles de données"""
    print("\n3. Vérification des modèles de données:")
    
    try:
        # Importer les modèles
        try:
            # Import des modules de modèles un par un pour identifier les problèmes spécifiques
            model_details = []
            
            try:
                from app.models.user import User
                model_details.append(("User", User.__tablename__))
                print("  ✅ Modèle User importé avec succès")
            except ImportError as e:
                print(f"  ❌ Erreur lors de l'import du modèle User: {e}")
            
            try:
                from app.models.exercise import Exercise
                model_details.append(("Exercise", Exercise.__tablename__))
                print("  ✅ Modèle Exercise importé avec succès")
            except ImportError as e:
                print(f"  ❌ Erreur lors de l'import du modèle Exercise: {e}")
            
            try:
                from app.models.attempt import Attempt
                model_details.append(("Attempt", Attempt.__tablename__))
                print("  ✅ Modèle Attempt importé avec succès")
            except ImportError as e:
                print(f"  ❌ Erreur lors de l'import du modèle Attempt: {e}")
            
            # Afficher les détails des modèles
            if model_details:
                print("\n  Détails des modèles:")
                for model, tablename in model_details:
                    print(f"    - {model} → table '{tablename}'")
            
        except Exception as e:
            print(f"  ❌ Erreur lors de l'import des modèles: {e}")
            return False
            
        return True
    
    except Exception as e:
        print(f"  ❌ Erreur lors de la vérification des modèles: {e}")
        return False

def check_data_normalization():
    """Vérifie la normalisation des types d'exercices et difficultés dans la base de données"""
    print("\n4. Vérification de la normalisation des données:")
    
    try:
        # Vérifier d'abord si nous utilisons SQLite
        db_path = os.path.join(os.getcwd(), "math_trainer.db")
        if not os.path.exists(db_path):
            print(f"  ⚠️ Base de données SQLite non trouvée à l'emplacement {db_path}")
            return False
        
        # Se connecter à la base de données SQLite
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Vérifier les types d'exercices
        print("  Vérification des types d'exercices:")
        cursor.execute("SELECT DISTINCT exercise_type FROM exercises")
        exercise_types = [row['exercise_type'] for row in cursor.fetchall()]
        
        valid_types = ['addition', 'subtraction', 'multiplication', 'division']
        invalid_types = [t for t in exercise_types if t.lower() not in valid_types]
        
        if invalid_types:
            print(f"  ⚠️ Types d'exercices non normalisés trouvés: {', '.join(invalid_types)}")
            print("  ℹ️ Exécutez fix_database.py pour corriger ces problèmes")
        else:
            print(f"  ✅ Types d'exercices corrects: {', '.join(exercise_types)}")
        
        # Vérifier les difficultés
        print("\n  Vérification des niveaux de difficulté:")
        cursor.execute("SELECT DISTINCT difficulty FROM exercises")
        difficulties = [row['difficulty'] for row in cursor.fetchall()]
        
        valid_difficulties = ['easy', 'medium', 'hard']
        invalid_difficulties = [d for d in difficulties if d.lower() not in valid_difficulties]
        
        if invalid_difficulties:
            print(f"  ⚠️ Niveaux de difficulté non normalisés trouvés: {', '.join(invalid_difficulties)}")
            print("  ℹ️ Exécutez fix_database.py pour corriger ces problèmes")
        else:
            print(f"  ✅ Niveaux de difficulté corrects: {', '.join(difficulties)}")
        
        # Vérifier les doublons dans user_stats
        print("\n  Vérification des doublons dans user_stats:")
        cursor.execute("""
        SELECT exercise_type, difficulty, COUNT(*) as count
        FROM user_stats
        GROUP BY exercise_type, difficulty
        HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"  ⚠️ Doublons trouvés dans user_stats: {len(duplicates)} combinaisons en double")
            for dup in duplicates:
                print(f"    - Type: {dup['exercise_type']}, Difficulté: {dup['difficulty']}, Nombre: {dup['count']}")
            print("  ℹ️ Exécutez fix_database.py pour fusionner ces doublons")
        else:
            print("  ✅ Aucun doublon trouvé dans user_stats")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors de la vérification de la normalisation: {e}")
        return False

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 