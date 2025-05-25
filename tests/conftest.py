"""
Configuration centralisée pour pytest.
Ce fichier importe toutes les fixtures pour les rendre disponibles globalement.
"""
import pytest
import os
from pathlib import Path
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.logic_challenge import LogicChallengeType, AgeGroup
from app.models.user import UserRole
from app.utils.db_helpers import get_enum_value, get_all_enum_values
from tests.utils.test_helpers import unique_username, unique_email
import json
from typing import Dict, Any

# Ajouter le répertoire racine au path pour faciliter les imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importer les modèles et la base de données
from app.db.base import Base, engine
from app.core.config import settings
from app.models.user import UserRole

# Importer l'application FastAPI
from app.main import app

# Configuration de l'environnement pour les tests
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configure l'environnement de test automatiquement au début de la session."""
    # Créer le dossier de résultats s'il n'existe pas
    Path("test_results").mkdir(exist_ok=True)

    # Définir les variables d'environnement pour les tests
    os.environ["TESTING"] = "true"

    # Utiliser la base de données PostgreSQL définie dans .env
    os.environ["TEST_DATABASE_URL"] = os.environ.get("DATABASE_URL")

    yield  # Exécuter les tests

# Configuration des fixtures
@pytest.fixture(scope="session")
def test_app():
    """Fixture pour configurer l'application de test"""
    from app.main import app

    # Configurer l'environnement de test
    os.environ["TESTING"] = "true"
    
    # Retourner l'application
    return app

@pytest.fixture(scope="session")
def test_client():
    """Fixture pour créer un client de test"""
    from fastapi.testclient import TestClient
    from app.main import app

    # Configurer l'environnement de test
    os.environ["TESTING"] = "true"

    # Créer un client de test
    client = TestClient(app)
    return client

# Fixture pour le client API
@pytest.fixture
def client():
    return TestClient(app)

# Fixture pour créer un utilisateur de test et obtenir un token d'authentification
@pytest.fixture
def auth_client():
    """Crée un utilisateur de test et retourne un client API authentifié"""
    client = TestClient(app)
    
    # Créer un utilisateur de test avec un nom unique
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"test_jedi_{unique_id}",
        "email": f"jedi_{unique_id}@test.com",
        "password": "Force123Jedi",
        "role": "padawan"
    }
    try:
        # Enregistrer l'utilisateur
        response = client.post("/api/users/", json=user_data)
        if response.status_code != 201:
            pytest.skip(f"Impossible de créer l'utilisateur de test: {response.text}")
        
        # Authentification
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        if response.status_code != 200:
            pytest.skip(f"Impossible d'authentifier l'utilisateur de test: {response.text}")
        
        token = response.json()["access_token"]
        
        # Retourner un client configuré avec les headers d'authentification
        client.headers.update({"Authorization": f"Bearer {token}"})
        
        return {
            "client": client,
            "user_data": user_data,
            "token": token,
            "user_id": response.json().get("user_id")
        }
    except Exception as e:
        pytest.skip(f"Erreur pendant la configuration de l'authentification: {str(e)}")

# Fixture pour créer une session de base de données pour les tests
@pytest.fixture
def db_session():
    # Utiliser la base de données PostgreSQL définie dans .env
    engine = create_engine(settings.DATABASE_URL)
    
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()

# Fixture pour créer un token expiré
@pytest.fixture
def expired_token_client():
    """Crée un utilisateur de test et retourne un client API avec un token expiré"""
    client = TestClient(app)
    
    # Créer un utilisateur de test avec un nom unique
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"test_jedi_expired_{unique_id}",
        "email": f"jedi_expired_{unique_id}@test.com",
        "password": "Force123Jedi",
        "role": "padawan"
    }
    try:
        # Enregistrer l'utilisateur
        response = client.post("/api/users/", json=user_data)
        if response.status_code != 201:
            pytest.skip(f"Impossible de créer l'utilisateur de test: {response.text}")
        
        # Créer manuellement un token expiré
        user_id = response.json()["id"]
        
        # Créer un token expiré (avec une date d'expiration dans le passé)
        payload = {
            "sub": user_data["username"],
            "role": user_data["role"],
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=30)  # Expiré depuis 30 minutes
        }
        
        # Encoder le token avec la clé secrète
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        
        # Configurer le client avec le token expiré
        client.headers.update({"Authorization": f"Bearer {expired_token}"})
        
        return {
            "client": client,
            "user_data": user_data,
            "token": expired_token,
            "user_id": user_id
        }
    except Exception as e:
        pytest.skip(f"Erreur pendant la création du token expiré: {str(e)}")

# Fixture pour créer un refresh token valide
@pytest.fixture
def refresh_token_client():
    """Crée un utilisateur de test et retourne un client API avec un refresh token valide"""
    client = TestClient(app)
    
    # Créer un utilisateur de test avec un nom unique
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"test_jedi_refresh_{unique_id}",
        "email": f"jedi_refresh_{unique_id}@test.com",
        "password": "Force123Jedi",
        "role": "padawan"
    }
    try:
        # Enregistrer l'utilisateur
        response = client.post("/api/users/", json=user_data)
        if response.status_code != 201:
            pytest.skip(f"Impossible de créer l'utilisateur de test: {response.text}")
        
        # Authentification pour obtenir les tokens
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        if response.status_code != 200:
            pytest.skip(f"Impossible d'authentifier l'utilisateur de test: {response.text}")
        
        # Extraire le refresh token
        tokens = response.json()
        if "refresh_token" not in tokens:
            pytest.skip("Le refresh token n'est pas présent dans la réponse")
            
        refresh_token = tokens["refresh_token"]
        
        return {
            "client": client,
            "user_data": user_data,
            "access_token": tokens["access_token"],
            "refresh_token": refresh_token,
            "user_id": tokens.get("user_id")
        }
    except Exception as e:
        pytest.skip(f"Erreur pendant la configuration du refresh token: {str(e)}")

# Fixture générique pour créer un client authentifié avec un rôle spécifique
@pytest.fixture
def role_client(db_session, request):
    """
    Fixture générique pour créer un client authentifié avec un rôle spécifique.
    
    Usage:
        @pytest.mark.parametrize('role', ['padawan', 'maitre', 'gardien', 'archiviste'])
        def test_function(role_client):
            client = role_client(role)
            # Utiliser le client...
    
    Ou pour une fixture spécifique:
        @pytest.fixture
        def padawan_client(role_client):
            return role_client('padawan')
    """
    def _make_client(role):
        # Créer un utilisateur avec le rôle spécifié
        unique_id = uuid.uuid4().hex[:8]
        user_data = {
            "username": f"{role}_{unique_id}",
            "email": f"{role}_{unique_id}@jedi.com",
            "password": "Force123Jedi",
            "role": role
        }
        
        # Créer un client
        test_client = TestClient(app)
        
        try:
            # Enregistrer l'utilisateur
            print(f"Tentative d'enregistrement de l'utilisateur avec rôle: {role}")
            response = test_client.post("/api/users/", json=user_data)
            print(f"Statut de la réponse d'enregistrement: {response.status_code}")
            if response.status_code != 201:
                print(f"Réponse d'erreur d'enregistrement: {response.text}")
                pytest.skip(f"Impossible de créer l'utilisateur de test: {response.text}")
            
            # Authentification
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            print(f"Tentative d'authentification de l'utilisateur: {login_data['username']}")
            response = test_client.post("/api/auth/login", json=login_data)
            print(f"Statut de la réponse d'authentification: {response.status_code}")
            if response.status_code != 200:
                print(f"Réponse d'erreur d'authentification: {response.text}")
                print(f"Headers de réponse: {response.headers}")
                pytest.skip(f"Impossible d'authentifier l'utilisateur de test: {response.text}")
            
            # Extraire le token
            print("Extraction du token...")
            tokens = response.json()
            print(f"Contenu de la réponse: {tokens}")
            access_token = tokens["access_token"]
            
            # Configurer le client avec le token
            test_client.headers.update({"Authorization": f"Bearer {access_token}"})
            print("Client authentifié configuré avec succès")
            
            return {
                "client": test_client,
                "user_data": user_data,
                "token": access_token,
                "user_id": tokens.get("user_id"),
                "role": role
            }
        except Exception as e:
            import traceback
            print(f"Erreur complète: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            pytest.skip(f"Erreur pendant la configuration du client {role}: {str(e)}")
    
    # Si un rôle spécifique est demandé via paramètre de requête
    if hasattr(request, 'param'):
        return _make_client(request.param)
    
    # Sinon, retourner la fonction
    return _make_client

# Fixtures spécifiques pour chaque rôle, utilisant la fixture générique
@pytest.fixture
def padawan_client(role_client):
    """Crée un client authentifié avec un rôle PADAWAN."""
    return role_client('padawan')

@pytest.fixture
def maitre_client(role_client):
    """Crée un client authentifié avec un rôle MAITRE."""
    return role_client('maitre')

@pytest.fixture
def gardien_client(role_client):
    """Crée un client authentifié avec un rôle GARDIEN."""
    return role_client('gardien')

@pytest.fixture
def archiviste_client(role_client):
    """Crée un client authentifié avec un rôle ARCHIVISTE."""
    return role_client('archiviste')

@pytest.fixture
def mock_exercise():
    """
    Fixture pour générer un exercice de test personnalisable.
    
    Usage:
        def test_function(mock_exercise):
            # Exercice par défaut
            exercise = mock_exercise()
            
            # Exercice personnalisé
            custom_exercise = mock_exercise(
                title="Titre personnalisé",
                exercise_type="multiplication",
                difficulty="maitre",
                question="Combien font 7x8?",
                correct_answer="56",
                choices=["48", "56", "63", "64"]
            )
    """
    def _create_exercise(**kwargs):
        # Valeurs par défaut
        default_values = {
            "title": "Exercice de test",
            "exercise_type": "addition",
            "difficulty": "initie",
            "question": "Combien font 2+2?",
            "correct_answer": "4",
            "choices": ["3", "4", "5", "6"],
            "ai_generated": False,
            "is_active": True,
            "is_archived": False
        }
        
        # Combiner les valeurs par défaut avec les valeurs personnalisées
        exercise_data = {**default_values, **kwargs}
        
        return exercise_data
    
    return _create_exercise

@pytest.fixture
def mock_user():
    """
    Fixture pour créer des données d'utilisateur de test.
    
    Returns:
        Fonction pour créer des données d'utilisateur avec des paramètres personnalisables.
    """
    def _create_user(**kwargs):
        """Crée un dictionnaire avec des données d'utilisateur de test."""
        from app.utils.db_helpers import adapt_enum_for_db
        
        # Valeurs par défaut
        username = kwargs.get('username', unique_username())
        email = kwargs.get('email', unique_email())
        password = kwargs.get('password', 'TestPass123!')
        
        # Créer le dictionnaire de données utilisateur
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'full_name': kwargs.get('full_name', 'Utilisateur de Test'),
            'role': kwargs.get('role', 'padawan'),  # La valeur brute sera adaptée par adapted_dict_to_user
            'is_active': kwargs.get('is_active', True),
            'grade_level': kwargs.get('grade_level', 3),
            'learning_style': kwargs.get('learning_style', 'visuel'),
            'preferred_difficulty': kwargs.get('preferred_difficulty', 'initie'),
            'preferred_theme': kwargs.get('preferred_theme'),
            'accessibility_settings': kwargs.get('accessibility_settings')
        }
        
        return user_data
    
    return _create_user

@pytest.fixture
def mock_request():
    """
    Fixture pour créer une requête mock standardisée.
    
    Usage:
        def test_function(mock_request):
            # Requête par défaut
            request = mock_request()
            
            # Requête personnalisée avec utilisateur authentifié
            request_auth = mock_request(authenticated=True, role="maitre")
            
            # Requête avec données JSON spécifiques
            request_data = mock_request(json_data={"key": "value"})
            
            # Requête avec paramètres de chemin
            request_path = mock_request(path_params={"exercise_id": 42})
    """
    def _create_request(authenticated=False, role="padawan", json_data=None, path_params=None, query_params=None):
        from unittest.mock import MagicMock
        
        # Créer un mock de requête
        mock_req = MagicMock()
        
        # Configurer l'authentification
        if authenticated:
            unique_id = uuid.uuid4().hex[:8]
            mock_req.user = {
                "id": 1,
                "username": f"test_user_{unique_id}",
                "role": role,
                "is_authenticated": True
            }
        else:
            mock_req.user = {"is_authenticated": False}
        
        # Configurer les données JSON
        if json_data:
            mock_req.json.return_value = json_data
            # Ajouter model_dump_json() pour retourner les données JSON
            mock_req.model_dump_json.return_value = json_data
        
        # Configurer les paramètres de chemin
        mock_req.path_params = path_params or {}
        
        # Configurer les paramètres de requête
        mock_req.query_params = query_params or {}
        
        return mock_req
    
    return _create_request

@pytest.fixture
def mock_api_response():
    """
    Fixture pour simuler une réponse d'API.
    
    Usage:
        def test_function(mock_api_response):
            # Réponse réussie par défaut (200)
            response = mock_api_response()
            
            # Réponse avec statut et données personnalisés
            error_response = mock_api_response(
                status_code=404,
                data={"detail": "Ressource non trouvée"},
                headers={"X-Error-Code": "NOT_FOUND"}
            )
    """
    def _create_response(status_code=200, data=None, headers=None):
        from unittest.mock import MagicMock
        
        # Créer un mock de réponse
        mock_resp = MagicMock()
        
        # Configurer le statut, les données et les en-têtes
        mock_resp.status_code = status_code
        mock_resp.headers = headers or {}
        
        # Configurer les données JSON
        mock_resp.json.return_value = data or {}
        
        # Ajouter model_dump_json() pour retourner les données JSON
        mock_resp.model_dump_json.return_value = data or {}
        
        # Pour les réponses texte
        if isinstance(data, str):
            mock_resp.text = data
        else:
            import json
            mock_resp.text = json.dumps(data or {})
        
        return mock_resp
    
    return _create_response

# Fixtures pour gérer les valeurs d'enum PostgreSQL

@pytest.fixture
def db_enum_values(db_session):
    """
    Fournit les valeurs d'enum pour PostgreSQL.
    Cette fixture permet d'utiliser les valeurs correctes pour les tests.
    """
    from app.utils.db_helpers import get_all_enum_values
    return get_all_enum_values()

@pytest.fixture
def logic_challenge_data(db_session):
    """Données de test pour les défis logiques avec valeurs d'enum adaptées."""
    from app.models.logic_challenge import LogicChallengeType, AgeGroup
    from app.utils.db_helpers import get_enum_value
    
    return {
        "title": "Test Logic Challenge",
        "description": "Un défi logique pour les tests",
        "challenge_type": get_enum_value(LogicChallengeType, LogicChallengeType.SEQUENCE.value, db_session),
        "age_group": get_enum_value(AgeGroup, AgeGroup.GROUP_10_12.value, db_session),
        "correct_answer": "42",
        "solution_explanation": "La réponse est toujours 42",
        "hints": ["indice1", "indice2", "indice3"]  # Format JSON liste
    }

@pytest.fixture
def user_data(db_session):
    """
    Fournit des données pour créer un utilisateur avec les valeurs PostgreSQL correctes.
    """
    from app.models.user import UserRole
    from app.utils.db_helpers import get_enum_value
    import uuid
    
    # Générer un ID unique pour éviter les conflits
    unique_id = uuid.uuid4().hex[:8]
    
    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "hashed_password": "hashed_password",
        "role": get_enum_value(UserRole, UserRole.MAITRE.value, db_session)
    }

@pytest.fixture(scope="function")
def logic_challenge_db(db_session):
    """
    Utilise la session PostgreSQL existante pour les tests de défis logiques.
    Cette fixture réutilise la base PostgreSQL au lieu de créer une base SQLite.
    """
    from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt, LogicChallengeType, AgeGroup
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    from app.utils.db_helpers import get_enum_value
    from sqlalchemy import text
    import uuid
    
    # Générer un ID unique pour ce test
    unique_id = uuid.uuid4().hex[:8]
    
    # Nettoyer les données existantes pour ce test dans le bon ordre (FK d'abord)
    try:
        # Utiliser text() pour les requêtes SQL brutes
        db_session.execute(text("DELETE FROM logic_challenge_attempts"))
        db_session.execute(text("DELETE FROM attempts WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%')"))
        db_session.execute(text("DELETE FROM logic_challenges"))
        db_session.execute(text("DELETE FROM users WHERE username LIKE 'test_%'"))
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        # Si l'approche SQL directe échoue, utiliser SQLAlchemy avec cascade
        # D'abord supprimer les tentatives
        db_session.query(LogicChallengeAttempt).delete()
        
        # Ensuite supprimer les challenges
        db_session.query(LogicChallenge).delete()
        
        # Enfin supprimer les utilisateurs de test (leurs tentatives seront supprimées en cascade)
        test_users = db_session.query(User).filter(User.username.like("test_%")).all()
        for user in test_users:
            db_session.delete(user)  # Utilise la suppression en cascade
        
        db_session.commit()
    
    try:
        # Créer un utilisateur de test unique
        test_user = User(
            username=f"test_jedi_{unique_id}",
            email=f"test_{unique_id}@jedi.com",
            hashed_password=get_password_hash("testpassword"),
            role=get_enum_value(UserRole, UserRole.GARDIEN)
        )
        db_session.add(test_user)
        db_session.commit()
        
        # Créer un défi logique de test
        test_challenge = LogicChallenge(
            title=f"Test Challenge {unique_id}",
            description="Description du défi de test",
            challenge_type=get_enum_value(LogicChallengeType, LogicChallengeType.SEQUENCE),
            age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_10_12),
            correct_answer="42",
            solution_explanation="La réponse est 42",
            hints='["Indice 1: C\'est un nombre", "Indice 2: C\'est un nombre entre 40 et 50", "Indice 3: C\'est la réponse à la question ultime"]',
            creator_id=test_user.id,
            difficulty_rating=3.0,
            estimated_time_minutes=15
        )
        db_session.add(test_challenge)
        db_session.commit()
        
        yield db_session
        
    finally:
        # Nettoyer après le test dans le bon ordre
        try:
            # Utiliser text() pour les requêtes SQL brutes
            db_session.execute(text("DELETE FROM logic_challenge_attempts"))
            db_session.execute(text(f"DELETE FROM logic_challenges WHERE title LIKE 'Test Challenge {unique_id}%'"))
            db_session.execute(text(f"DELETE FROM users WHERE username = 'test_jedi_{unique_id}'"))
            db_session.commit()
        except Exception:
            db_session.rollback()
            # Fallback avec SQLAlchemy et suppression en cascade
            db_session.query(LogicChallengeAttempt).delete()
            db_session.query(LogicChallenge).filter(LogicChallenge.title.like(f"Test Challenge {unique_id}%")).delete()
            test_user = db_session.query(User).filter(User.username == f"test_jedi_{unique_id}").first()
            if test_user:
                db_session.delete(test_user)  # Suppression en cascade des relations
            db_session.commit()

from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.utils.db_helpers import (
    get_enum_value, 
    adapt_enum_for_db
)
