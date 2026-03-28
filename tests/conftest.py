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
os.environ["OPENAI_API_KEY"] = ""
os.environ.setdefault("RUN_OPENAI_LIVE_TESTS", "0")

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
            # SECURITE: Ne pas dériver TEST_DATABASE_URL d'une URL externe (Render, RDS, etc.)
            # même si le nom de la base contient "test" (ex: mathakine_test_gii8 sur Render).
            _is_external_host = any(
                h in _db_url.lower()
                for h in (
                    "render.com",
                    "amazonaws.com",
                    "supabase",
                    "neon.tech",
                    "railway.app",
                )
            )
            if "test" in _db_name.lower() and not _is_external_host:
                os.environ["TEST_DATABASE_URL"] = _db_url
                print(f"  TEST_DATABASE_URL derive de DATABASE_URL (base: {_db_name})")
            else:
                print(
                    f"  ATTENTION: DATABASE_URL pointe vers '{_db_name}' (pas une base test locale)"
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
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from _pytest.outcomes import Failed
from jose import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Ajouter le repertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import configure_mappers

# App imports (apres TESTING=true)
import app.models  # noqa: F401 — force l'enregistrement Base.metadata avant tout accès DB

configure_mappers()  # Force la résolution des relations immédiatement (évite deadlock async)
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.db.base import Base, engine
from app.models.ai_eval_harness_run import AiEvalHarnessCaseResult, AiEvalHarnessRun
from app.models.attempt import Attempt
from app.models.challenge_progress import ChallengeProgress
from app.models.daily_challenge import DailyChallenge
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)
from app.models.point_event import PointEvent
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.spaced_repetition_item import SpacedRepetitionItem
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
# SECTION 0: CSRF — bypass via mock (jamais via env var en prod)
# ================================================================
# Le code de production ne contient aucun bypass TESTING.
# Les tests désactivent la validation CSRF via mock — la seule
# approche qui ne crée pas de surface d'attaque en production.


@pytest.fixture(autouse=True, scope="session")
def _bypass_csrf_in_tests():
    """Désactive la validation CSRF pour toute la session de tests.

    Utilise unittest.mock.patch sur validate_csrf_token — la production
    n'a aucun bypass basé sur TESTING ou variables d'environnement.
    """
    with patch("app.utils.csrf.validate_csrf_token", return_value=None):
        yield


@pytest.fixture(autouse=True, scope="session")
def _block_real_openai_calls_in_tests():
    """
    Interdit tout appel réel à OpenAI pendant les tests par défaut.

    Opt-in explicite uniquement avec RUN_OPENAI_LIVE_TESTS=1.
    Le verrou reste limité à pytest et n'impacte pas le runtime normal.
    """
    if os.getenv("RUN_OPENAI_LIVE_TESTS") == "1":
        yield
        return

    object.__setattr__(settings, "OPENAI_API_KEY", "")

    def _forbidden_openai_client(*args, **kwargs):
        raise AssertionError(
            "Real OpenAI calls are forbidden in tests. "
            "Mock AsyncOpenAI or enable RUN_OPENAI_LIVE_TESTS=1 explicitly."
        )

    with (
        patch("openai.AsyncOpenAI", side_effect=_forbidden_openai_client),
        patch(
            "server.handlers.chat_handlers.AsyncOpenAI",
            side_effect=_forbidden_openai_client,
        ),
    ):
        yield


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

    # F02/B1: certaines bases de test locales n'ont pas encore la table daily_challenges.
    # On la crée à la volée en test pour éviter les erreurs de cascade User -> DailyChallenge.
    DailyChallenge.__table__.create(bind=imported_engine, checkfirst=True)
    PointEvent.__table__.create(bind=imported_engine, checkfirst=True)
    ChallengeProgress.__table__.create(bind=imported_engine, checkfirst=True)
    # IA8 : tables harness eval (même principe que daily_challenges — base de test sans alembic à jour).
    AiEvalHarnessRun.__table__.create(bind=imported_engine, checkfirst=True)
    AiEvalHarnessCaseResult.__table__.create(bind=imported_engine, checkfirst=True)
    # SR F04 : recréer pour suivre le modèle ORM (ex. exercise_id NOT NULL + CASCADE)
    SpacedRepetitionItem.__table__.drop(bind=imported_engine, checkfirst=True)
    SpacedRepetitionItem.__table__.create(bind=imported_engine, checkfirst=True)

    engine_db_match = re.search(r"/([^/?]+)(?:\?|$)", engine_url)
    if engine_db_match:
        engine_db_name = engine_db_match.group(1)
        _engine_is_external = any(
            h in engine_url.lower()
            for h in (
                "render.com",
                "amazonaws.com",
                "supabase",
                "neon.tech",
                "railway.app",
            )
        )
        # Une DB externe est toujours considérée prod, même si son nom contient "test"
        # (ex: mathakine_test_gii8 sur Render = prod).
        if _engine_is_external or "test" not in engine_db_name.lower():
            environment = os.environ.get("ENVIRONMENT", "")
            if environment == "production" or _engine_is_external:
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
            # Lever même si "test" est dans le nom : mathakine_test_gii8 sur Render = prod.
            # La vérification host externe prend le dessus sur le nom.
            _is_ext = any(
                h in test_db_url.lower()
                for h in (
                    "render.com",
                    "amazonaws.com",
                    "supabase",
                    "neon.tech",
                    "railway.app",
                )
            )
            if test_db_name == prod_db_name and (
                "test" not in test_db_name.lower() or _is_ext
            ):
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
            if "test" not in (test_db_url or "").lower() and "localhost" not in (
                test_db_url or ""
            ):
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


def _ensure_recommendations_r5_columns() -> None:
    """Idempotent : colonnes R5 si migration Alembic pas encore appliquée sur la base de test."""
    engine = _get_session_engine()
    try:
        with engine.begin() as conn:
            try:
                conn.execute(
                    text(
                        "ALTER TABLE recommendations ADD COLUMN reason_code VARCHAR(80)"
                    )
                )
            except Exception:
                pass  # colonne déjà présente (ou dialecte)
            try:
                conn.execute(
                    text("ALTER TABLE recommendations ADD COLUMN reason_params JSONB")
                )
            except Exception:
                try:
                    conn.execute(
                        text(
                            "ALTER TABLE recommendations ADD COLUMN reason_params JSON"
                        )
                    )
                except Exception:
                    pass
    except Exception as schema_err:
        print(f"  [conftest] skip R5 column ensure: {schema_err}")


@pytest.fixture(scope="session", autouse=True)
def _session_ensure_recommendations_r5_columns():
    _ensure_recommendations_r5_columns()
    yield


@pytest.fixture
def db_session():
    """Session DB standard — vrais commits pour que les handlers HTTP (autre connexion) voient les données.

    auto_cleanup_test_data nettoie les tables après chaque test.
    """
    engine = _get_session_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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
    - Teardown explicite: supprime l'user par id (ne depend plus du cleanup global)
    - Yield le client configure + metadata
    """
    transport = httpx.ASGITransport(app=starlette_app)
    user_id_to_cleanup = None
    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            unique_id = uuid.uuid4().hex[:8]
            # Namespace reserve: fixture_auth_* hors cleanup global (teardown explicite)
            user_data = {
                "username": f"fixture_auth_{role}_{unique_id}",
                "email": f"fixture_auth_{role}_{unique_id}@example.com",
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
                    adapted_role = adapt_enum_for_db(
                        "UserRole", role, db_session_for_role
                    )
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
            user_id_to_cleanup = tokens.get("user", {}).get("id")

            # Forcer le cookie (en complement du Set-Cookie automatique)
            ac.cookies.set("access_token", access_token)

            yield {
                "client": ac,
                "user_data": user_data,
                "token": access_token,
                "user_id": user_id_to_cleanup,
                "role": role,
            }
    finally:
        # Teardown explicite: supprimer l'user par id (ADMIN_AUTH_FIXTURES_STABILIZATION)
        if user_id_to_cleanup is not None:
            try:
                sess_engine = _get_session_engine()
                TeardownSession = sessionmaker(
                    autocommit=False, autoflush=False, bind=sess_engine
                )
                teardown_sess = TeardownSession()
                try:
                    user = (
                        teardown_sess.query(User)
                        .filter(User.id == user_id_to_cleanup)
                        .first()
                    )
                    if user:
                        teardown_sess.delete(user)
                        teardown_sess.commit()
                finally:
                    teardown_sess.close()
            except Exception:
                pass


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

    # Nettoyage pre-test: challenges et attempts de test, SANS supprimer les users.
    # Raison: padawan_client peut s'exécuter avant logic_challenge_db (ordre pytest non garanti).
    # Supprimer les users ici provoquerait 401 sur tests utilisant les deux fixtures.
    # Les users test_% sont nettoyés par auto_cleanup après chaque test.
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
            text(
                "DELETE FROM logic_challenges WHERE creator_id IN "
                "(SELECT id FROM users WHERE username LIKE 'test_%')"
            )
        )
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

        # Ne pas supprimer les users ici (même motif: padawan_client peut avoir créé le sien)
        db_session.commit()

    try:
        # Creer un utilisateur de test (namespace fixture_chall_ hors patterns cleanup global)
        test_user = User(
            username=f"fixture_chall_{unique_id}",
            email=f"fixture_chall_{unique_id}@chall.example.com",
            hashed_password=get_password_hash("testpassword"),
            role=get_enum_value(UserRole, UserRole.GARDIEN),
        )
        db_session.add(test_user)
        db_session.commit()

        # Créer un défi logique (titre sans "test"/"Test" pour éviter collision cleanup)
        test_challenge = LogicChallenge(
            title=f"Défi fixture chall {unique_id}",
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
        db_session.refresh(test_challenge)

        # Exposer l'ID pour challenge_with_hints_id (évite query stale en ordre variable)
        db_session._logic_challenge_test_id = test_challenge.id

        yield db_session

    finally:
        # Nettoyage post-test: supprimer d'abord les attempts liés aux challenges (FK)
        try:
            # 1. Supprimer les attempts par user_id (fixture_chall_)
            db_session.execute(
                text(
                    f"DELETE FROM logic_challenge_attempts WHERE user_id IN "
                    f"(SELECT id FROM users WHERE username = 'fixture_chall_{unique_id}')"
                )
            )
            # 2. Supprimer les attempts qui référencent nos challenges (padawan peut avoir tenté)
            db_session.execute(
                text(
                    "DELETE FROM logic_challenge_attempts WHERE challenge_id IN "
                    "(SELECT id FROM logic_challenges WHERE title LIKE :pat)"
                ),
                {"pat": f"Défi fixture chall {unique_id}%"},
            )
            # 3. Puis supprimer les challenges
            db_session.execute(
                text(
                    f"DELETE FROM logic_challenges WHERE title LIKE 'Défi fixture chall {unique_id}%'"
                )
            )
            db_session.execute(
                text(f"DELETE FROM users WHERE username = 'fixture_chall_{unique_id}'")
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
                LogicChallenge.title.like(f"Défi fixture chall {unique_id}%")
            ).delete(synchronize_session=False)
            if test_user:
                db_session.delete(test_user)
            db_session.commit()


@pytest.fixture(scope="function")
def challenge_with_hints_id(logic_challenge_db):
    """ID du défi créé par logic_challenge_db (avec hints).

    Utilise l'ID exposé par logic_challenge_db pour éviter 404 ordre-dépendant.
    """
    challenge_id = getattr(logic_challenge_db, "_logic_challenge_test_id", None)
    if challenge_id is not None:
        return challenge_id
    # Fallback si attribut absent (compat)
    challenge = (
        logic_challenge_db.query(LogicChallenge)
        .filter(LogicChallenge.title.like("Défi fixture chall%"))
        .order_by(LogicChallenge.id.desc())
        .first()
    )
    assert (
        challenge is not None
    ), "logic_challenge_db doit créer un défi Défi fixture chall"
    return challenge.id


# ================================================================
# SECTION 7: AUTO CLEANUP
# ================================================================


@pytest.fixture(autouse=True, scope="function")
def _clear_adaptive_context_cache_between_tests():
    """F42-P2b: évite la fuite du cache in-process ``resolve_adaptive_context`` entre tests."""
    from app.services.exercises.adaptive_difficulty_service import (
        clear_resolve_adaptive_context_cache,
    )

    clear_resolve_adaptive_context_cache()
    yield
    clear_resolve_adaptive_context_cache()


@pytest.fixture(autouse=True, scope="function")
def auto_cleanup_test_data(db_session):
    """Nettoyage automatique des donnees de test.

    - Pre-yield: nettoie les donnees du test precedent (evite disparition
      prematuree des fixture users entre tests sequentiels)
    - Post-yield: nettoie les donnees du test courant
    """
    import logging
    import traceback

    from sqlalchemy.exc import InvalidRequestError, StatementError

    _cleanup_logger = logging.getLogger("tests.cleanup")

    def _do_cleanup(session):
        try:
            try:
                session.execute(text("SELECT 1"))
            except (InvalidRequestError, StatementError, Exception):
                # R5d: même engine que db_session / handlers — évite deux pools (FK, visibilité).
                sess = sessionmaker(
                    autocommit=False, autoflush=False, bind=_get_session_engine()
                )()
                try:
                    r = TestDataManager(sess).cleanup_test_data(dry_run=False)
                    if r.get("success") and r.get("total_deleted", 0) > 0:
                        _cleanup_logger.info(
                            f"Nettoyage (secours): {r['total_deleted']} elements"
                        )
                    if not r.get("success"):
                        pytest.fail(
                            "Nettoyage pre-test (session secours) echoue: "
                            f"{r.get('error', 'inconnue')}"
                        )
                finally:
                    sess.close()
                return
            r = TestDataManager(session).cleanup_test_data(dry_run=False)
            if r.get("success") and r.get("total_deleted", 0) > 0:
                _cleanup_logger.info(f"Nettoyage: {r['total_deleted']} elements")
            if not r.get("success"):
                pytest.fail(f"Nettoyage pre-test echoue: {r.get('error', 'inconnue')}")
        except Failed:
            raise
        except Exception as e:
            _cleanup_logger.error(f"Erreur nettoyage: {e}\n{traceback.format_exc()}")
            pytest.fail(f"Exception pendant nettoyage pre-test: {e}")

    # Pre-yield: nettoyer donnees du test precedent
    _do_cleanup(db_session)

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
            fallback_engine = _get_session_engine()
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
                if not result.get("success"):
                    pytest.fail(
                        "Nettoyage post-test (session secours) echoue: "
                        f"{result.get('error', 'inconnue')}"
                    )
            except Failed:
                raise
            except Exception as fallback_error:
                _cleanup_logger.error(
                    f"Erreur nettoyage (session secours): {fallback_error}\n{traceback.format_exc()}"
                )
                pytest.fail(
                    f"Exception nettoyage post-test (session secours): {fallback_error}"
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
        if not result.get("success"):
            pytest.fail(
                f"Nettoyage post-test echoue: {result.get('error', 'inconnue')}"
            )

    except Failed:
        raise
    except Exception as cleanup_error:
        _cleanup_logger.error(
            f"Erreur critique nettoyage: {cleanup_error}\n{traceback.format_exc()}"
        )
        pytest.fail(f"Exception critique nettoyage post-test: {cleanup_error}")


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
