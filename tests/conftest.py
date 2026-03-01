"""
Configuration centralisee pour pytest.
Migre de FastAPI TestClient vers httpx.AsyncClient (Starlette).

Architecture:
- Section 1: Securite (protection base de prod)
- Section 2: Database engine & session
- Section 3: HTTP client fixtures (httpx + Starlette)
- Section 4: Mock fixtures (donnees en memoire)
- Section 5: Enum & model fixtures
- Section 6: Logic challenge DB fixture
- Section 7: Auto cleanup
"""

# === IMPORTANT: Definir TESTING=true AVANT tout import applicatif ===
import os
import re as _re

os.environ["TESTING"] = "true"

# Charger .env AVANT tout import applicatif pour deriver TEST_DATABASE_URL
# Optionnel : si python-dotenv absent (env minimal), les variables doivent être déjà définies (CI)
try:
    from dotenv import load_dotenv as _load_dotenv

    # Ignorer .env en prod ; en dev/CI : override=False pour ne pas écraser les vars injectées
    if os.environ.get("ENVIRONMENT") != "production":
        _load_dotenv(override=False)
except ImportError:
    pass  # TEST_DATABASE_URL / DATABASE_URL déjà définis (p.ex. CI)

# Si TEST_DATABASE_URL n'est pas defini explicitement (CI le definit),
# tenter de le deriver de DATABASE_URL si la base est une base de test.
if not os.environ.get("TEST_DATABASE_URL"):
    _db_url = os.environ.get("DATABASE_URL", "")
    if _db_url:
        _db_name_match = _re.search(r"/([^/?]+)(?:\?|$)", _db_url)
        if _db_name_match:
            _db_name = _db_name_match.group(1)
            if "test" in _db_name.lower():
                os.environ["TEST_DATABASE_URL"] = _db_url
                print(f"  TEST_DATABASE_URL derive de DATABASE_URL (base: {_db_name})")
            else:
                print(
                    f"  ATTENTION: DATABASE_URL pointe vers '{_db_name}' (pas une base test)"
                )
                print(
                    "  Les tests utiliseront postgresql://postgres:postgres@localhost/test_mathakine par defaut"
                )

import json
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from jose import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Ajouter le repertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# App imports (apres TESTING=true)
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.db.base import Base, engine
from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.user import User, UserRole
from app.utils.db_helpers import (
    adapt_enum_for_db,
    get_all_enum_values,
    get_enum_value,
)

# Application Starlette
from enhanced_server import app as starlette_app

# Test utilities
from tests.utils.test_data_cleanup import TestDataManager
from tests.utils.test_helpers import (
    unique_email,
    unique_username,
    verify_user_email_for_tests,
)

# ================================================================
# SECTION 1: SECURITE - Protection de la base de production
# ================================================================


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configure l'environnement de test automatiquement.

    SECURITE : Verifie que les tests ne tournent JAMAIS sur la base de production.
    Verifie aussi l'engine SQLAlchemy deja cree (initialise a l'import).
    """
    import re

    Path("test_results").mkdir(exist_ok=True)
    os.environ["TESTING"] = "true"

    # SECURITE 1 : Verifier l'engine SQLAlchemy importe
    from app.db.base import engine as imported_engine

    engine_url = str(imported_engine.url)

    engine_db_match = re.search(r"/([^/?]+)(?:\?|$)", engine_url)
    if engine_db_match:
        engine_db_name = engine_db_match.group(1)
        if "test" not in engine_db_name.lower():
            environment = os.environ.get("ENVIRONMENT", "")
            if environment == "production" or "render" in engine_url.lower():
                raise RuntimeError(
                    f"SECURITE: L'engine SQLAlchemy pointe vers la base de PRODUCTION ({engine_db_name})!\n"
                    f"   URL: {engine_url}\n"
                    f"   Les tests NE DOIVENT JAMAIS tourner sur la base de production.\n"
                    f"   Solution: Definir TEST_DATABASE_URL=postgresql://postgres:postgres@localhost/test_mathakine"
                )
            else:
                print(
                    f"\n  ATTENTION: Les tests tournent sur la base '{engine_db_name}' (pas de base de test separee)"
                )
                print(
                    "   Les operations destructrices sont filtrees sur les donnees test_ uniquement.\n"
                )

    # SECURITE 2 : Definir TEST_DATABASE_URL par defaut
    if "TEST_DATABASE_URL" not in os.environ:
        default_test_db = "postgresql://postgres:postgres@localhost/test_mathakine"
        os.environ["TEST_DATABASE_URL"] = default_test_db
        print(
            f"  TEST_DATABASE_URL non defini, utilisation par defaut: {default_test_db}"
        )

    # SECURITE 3 : Verifier TEST_DATABASE_URL != DATABASE_URL en production
    test_db_url = os.environ.get("TEST_DATABASE_URL", "")
    prod_db_url = os.environ.get("DATABASE_URL", "")

    if test_db_url and prod_db_url and test_db_url == prod_db_url:
        # Extraire le nom de la base (derniere partie du path, apres le dernier /)
        test_db_match = re.search(r"/([^/?]+)(?:\?|$)", test_db_url)
        prod_db_match = re.search(r"/([^/?]+)(?:\?|$)", prod_db_url)
        if test_db_match and prod_db_match:
            test_db_name = test_db_match.group(1)
            prod_db_name = prod_db_match.group(1)
            if test_db_name == prod_db_name and "test" not in test_db_name.lower():
                raise RuntimeError(
                    f"SECURITE: TEST_DATABASE_URL pointe vers la meme base que DATABASE_URL ({test_db_name})!\n"
                    f"   Cela pourrait supprimer les donnees de production!\n"
                    f"   Solution: Definir TEST_DATABASE_URL vers une base de test separee."
                )

    yield


# ================================================================
# SECTION 2: DATABASE ENGINE & SESSION
# ================================================================
#
# INDUSTRIALISATION: Un seul engine pour fixtures ET handlers (app.db.base.engine).
# Évite les bugs d'isolation (random_offset, filtres) et garantit cohérence.
# Réf: DIAGNOSTIC_CHALLENGES_LIST_2026-02.md
# ================================================================

_test_engine = None


def get_test_engine():
    """Engine de test — DEPRECATED pour db_session. Utiliser _get_session_engine().
    Conservé pour compatibilité (cleanup fallback, scripts)."""
    global _test_engine
    if _test_engine is None:
        test_db_url = settings.SQLALCHEMY_DATABASE_URL
        if not test_db_url or test_db_url == settings.DATABASE_URL:
            if "test" not in (test_db_url or "").lower() and "localhost" not in (test_db_url or ""):
                raise RuntimeError(
                    f"SECURITE: Tentative d'utiliser la base de production dans les tests!\n"
                    f"   Assurez-vous que TEST_DATABASE_URL est defini."
                )
        _test_engine = create_engine(
            test_db_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            echo=False,
        )
    return _test_engine


def _get_session_engine():
    """Engine pour les tests. Utilise app.db.base pour unifier avec les handlers (évite FK/visibilité)."""
    from app.db.base import engine

    return engine


@pytest.fixture
def db_session():
    """Session DB avec rollback automatique et isolation complete."""
    session_engine = _get_session_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=session_engine)
    session = SessionLocal()

    try:
        yield session
    except Exception:
        try:
            session.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            if session.is_active:
                session.rollback()
        except Exception:
            pass
        finally:
            try:
                session.close()
            except Exception:
                pass


# ================================================================
# SECTION 3: HTTP CLIENT FIXTURES (httpx.AsyncClient + Starlette)
# ================================================================


@asynccontextmanager
async def _create_authenticated_client(role="padawan", db_session_for_role=None):
    """Helper interne: cree un client httpx authentifie avec un role donne.

    - Cree un utilisateur via l'API
    - Met a jour le role en DB si necessaire
    - Login pour obtenir le cookie access_token
    - Yield le client configure + metadata
    """
    transport = httpx.ASGITransport(app=starlette_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_id = uuid.uuid4().hex[:8]
        user_data = {
            "username": f"test_{role}_{unique_id}",
            "email": f"{role}_{unique_id}@test.com",
            "password": "Force123Jedi",
        }

        # Creer l'utilisateur via l'API (role PADAWAN par defaut)
        response = await ac.post("/api/users/", json=user_data)
        if response.status_code not in (200, 201):
            pytest.skip(f"Cannot create {role} user: {response.text}")

        # Marquer email verifie pour permettre le login (obligatoire en production)
        verify_user_email_for_tests(user_data["username"])

        # Mettre a jour le role en DB si different de padawan
        if role != "padawan" and db_session_for_role is not None:
            user = (
                db_session_for_role.query(User)
                .filter(User.username == user_data["username"])
                .first()
            )
            if user:
                adapted_role = adapt_enum_for_db("UserRole", role, db_session_for_role)
                user.role = adapted_role
                db_session_for_role.commit()

        # Login pour obtenir le cookie
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        response = await ac.post("/api/auth/login", json=login_data)
        if response.status_code != 200:
            pytest.skip(f"Cannot authenticate {role}: {response.text}")

        tokens = response.json()
        access_token = tokens["access_token"]

        # Forcer le cookie (en complement du Set-Cookie automatique)
        ac.cookies.set("access_token", access_token)

        yield {
            "client": ac,
            "user_data": user_data,
            "token": access_token,
            "user_id": tokens.get("user", {}).get("id"),
            "role": role,
        }


@pytest.fixture
def test_app():
    """L'application Starlette pour les tests."""
    return starlette_app


@pytest.fixture
async def client():
    """Client HTTP non authentifie pour tester l'API Starlette."""
    transport = httpx.ASGITransport(app=starlette_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_client():
    """Client HTTP authentifie (role PADAWAN). Cookie access_token configure."""
    async with _create_authenticated_client(role="padawan") as result:
        yield result


@pytest.fixture
async def expired_token_client():
    """Client avec un token expire (pour tester le rejet d'auth)."""
    transport = httpx.ASGITransport(app=starlette_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_id = uuid.uuid4().hex[:8]
        user_data = {
            "username": f"test_jedi_expired_{unique_id}",
            "email": f"jedi_expired_{unique_id}@test.com",
            "password": "Force123Jedi",
        }

        try:
            # Creer l'utilisateur
            response = await ac.post("/api/users/", json=user_data)
            if response.status_code not in (200, 201):
                pytest.skip(f"Cannot create test user: {response.text}")

            # Creer un token expire manuellement
            payload = {
                "sub": user_data["username"],
                "role": "padawan",
                "type": "access",
                "exp": datetime.now(timezone.utc) - timedelta(minutes=30),
            }
            expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            # Configurer le cookie avec le token expire
            ac.cookies.set("access_token", expired_token)

            yield {
                "client": ac,
                "user_data": user_data,
                "token": expired_token,
                "user_id": response.json().get("id"),
            }
        except Exception as e:
            pytest.skip(f"Error during expired token setup: {str(e)}")


@pytest.fixture
async def refresh_token_client():
    """Client avec un refresh token valide."""
    transport = httpx.ASGITransport(app=starlette_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_id = uuid.uuid4().hex[:8]
        user_data = {
            "username": f"test_jedi_refresh_{unique_id}",
            "email": f"jedi_refresh_{unique_id}@test.com",
            "password": "Force123Jedi",
        }

        try:
            response = await ac.post("/api/users/", json=user_data)
            if response.status_code not in (200, 201):
                pytest.skip(f"Cannot create test user: {response.text}")

            verify_user_email_for_tests(user_data["username"])

            login_data = {
                "username": user_data["username"],
                "password": user_data["password"],
            }
            response = await ac.post("/api/auth/login", json=login_data)
            if response.status_code != 200:
                pytest.skip(f"Cannot authenticate: {response.text}")

            tokens = response.json()
            # refresh_token uniquement en cookie HttpOnly (plus dans le body)
            refresh_token = (
                response.cookies.get("refresh_token") if response.cookies else None
            )
            if not refresh_token:
                pytest.skip("Refresh token not in cookie (login response)")

            yield {
                "client": ac,
                "user_data": user_data,
                "access_token": tokens["access_token"],
                "refresh_token": refresh_token,
                "user_id": tokens.get("user", {}).get("id"),
            }
        except Exception as e:
            pytest.skip(f"Error during refresh token setup: {str(e)}")


@pytest.fixture
def role_client(db_session):
    """Factory fixture pour créer un client authentifié avec un rôle spécifique.

    Usage (dans un test async):
        async def test_admin(role_client):
            async with role_client('maitre') as result:
                client = result["client"]
                response = await client.get("/api/users/me")
                assert response.status_code == 200
    """

    def _make_client(role):
        return _create_authenticated_client(role=role, db_session_for_role=db_session)

    return _make_client


# Raccourcis par role
@pytest.fixture
async def padawan_client():
    """Client authentifie avec role PADAWAN."""
    async with _create_authenticated_client(role="padawan") as result:
        yield result


@pytest.fixture
async def maitre_client(db_session):
    """Client authentifie avec role MAITRE."""
    async with _create_authenticated_client(
        role="maitre", db_session_for_role=db_session
    ) as result:
        yield result


@pytest.fixture
async def gardien_client(db_session):
    """Client authentifie avec role GARDIEN."""
    async with _create_authenticated_client(
        role="gardien", db_session_for_role=db_session
    ) as result:
        yield result


@pytest.fixture
async def archiviste_client(db_session):
    """Client authentifie avec role ARCHIVISTE."""
    async with _create_authenticated_client(
        role="archiviste", db_session_for_role=db_session
    ) as result:
        yield result


# ================================================================
# SECTION 4: MOCK FIXTURES (donnees de test en memoire)
# ================================================================


@pytest.fixture
def mock_exercise():
    """Factory pour generer des exercices de test (dict).

    Usage:
        exercise = mock_exercise()
        custom = mock_exercise(title="Custom", difficulty="maitre")
    """

    def _create_exercise(**kwargs):
        default_values = {
            "title": "Exercice de test",
            "exercise_type": "ADDITION",
            "difficulty": "INITIE",
            "age_group": "6-8",
            "question": "Combien font 2+2?",
            "correct_answer": "4",
            "choices": ["3", "4", "5", "6"],
            "ai_generated": False,
            "is_active": True,
            "is_archived": False,
        }
        exercise_data = {**default_values, **kwargs}

        if isinstance(exercise_data.get("exercise_type"), str):
            exercise_data["exercise_type"] = exercise_data["exercise_type"].upper()
        if isinstance(exercise_data.get("difficulty"), str):
            exercise_data["difficulty"] = exercise_data["difficulty"].upper()

        return exercise_data

    return _create_exercise


@pytest.fixture
def mock_user():
    """Factory pour créer des données d'utilisateur de test (dict).

    Usage:
        user_data = mock_user()
        admin = mock_user(role='maitre', username='admin_test')
    """

    def _create_user(**kwargs):
        username = kwargs.get("username", unique_username())
        email = kwargs.get("email", unique_email())
        password = kwargs.get("password", "TestPass123!")

        return {
            "username": username,
            "email": email,
            "password": password,
            "full_name": kwargs.get("full_name", "Utilisateur de Test"),
            "role": kwargs.get("role", "padawan"),
            "is_active": kwargs.get("is_active", True),
            "grade_level": kwargs.get("grade_level", 3),
            "learning_style": kwargs.get("learning_style", "visuel"),
            "preferred_difficulty": kwargs.get("preferred_difficulty", "initie"),
            "preferred_theme": kwargs.get("preferred_theme"),
            "accessibility_settings": kwargs.get("accessibility_settings"),
        }

    return _create_user


@pytest.fixture
def mock_request():
    """Factory pour créer des requêtes mock compatibles Starlette.

    Usage:
        request = mock_request()
        auth_request = mock_request(authenticated=True, role="maitre")
        data_request = mock_request(json_data={"key": "value"})
    """

    def _create_request(
        authenticated=False,
        role="padawan",
        json_data=None,
        path_params=None,
        query_params=None,
    ):
        mock_req = MagicMock()

        # Authentification
        if authenticated:
            uid = uuid.uuid4().hex[:8]
            mock_req.user = {
                "id": 1,
                "username": f"test_user_{uid}",
                "role": role,
                "is_authenticated": True,
            }
        else:
            mock_req.user = {"is_authenticated": False}

        # JSON body (async pour Starlette)
        mock_req.json = AsyncMock(return_value=json_data or {})

        # Cookies
        mock_req.cookies = {}
        if authenticated:
            mock_req.cookies["access_token"] = "mock_test_token"

        # Path params, query params, headers
        mock_req.path_params = path_params or {}
        mock_req.query_params = query_params or {}
        mock_req.headers = {}

        return mock_req

    return _create_request


@pytest.fixture
def mock_api_response():
    """Factory pour simuler une reponse HTTP.

    Usage:
        response = mock_api_response()
        error = mock_api_response(status_code=404, data={"detail": "Not found"})
    """

    def _create_response(status_code=200, data=None, headers=None):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.headers = headers or {}
        mock_resp.json.return_value = data or {}

        if isinstance(data, str):
            mock_resp.text = data
        else:
            mock_resp.text = json.dumps(data or {})

        return mock_resp

    return _create_response


# ================================================================
# SECTION 5: ENUM & MODEL FIXTURES
# ================================================================


@pytest.fixture
def db_enum_values(db_session):
    """Fournit les valeurs d'enum PostgreSQL."""
    return get_all_enum_values()


@pytest.fixture
def logic_challenge_data(db_session):
    """Données de test pour les défis logiques avec valeurs d'enum adaptées."""
    return {
        "title": "Test Logic Challenge",
        "description": "Un défi logique pour les tests",
        "challenge_type": get_enum_value(
            LogicChallengeType, LogicChallengeType.SEQUENCE.value, db_session
        ),
        "age_group": get_enum_value(AgeGroup, AgeGroup.GROUP_10_12.value, db_session),
        "correct_answer": "42",
        "solution_explanation": "La reponse est toujours 42",
        "hints": ["indice1", "indice2", "indice3"],
    }


@pytest.fixture
def user_data(db_session):
    """Données pour créer un utilisateur avec les valeurs PostgreSQL correctes."""
    uid = uuid.uuid4().hex[:8]
    return {
        "username": f"testuser_{uid}",
        "email": f"test_{uid}@example.com",
        "hashed_password": "hashed_password",
        "role": get_enum_value(UserRole, UserRole.MAITRE.value, db_session),
    }


# ================================================================
# SECTION 6: LOGIC CHALLENGE DB FIXTURE
# ================================================================


@pytest.fixture(scope="function")
def logic_challenge_db(db_session):
    """Session PostgreSQL avec données de défi logique pré-créées.

    Crée un utilisateur de test + un défi logique, puis nettoie après le test.
    SECURITE: Seules les donnees prefixees test_ sont touchees.
    """
    unique_id = uuid.uuid4().hex[:8]

    # Nettoyage pre-test des donnees de test existantes
    try:
        db_session.execute(
            text(
                "DELETE FROM logic_challenge_attempts WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%')"
            )
        )
        db_session.execute(
            text(
                "DELETE FROM attempts WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%')"
            )
        )
        db_session.execute(
            text("DELETE FROM logic_challenges WHERE title LIKE 'Test %'")
        )
        db_session.execute(text("DELETE FROM users WHERE username LIKE 'test_%'"))
        db_session.commit()
    except Exception:
        db_session.rollback()
        # Fallback ORM - toujours filtrer sur les donnees de test
        test_users = db_session.query(User).filter(User.username.like("test_%")).all()
        test_user_ids = [u.id for u in test_users]

        if test_user_ids:
            db_session.query(LogicChallengeAttempt).filter(
                LogicChallengeAttempt.user_id.in_(test_user_ids)
            ).delete(synchronize_session=False)
            db_session.query(Attempt).filter(Attempt.user_id.in_(test_user_ids)).delete(
                synchronize_session=False
            )

        db_session.query(LogicChallenge).filter(
            LogicChallenge.title.like("Test %")
        ).delete(synchronize_session=False)

        for user in test_users:
            db_session.delete(user)

        db_session.commit()

    try:
        # Creer un utilisateur de test
        test_user = User(
            username=f"test_jedi_{unique_id}",
            email=f"test_{unique_id}@jedi.com",
            hashed_password=get_password_hash("testpassword"),
            role=get_enum_value(UserRole, UserRole.GARDIEN),
        )
        db_session.add(test_user)
        db_session.commit()

        # Créer un défi logique de test
        test_challenge = LogicChallenge(
            title=f"Test Challenge {unique_id}",
            description="Description du défi de test",
            challenge_type=get_enum_value(
                LogicChallengeType, LogicChallengeType.SEQUENCE
            ),
            age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_10_12),
            correct_answer="42",
            solution_explanation="La reponse est 42",
            hints=["Indice 1", "Indice 2", "Indice 3"],
            creator_id=test_user.id,
            difficulty_rating=3.0,
            estimated_time_minutes=15,
        )
        db_session.add(test_challenge)
        db_session.commit()

        yield db_session

    finally:
        # Nettoyage post-test: supprimer d'abord les attempts liés aux challenges (FK)
        try:
            # 1. Supprimer les attempts par user_id (test_jedi)
            db_session.execute(
                text(
                    f"DELETE FROM logic_challenge_attempts WHERE user_id IN "
                    f"(SELECT id FROM users WHERE username = 'test_jedi_{unique_id}')"
                )
            )
            # 2. Supprimer les attempts qui référencent nos challenges (padawan peut avoir tenté)
            db_session.execute(
                text(
                    "DELETE FROM logic_challenge_attempts WHERE challenge_id IN "
                    "(SELECT id FROM logic_challenges WHERE title LIKE :pat)"
                ),
                {"pat": f"Test Challenge {unique_id}%"},
            )
            # 3. Puis supprimer les challenges
            db_session.execute(
                text(
                    f"DELETE FROM logic_challenges WHERE title LIKE 'Test Challenge {unique_id}%'"
                )
            )
            db_session.execute(
                text(f"DELETE FROM users WHERE username = 'test_jedi_{unique_id}'")
            )
            db_session.commit()
        except Exception:
            db_session.rollback()
            test_user = (
                db_session.query(User)
                .filter(User.username == f"test_jedi_{unique_id}")
                .first()
            )
            # Définir les challenges à supprimer
            challenges_to_delete = (
                db_session.query(LogicChallenge)
                .filter(LogicChallenge.title.like(f"Test Challenge {unique_id}%"))
                .all()
            )
            challenge_ids = [c.id for c in challenges_to_delete]
            # Supprimer d'abord les attempts (FK) par user_id puis par challenge_id
            if test_user:
                db_session.query(LogicChallengeAttempt).filter(
                    LogicChallengeAttempt.user_id == test_user.id
                ).delete(synchronize_session=False)
            if challenge_ids:
                db_session.query(LogicChallengeAttempt).filter(
                    LogicChallengeAttempt.challenge_id.in_(challenge_ids)
                ).delete(synchronize_session=False)
            db_session.query(LogicChallenge).filter(
                LogicChallenge.title.like(f"Test Challenge {unique_id}%")
            ).delete(synchronize_session=False)
            if test_user:
                db_session.delete(test_user)
            db_session.commit()


@pytest.fixture(scope="function")
def challenge_with_hints_id(logic_challenge_db):
    """ID du défi créé par logic_challenge_db (avec hints).

    Utilise pour les tests qui requièrent un défi avec indices (hint endpoint).
    """
    challenge = (
        logic_challenge_db.query(LogicChallenge)
        .filter(LogicChallenge.title.like("Test Challenge%"))
        .order_by(LogicChallenge.id.desc())
        .first()
    )
    assert challenge is not None, "logic_challenge_db doit créer un défi Test Challenge"
    return challenge.id


# ================================================================
# SECTION 7: AUTO CLEANUP
# ================================================================


@pytest.fixture(autouse=True, scope="function")
def auto_cleanup_test_data(db_session):
    """Nettoyage automatique des donnees de test apres chaque test.

    - S'execute automatiquement (autouse=True)
    - Identifie les donnees de test via TestDataManager
    - Preserve les utilisateurs permanents (ObiWan, maitre_yoda, etc.)
    - Gere les sessions en etat d'erreur (InFailedSqlTransaction)
    - Logging avec traceback complet en cas d'erreur
    """
    import logging
    import traceback

    _cleanup_logger = logging.getLogger("tests.cleanup")

    yield

    try:
        from sqlalchemy.exc import InvalidRequestError, StatementError

        try:
            db_session.execute(text("SELECT 1"))
        except (InvalidRequestError, StatementError, Exception):
            # Session en erreur : créer une nouvelle session pour le nettoyage
            _cleanup_logger.debug(
                "Session principale en erreur, creation d'une session de nettoyage"
            )
            fallback_engine = get_test_engine()
            CleanupSessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=fallback_engine
            )
            cleanup_session = CleanupSessionLocal()
            try:
                manager = TestDataManager(cleanup_session)
                result = manager.cleanup_test_data(dry_run=False)
                if result.get("success") and result.get("total_deleted", 0) > 0:
                    _cleanup_logger.info(
                        f"Nettoyage (session secours): {result['total_deleted']} elements supprimes"
                    )
                elif not result.get("success"):
                    _cleanup_logger.warning(
                        f"Nettoyage echoue (session secours): {result.get('error', 'inconnue')}"
                    )
            except Exception as fallback_error:
                _cleanup_logger.error(
                    f"Erreur nettoyage (session secours): {fallback_error}\n{traceback.format_exc()}"
                )
            finally:
                cleanup_session.close()
            return

        manager = TestDataManager(db_session)
        result = manager.cleanup_test_data(dry_run=False)
        if result.get("success") and result.get("total_deleted", 0) > 0:
            _cleanup_logger.info(
                f"Nettoyage: {result['total_deleted']} elements supprimes"
            )
        elif not result.get("success"):
            _cleanup_logger.warning(
                f"Nettoyage echoue: {result.get('error', 'inconnue')}"
            )

    except Exception as cleanup_error:
        _cleanup_logger.error(
            f"Erreur critique nettoyage: {cleanup_error}\n{traceback.format_exc()}"
        )


@pytest.fixture
def test_data_manager(db_session):
    """Instance de TestDataManager pour controle manuel du nettoyage."""
    return TestDataManager(db_session)


@pytest.fixture
def isolated_test_user(db_session):
    """Utilisateur de test avec nettoyage automatique garanti."""
    manager = TestDataManager(db_session)
    return manager.create_test_user(
        username_prefix="isolated_test",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
