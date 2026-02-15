# Évaluation projet Mathakine

**Date :** 07/02/2026  
**Type :** Évaluation  
**Statut :** ⭐ Document de référence actuel

> Ce document remplace `BILAN_COMPLET.md` (nov. 2025) et `PLAN_ACTION_2026-02-06.md`. Méthode : analyse statique, benchmark Duolingo/Khan/Brilliant.

---

## 1. Scores par domaine

| Domaine | Score | Verdict |
|---------|-------|---------|
| Qualite code | 6/10 | Correct, refactoring necessaire |
| Tests | 3.5/10 | **Insuffisant - risque #1** |
| Performance | 4.5/10 | Monitoring inexistant |
| Securite | 5.5/10 | Bases OK, failles a corriger |
| Industrialisation (CI/CD) | 4.25/10 | Pipeline incomplete |
| Evolutivite | 5.5/10 | Monolithe OK pour maintenant |
| Documentation | 4/10 | Texte bon, technique manquant |
| Accessibilite / UX | 7/10 | **Point fort du projet** |
| **Score global** | **5.0/10** | **MVP+ fonctionnel, pas industrialise** |

---

## 2. Qualite du code (6/10)

### Backend (Starlette + SQLAlchemy)

**Points forts :**
- Separation claire handlers / services / models
- 49 routes API bien organisees par domaine
- Adapter pattern pour DB (`EnhancedServerAdapter`)
- Pydantic schemas pour la validation

**Points faibles :**
- **Handlers trop longs** : `generate_ai_challenge_stream()` = 774 lignes, `get_user_stats()` = 271 lignes
- ~~**Duplication massive** : auth check copie dans chaque handler~~ → **CORRIGE** (08/02/2026) : decorateurs `@require_auth`, `@optional_auth`, `@require_auth_sse` eliminent 40+ blocs dupliques
- **Duplication restante** : pattern DB session repete ~50 fois, `safe_parse_json()` duplique dans 3 fichiers
- **Typage insuffisant** : ~40-50% couverture, aucun handler n'a de type retour, pas de mypy
- **Error handling inconsistant** : mix de `ErrorHandler.create_error_response()` et `JSONResponse()` direct
- **Estimé ~15,000-20,000 LOC backend**

### Frontend (Next.js 16 + TypeScript)

**Points forts :**
- Next.js App Router bien structure
- 18 hooks custom, 3 stores Zustand
- `strict: true` dans tsconfig
- Lazy loading des modals et charts
- API client centralise avec refresh auto

**Points faibles :**
- **30+ types `any`** concentres dans les composants de visualisation
- **Duplication Exercise/Challenge** : cards, modals, solvers quasi-identiques
- **Pas de `React.memo`** sur les composants de listes
- **Quelques textes hardcodes** restants (AlphaBanner, AccessibilityToolbar)

---

## 3. Tests (3.5/10) - RISQUE CRITIQUE

### Etat factuel

| Element | Backend | Frontend |
|---------|---------|----------|
| Fichiers de test | 47 | 4 unit + 2 E2E |
| Framework | pytest | Vitest + Playwright |
| Infrastructure CI | GitHub Actions | Configuree (non active) |
| Couverture mesuree | **Non** | **Non** |
| Couverture estimee | <20% | <5% |

### Problemes critiques
- ~~**`continue-on-error: true`** dans le workflow CI~~ → **CORRIGE** (08/02/2026) : retire, les tests bloquent maintenant le CI
- **Pas de rapport de couverture** genere ni suivi
- Le workflow CI avance (multi-stage, bandit, safety) est **desactive** (`workflow_dispatch` only)
- Frontend : aucun test sur les hooks metier, les pages, ou les stores

### Corrections apportees (08/02/2026)
- ✅ Suite de tests migree de FastAPI TestClient vers httpx.AsyncClient (Starlette natif)
- ✅ 396 tests collectes, 0 erreurs de collection, CI passe (test + lint + frontend build)
- ✅ Fixtures async avec safeguards production DB (filtrage deletions, warnings)
- `BILAN_COMPLET.md` affirmait "Tests coverage 40% -> 60%+" : **non verifie, aucune metrique disponible**

### Benchmark
- Standard industrie minimum : 60% couverture
- Khan Academy : 80%+ couverture
- Duolingo : tests E2E automatises sur chaque PR

---

## 4. Performance (4.5/10)

### Frontend
- **Lazy loading** : modals, charts, SSR desactive pour widgets lourds (+)
- **`optimizePackageImports`** configure pour lucide-react, radix, recharts (+)
- **PWA** avec service worker et cache runtime (+)
- **framer-motion** charge partout (~100KB) sans lazy loading (-)
- ~~**jspdf + xlsx** (~350KB) non lazy-loaded, utilises uniquement pour export~~ → **CORRIGE** (09/02/2026) : jspdf mis a jour v4.1.0, xlsx (vulnerable, abandonne) remplace par exceljs

### Backend
- **Index DB** ajoutes (11 index) (+)
- **Pas de cache** : Redis dans requirements mais non configure (-)
- **Pas de pagination optimisee** visible (-)
- **Requetes N+1 probables** dans les handlers de stats (-)

### Monitoring : INEXISTANT
- **Sentry** : SDK installe (v1.40.6) mais `sentry_sdk.init()` **jamais appele**
- **Prometheus** : client installe (v0.19.0) mais aucun endpoint `/metrics`
- **Zero metrique** : pas de p50/p95/p99, pas de taux d'erreur, pas d'alerting
- **Zero APM** : pas de New Relic, Datadog, ou equivalent

### Correction du bilan precedent
- `BILAN_COMPLET.md` affirmait "CI/CD operationnel" : partiellement vrai, mais sans monitoring on vole a l'aveugle

---

## 5. Securite (5.5/10)

### Points forts
- JWT + bcrypt + refresh tokens + HttpOnly cookies
- Pydantic schemas pour validation input
- SQLAlchemy ORM (protection SQL injection)
- Sanitization des prompts AI (`prompt_sanitizer.py`)
- Test SQL injection existant (`test_queries.py`)

### Failles identifiees
1. **Password logge en mode debug** (`app/core/security.py` lignes 92-93) - CRITIQUE
2. **f-string SQL** dans `server/database.py` ligne 93 (risque faible, valeur constante)
3. **CORS origins hardcodees** au lieu de variable d'environnement
4. ~~**Pas de Dependabot/Renovate**~~ → **CORRIGE** (08/02/2026) : Dependabot configure (GitHub Actions hebdo + npm hebdo avec groupement React/Next.js)
5. **Rate limiting** mentionne dans challenge_handlers mais implementation non verifiee
6. ~~**Pas de scan de dependances** automatique actif~~ → **PARTIELLEMENT CORRIGE** : Dependabot actif pour les dependances, bandit/safety reste dans workflow desactive
7. ~~**Vulnerabilites npm** (3 : webpack low, jspdf critical 5 CVE, xlsx high)~~ → **CORRIGE** (09/02/2026) : 0 vulnerabilite npm (`npm audit` clean)

---

## 6. Industrialisation CI/CD (4.25/10)

### Ce qui existe
- GitHub Actions workflow `tests.yml` (push/PR sur main/master/develop)
- PostgreSQL service container dans CI
- Flake8 + Black + isort references
- Render deployment avec `render.yaml`
- Migrations auto au demarrage (`start_render.sh`)
- Loguru bien configure (rotation, compression, retention 30-60j)

### Ameliorations apportees (08-09/02/2026)
- ✅ **Dependabot** configure (GitHub Actions + npm, groupement React/Next.js)
- ✅ **CI fiabilise** : `continue-on-error` retire, Flake8 F821 corrige, tests data fixtures corriges
- ✅ **GitHub Actions mis a jour** : checkout v6, upload/download-artifact v6/v7, codecov v5, setup-python v6
- ✅ **npm 0 vulnerabilite** : jspdf v4.1.0, xlsx remplace par exceljs

### Ce qui manque encore
- **Deploiement automatise** : pas de CD depuis CI vers Render
- **Environnement staging** : uniquement production
- **Rollback automatique** : aucun
- **Pre-commit hooks** : non configures
- ~~**Frontend en CI** : pas de build validation~~ → **CORRIGE** : frontend build inclus dans CI
- **Prettier** : non configure pour le frontend
- **mypy** : non configure pour le backend
- **`pyproject.toml`** : pas de config unifiee des outils Python

---

## 7. Evolutivite (5.5/10)

### Architecture actuelle
```
Frontend Next.js (3000) --> Backend Starlette (10000) --> PostgreSQL
```
Monolithe simple, adapte au volume actuel.

### Limites identifiees
- **Colonne JSON `accessibility_settings`** stocke notifications, langue, timezone, privacy : anti-pattern a terme (pas de requetes SQL possibles sur ces champs)
- **Duplication Exercise/Challenge** : ajouter un 3e type d'activite obligerait a dupliquer cards, modals, solvers, hooks
- **Pas de queue** (Celery/Redis) pour les traitements longs (generation AI)
- **Pas d'event-driven** architecture
- **Pas d'API versioning**

---

## 8. Documentation (4/10)

### Points forts
- 15 docs actifs bien organises apres rationalisation
- `README_TECH.md` couvre architecture et 48 routes API
- Getting Started guide complet
- Scripts i18n de validation

### Points faibles
- **Pas d'OpenAPI/Swagger** : aucune documentation API interactive
- **Pas de diagrammes** : aucun C4, sequence, ERD
- **Pas de runbooks** : aucune procedure d'incident production
- **Pas d'ADR** (Architecture Decision Records)
- **Docs historiques trompeuses** : `BILAN_COMPLET.md` affiche "Zero Technical Debt" et "Production Ready" - c'est faux

---

## 9. Accessibilite / UX (7/10) - POINT FORT

### Points forts
- **WCAG** : ARIA complet, toolbar d'accessibilite avec 5 modes
- **Modes accessibilite** : contraste eleve, dyslexie, focus, taille, mouvement reduit
- **i18n** : 2 langues (FR/EN), ~1060 cles chacune, scripts de validation
- **Gamification** : badges, points, niveaux, rangs
- **Multi-theme** : spatial, minimaliste, ocean, neutre
- **PWA** : installation possible, cache offline

### Points faibles
- Pas de streaks, pas de spaced repetition
- Pas de leaderboard actif
- Pas de notifications push
- Pas d'A/B testing UX
- Quelques textes d'accessibilite hardcodes en francais

---

## 10. Corrections des affirmations precedentes

| Affirmation (BILAN_COMPLET.md, nov. 2025) | Realite (fev. 2026) |
|---|---|
| "Zero Technical Debt" | Faux. Duplication, handlers geants, types manquants, monitoring inexistant |
| "Tests coverage 60%+" | Non mesure. Estimation : <20% backend, <5% frontend |
| "Production Ready" | Trompeur. Pas de monitoring, pas d'error tracking, tests insuffisants |
| "DRY Principle" | Ameliore. Auth centralise via decorateurs (08/02), pattern DB session reste repete ~50 fois |
| "SOLID Principles" | Partiellement. SRP viole (handlers de 774 lignes) |
| "CI/CD operationnel" | Ameliore. CI fiabilise (continue-on-error retire, Dependabot actif, Actions mises a jour) |
| "95% lisibilite" | Subjectif et non mesure. Ameliore mais loin de 95% |
| "Backend 100% API (37 routes)" | Mis a jour : 49 routes API actuellement |
| References vers ARCHITECTURE.md, API.md | Ces fichiers ont ete archives dans `_ARCHIVE_2026/` |

---

## 11. Plan d'action priorise

### Niveau 1 - Quick wins a fort impact (1-2 jours)

| # | Action | Impact | Effort | Statut |
|---|--------|--------|--------|--------|
| 1 | **Activer Sentry** : ajouter `sentry_sdk.init()` dans `server/app.py` | Monitoring prod | 30 min | ⏳ A faire |
| 2 | **Retirer `continue-on-error: true`** du workflow CI | Tests fiables | 5 min | ✅ Fait (08/02) |
| 3 | **Supprimer le log de password** dans `security.py` | Securite | 5 min | ⏳ A faire |
| 4 | **Creer decorateur auth** pour eliminer le copier-coller | DRY, maintenabilite | 1h | ✅ Fait (09/02) - `@require_auth`, `@optional_auth`, `@require_auth_sse` dans `server/auth.py` |
| 5 | **Creer context manager DB session** | DRY, maintenabilite | 1h | ⏳ A faire |
| 6 | **Ajouter Dependabot/Renovate** | Securite dependances | 15 min | ✅ Fait (08/02) - `.github/dependabot.yml` configure (Actions + npm) |

### Niveau 1 bis - Quick wins supplementaires realises

| # | Action | Impact | Date |
|---|--------|--------|------|
| A | **Corriger vulnerabilites npm** (3→0) : jspdf v4.1.0, xlsx→exceljs | Securite | 09/02/2026 |
| B | **Migrer tests backend** vers httpx.AsyncClient (Starlette natif) | Fiabilite CI | 08/02/2026 |
| C | **Fixer Flake8 F821** (`chat_stream_error` scope) | CI verte | 08/02/2026 |
| D | **Fixer test data** : `age_group` NOT NULL dans fixtures CI | CI verte | 08/02/2026 |
| E | **Mettre a jour GitHub Actions** : checkout v6, artifacts v6/v7, codecov v5 | Securite CI | 08/02/2026 |
| F | **Configurer groupement Dependabot** : React/React-DOM ensemble | Stabilite deps | 08/02/2026 |

### Niveau 2 - Fondations solides (1 semaine)

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 7 | **Mesurer la couverture de test reelle** et publier | Visibilite qualite | 2h |
| 8 | **Ecrire tests pour les hooks critiques** (useAuth, useExercises) | Fiabilite | 4h |
| 9 | **Ajouter les types retour** sur tous les handlers backend | Maintenabilite | 3h |
| 10 | **Remplacer les `any`** dans les visualizations par des interfaces | Type safety | 3h |
| 11 | **Ajouter un build frontend** dans le CI | Regression | 30 min |
| 12 | **Configurer pre-commit hooks** (black, isort, eslint) | Qualite continue | 1h |

### Niveau 3 - Passage a l'echelle (2-4 semaines)

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 13 | **Decouper les handlers geants** (>200 lignes) | Maintenabilite | 1 semaine |
| 14 | **Abstraire le pattern Exercise/Challenge** | Evolutivite | 3 jours |
| 15 | **Generer OpenAPI/Swagger** depuis les routes | Documentation API | 2 jours |
| 16 | **Migrer `accessibility_settings` JSON** vers colonnes dediees | Performance DB | 1 jour |
| 17 | **Configurer Prometheus + dashboard** | Observabilite | 2 jours |
| 18 | **Creer environnement staging** | Deploiement safe | 1 jour |

---

## 12. Verdict global

**Mathakine est un MVP+ fonctionnel** avec une bonne base architecturale et un point fort en accessibilite/UX. Le projet est au-dessus de la moyenne pour un projet solo/small-team a ce stade.

**Les 3 risques bloquants** pour passer au stade suivant :
1. **Tests insuffisants** (3.5/10) - Chaque modification est un pari
2. **Monitoring inexistant** (1/10) - On vole a l'aveugle en production
3. **Duplication code** (4/10 DRY) - Chaque evolution coute double

**Comparaison honnete** :
- Vs Duolingo/Khan Academy : ~20-25% de leur maturite technique (normal : equipes de 100-500 ingenieurs)
- Vs un projet solo du meme stade : au-dessus de la moyenne grace a l'accessibilite, l'i18n, et la structure frontend
- Pour atteindre "production-grade" : les actions Niveau 1 et 2 sont necessaires

---

*Document genere le 07/02/2026*  
*Derniere mise a jour : 09/02/2026 (actions Niveau 1 partiellement completees)*  
*Prochaine evaluation recommandee : apres implementation complete du Niveau 1 (Sentry, password log, DB session manager)*
