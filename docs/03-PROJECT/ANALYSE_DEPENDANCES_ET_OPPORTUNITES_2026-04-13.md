# Analyse Dépendances Et Opportunités 2026-04-13

> **[ANALYSE PONCTUELLE — 2026-04-13]** Certaines recommandations ont pu être appliquées depuis. Vérifier avant d'agir sur les versions suggérées.

> Périmètre: dépendances Python de `requirements.txt`
> Date: 2026-04-13
> Source de vérité technique: code du dépôt + versions actuellement pinées + release notes officielles

## Objectif

Ce document isole les montées de version Python récentes et répond à trois questions:

1. quelles upgrades apportent une valeur réelle pour Mathakine
2. quelles upgrades sont surtout de la maintenance/sécurité
3. quelles opportunités techniques restent à exploiter dans le code

Le document ne traite pas les dépendances frontend.

## Contexte Runtime

- Python projet: `3.12`
  - [pyproject.toml](D:/Mathakine/pyproject.toml)
  - [runtime.txt](D:/Mathakine/runtime.txt)
  - [.python-version](D:/Mathakine/.python-version)
- Runtime HTTP réel: `Starlette + Uvicorn + Gunicorn`
  - [server/app.py](D:/Mathakine/server/app.py)
  - [enhanced_server.py](D:/Mathakine/enhanced_server.py)
- Validation/config: `pydantic + pydantic-settings`
  - [config.py](D:/Mathakine/app/core/config.py)
- Persistence: `SQLAlchemy + PostgreSQL`
  - [base.py](D:/Mathakine/app/db/base.py)
- IA: `openai`
  - [challenge_ai_service.py](D:/Mathakine/app/services/challenges/challenge_ai_service.py)
  - [exercise_ai_service.py](D:/Mathakine/app/services/exercises/exercise_ai_service.py)
- Test stack: `pytest + pytest-asyncio + pytest-cov + httpx`

## Lots Mergés Récemment

Lots explicitement visibles dans l’historique de `requirements.txt`:

- `sphinx 7.2.6 -> 9.1.0`
- `requests 2.32.5 -> 2.33.1`
- `uvicorn 0.41.0 -> 0.44.0`
- `pillow 12.1.1 -> 12.2.0`

Autres upgrades déjà présentes et encore pertinentes dans l’état actuel:

- `starlette 0.49.3 -> 0.52.1`
- `sqlalchemy 2.0.46/48 -> 2.0.49`
- `pydantic 2.12.5`
- `pydantic-settings 2.13.1`
- `pytest 9.0.2`
- `pytest-cov 7.1.0`
- `openai 2.24.0`
- `redis 7.2.1`
- `typer 0.24.1`

## Résumé Exécutif

### Dépendances à forte valeur réelle pour le projet

- `uvicorn`
- `starlette`
- `pytest-cov`
- `pydantic`
- `openai`

### Dépendances surtout utiles pour maintenance/sécurité

- `pillow`
- `requests`
- `sphinx`
- `sqlalchemy`

### Dépendances à challenger sur leur présence

- `requests`
- `typer`
- `aiofiles`
- `psutil`
- `pillow`

Ces packages ne montrent pas d’usage direct clair dans `app/`, `server/` ou `tests/` au moment de cette analyse, ou seulement un usage marginal indirect.

## Analyse Dépendance Par Dépendance

### 1. Uvicorn 0.44.0

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- [server/app.py](D:/Mathakine/server/app.py)
- démarrage production via `gunicorn ... uvicorn.workers.UvicornWorker`

Apport utile:

- `0.44.0`: keepalive pings pour `websockets-sansio`
- `0.43.0`: émission de `http.disconnect` au shutdown pour réponses streamées
- `0.42.0`: accumulation des bodies via `bytearray`, évite des coûts O(n^2) sur corps fragmentés
- `0.42.0`: fixes sur l’implémentation websockets sans-io

Lecture projet:

- utile directement pour votre surface `StreamingResponse`, SSE et websocket
- la panne Render rencontrée n’a pas été causée par Uvicorn lui-même, mais par l’entrypoint custom lazy corrigé dans [enhanced_server.py](D:/Mathakine/enhanced_server.py)

Verdict:

- upgrade à forte valeur
- déjà justifiée par le runtime réel

Opportunités restantes:

- ajouter un test d’intégration de shutdown propre pour une réponse streamée longue
- ajouter un smoke test websocket si la surface websocket devient critique

### 2. Starlette 0.52.1

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- usage massif de `Request`, `Response`, `Routing`, `Middleware`, `StreamingResponse`
- accès fréquents à `request.state.user` et `app.state.templates`
  - [server/handlers](D:/Mathakine/server/handlers)
  - [server/auth.py](D:/Mathakine/server/auth.py)
  - [server/app.py](D:/Mathakine/server/app.py)

Apport utile:

- `0.52.0`: accès dictionnaire typé à `State` pour meilleure sûreté de typage
- `0.51.0`: `allow_private_network` dans `CORSMiddleware`
- `0.52.1`: correctif mineur `typing_extensions`

Lecture projet:

- la nouveauté la plus utile pour Mathakine est le typage de `state`
- votre code utilise encore beaucoup `request.state.user` en mode dynamique
- c’est un vrai levier de robustesse backend, pas juste de propreté

Verdict:

- dépendance très utile
- potentiel sous-exploité aujourd’hui

Opportunité recommandée:

- lot `BACKEND-TYPED-STATE-01`
- introduire un `TypedDict` de state applicatif
- réduire les `getattr(request.state, "user", ...)` et accès dynamiques

### 3. pytest-cov 7.1.0

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- suite de tests backend active
- usage des seuils et rapports de couverture dans la CI

Apport utile:

- corrige le calcul du total de couverture, indépendamment des options de reporting
- évite que `--cov-fail-under` varie selon le type de rapport généré

Lecture projet:

- c’est directement pertinent vu les écarts déjà observés entre mesures locales et CI sur d’autres piles
- même si le sujet le plus visible a été côté frontend/Vitest, la logique de “coverage gate fiable” vaut aussi ici

Verdict:

- forte utilité opérationnelle

Opportunités restantes:

- stabiliser et documenter un seul chemin de vérité couverture backend dans la CI
- éviter les scripts locaux qui changent les totaux selon le reporter

### 4. pytest 9.0.2

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- base complète de tests backend

Apport utile:

- `pytest 9.0.0`: support natif des subtests
- `pytest 9.0.0`: configuration TOML native
- `pytest 9.0.0`: mode strict global
- `pytest 9.0.2`: correctifs de compatibilité et désactivation par défaut du terminal progress hors Windows

Lecture projet:

- l’apport immédiatement utile est surtout le mode strict et les subtests
- pas de nécessité de migration urgente
- le support TOML natif est intéressant mais non prioritaire tant que [pytest.ini](D:/Mathakine/pytest.ini) reste clair

Verdict:

- utile, mais pas un chantier urgent

Opportunités restantes:

- envisager `strict` plus tard quand le bruit résiduel de la suite aura encore baissé
- utiliser les subtests pour certaines batteries paramétrées/verbeuses

### 5. Pydantic 2.12.5

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- schémas API et validation
- settings
- validation de requêtes et contrats backend

Apport utile:

- `exclude_if` au niveau champ
- `ensure_ascii` pour la sérialisation JSON
- contrôle de `extra` au moment de `model_validate(...)`
- garde-fou explicite sur les incompatibilités `pydantic-core`
- diverses corrections autour de `FieldInfo`, sérialisation et JSON Schema

Lecture projet:

- `exclude_if` est utile pour des DTO plus propres quand certains champs n’apportent rien s’ils valent `0`, `None` ou un sentinel métier
- `extra=` par validation peut être utile pour durcir certains points d’entrée sans changer le comportement global du modèle
- vos modèles de config et schémas sont déjà nombreux, donc les garde-fous de compatibilité ont de la valeur

Verdict:

- utile et réellement exploitable

Opportunités restantes:

- lot ciblé sur quelques schémas de sortie pour utiliser `exclude_if`
- durcissement ponctuel de validations avec `model_validate(..., extra="forbid")` sur entrées sensibles

### 6. pydantic-settings 2.13.1

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- [config.py](D:/Mathakine/app/core/config.py)

Lecture projet:

- la valeur est surtout structurelle: stabilité de `BaseSettings` sur Python 3.12, cohérence avec Pydantic 2.x
- ici, le vrai sujet n’est pas une nouveauté majeure de package, mais l’exploitation correcte de votre couche config existante

Verdict:

- utile mais surtout comme socle de stabilité

Opportunités restantes:

- continuer à retirer les `os.getenv` dispersés hors `Settings`
- renforcer la centralisation config dans [config.py](D:/Mathakine/app/core/config.py)

### 7. OpenAI 2.24.0

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- [challenge_ai_service.py](D:/Mathakine/app/services/challenges/challenge_ai_service.py)
- [exercise_ai_service.py](D:/Mathakine/app/services/exercises/exercise_ai_service.py)
- [chat_handlers.py](D:/Mathakine/server/handlers/chat_handlers.py)

Constat actuel:

- le code reste centré sur `AsyncOpenAI.chat.completions.create(...)`
- l’upgrade vers `2.24.0` apporte des évolutions dans la famille `Responses`/websocket/realtime sur les versions proches `2.22+`
- `2.24.0` lui-même est plutôt mineur dans son diff

Lecture projet:

- la vraie opportunité n’est pas “2.24.0” isolément
- la vraie opportunité est que la branche 2.x récente ouvre une modernisation vers `Responses API` ou websocket natif si vous souhaitez un tutorat plus riche, du streaming plus structuré, ou des agents plus avancés

Verdict:

- stratégique
- pas un gain automatique sans refactor ciblé

Opportunités restantes:

- spike `OPENAI-RESPONSES-SPIKE-01`
- comparer `chat.completions` actuel vs `responses`
- n’ouvrir ce chantier que si le produit a besoin d’un vrai gain de structure ou de capacité

### 8. SQLAlchemy 2.0.49

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- omniprésent dans `app/models`, `app/db`, `app/repositories`, `app/services`

Apport utile:

- correctifs ORM / SQL / typing / PostgreSQL
- pas de nouveauté produit majeure détectée pour votre usage

Lecture projet:

- la valeur est surtout stabilité et réduction de risques
- vu votre surface SQLAlchemy, ces bugfixes comptent, mais ne changent pas l’architecture du projet

Verdict:

- important, mais surtout en maintenance

Opportunités restantes:

- pas de chantier “feature” spécifique lié à cette montée
- continuer le durcissement typé et les tests repository/service

### 9. Requests 2.33.1

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- aucun import direct trouvé dans `app/`, `server/`, `tests/`

Lecture projet:

- l’upgrade est saine côté sécurité/maintenance
- mais elle n’apporte pas de valeur produit visible si le package n’est pas utilisé directement

Verdict:

- faible utilité actuelle

Opportunité / action:

- challenger la nécessité même de garder `requests` en dépendance directe

### 10. Pillow 12.2.0

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- aucun import direct `PIL` trouvé dans `app/`, `server/`, `tests/`

Apport utile:

- surtout des correctifs sécurité
- amélioration des performances de chargement lazy plugins
- quelques ajouts API autour du texte/image

Lecture projet:

- tant qu’il n’y a pas de code image direct identifié dans le cœur applicatif, c’est principalement une dépendance de sécurité/compatibilité

Verdict:

- utile pour durcir
- faible gain fonctionnel immédiat

Opportunité / action:

- confirmer si Pillow est requis par un script/doc/worker encore actif
- sinon challenger son maintien en dépendance directe

### 11. Sphinx 9.1.0

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- docs/dev uniquement

Apport utile:

- `add_static_dir()` pour extensions docs
- fixes autodoc / MyST / LaTeX

Lecture projet:

- aucune valeur runtime
- utile seulement si vous investissez plus sérieusement dans un pipeline de doc

Verdict:

- faible priorité projet
- bon upgrade de maintenance

### 12. Redis 7.2.1

Version:

- [requirements.txt](D:/Mathakine/requirements.txt)

Usage réel:

- [rate_limit_store.py](D:/Mathakine/app/utils/rate_limit_store.py)
- [readiness_probe.py](D:/Mathakine/app/utils/readiness_probe.py)
- [diagnostic_pending_storage.py](D:/Mathakine/app/services/diagnostic/diagnostic_pending_storage.py)

Lecture projet:

- valeur runtime réelle
- mais la version actuelle n’ouvre pas d’opportunité fonctionnelle évidente sans besoin produit supplémentaire

Verdict:

- dépendance importante
- pas de chantier opportunité clair issu de cette version seulement

## Opportunités Priorisées

### Priorité 1

#### BACKEND-TYPED-STATE-01

But:

- exploiter Starlette 0.52 pour typer `request.state` et `app.state`

Pourquoi:

- énorme surface d’accès dynamique à `request.state.user`
- améliore robustesse, lisibilité, mypy et cohérence handler/runtime

ROI:

- élevé

### Priorité 2

#### BACKEND-DEPS-PRUNE-01

But:

- auditer puis justifier ou retirer les dépendances sans usage direct clair

Candidats:

- `requests`
- `typer`
- `aiofiles`
- `psutil`
- `pillow`

Pourquoi:

- réduire surface CVE
- réduire bruit Dependabot
- clarifier le vrai runtime du projet

ROI:

- élevé et peu risqué si fait proprement

### Priorité 3

#### PYDANTIC-SCHEMAS-HARDEN-01

But:

- exploiter `exclude_if` et le contrôle `extra` ciblé

Pourquoi:

- gain de robustesse API
- meilleur contrôle des sorties et des validations sensibles

ROI:

- moyen

### Priorité 4

#### OPENAI-RESPONSES-SPIKE-01

But:

- comparer l’usage actuel `chat.completions` à `responses`

Pourquoi:

- opportunité réelle seulement si vous voulez enrichir la couche IA

ROI:

- stratégique, mais plus risqué et moins urgent

## Dépendances À Faible Valeur Immédiate

Packages dont l’upgrade est saine mais n’ouvre pas d’opportunité projet évidente à court terme:

- `requests`
- `pillow`
- `sphinx`
- `sqlalchemy`
- `typer`

Cela ne veut pas dire “inutiles”, mais “maintenance first, pas d’exploitation produit évidente”.

## Dépendances À Reconsidérer

Paquets à challenger explicitement:

- `requests`
- `typer`
- `aiofiles`
- `psutil`
- `pillow`

Question de gouvernance à poser pour chacun:

- usage direct dans `app/`, `server/`, `tests`?
- usage indirect par un script actif de prod, de migration ou de doc?
- simple héritage historique plus jamais consommé?

## Position Recommandée

Si un seul lot doit partir ensuite, le meilleur choix est:

### `BACKEND-TYPED-STATE-01`

Raison:

- dépend directement d’une nouveauté utile déjà présente dans la stack
- améliore le code sans changer le comportement métier
- faible risque
- cohérent avec vos exigences de typage fort et séparation claire

## Sources

- [Uvicorn release notes](https://www.uvicorn.org/release-notes/)
- [Starlette release notes](https://www.starlette.io/release-notes/)
- [Pydantic changelog](https://docs.pydantic.dev/latest/changelog/)
- [Pydantic v2.12 release article](https://pydantic.dev/articles/pydantic-v2-12-release)
- [pytest changelog](https://docs.pytest.org/en/stable/changelog.html)
- [pytest-cov changelog](https://pytest-cov.readthedocs.io/en/latest/changelog.html)
- [Pillow 12.2.0 release notes](https://pillow.readthedocs.io/en/stable/releasenotes/12.2.0.html)
- [Requests community updates](https://requests.readthedocs.io/en/latest/community/updates/)
- [Sphinx changelog](https://www.sphinx-doc.org/en/master/changes/index.html)
- [SQLAlchemy 2.0 changelog](https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html)
- [OpenAI Python changelog](https://raw.githubusercontent.com/openai/openai-python/main/CHANGELOG.md)
