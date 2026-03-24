# Audit Technique -- Mathakine -- 2026-03-22
> ⚠️ OBSOLETE comme source de verite runtime - snapshot historique de revue conserve pour trace.
> La reference actuelle pour la gouvernance IA runtime et l'observabilite est [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md).

---

## 0. Corrections post-audit appliquées (23-24/03/2026)

Suivi des findings de cet audit traités dans les sessions du 23 et du 24/03/2026.

| Ref | Finding | Statut | Commit / Référence |
|-----|---------|--------|--------------------|
| **T1** | Race condition gamification — `with_for_update()` absent | ✅ CORRIGÉ | `fix(gamification): guard with_for_update to PostgreSQL only (SQLite compat)` — garde dialect-aware `bind.dialect.name == "postgresql"` |
| **A4** | `GamificationService.apply_points` non appelé sur exercices standard | ✅ CORRIGÉ | `feat(gamification): apply points on correct exercise answer (EXERCISE_COMPLETED source)` — `PointEventSourceType.EXERCISE_COMPLETED` ajouté, appel dans `exercise_attempt_service.py` |
| **P4** | `func.random()` O(n) dans `list_challenges` | ✅ CORRIGÉ | `perf(challenges): replace func.random() O(n) with random_offset O(1) fallback` — `count()` + `random_offset` pour le cas `total=None` |
| **D5** | Endpoints gamification non documentés dans `API_QUICK_REFERENCE` | ✅ CORRIGÉ | Section gamification ajoutée (06/03/2026) — `point_events`, `apply_points`, surfaces `/me` + `/api/badges/stats` |
| **D6** | Pas d'ADR pour les décisions d'architecture | ✅ CORRIGÉ | `docs/05-ADR/` créé + `ADR-001-starlette-vs-fastapi.md` (23/03/2026) |
| **D8** | `REDIS_URL` absente de `.env.example` | ✅ CORRIGÉ | Section "Rate Limiting (Redis)" ajoutée dans `.env.example` avec commentaire crash prod (23/03/2026) |
| **B5** | Condition tautologique `!backendResponse.ok && status !== 200` | ✅ CORRIGÉ | DRY-1 — simplifié en `if (!backendResponse.ok)` |
| **B8 / B10** | Résolution backend divergente + `chat/stream` sans guard prod | ✅ CORRIGÉ | DRY-1 — helper partagé `frontend/lib/api/backendUrl.ts`, fallback localhost réservé au dev, validation URL prod explicite |
| **PR4** | Pas de `done` dans le flux SSE exercices | ✅ CORRIGÉ | DRY-2 — `done` émis sur succès et fins gérées (validation/persistance) |
| — | Logs SMTP/email exposent PII (`to_email`, `smtp_user`) | ✅ CORRIGÉ (hors audit initial) | `fix(security): mask PII in SMTP/email service logs` — helpers `_mask_email()` + `_mask_user()` dans `email_service.py` |
| **B4** | Routes chat proxy sans auth | ✅ REQUALIFIÉ | Décision produit assumée : chat public rate-limité ; non traité comme bug correctif |

**Score réestimé post-corrections** : ~7.8–8.0 / 10 (T1 + A4 + P4 étaient les 3 findings les plus critiques de cet audit).

**Encore ouvert (priorité conservée)** : B1 (fuite mémoire TokenTracker), B2 (double filtrage is_active/is_archived), B6 (NPE auto_correct_challenge), P1 (timeout exercices IA), P5 (circuit-breaker).

---

## Resume executif

**Score de sante globale : 7.0 / 10** → **~8.0 / 10** post-corrections 23-24/03/2026 (T1, A4, P4, D5, D6, D8, B5, B8/B10, PR4 résolus)

Le projet Mathakine presente une architecture backend bien structuree (separation service/handler/repository, policies typees, validations AI) et un frontend Next.js convenable. Cependant, l'audit revele des problemes d'ingenierie significatifs qui meritent attention avant le prochain palier de croissance.

### 3 risques prioritaires

1. **Fuite memoire en production (CRITIQUE)** -- Le `TokenTracker` et `generation_metrics` stockent tout en memoire sans aucune rotation ni limite. En production sous charge IA, la memoire du processus croit indefiniment.

2. **Double filtrage contradictoire sur `list_challenges` (MAJEUR)** -- La fonction filtre sur `is_active == True` en dur puis re-filtre via `_apply_challenge_filters` sur `is_archived == False` avec un parametre `active_only`. Les deux filtres coexistent sans coherence, ce qui peut exclure des resultats de facon inattendue.

3. **Resilience OpenAI cote exercices (MAJEUR)** -- Les exercices IA gardent des points de fragilite historiques hors micro-lot DRY (timeouts/retry etaient un des enjeux initiaux de cet audit). Le point "chat public sans auth" a ete requalifie depuis comme **decision produit assumee**, pas comme bug correctif.

---

## Volet 1 -- Bugs apparents

### Critiques

#### B1. Fuite memoire -- TokenTracker sans limite de taille
- **Fichier** : `app/utils/token_tracker.py:20-21`
- **Description** : `_usage_history` et `_daily_totals` sont des `defaultdict` qui grandissent indefiniment. Aucune rotation, aucun TTL, aucun plafond. En production avec generation IA reguliere, ceci constitue une fuite memoire lineaire.
- **Impact** : OOM apres des jours/semaines de fonctionnement continu, crash du serveur.
- **Recommandation** : Implementer une rotation par fenetre glissante (garder max N jours ou max N records) ou migrer les metriques vers une table SQL / Redis avec TTL.

#### B2. Double filtrage contradictoire dans `list_challenges` et `count_challenges`
- **Fichier** : `app/services/challenges/challenge_service.py:353` et `challenge_service.py:231`
- **Description** : `list_challenges` applique `.filter(LogicChallenge.is_active == True)` en dur (ligne 353), puis `_apply_challenge_filters` applique `.filter(LogicChallenge.is_archived == False)` si `active_only=True` (ligne 231). Ce sont deux colonnes differentes (`is_active` vs `is_archived`). La semantique est confuse : un challenge avec `is_active=True` et `is_archived=True` passe le premier filtre mais est exclu par le second.
- **Impact** : Comportement de filtrage imprevisible, resultats potentiellement incorrects dans la liste frontend.
- **Recommandation** : Unifier la logique de filtrage. Supprimer le filtre en dur et deleguer entierement a `_apply_challenge_filters`.

#### B3. `get_challenge_stats` effectue 3 requetes separees au lieu d'une
- **Fichier** : `app/services/challenges/challenge_service.py:554-601`
- **Description** : `get_challenge_stats` effectue 3 requetes SQL distinctes (total_attempts, correct_attempts, unique_users) alors que `record_attempt` (ligne 528-537) montre deja le pattern correct avec une seule requete agregee. Ce n'est pas seulement un probleme de performance, c'est aussi un bug de coherence : entre les 3 requetes, des tentatives peuvent etre ajoutees, donnant des stats incoherentes (ex: correct_attempts > total_attempts si un insert concurrent survient).
- **Impact** : Stats incoherentes sous charge, gaspillage de connexions DB.
- **Recommandation** : Fusionner en une seule requete agregee comme dans `record_attempt`.

### Majeurs

#### B4. Endpoints chat sans authentification
- **Fichier** : `frontend/app/api/chat/route.ts:38` et `frontend/app/api/chat/stream/route.ts:27`
- **Description** : Contrairement aux routes `generate-ai-stream` (exercices et defis) qui verifient `request.cookies.get("access_token")`, les routes chat transmettent les requetes au backend sans aucune verification d'identite cote proxy Next.js. La requete backend elle-meme n'a aucun header Cookie transmis.
- **Impact** : Tout utilisateur non authentifie peut generer du trafic OpenAI, avec un cout financier direct et un risque d'abus.
- **Recommandation** : Ajouter la verification d'authentification dans les deux routes chat, alignee sur le pattern des routes SSE.

#### B5. Condition tautologique dans le proxy SSE
- **Fichier** : `frontend/app/api/exercises/generate-ai-stream/route.ts:86`
- **Description** : `if (!backendResponse.ok && backendResponse.status !== 200)` -- la condition `!backendResponse.ok` est deja vraie quand status n'est pas dans 200-299. La deuxieme condition `status !== 200` est donc toujours vraie quand `!ok` l'est (sauf pour les status 201-299, qui sont ok). La condition revient a `!backendResponse.ok`, la deuxieme clause est inutile.
- **Impact** : Code mort / confusion de lecture. Aucun impact fonctionnel immediat, mais indique une incomprehension de l'API `Response.ok`.
- **Recommandation** : Simplifier en `if (!backendResponse.ok)`.

#### B6. `auto_correct_challenge` peut lever une exception non catchee
- **Fichier** : `app/services/challenges/challenge_validator.py:527`
- **Description** : Quand `expected_answer` est `None` (ligne 518, `expected_answer = analyze_pattern(...)` retourne `None`) et qu'on passe au bloc ligne 527 `if expected_answer.upper() not in ...`, cela leve `AttributeError: 'NoneType' object has no attribute 'upper'`. Le guard `if expected_answer:` (ligne 519) est seulement dans le bloc d'assignation `corrected["correct_answer"]`, mais la ligne 527 est hors du guard.
- **Impact** : Crash silencieux de la correction automatique des challenges PATTERN, l'erreur est catchee par le handler SSE mais le challenge est rejete.
- **Recommandation** : Deplacer la mise a jour de l'explication (lignes 526-532) dans le bloc `if expected_answer:`.

#### B7. Variable `generation_success` inutilisee
- **Fichier** : `app/services/challenges/challenge_ai_service.py:229`
- **Description** : La variable `generation_success` est declaree a `False`, mise a `True` (ligne 471) mais jamais lue par la suite. Code mort.
- **Impact** : Aucun impact fonctionnel, mais indique un mecanisme de suivi incomplet.
- **Recommandation** : Retirer la variable ou l'utiliser (ex: compteur de metriques).

#### B8. `BACKEND_URL` evalue au top-level du module
- **Fichier** : `frontend/app/api/challenges/generate-ai-stream/route.ts:6-9` et `exercises/generate-ai-stream/route.ts:6-9`
- **Description** : `BACKEND_URL` est calcule au moment de l'import du module (top-level const). En Next.js avec le runtime edge/node, cette valeur est figee au moment du build/premier chargement. Si `NEXT_PUBLIC_API_BASE_URL` est modifie par la suite (ex: container restart), la valeur ne change pas. La fonction `getBackendUrl()` recalcule partiellement, mais `BACKEND_URL` reste la valeur initiale.
- **Impact** : Potentiel mauvais routage si l'env var change en cours de vie du processus.
- **Recommandation** : Lire l'env var exclusivement dans `getBackendUrl()` sans const module-level.

### Mineurs

#### B9. `hasMore` jamais calcule cote backend
- **Fichier** : `frontend/hooks/usePaginatedContent.ts:111`
- **Description** : `hasMore: data?.hasMore ?? false` -- le backend retourne `items` et `total` mais jamais `hasMore`. Ce champ sera toujours `false`, ce qui desactive la pagination infinie cote frontend.
- **Impact** : Pagination infinie non fonctionnelle si implementee cote composant.
- **Recommandation** : Calculer `hasMore` cote frontend (`skip + limit < total`) ou l'ajouter a la reponse backend.

#### B10. Le `chat/stream` proxy ne verifie pas la prod en dur
- **Fichier** : `frontend/app/api/chat/stream/route.ts:22`
- **Description** : Contrairement aux autres proxies SSE, la route chat stream utilise `"http://localhost:10000"` comme fallback sans aucune garde production. Le fallback est inconditionnel (pas de check `process.env.NODE_ENV === "production"`).
- **Impact** : En production sans `NEXT_PUBLIC_API_BASE_URL` defini, les requetes chat sont routees vers localhost (connection refused).
- **Recommandation** : Ajouter la meme validation production que les routes SSE.

#### B11. `isCompleted` via `.includes()` -- O(n) par carte
- **Fichier** : `frontend/hooks/useCompletedItems.ts:43`
- **Description** : `isCompleted: (exerciseId: number) => (data || []).includes(exerciseId)` effectue une recherche lineaire. Avec 500+ exercises completes et 50 cartes affichees, c'est 25000 comparaisons par render.
- **Impact** : Performance degradee sur grands jeux de donnees.
- **Recommandation** : Convertir `data` en `Set<number>` une seule fois et utiliser `.has()`.

---

## Volet 2 -- Axes d'amelioration

### Architecture & Couplage

#### A1. Duplication de la logique de construction du payload utilisateur
- **Fichiers** : `app/services/auth/auth_session_service.py:27-61` (`build_authenticated_user_payload`) et `auth_session_service.py:131-204` (`get_current_user_payload`)
- **Description** : Deux fonctions construisent le meme type de payload utilisateur avec des champs legerement differents (l'une ajoute `is_authenticated`, l'autre non ; l'une utilise `int(getattr(user, "total_points", None) or 0)`, l'autre `user.total_points if hasattr(user, "total_points") else 0`). Trois patterns d'acces aux attributs coexistent : `getattr(user, x, None)`, `hasattr(user, x) + user.x`, et `user.x if hasattr(user, x) else default`.
- **Impact** : Drift semantique entre les deux payloads, risque de divergence future.
- **Recommandation** : Fusionner en une seule fonction parametree.

#### A2. `challenge_service.py` reste un "god module"
- **Fichier** : `app/services/challenges/challenge_service.py` (603 lignes)
- **Description** : Ce fichier regroupe creation, lecture, mise a jour, suppression, listing, comptage, statistiques, et enregistrement de tentatives. Malgre l'extraction de `challenge_api_mapper`, `challenge_query_service`, etc., le module reste le point central. L'extraction est partielle : `get_challenge_for_api` (ligne 202) delegue a `LogicChallengeService.get_challenge` puis a `challenge_to_detail_dict`, mais `get_challenge` (ligne 184) reste ici avec son propre filtre `is_active`.
- **Recommandation** : Extraire `record_attempt` et `get_challenge_stats` vers `challenge_attempt_service`, et `create_challenge` vers un `challenge_creation_service`.

#### A3. Inconsistance entre flux exercices et defis
- **Description** : Les exercices utilisent `ai_generation_policy.py` (allowlist, families, capabilities) avec un systeme typee elegant. Les defis utilisent `ai_config.py` (maps par type, TEMPERATURE_MAP, etc.) avec `challenge_ai_model_policy.py` par-dessus. Les deux systemes coexistent sans partager la meme abstraction.
- **Fichiers** : `app/core/ai_generation_policy.py` vs `app/core/ai_config.py`
- **Impact** : Toute modification de la politique modele doit etre faite en double.
- **Recommandation** : Unifier sous une seule abstraction `WorkloadModelPolicy` parametree par workload (exercises/challenges).

#### A4. GamificationService n'est pas appele depuis `submit_answer`
- **Fichier** : `app/services/exercises/exercise_attempt_service.py`
- **Description** : `submit_answer` appelle `update_user_streak`, `check_and_award_badges`, `record_exercise_completed` (daily challenge), mais jamais `GamificationService.apply_points` pour les exercices standard. Les points ne sont attribues que via badges et daily challenges. Un exercice reussi sans badge debloque ne rapporte zero point.
- **Impact** : Le systeme de points est incomplet -- l'apprenant ne voit pas de progression immediate.
- **Recommandation** : Ajouter un appel `apply_points` avec un `PointEventSourceType.EXERCISE_COMPLETED`.

### Performance & Resilience

#### P1. Appels OpenAI sans timeout explicite cote exercices
- **Fichier** : `app/services/exercises/exercise_ai_service.py:215`
- **Description** : `AsyncOpenAI(api_key=settings.OPENAI_API_KEY)` est instancie sans `timeout`. Le client utilise le timeout par defaut (600s). Cote defis, le timeout est configure via `ai_params["timeout"]` (90-180s).
- **Impact** : Un appel exercice IA bloque peut tenir 10 minutes avant de timeout.
- **Recommandation** : Configurer un timeout explicite aligne sur la policy exercices (90s par defaut).

#### P2. Pas de retry cote exercices IA
- **Fichier** : `app/services/exercises/exercise_ai_service.py:255`
- **Description** : `stream = await client.chat.completions.create(**api_kwargs)` -- aucun retry autour de cet appel. Cote defis, `create_stream_with_retry` utilise tenacity avec 3 tentatives et backoff exponentiel.
- **Impact** : Tout rate-limit transitoire ou erreur reseau rejette la generation sans seconde chance.
- **Recommandation** : Ajouter le meme decorateur `@retry` que le flux defis.

#### P3. TokenTracker en memoire -- non persistant, non distribue
- **Fichier** : `app/utils/token_tracker.py`
- **Description** : Le tracker est une instance globale en memoire. En deploiement multi-instance (Render avec scaling), chaque worker a sa propre copie, les stats sont fragmentees et perdues a chaque restart.
- **Impact** : Metriques de cout IA non fiables en production.
- **Recommandation** : Persister dans une table SQL (une ligne par appel, similaire a `point_events`) ou dans Redis.

#### P4. `func.random()` O(n) dans `list_challenges`
- **Fichier** : `app/services/challenges/challenge_service.py:319`
- **Description** : `query.order_by(func.random())` est un full table scan suivi d'un tri aleatoire. Avec un corpus de challenges croissant, cette requete deviendra lente (O(n log n)).
- **Impact** : Degradation progressive des temps de reponse de la page defis.
- **Recommandation** : L'optimisation `random_offset` (lignes 306-317) est deja implementee mais necessite que `total` soit passe. S'assurer que le handler passe toujours `total` pour eviter le fallback `func.random()`.

#### P5. Aucun circuit-breaker sur les appels OpenAI
- **Description** : Si l'API OpenAI est down, chaque tentative de generation attend le timeout complet (90-600s) avant d'echouer. Il n'y a pas de mecanisme pour detecter une panne globale et repondre immediatement "service indisponible".
- **Impact** : Sous panne OpenAI, les requetes s'accumulent, les threads sont bloques, le serveur peut devenir irresponsif.
- **Recommandation** : Implementer un circuit-breaker simple (compteur d'echecs recents, ouverture si > N echecs en M minutes).

### Qualite des tests

#### T1. Absence de test pour `GamificationService.apply_points` sous concurrence
- **Fichier** : `app/services/gamification/gamification_service.py:87`
- **Description** : Le commentaire "Pas de with_for_update ici : SQLite (tests) ne le supporte pas" revele que la protection contre les race conditions n'est pas testable avec le setup actuel. En PostgreSQL (prod), deux appels concurrents sur le meme user_id peuvent calculer `balance_before` simultanement et produire un solde incorrect.
- **Impact** : Points perdus ou doubles sous charge concurrente.
- **Recommandation** : Ajouter un test d'integration PostgreSQL avec `SELECT ... FOR UPDATE` et le documenter dans `conftest.py`.

#### T2. Pas de tests pour les proxies SSE Next.js
- **Fichiers** : `frontend/app/api/*/route.ts`
- **Description** : Aucun test unitaire pour les 4 routes proxy (exercises, challenges, chat, chat/stream). La logique d'authentification, de routage et de gestion d'erreurs n'est pas couverte.
- **Impact** : Les bugs de proxy (B4, B5, B8) ne sont detectes qu'en production.
- **Recommandation** : Ajouter des tests d'integration avec `next/test` ou MSW pour simuler les responses backend.

#### T3. Mocks fragiles sur les variables d'environnement
- **Description** : Plusieurs tests patchent `os.getenv("TESTING")` pour desactiver le rate limit. Ce pattern est fragile car il depend de la connaissance interne du code.
- **Fichier** : `app/utils/rate_limit.py:69`, `79`, `99`
- **Recommandation** : Injecter le store de rate limit via un parametre plutot que de verifier `os.getenv` directement.

### Frontend

#### F1. `useAIExerciseGenerator` melange logique et UI
- **Fichier** : `frontend/hooks/useAIExerciseGenerator.ts`
- **Description** : Le hook gere simultanement : l'etat de generation, la validation des inputs, l'appel fetch, le parsing SSE, l'invalidation de cache, et l'affichage des toasts. C'est a la fois un hook d'etat et un service.
- **Impact** : Difficulte de test, reuse limitee, logique metier dispersee.
- **Recommandation** : Extraire la logique fetch/SSE dans un service pur (`exerciseAiService.ts`), garder le hook comme glue etat + service.

#### F2. Le composant `Recommendations.tsx` ne pagine pas
- **Fichier** : `frontend/components/dashboard/Recommendations.tsx:70`
- **Description** : Toutes les recommandations sont rendues dans un `recommendations.map(...)` sans virtualisation ni pagination. Avec un moteur de recommandations actif, le nombre peut croitre.
- **Impact** : Render lent si > 20 recommandations.
- **Recommandation** : Limiter l'affichage a 5-6 items avec un "Voir plus" ou paginer.

#### F3. `getCsrfTokenFromCookie` appele sans verification
- **Fichier** : `frontend/hooks/useAIExerciseGenerator.ts:82` et `frontend/components/challenges/AIGenerator.tsx:73`
- **Description** : Si la fonction retourne `undefined`, le header `X-CSRF-Token` est simplement omis (spread conditionnel). Le backend pourrait rejeter la requete sans explication claire pour l'utilisateur.
- **Impact** : Erreur silencieuse si le cookie CSRF est absent.
- **Recommandation** : Logger un warning et afficher un message explicite si CSRF est absent.

---

## Volet 3 -- Manquements documentaires

### Documentation code

#### D1. `challenge_contract_policy.py` -- documentation exemplaire mais isolee
- **Fichier** : `app/services/challenges/challenge_contract_policy.py`
- **Observation** : Ce module est tres bien documente (docstrings, principes EdTech, commentaires clairs). En revanche, les fichiers homologues exercises (`exercise_ai_validation.py`, `exercise_stream_service.py`) sont beaucoup moins documentes.
- **Recommandation** : Aligner la documentation des services exercices sur le standard des defis.

#### D2. `gamification_service.py` -- pas de documentation des invariants
- **Fichier** : `app/services/gamification/gamification_service.py`
- **Description** : Le commentaire "Pas de with_for_update ici : SQLite (tests) ne le supporte pas" revele une decision d'architecture non documentee. Il n'y a pas d'ADR sur la concurrence du ledger de points.
- **Recommandation** : Documenter la decision et ses consequences dans un ADR.

#### D3. Scripts de maintenance sans docstrings
- **Fichiers** : `scripts/cleanup_edtech_aberrant_data.py`, `scripts/truncate_edtech_events.py`, `scripts/verify_user_deletion.py`, `scripts/debug_challenge_list.py`
- **Description** : Ces scripts manipulent la base de donnees de production mais n'ont pas de documentation d'usage, de parametres attendus, ni de conditions d'execution.
- **Recommandation** : Ajouter un bloc `if __name__ == "__main__"` avec argparse et une description.

### Documentation API

#### D4. Pas de specification OpenAPI / Swagger
- **Description** : Le projet utilise Starlette (pas FastAPI) et n'a pas de schema OpenAPI auto-genere. La documentation API est dans `docs/02-FEATURES/API_QUICK_REFERENCE.md` mais peut deriver du code reel.
- **Recommandation** : Generer un schema OpenAPI depuis les schemas Pydantic existants ou migrer les routes critiques vers FastAPI APIRouter.

#### D5. Endpoints gamification non documentes
- **Description** : Les endpoints `point_events` et le flux gamification (`apply_points`) ne sont pas documentes dans `API_QUICK_REFERENCE.md`.
- **Recommandation** : Ajouter les endpoints gamification dans la reference API.

### Documentation projet

#### D6. Pas d'ADR (Architecture Decision Records)
- **Description** : Plusieurs decisions d'architecture sont prises mais non documentees :
  - Pourquoi Starlette au lieu de FastAPI ?
  - Pourquoi un TokenTracker en memoire plutot qu'en DB ?
  - Pourquoi des allowlists explicites pour les modeles IA ?
  - Pourquoi `is_active` ET `is_archived` sur les challenges ?
  - Pourquoi sync_db_session + run_db_bound plutot que des sessions async ?
- **Recommandation** : Creer un repertoire `docs/05-ADR/` avec un ADR par decision.

#### D7. CHANGELOG absent ou implicite
- **Description** : Le `frontend/app/changelog/page.tsx` existe mais aucun fichier `CHANGELOG.md` racine n'est visible. Les notes de version sont dispersees dans les commits git.
- **Recommandation** : Maintenir un `CHANGELOG.md` a la racine au format Keep a Changelog.

### Variables d'environnement

#### D8. `REDIS_URL` absente de `.env.example`
- **Fichier** : `.env.example`
- **Description** : `REDIS_URL` est requise en production (`config.py:246-251`) pour le rate limit distribue, mais n'est pas documentee dans `.env.example`. Un deployeur ne sait pas qu'il doit la configurer.
- **Impact** : Crash au demarrage en production si `REDIS_URL` est absente.
- **Recommandation** : Ajouter `REDIS_URL=` avec un commentaire explicatif dans `.env.example`.

#### D9. Variables d'environnement Sentry sans documentation backend
- **Fichier** : `.env.example:98-103`
- **Description** : Les variables Sentry sont documentees mais uniquement cote monitoring. Le code backend qui les consomme n'est pas identifiable dans la config principale.
- **Recommandation** : Documenter quels fichiers consomment quelles variables.

---

## Patterns recurrents identifies

### PR1. Acces aux attributs utilisateur inconsistant (10+ occurrences)

Trois patterns coexistent dans le meme projet :
```python
# Pattern A : getattr avec default
total = int(getattr(user, "total_points", None) or 0)
# Pattern B : hasattr + access direct
total = user.total_points if hasattr(user, "total_points") else 0
# Pattern C : access direct (crash si attribut absent)
total = user.total_points
```

**Fichiers concernes** :
- `auth_session_service.py:36-59` (Pattern A et B melanges)
- `auth_session_service.py:152-204` (Pattern B)
- `gamification_service.py:36-57` (Pattern A)

**Recommandation** : Standardiser sur Pattern A dans un helper `user_field(user, name, default)`.

### PR2. Filtrage SQLAlchemy avec `== True` / `== False` (20+ occurrences)

```python
.filter(LogicChallenge.is_active == True)    # PEP 8 deconseille
.filter(LogicChallenge.is_archived == False)  # mieux : .is_(True) / .is_(False)
```

**Fichiers** : `challenge_service.py`, `user_service.py`, `badge_award_service.py`, `admin_overview_service.py`, etc.

**Impact** : Linting, mais fonctionnellement correct avec SQLAlchemy (qui surcharge `__eq__`).
**Recommandation** : Remplacer par `.is_(True)` / `.is_(False)` pour eviter les warnings.

### PR3. Duplication du pattern `getBackendUrl()` (4 occurrences)

Chaque route API Next.js (`chat/route.ts`, `chat/stream/route.ts`, `exercises/generate-ai-stream/route.ts`, `challenges/generate-ai-stream/route.ts`) reimplemente la meme logique de resolution de l'URL backend avec des variations (certaines valident la production, d'autres non -- cf. B10).

**Recommandation** : Extraire dans un `lib/api/backendUrl.ts` partage.

### PR4. Absence systematique de `done` event dans le flux SSE exercices

Le flux defis emet un `data: {"type": "done"}` final (challenge_ai_service.py:495), mais le flux exercices (`exercise_ai_service.py`) n'emet jamais de `done`. Le frontend se fie a la fermeture du stream pour detecter la fin.

**Impact** : Pas de probleme fonctionnel immediat, mais le frontend ne peut pas distinguer "fin normale" de "stream coupe". Inconsistance de contrat entre les deux flux.

**Recommandation** : Ajouter `data: {"type": "done"}` en fin de flux exercices.

### PR5. `generation_metrics.record_generation` utilise `challenge_type` pour les exercices

**Fichier** : `app/services/exercises/exercise_ai_service.py:196`

Le parametre `challenge_type=metrics_key` est nomme `challenge_type` mais reÃ§oit une cle exercice (`exercise_ai:addition`). L'API de `generation_metrics` ne distingue pas exercices et defis au niveau du champ.

**Recommandation** : Renommer le parametre en `workload_key` ou `content_type`.

---

## Plan d'action recommande

### Priorite 1 -- Impact eleve, effort faible (1-2 jours)

| # | Action | Fichier(s) | Impact | Statut |
|---|--------|-----------|--------|--------|
| 1 | Corriger la fuite memoire du TokenTracker (rotation/plafond) | `token_tracker.py` | Stabilite prod | ❌ Ouvert |
| 2 | Ajouter auth sur les routes chat proxy | `chat/route.ts`, `chat/stream/route.ts` | Securite | ❌ Ouvert |
| 3 | Ajouter `REDIS_URL` dans `.env.example` | `.env.example` | Deployabilite | ✅ CORRIGÉ 23/03/2026 |
| 4 | Corriger `auto_correct_challenge` NPE | `challenge_validator.py:527` | Correction auto | ❌ Ouvert |
| 5 | Ajouter timeout+retry au flux exercices IA | `exercise_ai_service.py` | Resilience | ❌ Ouvert |

### Priorite 2 -- Impact eleve, effort moyen (3-5 jours)

| # | Action | Fichier(s) | Impact | Statut |
|---|--------|-----------|--------|--------|
| 6 | Unifier le double filtrage `is_active`/`is_archived` | `challenge_service.py` | Correctness | ❌ Ouvert |
| 7 | Unifier les payloads utilisateur en un helper | `auth_session_service.py` | Maintenabilite | ❌ Ouvert |
| 8 | Extraire `getBackendUrl()` dans un module partage frontend | Routes API Next.js | DRY | ❌ Ouvert |
| 9 | Ajouter `GamificationService.apply_points` aux exercices | `exercise_attempt_service.py` | Completude produit | ✅ CORRIGÉ 23/03/2026 |
| 10 | Migrer TokenTracker vers table SQL | `token_tracker.py` | Observabilite | ❌ Ouvert |

### Priorite 3 -- Impact moyen, effort important (1-2 semaines)

| # | Action | Fichier(s) | Impact | Statut |
|---|--------|-----------|--------|--------|
| 11 | Unifier les policies modele IA (exercices/defis) | `ai_config.py`, `ai_generation_policy.py` | Architecture | ❌ Ouvert |
| 12 | Creer des ADR pour les decisions cles | `docs/05-ADR/` | Documentation | ✅ CORRIGÉ — ADR-001 créé 23/03/2026 ; ouvrir des ADRs supplémentaires si nouvelles décisions structurelles |
| 13 | Ajouter des tests pour les proxies SSE | `frontend/app/api/` | Couverture | ❌ Ouvert |
| 14 | Implementer un circuit-breaker OpenAI | Nouveau module | Resilience | ❌ Ouvert |
| 15 | Generer un schema OpenAPI | Infrastructure | Documentation API | ❌ Ouvert |

---

*Audit conduit par analyse statique du code source. Aucune execution de tests ni deploiement implique.*

