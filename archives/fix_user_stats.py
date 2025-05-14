import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("Erreur: DATABASE_URL non définie")
    exit(1)

try:
    # Se connecter à PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Vérifier si la table user_stats existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'user_stats'
        );
    """)
    
    table_exists = cursor.fetchone()[0]
    
    if table_exists:
        print("La table user_stats existe.")
        
        # Vérifier la séquence associée à la colonne id
        cursor.execute("""
            SELECT pg_get_serial_sequence('user_stats', 'id');
        """)
        
        sequence_name = cursor.fetchone()[0]
        
        if sequence_name:
            print(f"La séquence pour user_stats.id est: {sequence_name}")
        else:
            print("ERREUR: Aucune séquence n'est associée à la colonne id.")
            
            # Supprimer la table et la recréer
            print("Suppression et recréation de la table user_stats...")
            cursor.execute("DROP TABLE IF EXISTS user_stats;")
            
            cursor.execute("""
                CREATE TABLE user_stats (
                    id SERIAL PRIMARY KEY,
                    exercise_type VARCHAR(50) NOT NULL,
                    difficulty VARCHAR(50) NOT NULL,
                    total_attempts INTEGER DEFAULT 0,
                    correct_attempts INTEGER DEFAULT 0,
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            print("Table user_stats recréée avec succès.")
    else:
        print("La table user_stats n'existe pas. Création en cours...")
        
        cursor.execute("""
            CREATE TABLE user_stats (
                id SERIAL PRIMARY KEY,
                exercise_type VARCHAR(50) NOT NULL,
                difficulty VARCHAR(50) NOT NULL,
                total_attempts INTEGER DEFAULT 0,
                correct_attempts INTEGER DEFAULT 0,
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("Table user_stats créée avec succès.")
    
    # Vérifier si des données existent dans la table
    cursor.execute("SELECT COUNT(*) FROM user_stats")
    stats_count = cursor.fetchone()[0]
    
    if stats_count == 0:
        print("Insertion des données par défaut dans user_stats...")
        
        # Ajouter des statistiques par défaut
        for exercise_type in ['addition', 'subtraction', 'multiplication', 'division']:
            for difficulty in ['easy', 'medium', 'hard']:
                cursor.execute("""
                    INSERT INTO user_stats (exercise_type, difficulty, total_attempts, correct_attempts)
                    VALUES (%s, %s, 0, 0) RETURNING id
                """, (exercise_type, difficulty))
                inserted_id = cursor.fetchone()[0]
                print(f"Inséré: {exercise_type}, {difficulty} -> ID: {inserted_id}")
    else:
        print(f"La table user_stats contient déjà {stats_count} enregistrements.")
    
    conn.close()
    print("Réparation de la base de données terminée.")

except Exception as e:
    print(f"Erreur: {e}")
    exit(1) 