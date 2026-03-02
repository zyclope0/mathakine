# Audit Code — Cleanup & Fiabilité

**Date :** 01/03/2026
**Type :** Audit code (bugs, dead code, incohérences)
**Périmètre :** `app/`, `server/`, `frontend/`
**Méthode :** Inspection systématique fichier par fichier, vérification des appels via grep

---

## Sommaire

1. [Résumé exécutif](#1-résumé-exécutif)
2. [CRITICAL — Correction immédiate](#2-critical)
3. [HIGH — Bugs importants et dead code volumineux](#3-high)
4. [MEDIUM — Prochain nettoyage](#4-medium)
5. [LOW — A nettoyer quand opportun](#5-low)
6. [Plan d'action](#6-plan-daction)
7. [Historique des corrections](#7-historique-des-corrections)

---

## 1. Résumé exécutif

| Sévérité | Bugs | Dead Code | Incohérences | Total |
|----------|------|-----------|--------------|-------|
| **CRITICAL** | 4 | 0 | 0 | **4** |
| **HIGH** | 6 | 5 | 4 | **15** |
| **MEDIUM** | 9 | 7 | 4 | **20** |
| **LOW** | 2 | 5 | 1 | **8** |
| **Total** | **21** | **17** | **9** | **47** |

---

## 2. CRITICAL — Correction immédiate {#2-critical}

### C1. Refresh token fallback accepte des tokens expirés indéfiniment

| | |
|---|---|
| **Fichier** | `server/handlers/auth_handlers.py:436-478` |
| **Catégorie** | BUG — Sécurité |
| **Statut** | ✅ Corrigé 01/03 |

```python
payload = jwt.decode(
    access_token_fallback,
    settings.SECRET_KEY,
    algorithms=[settings.ALGORITHM],
    options={"verify_exp": False},  # ← Ne vérifie PAS l'expiration
)
```

**Impact :** Un access_token expiré depuis des semaines/mois suffit pour obtenir de nouveaux tokens valides. N'importe quel token fuité devient un accès permanent. Exploitable en production.

**Correction :** Limite 7 jours ajoutée — tokens expirés depuis > 7j rejetés. Tokens sans claim `exp` rejetés aussi. `verify_exp: False` reste présent (décodage) mais la garde post-décodage bloque les abus.

---

### C2. `record_attempt` crash via `ImportError` non attrapé

| | |
|---|---|
| **Fichier** | `app/services/exercise_service.py:799-830` |
| **Catégorie** | BUG — Runtime crash |
| **Statut** | ✅ Corrigé 01/03 |

```python
from server.database import get_db_connection  # ← ImportError possible
conn = get_db_connection()
cursor = conn.cursor()
```

**Impact :** Si l'exercice n'est pas trouvé par l'ORM, le code tente un import runtime de `server.database`. L'`ImportError` n'est pas attrapé (seul `SQLAlchemyError` l'est), ce qui crashe le flow de soumission de réponse et corrompt potentiellement la transaction.

**Correction :** Supprimer ce bloc dead entièrement (voir C3).

---

### C3. `exercise_dict = None; if exercise_dict:` — branche morte critique

| | |
|---|---|
| **Fichier** | `app/services/exercise_service.py:780-782` |
| **Catégorie** | BUG / DEAD_CODE |
| **Statut** | ✅ Corrigé 01/03 |

```python
exercise_dict = None
if exercise_dict:  # ← TOUJOURS False
    logger.info(
```

**Impact :** Le fallback PostgreSQL direct est entièrement mort. Le code donne l'impression qu'il y a un filet de sécurité, mais il n'y en a aucun. Lié à C2 — tout le bloc (lignes 778-830) doit être supprimé.

**Correction :** Supprimer le bloc dead `server.database` import dans `record_attempt`.

---

### C4. `UserStats` query sans filtre `user_id` — corruption de données

| | |
|---|---|
| **Fichier** | `app/services/exercise_service.py:994-1000` |
| **Catégorie** | BUG — Données |
| **Statut** | ✅ Corrigé 01/03 — dead write supprimé (aucun consumer ne lit cette table) |

```python
user_stat = (
    aux_session.query(UserStats)
    .filter(
        UserStats.exercise_type == ex_type_val,
        UserStats.difficulty == diff_val,
    )
    .first()
)
```

**Impact :** La requête filtre par `exercise_type` et `difficulty` mais **jamais par `user_id`**. Tous les utilisateurs partagent les mêmes lignes de stats. Les compteurs sont globaux au lieu d'être par utilisateur.

**Correction :** Suppression du bloc d'écriture `user_stats` dans `update_progress_after_attempt` (~55 lignes). La table n'est lue par aucun consumer (le dashboard utilise `attempts JOIN exercises` via `UserService.get_user_stats()`). Table conservée pour cohérence Alembic.

---

## 3. HIGH — Bugs importants et dead code volumineux {#3-high}

### H1. Subtraction choice generation crashe aléatoirement

| | |
|---|---|
| **Fichier** | `server/exercise_generator.py:163` |
| **Catégorie** | BUG — Runtime crash |
| **Statut** | ✅ Corrigé 01/03 |

```python
str(result - random.randint(1, min(3, result // 2)))
# Quand result == 1 : result // 2 = 0, min(3, 0) = 0, random.randint(1, 0) → ValueError
```

**Impact :** Bug intermittent mais certain avec assez de générations. Crashe la requête de génération d'exercice.

**Correction :** `min(3, max(1, result // 2))`.

---

### H2. `GET /api/exercises/generate` retourne du HTML dans une API JSON

| | |
|---|---|
| **Fichier** | `server/handlers/exercise_handlers.py:82-108` |
| **Catégorie** | BUG — Contrat API cassé |
| **Statut** | ✅ Corrigé 01/03 |

**Impact :** Le handler retourne `RedirectResponse(url="/exercises?generated=true")` en succès et `TemplateResponse("error.html")` en erreur. Code legacy HTML dans une API JSON pure.

**Correction :** Route GET supprimée de `server/routes/exercises.py`. Le handler reste disponible pour les tests existants mais n'est plus exposé via HTTP. Seul le POST (`generate_exercise_api`) est conservé.

---

### H3. `challenges/AIGenerator.tsx` bypass le proxy API — cassé en prod cross-domain

| | |
|---|---|
| **Fichier** | `frontend/components/challenges/AIGenerator.tsx:99-126` |
| **Catégorie** | BUG — Production |
| **Statut** | ✅ Corrigé 01/03 |

**Impact :** Contrairement à `exercises/AIGenerator.tsx` qui utilise le proxy Next.js et `ensureFrontendAuthCookie()`, celui-ci fait un `fetch` cross-origin direct. En production (domaines séparés), les cookies auth ne sont pas envoyés → 401 systématique.

**Correction :** Aligné sur le pattern `exercises/AIGenerator.tsx` : ajout de `ensureFrontendAuthCookie()` et utilisation du proxy Next.js `/api/challenges/generate-ai-stream` (route proxy déjà existante).

---

### H4. `settings_reader.py` — `DetachedInstanceError` potentiel

| | |
|---|---|
| **Fichier** | `app/utils/settings_reader.py:12-16` |
| **Catégorie** | BUG — Runtime crash |
| **Statut** | ✅ Corrigé 01/03 |

```python
async def get_setting_bool(key: str, default: bool = False) -> bool:
    async with db_session() as db:
        row = db.query(Setting).filter(Setting.key == key).first()
    if not row or row.value is None:  # ← accès APRÈS fermeture de session
        return default
```

**Impact :** `row.value` accédé après fermeture de session → `DetachedInstanceError` possible.

**Correction :** Déplacer l'accès à `row.value` dans le `async with`.

---

### H5. `auth_service.py` — `except` blocks inatteignables + variable morte

| | |
|---|---|
| **Fichier** | `app/services/auth_service.py:335-374` |
| **Catégorie** | BUG / DEAD_CODE |
| **Statut** | ✅ Corrigé 01/03 |

**Impact :** `role_value` assigné mais jamais utilisé. Le `return` ligne 337 rend les blocs `except jwt.ExpiredSignatureError` et `except JWTError` plus bas inatteignables → les tokens expirés reçoivent un message d'erreur générique.

**Correction :** Suppression de `role_value` (dead variable), suppression du commentaire orphelin `# ... (le code précédent reste le même) ...` qui précédait les except blocks. Les blocs except sont maintenant atteignables normalement.

---

### H6. CSRF enforced sur 3 endpoints sur 15+ state-changing

| | |
|---|---|
| **Fichiers** | `auth_handlers.py`, `user_handlers.py` |
| **Catégorie** | INCONSISTENCY — Sécurité |
| **Statut** | ✅ Corrigé 02/03 |

**Protégés avant :** 3 endpoints (reset-password, password change, delete account) via appels manuels dans les handlers.

**Correction :** `CsrfMiddleware` centralisé dans `server/middleware.py` — protège automatiquement **tous** les endpoints state-changing (`POST/PUT/PATCH/DELETE`) sauf les routes exemptées (login, register, refresh, forgot-password, etc.). Les appels manuels `validate_csrf_token()` dans les handlers ont été supprimés. Frontend : `apiRequest()` injecte automatiquement `X-CSRF-Token` depuis le cookie. 23 tests unitaires couvrent la configuration et le comportement fonctionnel.

---

### H7. Leaderboard: middleware dit "public", handler dit "privé"

| | |
|---|---|
| **Fichiers** | `server/middleware.py:154` + `server/handlers/user_handlers.py:279` |
| **Catégorie** | INCONSISTENCY |
| **Statut** | ✅ Corrigé 01/03 |

**Impact :** Le middleware whitelist `GET /api/users/leaderboard` comme public. Le handler a `@require_auth @require_full_access`. L'entrée whitelist est trompeuse et inutile.

**Correction :** Entrée retirée de `_AUTH_PUBLIC_EXACT` dans `server/middleware.py`. Test unitaire mis à jour (`test_leaderboard_get_requires_auth`).

---

### H8. `BadgeService` instancié deux fois sur session potentiellement corrompue

| | |
|---|---|
| **Fichier** | `app/services/exercise_service.py:362-406` |
| **Catégorie** | BUG |
| **Statut** | ✅ Corrigé 01/03 |

**Impact :** `BadgeService(db)` créé une première fois (l.363) puis re-créé (l.406) si le premier check a échoué. La session peut être dans un état inconsistant.

**Correction :** Suppression de la seconde instanciation. Réutilisation de l'instance `badge_service` déjà créée en l.363, avec protection try/except pour `get_closest_progress_notification`.

---

### H9. Dead code massif — modules entiers jamais appelés en production

| Fichier | Fonction(s) mortes | ~Lignes |
|---------|-------------------|---------|
| `app/utils/enum_mapping.py` | **Tout le module** (10 fonctions) | ~128 |
| `app/utils/response_formatters.py` | `format_paginated_response` | ~36 |
| `app/utils/generation_metrics.py` | `get_success_rate`, `get_validation_failure_rate`, `get_auto_correction_rate`, `get_average_duration`, `get_summary` | ~140 |
| `app/utils/token_tracker.py` | `get_stats`, `get_daily_summary` | ~80 |
| `server/template_handler.py` | `render_template`, `render_error` | ~90 |
| `server/exercise_generator_helpers.py` | `generate_contextual_question` | ~90 |
| `app/utils/rate_limiter.py` | `get_user_stats` | ~15 |
| **Total** | | **~580** |

> Note : certaines fonctions sont couvertes par des tests unitaires dédiés mais n'ont aucun appelant en production.

---

## 4. MEDIUM — Prochain nettoyage {#4-medium}

| # | Fichier | Problème | Catégorie |
|---|---------|----------|-----------|
| M1 | `exercise_service.py:448-459` | `valid_types`/`valid_difficulties` calculés mais jamais utilisés (filter commenté) | ✅ Corrigé 01/03 |
| M2 | `challenge_service.py:582-601` | `stats.total` peut être `None` → `TypeError` dans le calcul de success_rate | ✅ Corrigé 01/03 |
| M3 | `user_service.py:384-395` | Calcul de niveau fragile à la borne max (`xp >= 5500`) | BUG |
| M4 | `rate_limit.py:22` | `_rate_limit_store` grossit indéfiniment — fuite mémoire lente | ✅ Corrigé 01/03 |
| M5 | `token_tracker.py:168-179` | `key.split("_")[0]` tronque les types contenant `_` | BUG |
| M6 | `simple_ttl_cache.py:17-22` | TOCTOU race sur init du lock asyncio | BUG |
| M7 | `transaction.py:49-54` | `if not savepoint.is_active` toujours True après commit → condition inutile | INCONSISTENCY |
| M8 | `server/routes/exercises.py:30-34` | GET `/api/exercises/generate` crée en DB (non-idempotent, CSRF vector) | ✅ Corrigé 01/03 (supprimé avec H2) |
| M9 | `exercise_handlers.py:249-264` | Validation des params après le normalize qui les a déjà defaultés | ✅ Corrigé 01/03 |
| M10 | `challenge_handlers.py:784` | `get_challenge_hint` sans auth decorator (protection middleware seule) | ✅ Corrigé 01/03 |
| M11 | `user_handlers.py:664-665` | `delete_cookie` sans flags `SameSite`/`Secure`/`path` → cookies non supprimés en prod | ✅ Corrigé 01/03 |
| M12 | `frontend/lib/utils/format.ts:13` | `rate <= 0` traite 0% de succès comme invalide (devrait être `rate < 0`) | ✅ Corrigé 01/03 |
| M13 | `frontend/hooks/useAuth.ts:90-107` | Strings françaises hardcodées au milieu du i18n | INCONSISTENCY |
| M14 | `frontend/components/challenges/ChallengeSolver.tsx:86` | `console.warn` non gated fuit les hints dans la console en prod | ✅ Corrigé 01/03 |
| M15 | `frontend/lib/utils.ts` vs `frontend/lib/utils/cn.ts` | Fichier dupliqué identique — `cn()` existe en double | DEAD_CODE |
| M16 | `frontend/components/challenges/ChallengeModal.tsx:28` | `onChallengeCompleted` prop acceptée mais ignorée (underscore-prefixed) | DEAD_CODE |
| M17 | `frontend/components/exercises/AIGenerator.tsx:308+371` | Double bouton cancel pendant la génération | INCONSISTENCY |

---

## 5. LOW — A nettoyer quand opportun {#5-low}

| # | Fichier | Problème | Catégorie |
|---|---------|----------|-----------|
| L1 | `exercise_service.py:29-52` | `ExerciseServiceProtocol` jamais importé | ✅ Corrigé 01/03 |
| L2 | `recommendation_service.py:570-584` | `mark_recommendation_as_shown` jamais appelé | DEAD_CODE |
| L3 | `enhanced_server_adapter.py:323-402` | `execute_raw_query`, `get_logic_challenges`, `get_logic_challenge` jamais appelés | DEAD_CODE |
| L4 | `db/adapter.py:76-112` | `list_active` jamais appelé en prod (seulement tests) | DEAD_CODE |
| L5 | `db_helpers.py:10-35` | `get_db_engine`, `is_postgresql` jamais appelés en prod | DEAD_CODE |
| L6 | `translation.py:89-142` | `build_translations_dict`, `build_translations_array` jamais appelés | DEAD_CODE |
| L7 | `json_utils.py:44-45` | `JSONDecodeError(text=None)` crashe en `TypeError` si input `None` | ✅ Corrigé 01/03 |
| L8 | `email_verification.py:24-38` | `datetime.now(timezone.utc)` comparé à un datetime potentiellement naïf | ✅ Corrigé 01/03 |

---

## 6. Plan d'action {#6-plan-daction}

### Immédiat (sécurité)

| Priorité | Item | Action |
|----------|------|--------|
| 1 | **C1** | Supprimer ou limiter le fallback refresh (max 7 jours) |
| 2 | **H6** | Étendre CSRF à tous les endpoints state-changing |

### Court terme (fiabilité)

| Priorité | Item | Action |
|----------|------|--------|
| 3 | **C2/C3** | Supprimer le bloc dead `server.database` import dans `record_attempt` |
| 4 | **C4** | Ajouter filtre `user_id` à la requête `UserStats` |
| 5 | **H1** | Guard `result // 2` avec `max(1, ...)` |
| 6 | **H3** | Faire passer `challenges/AIGenerator` par le proxy Next.js |
| 7 | **H4** | Déplacer l'accès à `row.value` dans le `async with` |

### Nettoyage (tech debt)

| Priorité | Item | Action |
|----------|------|--------|
| 8 | **H9** | Supprimer les ~580 lignes de dead code identifiées |
| 9 | **H2** | Supprimer le GET handler HTML legacy sur `/api/exercises/generate` |
| 10 | **M1–M17** | Items MEDIUM selon priorité |

---

## 7. Historique des corrections {#7-historique-des-corrections}

| Date | Item | Détail |
|------|------|--------|
| 01/03/2026 | — | Création du document (audit initial) |
| 01/03/2026 | C1 | Fallback refresh : limite 7 jours + rejet tokens sans `exp` |
| 01/03/2026 | C2/C3 | Suppression bloc dead `server.database` dans `record_attempt` |
| 01/03/2026 | H1 | Guard `max(1, result // 2)` pour subtraction choices |
| 01/03/2026 | H4 | Accès `row.value` déplacé dans le context manager |
| 01/03/2026 | C4 | Dead write `user_stats` supprimé (~55 lignes) — aucun consumer, table conservée pour Alembic |
| 01/03/2026 | H2+M8 | Route GET `/api/exercises/generate` supprimée (HTML legacy) |
| 01/03/2026 | H3 | `challenges/AIGenerator.tsx` → proxy Next.js + `ensureFrontendAuthCookie()` |
| 01/03/2026 | H5 | `auth_service.py` : suppression `role_value` mort + except blocks restaurés |
| 01/03/2026 | H7 | Leaderboard retiré de la whitelist middleware (protégé par handler) |
| 01/03/2026 | H8 | `BadgeService` : suppression double instanciation, réutilisation instance existante |
| 01/03/2026 | M1 | Suppression `valid_types`/`valid_difficulties` dead code dans `list_exercises` |
| 01/03/2026 | M2 | Guard `stats.total`/`stats.correct` contre `None` dans `challenge_service` |
| 01/03/2026 | M4 | `rate_limit.py` : nettoyage des clés vides pour éviter fuite mémoire |
| 01/03/2026 | M9 | Validation des params avant normalisation dans `generate_exercise_api` |
| 01/03/2026 | M10 | `@require_auth @require_full_access` ajoutés sur `get_challenge_hint` |
| 01/03/2026 | M11 | `delete_cookie` avec `path`, `samesite`, `secure` dans `delete_user_me` |
| 01/03/2026 | M12 | `formatSuccessRate` : `rate < 0` au lieu de `rate <= 0` (0% est valide) |
| 01/03/2026 | M14 | `console.warn` supprimé dans `ChallengeSolver.tsx` (fuite hints en prod) |
| 01/03/2026 | L1 | Suppression `ExerciseServiceProtocol` + import `Protocol` inutilisé |
| 01/03/2026 | L7 | `json_utils.py` : guard `text or ""` pour éviter `TypeError` sur `None` |
| 01/03/2026 | L8 | `email_verification.py` : ajout `.replace(tzinfo=utc)` pour datetimes naïfs |
| 02/03/2026 | H6 | CSRF centralisé via `CsrfMiddleware` — couvre tous les endpoints state-changing |

---

## Références

- [AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md](./AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md) — Audit backend (itérations 1–5)
- [REFACTOR_STATUS_2026-02.md](./REFACTOR_STATUS_2026-02.md) — État du refactoring
- [docs/01-GUIDES/TESTING.md](../01-GUIDES/TESTING.md) — Guide tests
