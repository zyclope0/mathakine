import os
import psycopg2
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
print("Chargement des variables d'environnement depuis .env")

# Vérifier les variables d'environnement
print("=== Vérification des variables d'environnement ===")
DATABASE_URL = os.environ.get("DATABASE_URL", "")
print(f"DATABASE_URL: {'Définie (longueur: ' + str(len(DATABASE_URL)) + ')' if DATABASE_URL else 'Non définie'}")

# Chemins critiques
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = str(BASE_DIR / 'templates')
STATIC_DIR = str(BASE_DIR / 'static')

print("\n=== Vérification des chemins ===")
print(f"Chemin de base: {BASE_DIR}")
print(f"Dossier templates: {TEMPLATES_DIR} (existe: {os.path.exists(TEMPLATES_DIR)})")
print(f"Dossier static: {STATIC_DIR} (existe: {os.path.exists(STATIC_DIR)})")

# Liste les templates
if os.path.exists(TEMPLATES_DIR):
    print("\n=== Templates disponibles ===")
    for file in os.listdir(TEMPLATES_DIR):
        print(f"- {file}")

# Vérifier la connexion à la base de données
print("\n=== Test de connexion à la base de données ===")
try:
    if not DATABASE_URL:
        print("Impossible de tester la connexion: DATABASE_URL non définie")
    else:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("Connexion à la base de données établie avec succès")
        
        # Vérifier les tables
        print("\n=== Tables dans la base de données ===")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
        
        # Vérifier le contenu de la table exercises
        print("\n=== Contenu de la table exercises ===")
        cursor.execute("SELECT COUNT(*) FROM exercises")
        count = cursor.fetchone()[0]
        print(f"Nombre total d'exercices: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM exercises WHERE is_archived = FALSE")
        active_count = cursor.fetchone()[0]
        print(f"Nombre d'exercices actifs: {active_count}")
        
        if count > 0:
            print("\n=== 5 derniers exercices ===")
            cursor.execute("SELECT id, title, exercise_type, difficulty FROM exercises ORDER BY id DESC LIMIT 5")
            exercises = cursor.fetchall()
            for ex in exercises:
                print(f"ID: {ex[0]}, Titre: {ex[1]}, Type: {ex[2]}, Difficulté: {ex[3]}")
        
        conn.close()
except Exception as e:
    print(f"Erreur lors de la connexion à la base de données: {e}")

print("\n=== Test de l'environnement Python ===")
print(f"Version Python: {sys.version}")
print(f"Psycopg2 version: {psycopg2.__version__}") 