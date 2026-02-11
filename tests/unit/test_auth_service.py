"""
Tests unitaires pour le service d'authentification (auth_service.py).
Ces tests vérifient le bon fonctionnement des fonctions liées à l'authentification.
"""
import pytest
from datetime import datetime, timedelta, timezone
from starlette.exceptions import HTTPException
from unittest.mock import patch, MagicMock
from jose import jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid


from app.services.auth_service import (
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    authenticate_user,
    create_user,
    create_user_token,
    refresh_access_token,
    update_user
)
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.config import settings
from tests.utils.test_helpers import unique_username, unique_email, dict_to_user, adapted_dict_to_user
from app.utils.db_helpers import get_enum_value, adapt_enum_for_db

# Fonction utilitaire pour convertir un dictionnaire en User
def dict_to_user(user_data):
    """Convertit les données de dictionnaire en objet User."""
    # S'assurer que le rôle est adapté pour PostgreSQL
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.config import settings
    
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as session:
        # Adapter le rôle pour PostgreSQL
        role = user_data.get("role")
        if role:
            if hasattr(role, "value"):
                role = role.value
            role = adapt_enum_for_db("UserRole", role, session)
    
        # Convertir les structures de données complexes en JSON si nécessaire
        accessibility_settings = user_data.get("accessibility_settings")
        
        # Adapter les autres valeurs enum si présentes
        preferred_difficulty = user_data.get("preferred_difficulty")
        if preferred_difficulty:
            preferred_difficulty = adapt_enum_for_db("DifficultyLevel", preferred_difficulty, session)
        
        # Créer et retourner l'utilisateur
        return User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=user_data.get("hashed_password", get_password_hash(user_data["password"])),
            full_name=user_data.get("full_name"),
            role=role,
            is_active=user_data.get("is_active", True),
            grade_level=user_data.get("grade_level"),
            learning_style=user_data.get("learning_style"),
            preferred_difficulty=preferred_difficulty,
            preferred_theme=user_data.get("preferred_theme"),
            accessibility_settings=accessibility_settings
        )

# Tests pour get_user_by_username
def test_get_user_by_username_existing(db_session, mock_user):
    """Teste la récupération d'un utilisateur existant par son nom d'utilisateur."""
    # Créer un utilisateur de test
    username = unique_username()
    user_data = mock_user(username=username)
    
    # Adapter le rôle pour PostgreSQL avant de créer l'utilisateur
    adapted_role = adapt_enum_for_db("UserRole", user_data.get("role", "padawan"), db_session)
    
    # Créer l'utilisateur directement en utilisant le rôle adapté
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data.get("hashed_password", get_password_hash(user_data["password"])),
        full_name=user_data.get("full_name"),
        role=adapted_role,
        is_active=user_data.get("is_active", True),
        grade_level=user_data.get("grade_level"),
        learning_style=user_data.get("learning_style"),
        preferred_difficulty=user_data.get("preferred_difficulty"),
        preferred_theme=user_data.get("preferred_theme")
    )
    
    db_session.add(user)
    db_session.commit()
    
    # Récupérer l'utilisateur par son nom
    result = get_user_by_username(db_session, username)
    
    # Vérifier le résultat
    assert result is not None
    assert result.username == username
    assert result.id == user.id

def test_get_user_by_username_nonexistent(db_session):
    """Teste la récupération d'un utilisateur non existant par son nom d'utilisateur."""
    # Récupérer un utilisateur qui n'existe pas
    result = get_user_by_username(db_session, "nonexistent_user")
    
    # Vérifier que le résultat est None
    assert result is None

# Tests pour get_user_by_email
def test_get_user_by_email_existing(db_session, mock_user):
    """Teste la récupération d'un utilisateur existant par son email."""
    # Créer un utilisateur de test avec un email unique
    email = unique_email()
    user_data = mock_user(email=email)
    
    # Adapter le rôle pour PostgreSQL
    adapted_role = adapt_enum_for_db("UserRole", user_data.get("role", "padawan"), db_session)
    
    # Créer l'utilisateur avec le rôle adapté
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data.get("hashed_password", get_password_hash(user_data["password"])),
        full_name=user_data.get("full_name"),
        role=adapted_role,
        is_active=user_data.get("is_active", True),
        grade_level=user_data.get("grade_level"),
        learning_style=user_data.get("learning_style"),
        preferred_difficulty=user_data.get("preferred_difficulty"),
        preferred_theme=user_data.get("preferred_theme")
    )
    
    db_session.add(user)
    db_session.commit()
    
    # Récupérer l'utilisateur par son email
    result = get_user_by_email(db_session, email)
    
    # Vérifier le résultat
    assert result is not None
    assert result.email == email
    assert result.id == user.id

def test_get_user_by_email_nonexistent(db_session):
    """Teste la récupération d'un utilisateur non existant par son email."""
    # Récupérer un utilisateur qui n'existe pas
    result = get_user_by_email(db_session, "nonexistent@example.com")
    
    # Vérifier que le résultat est None
    assert result is None

# Tests pour get_user_by_id
def test_get_user_by_id_existing(db_session, mock_user):
    """Teste la récupération d'un utilisateur existant par son ID."""
    # Créer un utilisateur de test
    user_data = mock_user()
    
    # Adapter le rôle pour PostgreSQL
    adapted_role = adapt_enum_for_db("UserRole", user_data.get("role", "padawan"), db_session)
    
    # Créer l'utilisateur avec le rôle adapté
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data.get("hashed_password", get_password_hash(user_data["password"])),
        full_name=user_data.get("full_name"),
        role=adapted_role,
        is_active=user_data.get("is_active", True),
        grade_level=user_data.get("grade_level"),
        learning_style=user_data.get("learning_style"),
        preferred_difficulty=user_data.get("preferred_difficulty"),
        preferred_theme=user_data.get("preferred_theme")
    )
    
    db_session.add(user)
    db_session.commit()
    
    # Récupérer l'utilisateur par son ID
    result = get_user_by_id(db_session, user.id)
    
    # Vérifier le résultat
    assert result is not None
    assert result.id == user.id

def test_get_user_by_id_nonexistent(db_session):
    """Teste la récupération d'un utilisateur non existant par son ID."""
    # Récupérer un utilisateur qui n'existe pas
    result = get_user_by_id(db_session, 9999)
    
    # Vérifier que le résultat est None
    assert result is None

# Tests pour authenticate_user
def test_authenticate_user_success(db_session, mock_user):
    """Teste l'authentification d'un utilisateur avec des identifiants valides."""
    # Créer un utilisateur de test
    user_data = mock_user()
    clear_password = user_data["password"]
    
    # Adapter le rôle pour PostgreSQL
    adapted_role = adapt_enum_for_db("UserRole", user_data.get("role", "padawan"), db_session)
    
    # Créer l'utilisateur avec le rôle adapté
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data.get("hashed_password", get_password_hash(user_data["password"])),
        full_name=user_data.get("full_name"),
        role=adapted_role,
        is_active=user_data.get("is_active", True),
        grade_level=user_data.get("grade_level"),
        learning_style=user_data.get("learning_style"),
        preferred_difficulty=user_data.get("preferred_difficulty"),
        preferred_theme=user_data.get("preferred_theme")
    )
    
    db_session.add(user)
    db_session.commit()
    
    # Authentifier l'utilisateur
    result = authenticate_user(db_session, user.username, clear_password)
    
    # Vérifier le résultat
    assert result is not None
    assert result.id == user.id
    assert result.username == user.username

def test_authenticate_user_invalid_password(db_session, mock_user):
    """Teste l'authentification d'un utilisateur avec un mot de passe invalide."""
    # Créer un utilisateur de test
    user_data = mock_user()
    hashed_password = get_password_hash("CorrectPassword123")
    
    # Adapter le rôle pour PostgreSQL
    adapted_role = adapt_enum_for_db("UserRole", user_data.get("role", "padawan"), db_session)
    
    # Créer l'utilisateur avec le rôle adapté
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hashed_password,
        full_name=user_data.get("full_name"),
        role=adapted_role,
        is_active=user_data.get("is_active", True),
        grade_level=user_data.get("grade_level"),
        learning_style=user_data.get("learning_style"),
        preferred_difficulty=user_data.get("preferred_difficulty"),
        preferred_theme=user_data.get("preferred_theme")
    )
    
    db_session.add(user)
    db_session.commit()
    
    # Tenter d'authentifier l'utilisateur avec un mauvais mot de passe
    result = authenticate_user(db_session, user.username, "WrongPassword123")
    
    # Vérifier que l'authentification a échoué
    assert result is None

def test_authenticate_user_nonexistent(db_session):
    """Teste l'authentification d'un utilisateur qui n'existe pas."""
    # Tenter d'authentifier un utilisateur qui n'existe pas
    result = authenticate_user(db_session, "nonexistent_user", "AnyPassword123")
    
    # Vérifier que l'authentification échoue
    assert result is None

def test_authenticate_user_exception_during_verification(db_session, mock_user):
    """Teste la gestion des exceptions dans authenticate_user lors de la vérification."""
    # Créer un utilisateur de test
    user_data = mock_user()
    
    # Créer l'utilisateur avec le rôle adapté
    user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(user)
    db_session.commit()
    
    # Simuler une exception pendant la vérification du mot de passe
    with patch('app.services.auth_service.verify_password') as mock_verify:
        mock_verify.side_effect = Exception("Test exception")
        
        # Tenter d'authentifier l'utilisateur
        result = authenticate_user(db_session, user.username, "AnyPassword123")
        
        # Vérifier que l'authentification échoue proprement
        assert result is None
        
        # Vérifier que verify_password a été appelé
        mock_verify.assert_called_once()

# Tests pour create_user
def test_create_user_success(db_session):
    """Teste la création d'un nouvel utilisateur."""
    # Créer les données utilisateur
    username = unique_username()
    email = unique_email()
    
    user_data = UserCreate(
        username=username,
        email=email,
        password="TestPassword123",
        role="padawan"
    )
    
    # Créer l'utilisateur
    created_user = create_user(db_session, user_data)
    
    # Vérifier que l'utilisateur a été créé correctement
    assert created_user is not None
    assert created_user.username == username
    assert created_user.email == email
    
    # Vérifier que le rôle a été correctement adapté pour PostgreSQL
    # Le service retourne un objet User avec l'enum Python, pas la valeur PostgreSQL
    assert created_user.role == UserRole.PADAWAN, f"Expected role {UserRole.PADAWAN}, got {created_user.role}"
    
    # Vérifier que le mot de passe a été haché
    assert created_user.hashed_password != "TestPassword123"
    assert verify_password("TestPassword123", created_user.hashed_password)

def test_create_user_duplicate_username(db_session, mock_user):
    """Teste la création d'un utilisateur avec un nom d'utilisateur déjà utilisé."""
    # Créer un utilisateur existant avec un nom unique
    username = unique_username()
    user_data = mock_user(username=username, email=unique_email())
    
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    existing_user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(existing_user)
    db_session.commit()
    
    # Tenter de créer un nouvel utilisateur avec le même nom d'utilisateur
    new_user_data = UserCreate(
        username=username,  # Même nom d'utilisateur
        email=unique_email(),  # Email différent
        password="AnotherPassword123",
        role="padawan"
    )
    
    # Vérifier que la création échoue avec une erreur HTTP 409 (CONFLICT)
    with pytest.raises(HTTPException) as excinfo:
        create_user(db_session, new_user_data)
    
    # Vérifier l'erreur
    assert excinfo.value.status_code == 409  # ✅ 409 CONFLICT au lieu de 400
    assert "Ce nom d'utilisateur est déjà utilisé" in str(excinfo.value.detail)

def test_create_user_duplicate_email(db_session, mock_user):
    """Teste la création d'un utilisateur avec un email déjà utilisé."""
    # Créer un utilisateur existant avec un email unique
    email = unique_email()
    user_data = mock_user(username=unique_username(), email=email)
    
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    existing_user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(existing_user)
    db_session.commit()
    
    # Tenter de créer un nouvel utilisateur avec le même email
    new_user_data = UserCreate(
        username=unique_username(),  # Nom d'utilisateur différent
        email=email,  # Même email
        password="AnotherPassword123",
        role="padawan"
    )
    
    # Vérifier que la création échoue avec une erreur HTTP 409 (CONFLICT)
    with pytest.raises(HTTPException) as excinfo:
        create_user(db_session, new_user_data)
    
    # Vérifier l'erreur
    assert excinfo.value.status_code == 409  # ✅ 409 CONFLICT au lieu de 400
    assert "Cet email est déjà utilisé" in str(excinfo.value.detail)

# Tests pour create_user_token
def test_create_user_token(mock_user):
    """Teste la création des tokens pour un utilisateur."""
    # Créer un utilisateur pour le test
    user_data = mock_user(role="maitre")
    
    # Convertir en instance de User
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data.get("hashed_password", get_password_hash(user_data["password"])),
        full_name=user_data.get("full_name"),
        role=user_data.get("role", "padawan"),
        is_active=user_data.get("is_active", True),
        grade_level=user_data.get("grade_level"),
        learning_style=user_data.get("learning_style"),
        preferred_difficulty=user_data.get("preferred_difficulty")
    )
    
    # Créer les tokens
    tokens = create_user_token(user)
    
    # Vérifier la structure de la réponse
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert "token_type" in tokens
    assert tokens["token_type"] == "bearer"
    
    # Vérifier le contenu du token d'accès
    access_payload = jwt.decode(
        tokens["access_token"], 
        settings.SECRET_KEY, 
        algorithms=["HS256"]
    )
    assert access_payload["sub"] == user.username
    # Comparer avec la valeur string du rôle, pas l'objet enum
    assert access_payload["role"] == user.role if isinstance(user.role, str) else user.role.value
    assert access_payload["type"] == "access"
    
    # Vérifier le contenu du refresh token
    refresh_payload = jwt.decode(
        tokens["refresh_token"], 
        settings.SECRET_KEY, 
        algorithms=["HS256"]
    )
    assert refresh_payload["sub"] == user.username
    # Comparer avec la valeur string du rôle, pas l'objet enum
    assert refresh_payload["role"] == user.role if isinstance(user.role, str) else user.role.value
    assert refresh_payload["type"] == "refresh"

# Tests pour refresh_access_token
def test_refresh_access_token_valid(db_session, mock_user):
    """Teste le rafraîchissement d'un token avec un refresh token valide."""
    # Créer un utilisateur pour le test
    user_data = mock_user()
    
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(user)
    db_session.commit()
    
    # Créer un refresh token valide
    refresh_token_expires = timedelta(days=1)
    # Utiliser la valeur string du rôle pour la sérialisation JWT
    role_value = user.role if isinstance(user.role, str) else user.role.value
    refresh_token_data = {"role": role_value, "type": "refresh"}
    
    refresh_token = jwt.encode(
        {
            "sub": user.username,
            "exp": datetime.now() + refresh_token_expires,
            **refresh_token_data
        },
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    # Rafraîchir le token
    result = refresh_access_token(db_session, refresh_token)
    
    # Vérifier la structure de la réponse
    assert "access_token" in result
    assert "token_type" in result
    assert result["token_type"] == "bearer"
    
    # Vérifier le contenu du nouveau token
    new_payload = jwt.decode(
        result["access_token"], 
        settings.SECRET_KEY, 
        algorithms=["HS256"]
    )
    assert new_payload["sub"] == user.username
    # Comparer avec la valeur string du rôle
    assert new_payload["role"] == role_value
    assert new_payload["type"] == "access"

def test_refresh_access_token_invalid_token(db_session):
    """Teste le rafraîchissement avec un token invalide."""
    # Tenter de rafraîchir avec un token invalide
    with pytest.raises(HTTPException) as exc_info:
        refresh_access_token(db_session, "invalid_token")
    
    # Vérifier les détails de l'exception
    assert exc_info.value.status_code == 401
    assert "Token JWT invalide" in exc_info.value.detail or "Token invalide" in exc_info.value.detail or "Token invalid" in exc_info.value.detail

def test_refresh_access_token_wrong_type(db_session, mock_user):
    """Teste le rafraîchissement avec un token qui n'est pas un refresh token."""
    # Créer un utilisateur pour le test
    user_data = mock_user()
    
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(user)
    db_session.commit()
    
    # Créer un token d'accès (pas un refresh token)
    token_expires = timedelta(minutes=15)
    # Utiliser la valeur string du rôle pour la sérialisation JWT
    role_value = user.role if isinstance(user.role, str) else user.role.value
    token_data = {"role": role_value, "type": "access"}  # Type incorrect
    
    access_token = jwt.encode(
        {
            "sub": user.username,
            "exp": datetime.now() + token_expires,
            **token_data
        },
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    # Tenter de rafraîchir avec un token du mauvais type
    with pytest.raises(HTTPException) as exc_info:
        refresh_access_token(db_session, access_token)
    
    # ✅ CORRECTION : Vérifier les détails de l'exception (401 UNAUTHORIZED)
    assert exc_info.value.status_code == 401  # ✅ 401 UNAUTHORIZED au lieu de 500
    assert "Token de rafraîchissement invalide" in exc_info.value.detail

def test_refresh_access_token_user_not_found(db_session):
    """
    Teste la génération d'un nouveau token d'accès quand l'utilisateur n'existe pas.
    """
    # Token avec un sujet qui n'existe pas
    token_data = {
        "sub": "nonexistent_user",
        "role": "padawan",
        "type": "refresh",
        "exp": datetime.now() + timedelta(days=30)
    }
    
    # Encoder le token avec la clé secrète
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")
    
    # ✅ CORRECTION : Vérifier que le rafraîchissement échoue avec une erreur HTTP 401 (UNAUTHORIZED)
    with pytest.raises(HTTPException) as excinfo:
        refresh_access_token(db_session, token)
    
    # Vérifier l'erreur
    assert excinfo.value.status_code == 401  # ✅ 401 UNAUTHORIZED au lieu de 500
    assert "Utilisateur non trouvé" in excinfo.value.detail

def test_refresh_access_token_expired_token(db_session, mock_user):
    """Teste le rafraîchissement d'un token expiré."""
    # Créer un utilisateur de test
    user_data = mock_user()
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(user)
    db_session.commit()
    
    # Créer un token expiré (date d'expiration déjà passée)
    # Utiliser la valeur string du rôle pour la sérialisation JWT
    role_value = user.role if isinstance(user.role, str) else user.role.value
    expired_token_data = {
        "sub": user.username,
        "role": role_value,
        "type": "refresh",
        "exp": datetime.timestamp(datetime.now() - timedelta(days=1))  # Token déjà expiré
    }
    
    # Signer le token expiré avec la clé secrète
    expired_token = jwt.encode(expired_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Tenter de rafraîchir le token expiré
    with pytest.raises(HTTPException) as excinfo:
        refresh_access_token(db_session, expired_token)
    
    # Vérifier que l'exception levée est bien celle attendue (401 Unauthorized)
    assert excinfo.value.status_code == 401
    assert "Token JWT invalide ou malformé" in excinfo.value.detail


def test_refresh_access_token_tampered_token(db_session, mock_user):
    """Teste le rafraîchissement d'un token falsifié."""
    # Créer un utilisateur de test
    user_data = mock_user()
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(user)
    db_session.commit()
    
    # Créer un token valide puis le modifier
    # Utiliser la valeur string du rôle pour la sérialisation JWT
    role_value = user.role if isinstance(user.role, str) else user.role.value
    valid_token_data = {
        "sub": user.username,
        "role": role_value,
        "type": "refresh",
        "exp": datetime.timestamp(datetime.now() + timedelta(days=1))
    }
    
    # Signer le token valide avec la clé secrète
    valid_token = jwt.encode(valid_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Falsifier le token en le modifiant (ajouter des caractères)
    tampered_token = valid_token + "abc"
    
    # Tenter de rafraîchir le token falsifié
    with pytest.raises(HTTPException) as excinfo:
        refresh_access_token(db_session, tampered_token)
    
    # Vérifier que l'exception levée est bien celle attendue
    assert excinfo.value.status_code == 401
    assert "Token JWT invalide ou malformé" in excinfo.value.detail


def test_refresh_access_token_valid_token_but_deleted_user(db_session, mock_user):
    """Teste le rafraîchissement d'un token valide pour un utilisateur qui a été supprimé."""
    # Créer un utilisateur de test
    user_data = mock_user()
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(user)
    db_session.commit()
    
    # ✅ CORRECTION : Créer un vrai refresh token manuellement
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    # Utiliser la valeur string du rôle pour la sérialisation JWT
    role_value = user.role if isinstance(user.role, str) else user.role.value
    
    # Créer un refresh token manuellement avec jwt.encode
    valid_token = jwt.encode(
        {
            "sub": user.username,
            "role": role_value,
            "type": "refresh",  # ✅ IMPORTANT : Type refresh
            "exp": datetime.now(timezone.utc) + refresh_token_expires
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    # Supprimer l'utilisateur de la base de données
    db_session.delete(user)
    db_session.commit()
    
    # Tenter de rafraîchir le token (pour un utilisateur qui n'existe plus)
    with pytest.raises(HTTPException) as excinfo:
        refresh_access_token(db_session, valid_token)
    
    # ✅ CORRECTION : Vérifier que l'exception levée correspond à 401 UNAUTHORIZED
    assert excinfo.value.status_code == 401  # ✅ 401 UNAUTHORIZED au lieu de 500
    assert "Utilisateur non trouvé" in excinfo.value.detail


def test_create_user_with_full_profile_data(db_session):
    """Teste la création d'un utilisateur avec toutes les données de profil optionnelles."""
    # Créer un utilisateur complet avec toutes les données optionnelles
    user_data = UserCreate(
        username=unique_username(),
        email=unique_email(),
        password="ComplexPassw0rd!",
        full_name="Test Complete User",
        role=UserRole.PADAWAN,  # Utiliser l'enum Python directement
        grade_level=5,
        learning_style="visuel",
        preferred_difficulty="INITIE",
        preferred_theme="dark",
        accessibility_settings={"high_contrast": True, "large_text": True}
    )
    
    # Créer l'utilisateur via le service
    user = create_user(db_session, user_data)
    
    # Vérifications
    assert user is not None
    assert user.id is not None
    assert user.username == user_data.username
    assert user.email == user_data.email
    assert user.full_name == user_data.full_name
    # Vérifier que le rôle a été correctement stocké (enum Python)
    assert user.role == UserRole.PADAWAN
    assert user.grade_level == 5
    assert user.learning_style == "visuel"
    assert user.preferred_difficulty == "INITIE"
    assert user.preferred_theme == "dark"
    assert user.accessibility_settings == {"high_contrast": True, "large_text": True}
    assert user.is_active is True


def test_update_user_without_password_change(db_session, mock_user):
    """Teste la mise à jour d'un utilisateur sans changer le mot de passe."""
    # Créer un utilisateur de test
    user_data = mock_user()
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(user)
    db_session.commit()
    
    # Données de mise à jour sans mot de passe
    update_data = UserUpdate(
        full_name="Updated Name",
        email=unique_email(),
        preferred_theme="dark",
        accessibility_settings={"high_contrast": True}
    )
    
    # Sauvegarder le mot de passe actuel pour vérification
    original_password = user.hashed_password
    
    # Mettre à jour l'utilisateur
    updated_user = update_user(db_session, user, update_data)
    
    # Vérifications
    assert updated_user is not None
    assert updated_user.id == user.id
    assert updated_user.full_name == "Updated Name"
    assert updated_user.email == update_data.email
    assert updated_user.preferred_theme == "dark"
    assert updated_user.accessibility_settings == {"high_contrast": True}
    # Vérifier que le mot de passe n'a pas changé
    assert updated_user.hashed_password == original_password

# Tests pour update_user
def test_update_user_success(db_session, mock_user):
    """Teste la mise à jour des informations d'un utilisateur."""
    # Créer un utilisateur pour le test
    user_data = mock_user()
    
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(user)
    db_session.commit()
    
    # Données pour la mise à jour
    update_data = UserUpdate(
        full_name="Nouveau Nom Complet",
        grade_level=10,
        learning_style="visuel",
        preferred_difficulty="chevalier",
        preferred_theme="dark"
    )
    
    # Mettre à jour l'utilisateur
    result = update_user(db_session, user, update_data)
    
    # Vérifier les modifications
    assert result.id == user.id
    assert result.full_name == update_data.full_name
    assert result.grade_level == update_data.grade_level
    assert result.learning_style == update_data.learning_style
    # Selon l'implémentation, la difficulté peut rester en minuscules
    assert result.preferred_difficulty == "chevalier"
    assert result.preferred_theme == update_data.preferred_theme
    
    # Vérifier que les données qui ne devaient pas changer n'ont pas changé
    assert result.username == user.username
    assert result.email == user.email
    assert result.role == user.role

def test_update_user_password(db_session, mock_user):
    """Teste la mise à jour du mot de passe d'un utilisateur."""
    # Créer un utilisateur pour le test
    original_password = "OriginalPassword123"
    hashed_password = get_password_hash(original_password)
    user_data = mock_user(password=original_password)
    
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    user = adapted_dict_to_user(user_data, db_session)
    user.hashed_password = hashed_password  # S'assurer que le mot de passe est bien défini
    
    db_session.add(user)
    db_session.commit()
    
    # Nouveau mot de passe
    new_password = "NewPassword456"
    
    # Données pour la mise à jour (uniquement le mot de passe)
    update_data = UserUpdate(
        password=new_password
    )
    
    # Mettre à jour l'utilisateur
    result = update_user(db_session, user, update_data)
    
    # Vérifier que le mot de passe a été modifié
    assert authenticate_user(db_session, user.username, original_password) is None
    assert authenticate_user(db_session, user.username, new_password) is not None

def test_refresh_access_token_generic_exception(db_session, mock_user):
    """Teste la gestion d'une exception générique dans refresh_access_token."""
    # Créer un utilisateur de test
    user_data = mock_user()
    # Utiliser la fonction qui adapte les valeurs d'enum pour PostgreSQL
    user = adapted_dict_to_user(user_data, db_session)
    
    db_session.add(user)
    db_session.commit()
    
    # Créer un token valide pour cet utilisateur
    access_token_expires = timedelta(minutes=30)
    # Utiliser la valeur string du rôle pour la sérialisation JWT
    role_value = user.role if isinstance(user.role, str) else user.role.value
    refresh_token = jwt.encode(
        {
            "sub": user.username, 
            "role": role_value,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + access_token_expires
        },
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    # Mocker jwt.decode pour qu'il lève une exception générique
    with patch('app.services.auth_service.jwt.decode', side_effect=Exception("Test unexpected error")):
        # Vérifier que refresh_access_token lève HTTPException 500 pour les exceptions génériques
        with pytest.raises(HTTPException) as excinfo:
            refresh_access_token(db_session, refresh_token)
        
        # Vérifier les détails de l'exception (500 Erreur interne du serveur)
        assert excinfo.value.status_code == 500
        assert "Erreur interne du serveur" in excinfo.value.detail
