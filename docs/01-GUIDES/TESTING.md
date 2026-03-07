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
5. [Plan de test manuel — Environnement dev](#plan-test-manuel-dev)
6. [CI/CD](#cicd)
7. [Best practices](#best-practices)
8. [Modifications recentes](#modifications-recentes)

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

### Tests actuels (03/03/2026)
- ✅ **Backend** : 472 tests passent (dont 23 CSRF), 0 failures, ~30% couverture (app + server)
- ✅ **Frontend** : 61 tests (Vitest) — utils/lib/format (`hasAiTag`, `formatSuccessRate`), validations dashboard/exercise, composants (BadgeCard — alt descriptif), hooks
- ✅ **CI** : Tests + couverture backend et frontend, upload Codecov (flags backend/frontend)
- ✅ **Tests critiques** : auth, challenges, exercises, user_exercise_flow, admin analytics EdTech
- ✅ **Base de test separee** : `TEST_DATABASE_URL` obligatoire (protection production)
- ✅ **Tests async** : httpx.AsyncClient + pytest-asyncio (Starlette natif)

---

## ⚙️ CONFIGURATION TESTS {#configuration}

### Backend (pytest)

#### Commande unique (recommandé)
```bash
make test-backend-local
```
ou sans Make : `python scripts/test_backend_local.py` — démarre PostgreSQL (Docker si absent), init DB, pytest.

#### Quick start manuel avec Docker
> **Connection refused localhost:5432 ?** — Les tests backend nécessitent PostgreSQL. Avec Docker :

```bash
# 1. Démarrer PostgreSQL (postgres:15, port 5432)
docker run -d --name pg-mathakine -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15

# 2. Préparer la base de test (crée la base + migrations + données de test)
python scripts/check_local_db.py

# 3. Lancer les tests
python -m pytest tests/ -q -m "not slow"
```

Voir [CREATE_TEST_DATABASE.md](CREATE_TEST_DATABASE.md) pour plus d’options. Alternative tout-en-un : `make test-backend-local`.

#### Prérequis
> **Important** : Les tests backend nécessitent l'installation complète des dépendances.
> Sans `python-dotenv` (chargement du `.env`), `pytest` échouera au démarrage.
```bash
pip install -r requirements.txt
```

#### Installation minimale (CI, variables déjà définies)
```bash
pip install pytest pytest-cov pytest-asyncio httpx python-dotenv
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
# tests/unit/test_logic_challenge_service.py
import pytest
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from app.services.logic_challenge_service import LogicChallengeService

@pytest.mark.unit
def test_get_challenge(db_session):
    """Test récupération d'un défi logique par ID"""
    challenge = LogicChallenge(
        title="Test Get Challenge",
        description="Un défi de test",
        challenge_type="SEQUENCE",
        age_group="GROUP_10_12",
        correct_answer="42",
        solution_explanation="Explication",
        difficulty_rating=3.0,
    )
    db_session.add(challenge)
    db_session.commit()

    result = LogicChallengeService.get_challenge(db_session, challenge.id)

    assert result is not None
    assert result.id == challenge.id
    assert result.title == "Test Get Challenge"

@pytest.mark.unit
def test_list_challenges(db_session):
    """Test liste des défis logiques"""
    results = LogicChallengeService.list_challenges(db_session, limit=10)

    assert isinstance(results, list)
    assert all(hasattr(c, "title") and hasattr(c, "challenge_type") for c in results)
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

# Tests unitaires uniquement (services, logique, unicité routes)
pytest tests/unit/ -v

# Tests API / integration uniquement
pytest tests/api/ tests/integration/ tests/functional/ -v

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

### Plan de test manuel — Environnement dev {#plan-test-manuel-dev}

> Checklist pour valider l’interface manuellement en local. Backend et frontend doivent être démarrés (`make dev` ou `python enhanced_server.py` + `cd frontend && npm run dev`).

#### Pré-requis

| Étape | Action | Résultat attendu |
|-------|--------|------------------|
| 1 | Démarrer le backend | Serveur écoute (ex. port 8000) |
| 2 | Démarrer le frontend | App Next.js sur http://localhost:3000 |
| 3 | Créer ou se connecter avec un compte test | Authentification OK, redirection vers `/dashboard` ou `/onboarding` |

---

#### Profil (`/profile`)

| Étape | Action | Résultat attendu |
|-------|--------|------------------|
| 1 | Accéder à `/profile` (menu utilisateur → Profil) | Infos personnelles affichées (username, email masqué, tranche d’âge, thème) |
| 2 | Onglet « Infos personnelles » : modifier nom affiché (display_name) → Enregistrer | Toast succès, données mises à jour |
| 3 | Onglet « Préférences d’apprentissage » : modifier tranche d’âge → Enregistrer | Toast succès, préférences enregistrées |
| 4 | Onglet « Sécurité » : ouvrir le formulaire de changement de mot de passe | Formulaire affiché (mot de passe actuel, nouveau, confirmation) |
| 5 | Changer le mot de passe avec valeurs valides | Toast succès, déconnexion puis reconnexion avec nouveau MDP |
| 6 | Changer le mot de passe avec mauvais mot de passe actuel | Erreur affichée, MDP inchangé |

---

#### Paramètres et suppression de compte (`/settings`)

| Étape | Action | Résultat attendu |
|-------|--------|------------------|
| 1 | Accéder à `/settings` | Langue, notifications, confidentialité, données, sessions, zone de suppression visibles |
| 2 | Modifier une préférence (ex. langue) → Enregistrer | Toast succès |
| 3 | Onglet « Sessions actives » : vérifier la liste | Sessions actuelles affichées (appareil, date, etc.) |
| 4 | Révocation d’une session autre que la courante | Session retirée de la liste (ou erreur explicite si non supporté) |
| 5 | Compte vérifié : cliquer « Supprimer mon compte » → confirmer | Redirection vers `/`, compte supprimé, déconnexion |
| 6 | Compte non vérifié : supprimer le compte | Idem — suppression possible (RGPD) sans vérification préalable |

---

#### Classement (`/leaderboard`)

| Étape | Action | Résultat attendu |
|-------|--------|------------------|
| 1 | Accéder à `/leaderboard` (ou widget dashboard → lien) | Liste des utilisateurs avec rangs, points, niveaux |
| 2 | Filtrer par tranche d’âge (ex. 8–10 ans) | Classement filtré selon la tranche |
| 3 | Filtrer « Tous les âges » | Retour au classement global |

---

#### Progression et Dashboard (`/dashboard`)

| Étape | Action | Résultat attendu |
|-------|--------|------------------|
| 1 | Accéder à `/dashboard` | Stats (exercices, défis, niveau), graphiques, recommandations |
| 2 | Changer la plage temporelle (7j, 30j, 90j) | Données mises à jour |
| 3 | Vérifier le widget « Progression des défis » | Nb complétés, progression par type affichée |
| 4 | Vérifier le widget « Recommandations » | Exercices/défis suggérés avec liens cliquables |
| 5 | Accéder à `/badges` | Badges débloqués et non débloqués affichés |

---

#### Exercices (`/exercises`, `/exercises/[id]`)

| Étape | Action | Résultat attendu |
|-------|--------|------------------|
| 1 | Accéder à `/exercises` | Liste d’exercices avec cards |
| 2 | Filtrer par type (ex. calcul, géométrie) | Liste filtrée |
| 3 | Filtrer par tranche d’âge | Liste filtrée |
| 4 | Activer « Masquer les complétés » | Exercices complétés masqués |
| 5 | Recherche texte | Résultats filtrés (si implémenté côté API) |
| 6 | Paginer (page 2) | Nouveaux exercices affichés |
| 7 | Cliquer sur un exercice → ouvrir `/exercises/[id]` | Page de résolution chargée |
| 8 | Soumettre une réponse correcte | Feedback succès, progression mise à jour |
| 9 | Soumettre une réponse incorrecte | Feedback erreur, possibilité de réessayer |
| 10 | Retour à la liste | Progression et stats actualisées (badge complété si applicable) |

---

#### Défis (`/challenges`, `/challenge/[id]`)

| Étape | Action | Résultat attendu |
|-------|--------|------------------|
| 1 | Accéder à `/challenges` | Liste de défis avec cards |
| 2 | Filtrer par type, tranche d’âge, masquer complétés | Liste filtrée |
| 3 | Paginer | Nouveaux défis affichés |
| 4 | Cliquer sur un défi → ouvrir `/challenge/[id]` | Page de résolution chargée |
| 5 | Résoudre un défi (selon type : logique, visuel, etc.) | Feedback et mise à jour progression |
| 6 | Retour liste | Progression des défis cohérente avec le dashboard |

---

#### Recommandations

| Étape | Action | Résultat attendu |
|-------|--------|------------------|
| 1 | Sur le dashboard : afficher le widget Recommandations | Exercices et/ou défis suggérés |
| 2 | Cliquer sur une recommandation (exercice) | Redirection vers `/exercises/[id]` |
| 3 | Cliquer sur une recommandation (défi) | Redirection vers `/challenge/[id]` |

---

#### Utilisateur non vérifié

| Étape | Action | Résultat attendu |
|-------|--------|------------------|
| 1 | Se connecter avec un compte non vérifié | Bannière « Vérifiez votre email » affichée |
| 2 | Accéder à `/profile` | Profil affiché (lecture, édition limitée selon implémentation) |
| 3 | Accéder à `/settings` → Supprimer mon compte | Compte supprimé sans vérification préalable |

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

### Contexte BDD test / prod (refactor 22/02/2026)

| Environnement | Base de données | Initialisation |
|---------------|-----------------|----------------|
| **CI (GitHub Actions)** | `test_mathakine` (PostgreSQL 15) | Schéma uniquement (`create_tables`). Pas de seed ObiWan. Tests isolés via fixtures. |
| **Développement local (Docker)** | `test_mathakine` ou similaire | Optionnel : `create_tables_with_test_data()` pour seed de démo (scripts). |
| **Production** | Base dédiée prod | Jamais de seed. Migrations Alembic uniquement. |

> **Important** : La BDD prod est totalement isolée. Le refactor CI (suppression du seed global) n'impacte que l'environnement de test. Risque minimal.

### GitHub Actions Workflow (.github/workflows/tests.yml)

| Job | Actions |
|-----|---------|
| **test** | PostgreSQL 15, schema init uniquement (sans seed), pytest (unit+api+integration), coverage + JUnit XML, upload Codecov (coverage + test_results, flag backend) |
| **lint** | flake8, black, isort, mypy (backend) |
| **frontend** | npm ci, tsc --noEmit, ESLint, vitest --coverage --reporter=junit, upload Codecov (coverage + test_results, flag frontend), build |

Un echec de test ou de lint bloque le merge. Les rapports de couverture sont envoyes a Codecov (backend + frontend separes).

### Test d'unicite des routes (15/02/2026)

Le fichier `tests/unit/test_routes_uniqueness.py` verifie qu'aucune route API ne partage le meme couple (method, path). Une collision provoquerait un routage errone vers Starlette. Le test parcourt `get_routes()` (Route + Mount) et echoue si un doublon est detecte.

**Configuration couverture :**
- `.coveragerc` — sources (app, server), `relative_files=True` (chemins relatifs pour Codecov CI), exclusions, rapport XML
- **Codecov** : ajouter `CODECOV_TOKEN` dans GitHub Secrets. Installer l'[app Codecov](https://github.com/apps/codecov) pour le badge (sinon GitHub affiche "unknown").

---

## 📌 RÈGLE PROJET : TESTS SYSTÉMATIQUES {#regle-tests}

> **À chaque nouvelle fonctionnalité, implémentation ou correction** : challenger systématiquement la pertinence de créer ou mettre à jour un test.
>
> - **Nouvelle fonctionnalité** → envisager 1+ tests (unitaire ou intégration selon le périmètre)
> - **Nouvelle implémentation** (service, handler, utilitaire) → au minimum 1 test de non-régression
> - **Correction de bug** → ajouter un test qui aurait détecté le bug (test de régression)
>
> Si le test n’est pas pertinent (ex. changement cosmétique, config), le documenter brièvement dans le commit.

**Références :**
- Plan 4.1 (random_offset challenge_service) : [AUDIT_BACKEND § Plan 4.1](../03-PROJECT/AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md#plan-41-à-100--random_offset-challenge_service)

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

> **REGLE ABSOLUE** : Aucun test ne doit créer de données (attempts, progress, recommendations) au nom de ces utilisateurs. Aucun `delete()` sans `.filter()` n'est autorise sur les tables partagees (attempts, progress, exercises, users).

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

### 03/03/2026 – Audit Architecture Backend Phases 0→4

| Domaine | Modification |
|---------|---------------|
| **Phase 2** | `test_queries.py` supprimé (13 tests obsolètes, `queries.py` dead code supprimé). `test_auth_service.py` : 33 tests adaptés (retour tuple, plus d'HTTPException). |
| **Phase 3** | Nouveaux fichiers de test : `test_challenge_answer_service.py` (47 tests caractérisation), `test_chat_service.py` (19 tests), `test_admin_*.py` (services décomposés). |
| **Phase 4.5** | `test_transaction.py`, `test_db_adapter.py`, `test_exercise_service.py`, `test_logic_challenge_service.py`, `test_user_service.py` : API booléenne → exceptions (`pytest.raises(DatabaseOperationError/UserNotFoundError/…)`). |
| **Résultat** | 472 tests, 0 failures (vs ~526 avant, dont 13 obsolètes supprimés). |
| **Référence** | [AUDIT_ARCHITECTURE_BACKEND_2026-03.md](../03-PROJECT/AUDIT_ARCHITECTURE_BACKEND_2026-03.md) |

### 02/03/2026 – CSRF centralisé (audit H6), nettoyage code (audit cleanup)

| Domaine | Modification |
|---------|---------------|
| **Sécurité** | `CsrfMiddleware` centralisé dans `server/middleware.py` — protège automatiquement tous les endpoints state-changing. Appels manuels `validate_csrf_token()` supprimés des handlers. |
| **Frontend** | `apiRequest()` injecte automatiquement `X-CSRF-Token` depuis le cookie. Injections manuelles supprimées de `useSettings`, `useProfile`, `reset-password/page.tsx`. |
| **Nouveaux tests** | `tests/unit/test_csrf_middleware.py` : 23 tests unitaires (config + dispatch). `tests/unit/test_auth_middleware.py` : `test_leaderboard_get_requires_auth` (H7). |
| **Fixes audit C1-H8** | Refresh token fallback durci, soustraction choices, DetachedInstanceError, dead code BadgeService, route GET /api/exercises/generate supprimée, leaderboard sorti de la whitelist publique. |
| **Référence** | [AUDIT_CODE_CLEANUP_2026-03-01.md](../03-PROJECT/AUDIT_CODE_CLEANUP_2026-03-01.md) — 47 findings, ~30 corrigés |

### 22/02/2026 – Mypy CI, types critiques (audit backend 5.2)

| Domaine | Modification |
|---------|---------------|
| **CI lint** | mypy ajouté au job lint : `mypy app/ server/ --ignore-missing-imports` |
| **Types critiques** | adapter.list_active(limit, offset) Optional[int], error_handler.create_error_response(include_details) Optional[bool], pyproject overrides no-any-return pour modules critiques |
| **Référence** | [AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md](../03-PROJECT/AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md) § 5.2 |

### 22/02/2026 – Refactor CI ObiWan, couverture ExerciseService

| Domaine | Modification |
|---------|---------------|
| **CI** | Initialisation DB : schéma uniquement (`create_tables`), suppression du seed global ObiWan. Tests isolés via fixtures. |
| **ExerciseService** | 3 tests unitaires pour `submit_answer_result` : réponse correcte, incorrecte, exercice inexistant (zone critique P2). |
| **Scripts locaux** | `check_local_db.py`, `test_backend_local.py` : variable `SKIP_SEED=true` pour schéma seul (aligné CI). Par défaut : schéma + seed. |
| **test_challenge_service_integration** | Fix flaky : filtre `LogicChallengeType.SEQUENCE.value`, titre unique, `limit=100` pour `list_challenges`. |

### 26/02/2026 – Refactoring auth service, tests unitaires

| Domaine | Modification |
|---------|--------------|
| **auth_handlers** | `verify_email` et `api_reset_password` passent par `AuthService.verify_email_token`, `AuthService.reset_password_with_token` — plus d'accès DB direct |
| **user_handlers** | Réponse `PUT /api/users/me` inclut `is_email_verified` |
| **Tests unitaires** | `test_auth_service.py` : `test_verify_email_token_*`, `test_reset_password_with_token_*` (succès, invalid, expired, already_verified) |
| **Tests API** | `test_auth_flow.py` : `test_verify_email_success`, `test_verify_email_invalid_token` ; `test_user_endpoints.py` : régression `is_email_verified` sur mise à jour profil |
| **Documentation** | `AUTH_FLOW.md` : mention AuthService ; [INVENTAIRE_HANDLERS_DB_DIRECTE](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INVENTAIRE_HANDLERS_DB_DIRECTE.md) : auth refactoré ; `CHANGELOG.md` 2.2.2-alpha.1 |

### 15/02/2026 – Quality gates CI, test unicité routes

| Domaine | Modification |
|---------|---------------|
| **Test unicité routes** | `tests/unit/test_routes_uniqueness.py` : détecte les collisions (method, path) dans `get_routes()`. Échoue si deux routes partagent le même couple. |
| **CI backend** | Séparation unit (tests/unit/) et integration (tests/api/, integration/, functional/). `coverage combine` pour agréger la couverture. |
| **CI frontend** | `npm run lint` (ESLint) ajouté avant tests et build. |

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
| `/api/exercises/generate` | POST | Creer un exercice (`exercise_type` requis ; `age_group` optionnel, resolu automatiquement si `adaptive=true` + utilisateur authentifie) |
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

