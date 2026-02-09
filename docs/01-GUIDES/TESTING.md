# 🧪 TESTING GUIDE - MATHAKINE

**Version** : 3.0.0  
**Date** : 09 fevrier 2026 (mise a jour)  
**Audience** : Developpeurs, QA

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble](#vue-ensemble)
2. [Configuration tests](#configuration)
3. [Tests backend](#tests-backend)
4. [Tests frontend](#tests-frontend)
5. [CI/CD](#cicd)
6. [Best practices](#best-practices)

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
- **Unit tests** : 80%+
- **Integration tests** : 60%+
- **E2E tests** : Scénarios critiques
- **Global coverage** : 70%+

### Tests actuels (09/02/2026)
- ✅ **47 fichiers de tests** backend + 4 unit + 2 E2E frontend
- ✅ **396 tests collectes** (CI verte)
- ⚠️ **Couverture non mesuree** (pas de rapport genere en CI)
- ✅ **CI/CD automatise** : GitHub Actions (lint + test + frontend build), `continue-on-error` retire
- ✅ **Tests critiques** : auth, challenges, exercises
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

### Frontend (Jest + React Testing Library)

#### Installation
```bash
cd frontend
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

#### jest.config.js
```javascript
// frontend/jest.config.js
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  testMatch: [
    '**/__tests__/**/*.{js,jsx,ts,tsx}',
    '**/*.{spec,test}.{js,jsx,ts,tsx}'
  ],
  collectCoverageFrom: [
    'app/**/*.{js,jsx,ts,tsx}',
    'components/**/*.{js,jsx,ts,tsx}',
    'hooks/**/*.{js,jsx,ts,tsx}',
    'lib/**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
}

module.exports = createJestConfig(customJestConfig)
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

### Tests composants

```typescript
// frontend/__tests__/components/ChallengeCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ChallengeCard } from '@/components/challenges/ChallengeCard';

const mockChallenge = {
  id: 1,
  title: 'Test Challenge',
  description: 'Test description',
  challenge_type: 'SEQUENCE',
  difficulty_rating: 2.5,
};

describe('ChallengeCard', () => {
  it('renders challenge information', () => {
    render(<ChallengeCard challenge={mockChallenge} />);
    
    expect(screen.getByText('Test Challenge')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });
  
  it('displays difficulty rating', () => {
    render(<ChallengeCard challenge={mockChallenge} />);
    
    expect(screen.getByText(/2.5/)).toBeInTheDocument();
  });
  
  it('calls onSelect when clicked', () => {
    const onSelect = jest.fn();
    render(<ChallengeCard challenge={mockChallenge} onSelect={onSelect} />);
    
    const card = screen.getByRole('button');
    card.click();
    
    expect(onSelect).toHaveBeenCalledWith(mockChallenge);
  });
});
```

### Tests hooks

```typescript
// frontend/__tests__/hooks/useChallenges.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChallenges } from '@/hooks/useChallenges';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useChallenges', () => {
  it('fetches challenges successfully', async () => {
    const { result } = renderHook(() => useChallenges(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    
    expect(result.current.data).toBeDefined();
    expect(Array.isArray(result.current.data)).toBe(true);
  });
});
```

### Tests E2E (Playwright)

```typescript
// frontend/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('user can login successfully', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    
    // Remplir formulaire
    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'testpassword');
    
    // Soumettre
    await page.click('[type="submit"]');
    
    // Vérifier redirection vers dashboard
    await expect(page).toHaveURL('http://localhost:3000/dashboard');
    
    // Vérifier contenu
    await expect(page.locator('h1')).toContainText('Dashboard');
  });
  
  test('shows error with invalid credentials', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    
    await page.fill('[name="username"]', 'invalid');
    await page.fill('[name="password"]', 'wrong');
    await page.click('[type="submit"]');
    
    // Vérifier message d'erreur
    await expect(page.locator('.error-message')).toContainText('Invalid credentials');
  });
});
```

### Lancer les tests

```bash
cd frontend

# Tests unitaires
npm run test

# Tests avec coverage
npm run test:coverage

# Tests en mode watch
npm run test:watch

# Tests E2E
npm run test:e2e

# Tests E2E en mode UI
npm run test:e2e:ui
```

---

## 🔄 CI/CD {#cicd}

### GitHub Actions Workflow

```yaml
# .github/workflows/tests.yml (simplifie - voir le fichier reel pour la version complete)
# Mis a jour 08/02/2026 : GitHub Actions v6, Dependabot actif
name: Tests

on:
  push:
    branches: [main, master, develop]
  pull_request:
    branches: [main, master, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_mathakine
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v6       # Mis a jour via Dependabot
      
      - name: Set up Python
        uses: actions/setup-python@v6   # Mis a jour via Dependabot
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio httpx
      
      - name: Run tests
        env:
          TEST_DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_mathakine
          TESTING: "true"
        run: |
          pytest tests/ -v --cov=app --cov=server --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v5  # Mis a jour via Dependabot
        with:
          files: ./coverage.xml
          flags: backend
  
  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install & Build
        run: |
          cd frontend
          npm ci
          npm run build
```

> **Note** : Le workflow CI actuel n'utilise plus `continue-on-error: true` (retire le 08/02/2026). Un echec de test bloque le merge.

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

## 📚 RESSOURCES

- [pytest Documentation](https://docs.pytest.org/)
- [Testing Library](https://testing-library.com/)
- [Playwright](https://playwright.dev/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Development Guide](DEVELOPMENT.md)

---

**Bon testing !** 🧪✅

