"""
Script de test pour vérifier la structure de la base de données
et comprendre comment les données sont stockées
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Construire depuis les variables individuelles
    POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "mathakine")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

db_info = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'local'
print(f"Connexion a la base de donnees: {db_info}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_table_structure():
    """Vérifie la structure de la table exercises"""
    print("\n" + "="*80)
    print("STRUCTURE DE LA TABLE EXERCISES")
    print("="*80)
    
    inspector = inspect(engine)
    
    if 'exercises' in inspector.get_table_names():
        columns = inspector.get_columns('exercises')
        print("\nColonnes de la table 'exercises':")
        for col in columns:
            col_type = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col['default'] else ""
            print(f"  - {col['name']:20} {col_type:30} {nullable}{default}")
    else:
        print("Table 'exercises' non trouvee")

def check_sample_data():
    """Vérifie un échantillon de données"""
    print("\n" + "="*80)
    print("ECHANTILLON DE DONNEES")
    print("="*80)
    
    with engine.connect() as conn:
        # Récupérer quelques exercices
        result = conn.execute(text("""
            SELECT 
                id, 
                title, 
                exercise_type, 
                difficulty,
                created_at,
                updated_at,
                choices,
                ai_generated,
                view_count
            FROM exercises 
            WHERE is_archived = false 
            LIMIT 3
        """))
        
        exercises = result.fetchall()
        
        if not exercises:
            print("⚠️  Aucun exercice trouvé dans la base de données")
            return
        
        print(f"\n{len(exercises)} exercice(s) trouve(s):\n")
        
        for i, ex in enumerate(exercises, 1):
            print(f"--- Exercice {i} ---")
            print(f"  ID: {ex.id}")
            print(f"  Titre: {ex.title}")
            print(f"  Type: {ex.exercise_type} (type Python: {type(ex.exercise_type).__name__})")
            print(f"  Difficulté: {ex.difficulty} (type Python: {type(ex.difficulty).__name__})")
            print(f"  Created_at: {ex.created_at} (type Python: {type(ex.created_at).__name__})")
            print(f"  Updated_at: {ex.updated_at} (type Python: {type(ex.updated_at).__name__})")
            print(f"  Choices: {ex.choices} (type Python: {type(ex.choices).__name__})")
            print(f"  AI Generated: {ex.ai_generated}")
            print(f"  View Count: {ex.view_count}")
            print()

def check_enum_types():
    """Vérifie les types ENUM dans PostgreSQL"""
    print("\n" + "="*80)
    print("TYPES ENUM DANS POSTGRESQL")
    print("="*80)
    
    with engine.connect() as conn:
        # Vérifier les types ENUM
        result = conn.execute(text("""
            SELECT t.typname, e.enumlabel
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            WHERE t.typname IN ('exercisetype', 'difficultylevel', 'userrole')
            ORDER BY t.typname, e.enumsortorder
        """))
        
        enums = result.fetchall()
        
        if enums:
            current_type = None
            for enum_type, enum_value in enums:
                if enum_type != current_type:
                    print(f"\n{enum_type}:")
                    current_type = enum_type
                print(f"  - {enum_value}")
        else:
            print("⚠️  Aucun type ENUM trouvé (peut-être stocké en VARCHAR)")

def test_json_serialization():
    """Teste la sérialisation JSON d'un exercice"""
    print("\n" + "="*80)
    print("TEST DE SERIALISATION JSON")
    print("="*80)
    
    from app.models.exercise import Exercise
    from app.db.base import Base
    
    db = SessionLocal()
    try:
        # Récupérer un exercice via SQLAlchemy
        exercise = db.query(Exercise).filter(Exercise.is_archived == False).first()
        
        if not exercise:
            print("⚠️  Aucun exercice trouvé pour le test")
            return
        
        print(f"\nExercice recupere: {exercise.title}")
        print(f"\nTypes Python des attributs:")
        print(f"  exercise_type: {type(exercise.exercise_type).__name__} = {exercise.exercise_type}")
        print(f"  difficulty: {type(exercise.difficulty).__name__} = {exercise.difficulty}")
        print(f"  created_at: {type(exercise.created_at).__name__} = {exercise.created_at}")
        print(f"  updated_at: {type(exercise.updated_at).__name__} = {exercise.updated_at}")
        print(f"  choices: {type(exercise.choices).__name__} = {exercise.choices}")
        
        # Tester la sérialisation
        print(f"\nTest de serialisation:")
        try:
            # Test avec notre fonction helper
            from app.services.enhanced_server_adapter import _serialize_exercise
            serialized = _serialize_exercise(exercise)
            print(f"Serialisation reussie!")
            print(f"  exercise_type serialise: {serialized['exercise_type']} (type: {type(serialized['exercise_type']).__name__})")
            print(f"  difficulty serialise: {serialized['difficulty']} (type: {type(serialized['difficulty']).__name__})")
            print(f"  created_at serialise: {serialized['created_at']} (type: {type(serialized['created_at']).__name__})")
            print(f"  choices serialise: {serialized['choices']} (type: {type(serialized['choices']).__name__})")
            
            # Tester JSON dumps
            json_str = json.dumps(serialized, indent=2)
            print(f"\nJSON.dumps() reussi!")
            print(f"  Taille: {len(json_str)} caracteres")
            
        except Exception as e:
            print(f"Erreur lors de la serialisation: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == "__main__":
    try:
        check_table_structure()
        check_sample_data()
        check_enum_types()
        test_json_serialization()
        print("\n" + "="*80)
        print("Verification terminee!")
        print("="*80)
    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()

