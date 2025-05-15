import sqlite3
import os
from dotenv import load_dotenv
from app.db.queries import ExerciseQueries, ResultQueries, UserQueries, SettingQueries

def init_database():
    """Initialise la base de données avec les tables nécessaires"""
    load_dotenv()
    
    # Récupérer l'URL de la base de données depuis les variables d'environnement
    database_url = os.getenv("DATABASE_URL", "sqlite:///./mathakine.db")
    
    # Si c'est une URL SQLite, extraire le chemin du fichier
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Se connecter à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Créer les tables
            print("Création de la table users...")
            cursor.execute(UserQueries.CREATE_TABLE.replace("SERIAL", "INTEGER"))
            
            print("Création de la table exercises...")
            cursor.execute(ExerciseQueries.CREATE_TABLE.replace("SERIAL", "INTEGER").replace("JSONB", "TEXT"))
            
            print("Création de la table results...")
            cursor.execute(ResultQueries.CREATE_TABLE.replace("SERIAL", "INTEGER"))
            
            print("Création de la table settings...")
            cursor.execute(SettingQueries.CREATE_TABLE.replace("SERIAL", "INTEGER"))
            
            # Créer la table user_stats si elle n'existe pas
            print("Création de la table user_stats...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_type VARCHAR(50) NOT NULL,
                difficulty VARCHAR(50) NOT NULL,
                total_attempts INTEGER DEFAULT 0,
                correct_attempts INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            conn.commit()
            print("Base de données initialisée avec succès!")
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la base de données: {e}")
            conn.rollback()
            raise
        
        finally:
            conn.close()
    else:
        print("Cette version ne supporte que SQLite pour le moment.")
        print("Veuillez configurer DATABASE_URL avec une URL SQLite.")

if __name__ == "__main__":
    init_database() 