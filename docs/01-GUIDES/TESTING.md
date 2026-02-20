# 🧪 TESTING GUIDE - MATHAKINE

**Version** : 3.1.0  
**Date** : 11 fevrier 2026 (mise a jour)  
**Audience** : Developpeurs, QA

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble](#vue-ensemble)
2. [Configuration tests](#configuration)
3. [Tests backend](#tests-backend)
4. [Tests frontend](#tests-frontend)
5. [CI/CD](#cicd)
6. [Best practices](#best-practices)
7. [Modifications recentes](#modifications-recentes)

---

## 🎯 VUE D'ENSEMBLE {#vue-ensemble}

### Stratégie de tests

```
┌─────────────────────────────────────────┐
│        Tests Pyramide                    │
├─────────────────────────────────────────┤
│              E2E (5%)                    │
│          ▲  Playwright                   │
│         ││                               │
│       Integration (25%)                  │
│      ▲  pytest + httpx.AsyncClient       │
│     ││                                   │
│   Unit Tests (70%)                       │
│  ▲  pytest + Vitest                      │
│ ││                                       │
└─────────────────────────────────────────┘
```

> **Migration 08/02/2026** : Les tests backend ont ete migres de `starlette.testclient.TestClient` (sync) vers `httpx.AsyncClient` (async natif Starlette). Tous les tests d'integration utilisent desormais `pytest-asyncio`.

### Objectifs coverage
- **Unit tests** : 80%+ (objectif long terme)
- **Integration tests** : 60%+
- **E2E tests** : Scenarios critiques
- **Global coverage** : 70%+

> **Strategie actuelle** : Augmenter progressivement plutot qu'en bloc. Pour chaque nouvelle feature importante, ajouter 1-2 tests. Passer a une phase de montée en couverture quand les features sont stabilisees.

### Tests actuels (20/02/2026)
- ✅ **Backend** : ~375 tests passent, skippes réduits, ~48% couverture (app + server)
- ✅ **Frontend** : 31 tests (Vitest), utils/lib validations + composants + hooks
- ✅ **CI** : Tests + couverture backend et frontend, upload Codecov (flags backend/frontend)
- ✅ **Tests critiques** : auth, challenges, exercises, user_exercise_flow
- ✅ **Base de test separee** : `TEST_DATABASE_URL` obligatoire (protection production)
- ✅ **Tests async** : httpx.AsyncClient + pytest-asyncio (Starlette natif)

---

## ⚙️ CONFIGURATION TESTS {#configuration}

### Backend (pytest)

#### Installation
```bash
pip install pytest pytest-cov pytest-asyncio
```

#### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    -v
    --strict-markers
    --tb=short
    --cov=app
    --cov=server
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml

markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
    critical: marks tests as critical paths
```

#### conftest.py

**⚠️ IMPORTANT** : Les tests utilisent `TEST_DATABASE_URL` (PostgreSQL) et `httpx.AsyncClient`. Voir [CREATE_TEST_DATABASE.md](CREATE_TEST_DATABASE.md) pour la configuration.

```python
# tests/conftest.py (simplifie - voir le fichier reel pour la version complete)
import pytest
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from server.app import create_app

# Database de test - DOIT etre definie dans l'environnement
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise Exception("TEST_DATABASE_URL doit etre definie pour executer les tests")

@pytest.fixture(scope="session")
def engine():
    """Engine SQLAlchemy pour tests"""
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(engine):
    """Session DB pour chaque test"""
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="module")
async def client():
    """Client de test async (httpx.AsyncClient)"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_user(db):
    """Utilisateur de test"""
    from app.models.user import User
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role="student"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

> **Note** : Le `conftest.py` reel inclut egalement des safeguards pour empecher toute operation destructive sur la base de production (filtrage des DELETE/TRUNCATE, warnings si `TEST_DATABASE_URL` n'est pas defini).

### Frontend (Vitest + React Testing Library)

#### Installation
```bash
cd frontend
npm ci  # inclut vitest, @testing-library/react, @testing-library/user-event, @vitest/coverage-v8
```

#### vitest.config.ts
```typescript
// frontend/vitest.config.ts
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: ['**/__tests__/**', '**/*.config.*', '**/types/**'],
    },
  },
  resolve: { alias: { '@': path.resolve(__dirname, './') } },
});
```

---

## 🐍 TESTS BACKEND {#tests-backend}

### Tests unitaires

#### Service tests
```python
# tests/unit/test_challenge_service.py
import pytest
from app.services import challenge_service
from app.schemas.logic_challenge import LogicChallengeCreate

@pytest.mark.unit
def test_create_challenge(db):
    """Test création d'un challenge"""
    # Arrange
    challenge_data = LogicChallengeCreate(
        title="Test Challenge",
        description="Test description",
        challenge_type="SEQUENCE",
        age_group="GROUP_10_12",
        correct_answer="42",
        solution_explanation="Test explanation"
    )
    
    # Act
    result = challenge_service.create_challenge(db, challenge_data)
    
    # Assert
    assert result.id is not None
    assert result.title == "Test Challenge"
    assert result.challenge_type == "SEQUENCE"

@pytest.mark.unit
def test_get_challenge_by_id(db, sample_challenge):
    """Test récupération challenge par ID"""
    # Act
    result = challenge_service.get_challenge_by_id(db, sample_challenge.id)
    
    # Assert
    assert result is not None
    assert result.id == sample_challenge.id
    assert result.title == sample_challenge.title

@pytest.mark.unit
def test_list_challenges_with_filters(db, sample_challenges):
    """Test liste challenges avec filtres"""
    # Act
    results = challenge_service.list_challenges(
        db,
        challenge_type="SEQUENCE",
        age_group="GROUP_10_12"
    )
    
    # Assert
    assert len(results) > 0
    assert all(c.challenge_type == "SEQUENCE" for c in results)
```

#### Constants tests
```python
# tests/unit/test_constants.py
import pytest
from app.core.constants import (
    normalize_challenge_type,
    normalize_age_group,
    CHALLENGE_TYPES_DB,
    AGE_GROUPS_DB
)

@pytest.mark.unit
class TestNormalization:
    """Tests des fonctions de normalisation"""
    
    def test_normalize_challenge_type_lowercase(self):
        """Test normalisation type minuscule"""
        assert normalize_challenge_type("sequence") == "SEQUENCE"
        assert normalize_challenge_type("pattern") == "PATTERN"
    
    def test_normalize_challenge_type_uppercase(self):
        """Test normalisation type majuscule"""
        assert normalize_challenge_type("SEQUENCE") == "SEQUENCE"
    
    def test_normalize_challenge_type_invalid(self):
        """Test normalisation type invalide"""
        with pytest.raises(ValueError):
            normalize_challenge_type("invalid_type")
    
    def test_normalize_age_group(self):
        """Test normalisation groupe d'âge"""
        assert normalize_age_group("age_6_8") == "GROUP_6_8"
        assert normalize_age_group("GROUP_10_12") == "GROUP_10_12"
```

### Tests d'intégration

#### API tests
```python
# tests/api/test_challenges_flow.py
import pytest

@pytest.mark.api
@pytest.mark.critical
class TestChallengesFlow:
    """Tests du flow complet challenges"""
    
    def test_list_challenges(self, client, auth_headers):
        """Test GET /api/challenges"""
        response = client.get(
            "/api/challenges",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_challenge_details(self, client, sample_challenge, auth_headers):
        """Test GET /api/challenges/{id}"""
        response = client.get(
            f"/api/challenges/{sample_challenge.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_challenge.id
        assert "title" in data
        assert "challenge_type" in data
    
    def test_submit_challenge_attempt_correct(self, client, sample_challenge, auth_headers):
        """Test POST /api/challenges/{id}/attempt - réponse correcte"""
        response = client.post(
            f"/api/challenges/{sample_challenge.id}/attempt",
            json={"user_answer": sample_challenge.correct_answer},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True
        assert "points_earned" in data
    
    def test_submit_challenge_attempt_incorrect(self, client, sample_challenge, auth_headers):
        """Test POST /api/challenges/{id}/attempt - réponse incorrecte"""
        response = client.post(
            f"/api/challenges/{sample_challenge.id}/attempt",
            json={"user_answer": "wrong_answer"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is False
    
    def test_challenges_filters(self, client, auth_headers):
        """Test filtres challenges"""
        response = client.get(
            "/api/challenges?challenge_type=SEQUENCE&age_group=GROUP_10_12",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for challenge in data:
            assert challenge["challenge_type"] == "SEQUENCE"
            assert challenge["age_group"] == "GROUP_10_12"
```

#### Auth flow tests
```python
# tests/api/test_auth_flow.py
import pytest

@pytest.mark.api
@pytest.mark.critical
class TestAuthFlow:
    """Tests du flow d'authentification"""
    
    def test_login_success(self, client, sample_user):
        """Test connexion réussie"""
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
    
    def test_login_invalid_credentials(self, client):
        """Test connexion avec mauvais credentials"""
        response = client.post("/api/auth/login", json={
            "username": "invalid",
            "password": "wrong"
        })
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """Test GET /api/users/me"""
        response = client.get(
            "/api/users/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
    
    def test_refresh_token(self, client, refresh_token):
        """Test POST /api/auth/refresh"""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
```

### Lancer les tests

```bash
# Tous les tests
pytest tests/ -v

# Tests unitaires uniquement
pytest tests/unit/ -v

# Tests API uniquement
pytest tests/api/ -v

# Tests critiques uniquement
pytest tests/ -v -m critical

# Tests avec coverage
pytest tests/ -v --cov --cov-report=html

# Test spécifique
pytest tests/api/test_auth_flow.py::TestAuthFlow::test_login_success -v

# Tests en parallèle (plus rapide)
pytest tests/ -v -n auto
```

---

## ⚛️ TESTS FRONTEND {#tests-frontend}

### Composants avec contexte (NextIntl, React Query)

Pour les composants utilisant `useTranslations` ou `useCompletedExercises`, fournir les providers :

```typescript
// frontend/__tests__/unit/components/ExerciseCard.test.tsx
import { NextIntlClientProvider } from 'next-intl';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import fr from '@/messages/fr.json';

vi.mock('@/hooks/useCompletedItems', () => ({
  useCompletedExercises: () => ({ isCompleted: () => false }),
}));

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        {children}
      </QueryClientProvider>
    </NextIntlClientProvider>
  );
}

it('affiche le titre', () => {
  render(<ExerciseCard exercise={mockExercise} />, { wrapper: TestWrapper });
  expect(screen.getByText('Test Exercise')).toBeInTheDocument();
});
```

### Composants avec menu déroulant (userEvent)

Pour les composants dont le contenu est dans un popover/menu fermé par défaut (ex. AccessibilityToolbar) :

```typescript
import userEvent from '@testing-library/user-event';

it('affiche les options après ouverture du menu', async () => {
  render(<AccessibilityToolbar />);
  await userEvent.click(screen.getByRole('button', { name: /options d'accessibilité/i }));
  expect(screen.getByRole('switch', { name: /contraste élevé/i })).toBeInTheDocument();
});
```

### Tests composants (exemple simple)

```typescript
// frontend/__tests__/unit/components/BadgeCard.test.tsx
import { render, screen } from '@testing-library/react';
import { BadgeCard } from '@/components/badges/BadgeCard';

describe('BadgeCard', () => {
  it('affiche le nom du badge', () => {
    render(<BadgeCard badge={mockBadge} isEarned={false} />);
    expect(screen.getByText('Premiers Pas')).toBeInTheDocument();
  });
});
```

### Tests hooks

```typescript
// frontend/__tests__/unit/hooks/useAccessibleAnimation.test.ts
import { renderHook } from '@testing-library/react';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';

describe('useAccessibleAnimation', () => {
  it('retourne des variants et transition', () => {
    const { result } = renderHook(() => useAccessibleAnimation());
    expect(result.current.createVariants).toBeDefined();
    expect(result.current.shouldReduceMotion).toBe(false);
  });
});
```

### Tests E2E (Playwright)

```typescript
// frontend/__tests__/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('user can login successfully', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'testpassword');
    await page.click('[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
  });
});
```

### Lancer les tests

```bash
cd frontend

# Tests unitaires (Vitest)
npm run test

# Tests avec coverage
npm run test:coverage

# Tests en mode watch
npm run test -- --watch

# Interface UI interactive
npm run test:ui

# Tests E2E (Playwright)
npm run test:e2e
npm run test:e2e:ui
```

---

### Priorités de couverture frontend {#priorites-couverture}

> **Contexte** (audit 20/02/2026) : Les tests unitaires passent mais couvrent un sous-ensemble réduit (~4 fichiers vs ~120+ modules). Stratégie pragmatique : prioriser par impact sans complexifier.

#### Priorité 1 — Utils et validations (effort faible)

Fonctions pures, peu de mocks, faciles à maintenir.

| Cible | Fichier | Cas testés |
|-------|---------|------------|
| `safeValidateUserStats` | `lib/validations/dashboard.ts` | null/undefined, level (objet/number), progress_over_time, exercises_by_day |
| `extractShapeChoicesFromVisualData` | `lib/utils/visualChallengeUtils.ts` | shapes, layout, formats mixtes |

#### Priorité 2 — Régression sur bugs corrigés

À chaque correction de bug significative : ajouter un test minimal pour éviter le retour.

#### Priorité 3 — Hooks métier (effort moyen)

Hooks avec logique réutilisable : `usePaginatedContent`, logique de filtre, etc.

#### À éviter pour l'instant

- Couvrir toutes les pages (trop de mocks : API, router, i18n, stores)
- Tester des composants purement présentationnels sans logique
- Tests trop couplés à l’implémentation

#### Corrections appliquées (15/02/2026) — tests ajoutés

| Zone modifiée | Test ajouté |
|---------------|-------------|
| `safeValidateUserStats` (typage level, progress_over_time, exercises_by_day) | `__tests__/unit/lib/validations/dashboard.test.ts` |

---

## 🔄 CI/CD {#cicd}

### GitHub Actions Workflow (.github/workflows/tests.yml)

| Job | Actions |
|-----|---------|
| **test** | PostgreSQL 15, pytest avec --cov, coverage.xml, upload Codecov (flag backend) |
| **lint** | flake8, black, isort |
| **frontend** | npm ci, tsc --noEmit, **npm run test:coverage**, upload Codecov (flag frontend), npm run build |

Un echec de test bloque le merge. Les rapports de couverture sont envoyes a Codecov (backend + frontend separes).

**Configuration couverture :**
- `.coveragerc` — sources (app, server), exclusions (tests, migrations, etc.), rapport XML
- **Codecov** : pour un badge et des rapports PR, ajouter `CODECOV_TOKEN` dans GitHub Secrets (Settings → Secrets → Actions). Repo public : optionnel. Repo privé : requis.

---

## ✅ BEST PRACTICES {#best-practices}

### Général

1. **Tests avant code** (TDD)
```python
# 1. Écrire le test (fail)
def test_calculate_score():
    assert calculate_score(user_id=1) == 85.5

# 2. Écrire le code (pass)
def calculate_score(user_id: int) -> float:
    # Implementation
    return 85.5

# 3. Refactor
```

2. **AAA Pattern**
```python
def test_something():
    # Arrange - Préparer
    user = create_test_user()
    
    # Act - Agir
    result = service.do_something(user)
    
    # Assert - Vérifier
    assert result == expected_value
```

3. **Tests isolés**
```python
# ✅ CORRECT - Chaque test est indépendant
def test_create_user(db):
    user = create_user(db, "testuser")
    assert user.username == "testuser"

def test_update_user(db):
    user = create_user(db, "testuser")  # Créer ici
    updated = update_user(db, user.id, "newname")
    assert updated.username == "newname"

# ❌ INCORRECT - Tests dépendants
def test_create_then_update(db):
    user = create_user(db, "testuser")
    updated = update_user(db, user.id, "newname")
    # Trop de choses testées en même temps
```

4. **Noms explicites**
```python
# ✅ CORRECT
def test_login_with_invalid_credentials_returns_401():
    pass

# ❌ INCORRECT
def test_login():
    pass
```

5. **Utiliser fixtures**
```python
@pytest.fixture
def authenticated_client(client, sample_user):
    """Client avec authentification"""
    token = create_access_token(sample_user.id)
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

def test_protected_route(authenticated_client):
    response = authenticated_client.get("/api/protected")
    assert response.status_code == 200
```

6. **Mocker externes**
```python
from unittest.mock import patch, MagicMock

@patch('app.services.openai_service.OpenAI')
def test_ai_generation(mock_openai, db):
    """Test génération IA sans appeler vraiment l'API"""
    # Mock la réponse
    mock_openai.return_value.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Generated content"))]
    )
    
    # Tester
    result = generate_challenge_with_ai(db, "SEQUENCE", "MEDIUM")
    assert result.title == "Generated content"
```

---

## 🧹 GESTION DES DONNEES DE TEST {#test-data}

### Utilisateurs permanents (JAMAIS supprimes)

Les utilisateurs suivants sont des comptes de demonstration ou de seed. Ils ne doivent **JAMAIS** etre supprimes, modifies ou impactes par les tests :

| Username | Role | Description |
|----------|------|-------------|
| `ObiWan` | Demonstration | Utilisateur de demo visible sur le dashboard |
| `maitre_yoda` | Maitre | Utilisateur seed pour la creation d'exercices |
| `padawan1` | Padawan | Utilisateur seed eleve |
| `gardien1` | Gardien | Utilisateur seed administrateur |

> **REGLE ABSOLUE** : Aucun test ne doit creer de donnees (attempts, progress, recommendations) au nom de ces utilisateurs. Aucun `delete()` sans `.filter()` n'est autorise sur les tables partagees (attempts, progress, exercises, users).

### Conventions de nommage des donnees de test

Tous les tests doivent utiliser des noms qui correspondent aux patterns de nettoyage automatique :

**Usernames** (prefixes acceptes) :
```
test_%, new_test_%, duplicate_%, cascade_%, creator_%, service_%,
auth_test_%, isolated_%, flow_%, jedi_%, login_test_%, cascade_test_%
```

**Emails** (domaines de test) :
```
*@test.com, *@jedi.com, *@test.example.com, *@example.com
```

**Titres d'exercices** :
```
%test%, %Test%, %TEST%, Cascade %, Dashboard %
```

**Titres de defis** :
```
%test%, %Test%, %TEST%, Défi Auto-%, Nouveau défi%
```

### Nettoyage automatique (TestDataManager)

Le nettoyage s'execute automatiquement apres chaque test via la fixture `auto_cleanup_test_data` dans `tests/conftest.py`. Il utilise `TestDataManager` (`tests/utils/test_data_cleanup.py`) qui :

1. Identifie les donnees de test par patterns de noms
2. Exclut les utilisateurs permanents de toute suppression
3. Protege les attempts/progress des utilisateurs permanents meme sur des exercices de test
4. Supprime dans l'ordre FK : challenge_attempts → attempts → recommendations → progress → challenges → exercises → users

### Nettoyage one-shot (production)

Si des donnees de test ont persiste en production, utiliser le script de nettoyage :

```bash
# Mode dry-run (affiche sans supprimer)
python scripts/cleanup_test_data_production.py

# Mode execution (supprime reellement, demande confirmation)
python scripts/cleanup_test_data_production.py --execute
```

Ce script protege les memes utilisateurs permanents et respecte le meme ordre FK.

### Regles de securite pour les tests

1. **JAMAIS** de `db_session.query(Model).delete()` sans `.filter()` - utiliser toujours un filtre sur les patterns de test
2. **JAMAIS** d'operations sur la table `progress` ou `attempts` sans filtrer par `user_id` de test
3. **TOUJOURS** utiliser `unique_username()` / `unique_email()` pour generer des noms uniques
4. **TOUJOURS** commiter via la session de test si possible, pour que le rollback de fixture fonctionne
5. Si le test doit `commit()`, s'assurer que le `TestDataManager` pourra identifier les donnees creees

---

## 📝 MODIFICATIONS RECENTES {#modifications-recentes}

### 20/02/2026 – Nettoyage skips, suppression delete_exercise, nouveaux tests

| Domaine | Modification |
|---------|--------------|
| **Suppression DELETE /api/exercises/{id}** | Handler et route supprimés (pas de frontend, archivage prévu dans l'admin). Fichiers : `test_deletion_endpoints.py` supprimé, `test_exercise_endpoints`, `test_role_permissions` mis à jour. |
| **Suppression tests obsolètes** | `test_create_logic_challenge` (POST challenges non implémenté), `test_cli.py` (mathakine_cli archivé), `test_conditional_test_based_on_db_engine` (SQLite non utilisé). |
| **Réactivation skips** | `test_refresh_token` (auth_flow), `test_refresh_token_from_cookie_only` (auth_no_fallback), `test_sse_multiple_connections` (asyncio.gather). |
| **test_challenges_flow** | `test_generate_ai_challenge_stream` : `skipif(not OPENAI_API_KEY)` pour exécution quand clé dispo. |
| **test_db_init_service** | Suppression 2 skips schema (exercises/attempts integration). Nouveau `test_create_test_exercises_and_attempts_with_mocked_session`. |
| **Nouveaux tests base** | `test_base_endpoints.py` : `test_health_endpoint`, `test_robots_txt`, `test_csrf_token_endpoint`. |
| **Fixtures auth** | Extraction refresh_token depuis Set-Cookie pour tests HTTP (cookie Secure non transmis). |

### 15/02/2026 – Priorités couverture + tests régression

| Domaine | Modification |
|---------|--------------|
| **Priorités couverture** | Nouvelle section § Priorités de couverture frontend : utils/validations (P1), régression bugs (P2), hooks (P3). Éviter : pages entières, composants purement présentationnels. |
| **safeValidateUserStats** | 11 tests ajoutés (`__tests__/unit/lib/validations/dashboard.test.ts`) : null/undefined, level (objet/number), progress_over_time, exercises_by_day, exercises_by_type. |
| **Documentation** | Rappel corrections 15/02 : typage visualData (renderers), useAccessibleAnimation, validation dashboard, vitest.setup. |

### Fevrier 2026 – Session couverture et stabilisation

| Domaine | Modification |
|---------|--------------|
| **Backend** | `test_user_exercise_flow.py` : utilise `POST /api/exercises/generate` (pas de POST /api/exercises/), parametre `answer` pour les tentatives, `GET /api/users/stats` pour les stats |
| **Frontend** | `ExerciseCard.test.tsx` : wrapper NextIntlClientProvider + QueryClientProvider, mock useCompletedItems |
| **Frontend** | `AccessibilityToolbar` : tests adaptes (ouverture menu via userEvent, role="switch"), aria-label sur les options |
| **Frontend** | `BadgeCard.test.tsx` : mocks alignes sur types Badge/UserBadge (plus de requirements, achievement_id) |
| **Next.js 16** | Migration middleware.ts → proxy.ts (convention depreciee) |
| **CI** | Tests frontend avec coverage avant build, upload Codecov backend + frontend |
| **Dependances** | @testing-library/user-event, @vitest/coverage-v8 ajoutes |

### API exercices utiles

| Endpoint | Methode | Note |
|----------|---------|------|
| `/api/exercises/generate` | POST | Creer un exercice (exercise_type, age_group requis) |
| `/api/exercises/{id}/attempt` | POST | Soumettre une tentative (parametre `answer` ou `selected_answer`) |
| `/api/users/stats` | GET | Stats du user connecte (pas /api/users/{id}/stats) |

---

## 📚 RESSOURCES

- [pytest Documentation](https://docs.pytest.org/)
- [Vitest](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Playwright](https://playwright.dev/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Development Guide](DEVELOPMENT.md)

---

**Bon testing !** 🧪✅

