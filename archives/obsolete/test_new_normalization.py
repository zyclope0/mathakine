"""Test de vérification de la normalisation des données dans la base de données."""
import os
import pytest
from sqlalchemy import inspect, text
import sys

# Ajouter le répertoire parent au chemin pour permettre l'importation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports différés pour éviter les problèmes au moment de la collection
def get_app_imports():
    from app.db.base import engine, get_db
    from app.models.exercise import ExerciseType, DifficultyLevel
    from app.models.user import UserRole
    return engine, get_db, ExerciseType, DifficultyLevel, UserRole

@pytest.fixture
def db_session():
    """Fixture pour obtenir une session de base de données."""
    _, get_db, _, _, _ = get_app_imports()
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def valid_values():
    """Fixture pour obtenir les valeurs valides des énumérations."""
    _, _, ExerciseType, DifficultyLevel, UserRole = get_app_imports()
    return {
        'exercise_types': [t.value for t in ExerciseType],
        'difficulties': [d.value for d in DifficultyLevel],
        'roles': [r.value for r in UserRole]
    }

@pytest.fixture
def has_tables():
    """Fixture pour vérifier l'existence des tables."""
    engine, _, _, _, _ = get_app_imports()
    inspect_engine = inspect(engine)
    tables = inspect_engine.get_table_names()
    return {
        'attempts': 'attempts' in tables,
        'exercises': 'exercises' in tables,
        'users': 'users' in tables
    }

def test_exercise_types_normalized(db_session, valid_values, has_tables):
    """Vérifie que tous les types d'exercices sont correctement normalisés."""
    if not has_tables['exercises']:
        pytest.skip("Table exercises non trouvée")
        
    # Utiliser SQLAlchemy avec text()
    result = db_session.execute(text("SELECT DISTINCT exercise_type FROM exercises"))
    exercise_types = [row[0] for row in result.fetchall()]
    
    # Vérifier que tous les types sont valides
    for ex_type in exercise_types:
        assert ex_type in valid_values['exercise_types'], f"Type d'exercice '{ex_type}' n'est pas valide"

def test_difficulties_normalized(db_session, valid_values, has_tables):
    """Vérifie que toutes les difficultés sont correctement normalisées."""
    if not has_tables['exercises']:
        pytest.skip("Table exercises non trouvée")
        
    # Utiliser SQLAlchemy avec text()
    result = db_session.execute(text("SELECT DISTINCT difficulty FROM exercises"))
    difficulties = [row[0] for row in result.fetchall()]
    
    # Vérifier que toutes les difficultés sont valides
    for diff in difficulties:
        assert diff in valid_values['difficulties'], f"Difficulté '{diff}' n'est pas valide"

def test_attempts_normalized(db_session, has_tables):
    """Vérifie que les tentatives ont des données cohérentes."""
    if not has_tables['attempts']:
        pytest.skip("Table attempts non trouvée")
        
    # Vérifier la présence de l'auto-incrémentation sur l'ID
    result = db_session.execute(text("""
        SELECT column_default 
        FROM information_schema.columns 
        WHERE table_name = 'attempts' AND column_name = 'id'
    """))
    column_default = result.scalar()
    
    assert column_default is not None, "La colonne id n'a pas de valeur par défaut"
    assert "nextval" in str(column_default), "La colonne id n'utilise pas nextval pour l'auto-incrémentation"
    
    # Vérifier que les clés étrangères sont valides
    result = db_session.execute(text("""
        SELECT a.id, a.user_id, a.exercise_id 
        FROM attempts a
        LEFT JOIN users u ON a.user_id = u.id
        LEFT JOIN exercises e ON a.exercise_id = e.id
        WHERE u.id IS NULL OR e.id IS NULL
    """))
    invalid_fks = result.fetchall()
    
    assert len(invalid_fks) == 0, f"Trouvé {len(invalid_fks)} tentatives avec des clés étrangères invalides"

def test_user_roles_normalized(db_session, valid_values, has_tables):
    """Vérifie que tous les rôles utilisateurs sont correctement normalisés."""
    if not has_tables['users']:
        pytest.skip("Table users non trouvée")
        
    # Utiliser SQLAlchemy avec text()
    result = db_session.execute(text("SELECT DISTINCT role FROM users"))
    roles = [row[0] for row in result.fetchall()]
    
    # Vérifier que tous les rôles sont valides (insensible à la casse)
    valid_roles_upper = [role.upper() for role in valid_values['roles']]
    for role in roles:
        assert role.upper() in valid_roles_upper, f"Rôle '{role}' n'est pas valide" 