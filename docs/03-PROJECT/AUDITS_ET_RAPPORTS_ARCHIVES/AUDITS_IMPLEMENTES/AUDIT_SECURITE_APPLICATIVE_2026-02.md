# Audit de sécurité applicative — Mathakine

**Date :** Février 2026  
**Périmètre :** Backend (Starlette/Python), Frontend (Next.js), API REST  
**Référence :** OWASP Top 10, bonnes pratiques cybersécurité

---

## Résumé exécutif

**État initial (Février 2026) :**

| Niveau      | Nombre |
|-------------|--------|
| Critique    | 2      |
| Élevé       | 3      |
| Moyen       | 4      |
| Faible      | 2      |

**État actuel (post-corrections) :** toutes les vulnérabilités identifiées ont été corrigées. ✅

---

## 1. Vulnérabilités critiques

### 1.1 Exposition de tracebacks et messages d'erreur au client

**Niveau de criticité :** Critique

**Localisation :** 
- `server/handlers/user_handlers.py` — lignes 483-484, 504-505, 619-620, 642-643, 754-755, 948-949, 1027-1028, 1073-1074, 1101-1102, 1247-1248, 1302, 1357
- `server/handlers/challenge_handlers.py` — lignes 405-406, 451-452, 534-535, 559-560, 583-584, 1002, 1320
- `server/handlers/exercise_handlers.py` — lignes 99-100, 372-375, 848, 853, 949-950, 1199-1203
- `server/handlers/chat_handlers.py` — lignes 292, 480
- `server/handlers/badge_handlers.py` — lignes 43, 68, 97, 160, 181
- `server/handlers/recommendation_handlers.py` — lignes 91, 121, 150
- `app/utils/error_handler.py` — lignes 50-57

**Vecteur d'attaque :** Un attaquant provoque une exception (requête malformée, ID invalide, etc.). La réponse HTTP contient `str(e)` ou `traceback.format_exc()`, exposant potentiellement :
- Schéma de base de données
- Chemins de fichiers
- Structure interne de l'application
- Versions de bibliothèques

**Remédiation :**

```python
# Avant (vulnérable)
except Exception as e:
    traceback.print_exc()
    return JSONResponse({"error": str(e)}, status_code=500)

# Après (sécurisé)
except Exception as e:
    logger.exception("Erreur lors du traitement")
    user_message = "Une erreur est survenue. Veuillez réessayer."
    if settings.LOG_LEVEL.upper() == "DEBUG":
        user_message = str(e)  # Uniquement en dev
    return JSONResponse({"error": user_message}, status_code=500)
```

Pour `ErrorHandler.create_error_response` :

```python
# S'assurer que include_details n'est JAMAIS True en production
if include_details is None:
    include_details = (
        settings.LOG_LEVEL.upper() == "DEBUG" 
        and os.getenv("ENVIRONMENT") != "production"
    )
```

---

### 1.2 Route sync-cookie accepte un token sans validation

**Niveau de criticité :** Critique

**Localisation :** `frontend/app/api/auth/sync-cookie/route.ts` — lignes 11-56

**Vecteur d'attaque :** La route `POST /api/auth/sync-cookie` reçoit un `access_token` dans le body et le pose en cookie sans vérifier sa signature ni son expiration. Un attaquant peut :
1. Forger une requête vers cette URL (via phishing/XSS) avec un token qu'il contrôle
2. Si l'utilisateur est sur le même domaine, le token malveillant remplace le cookie légitime
3. Escalade vers session hijacking si le token est valide (obtenu par autre vecteur)

**Remédiation :**

```typescript
// Option 1 : Valider le token via le backend avant de le poser
// Le frontend ne doit poser le cookie qu'après vérification par le backend
export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));
  const accessToken = body?.access_token;
  
  if (!accessToken || typeof accessToken !== "string") {
    return new Response(JSON.stringify({ error: "access_token requis" }), { status: 400 });
  }

  // Valider le token côté backend avant de le poser
  const verifyRes = await fetch(`${process.env.BACKEND_URL}/api/auth/validate-token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: accessToken }),
  });
  
  if (!verifyRes.ok) {
    return new Response(JSON.stringify({ error: "Token invalide" }), { status: 401 });
  }

  // Poursuivre avec Set-Cookie...
}
```

```python
# Backend : ajouter GET/POST /api/auth/validate-token
async def validate_token(request: Request):
    data = await request.json()
    token = data.get("token")
    try:
        payload = decode_token(token)
        return JSONResponse({"valid": True, "user_id": payload.get("sub")})
    except HTTPException:
        return JSONResponse({"valid": False}, status_code=401)
```

---

## 2. Vulnérabilités élevées

### 2.1 Absence de sanitization des messages chat (injection de prompt)

**Niveau de criticité :** Élevé

**Localisation :** `server/handlers/chat_handlers.py` — lignes 154-156, 167-168

**Vecteur d'attaque :** Le message utilisateur est envoyé directement à l'API OpenAI sans sanitization. Un attaquant peut injecter des instructions pour :
- Faire divulguer le prompt système
- Contourner les restrictions (ex. "ignore previous instructions")
- Générer du contenu indésirable

**Remédiation :**

```python
# Dans chat_api et chat_api_stream, avant l'envoi à OpenAI
from app.utils.prompt_sanitizer import sanitize_user_prompt, validate_prompt_safety

message = data.get('message', '')
is_safe, safety_reason = validate_prompt_safety(message)
if not is_safe:
    return JSONResponse(
        {"error": f"Message invalide: {safety_reason}"},
        status_code=400
    )
message = sanitize_user_prompt(message, max_length=2000)

# Limiter la longueur de conversation_history
conversation_history = data.get('conversation_history', [])[:20]
```

---

### 2.2 Mot de passe reset : exigence trop faible (6 caractères)

**Niveau de criticité :** Élevé

**Localisation :** `server/handlers/auth_handlers.py` — ligne 593

**Vecteur d'attaque :** `len(password) < 6` autorise des mots de passe extrêmement faibles lors du reset. La création de compte impose 8 caractères + chiffre + majuscule, mais le reset n'impose que 6. Incohérence et surface d'attaque accrue.

**Remédiation :**

```python
# Avant
if not password or len(password) < 6:
    return JSONResponse(
        {"error": "Le mot de passe doit contenir au moins 6 caractères"},
        status_code=400
    )

# Après (aligné avec create_user_account)
if not password or len(password) < 8:
    return JSONResponse(
        {"error": "Le mot de passe doit contenir au moins 8 caractères"},
        status_code=400
    )
if not any(char.isdigit() for char in password):
    return JSONResponse(
        {"error": "Le mot de passe doit contenir au moins un chiffre"},
        status_code=400
    )
if not any(char.isupper() for char in password):
    return JSONResponse(
        {"error": "Le mot de passe doit contenir au moins une majuscule"},
        status_code=400
    )
```

---

### 2.3 SECRET_KEY générée automatiquement si vide

**Niveau de criticité :** Élevé

**Localisation :** `app/core/config.py` — lignes 36-38

**Vecteur d'attaque :** Si `SECRET_KEY` n'est pas définie en production, une clé est générée à chaque redémarrage. Les tokens JWT émis avant un redémarrage deviennent invalides, et pire : en multi-instance, chaque instance a une clé différente, rendant les sessions incohérentes. En cas de fuite de configuration, une clé prédictible ou réutilisable augmente le risque.

**Remédiation :** ✅ **Implémenté** (13/02/2026) — `raise ValueError` si vide en prod ; génération auto en dev/tests.

---

## 3. Vulnérabilités moyennes

### 3.1 DatabaseAdapter.execute_query : paramètres et format SQL

**Niveau de criticité :** Moyen

**Localisation :** `app/db/adapter.py` — lignes 186-207

**Vecteur d'attaque :** La méthode accepte `params` sous forme de `Tuple` ou `dict`. SQLAlchemy `text()` attend des paramètres nommés (`:param`) ou positionnels (`:1`, `:2`). Si un appelant passe une chaîne concaténée dans `query` ou utilise un mauvais format de paramètres, une injection SQL est possible. L'usage actuel via `execute_raw_query` est limité, mais l'API est risquée.

**Remédiation :** ✅ **Implémenté** (13/02/2026) — params dict obligatoire, `TypeError` si tuple, doc ajoutée.

---

### 3.2 Absence de protection CSRF pour les API modifiant des données

**Niveau de criticité :** Moyen

**Localisation :** Application globale — cookies `SameSite=Lax`, pas de token CSRF

**Vecteur d'attaque :** Avec `SameSite=Lax`, les requêtes POST cross-site ne contiennent pas les cookies. Mais si `SameSite=None` est utilisé (cross-domain avec frontend séparé), ou en cas de sous-domaine partagé, un site tiers peut provoquer des actions au nom de l'utilisateur (ex. changement de mot de passe, suppression de compte).

**Remédiation :** ✅ **Implémenté** (13/02/2026) — Endpoint `GET /api/auth/csrf`, pattern double-submit. Protection reset-password, change-password, delete-account.

---

### 3.3 DEFAULT_ADMIN_PASSWORD faible en configuration

**Niveau de criticité :** Moyen

**Localisation :** `app/core/config.py` — ligne 65

**Vecteur d'attaque :** `DEFAULT_ADMIN_PASSWORD = "admin"` en fallback. Si un déploiement oublie de définir `DEFAULT_ADMIN_EMAIL` et `DEFAULT_ADMIN_PASSWORD`, un compte admin par défaut avec mot de passe trivial peut être exploité.

**Remédiation :** ✅ **Implémenté** (13/02/2026) — `raise ValueError` au démarrage si vide ou "admin" en prod (ENVIRONMENT=production).

---

### 3.4 Rate limiting non appliqué sur les endpoints sensibles

**Niveau de criticité :** Moyen

**Localisation :** `app/core/config.py` — `RATE_LIMIT_PER_MINUTE` défini mais non utilisé dans les handlers

**Vecteur d'attaque :** Endpoints comme `/api/auth/login`, `/api/auth/forgot-password`, `POST /api/users/` ne sont pas limités. Permet le bruteforce de mots de passe, l'énumération d'utilisateurs et l'abus de ressources.

**Remédiation :**

```python
# Ajouter un middleware ou décorateur rate limit
# Exemple avec slowapi ou implémentation custom
from functools import wraps
from collections import defaultdict
from time import time

_rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # secondes
RATE_LIMIT_MAX = 5  # requêtes par fenêtre pour login/forgot-password

def rate_limit(key_func):
    def decorator(f):
        @wraps(f)
        async def wrapped(request, *args, **kwargs):
            key = key_func(request)
            now = time()
            _rate_limit_store[key] = [t for t in _rate_limit_store[key] if now - t < RATE_LIMIT_WINDOW]
            if len(_rate_limit_store[key]) >= RATE_LIMIT_MAX:
                return JSONResponse({"error": "Trop de tentatives"}, status_code=429)
            _rate_limit_store[key].append(now)
            return await f(request, *args, **kwargs)
        return wrapped
    return decorator

# Sur login
@rate_limit(lambda r: r.client.host + ":login")
async def api_login(request): ...
```

---

## 4. Vulnérabilités faibles

### 4.1 Logging de données potentiellement sensibles

**Niveau de criticité :** Faible

**Localisation :** `app/services/auth_service.py` — ligne 86 ; autres handlers

**Vecteur d'attaque :** En mode DEBUG, `user.hashed_password` ou d'autres données sensibles peuvent apparaître dans les logs. En cas de fuite de fichiers de log, exposition de hashes.

**Remédiation :** Éviter de logger les mots de passe (même hashés), tokens, ou PII. Utiliser des placeholders : `logger.debug("Authentification pour user_id=%s", user.id)`.

---

### 4.2 CORS : allow_headers="*"

**Niveau de criticité :** Faible

**Localisation :** `server/middleware.py` — ligne 119

**Vecteur d'attaque :** `allow_headers=["*"]` autorise tout header. En soi moins critique avec des origines restreintes, mais élargit la surface d'attaque pour des headers personnalisés.

**Remédiation :** Limiter aux headers nécessaires. ✅ **Implémenté** : `allow_headers=["Content-Type", "Authorization", "Accept", "Accept-Language"]` (13/02/2026).

---

## 5. Points positifs identifiés

- Pas de `dangerouslySetInnerHTML` / `eval` côté frontend (React échappe par défaut)
- Mots de passe hachés avec bcrypt
- Cookies `HttpOnly` pour le token d'accès
- Pas d'énumération d'emails sur forgot-password (message identique)
- Paramètres des requêtes SQL (challenge_handlers, exercise_service) correctement liés
- Sanitization des prompts pour la génération d'exercices et de défis IA
- Validation des types de challenges et âges via allow-lists

---

## 6. Plan d'action recommandé

| Priorité | Action |
|----------|--------|
| P0 | Corriger l'exposition des erreurs (1.1) |
| P0 | Sécuriser la route sync-cookie (1.2) |
| P1 | Ajouter la sanitization des messages chat (2.1) |
| P1 | Renforcer les critères du mot de passe reset (2.2) |
| P1 | Bloquer le démarrage en prod sans SECRET_KEY (2.3) |
| P2 | Renforcer `execute_query` et documenter son usage (3.1) |
| P2 | Implémenter la protection CSRF pour actions sensibles (3.2) |
| P2 | Renforcer la config admin par défaut (3.3) |
| P2 | Mettre en place le rate limiting (3.4) |

---

## 7. Suivi des corrections (Février 2026)

### Corrections implémentées

| Faille | Statut | Détails |
|--------|--------|---------|
| **1.1** Exposition des erreurs au client | ✅ Corrigé | `get_safe_error_message()` ajouté dans `error_handler.py`. Tous les handlers (user, challenge, exercise, chat, badge, recommendation) utilisent désormais ce helper. `ErrorHandler.create_error_response` n'expose plus traceback ni message technique en production (`ENVIRONMENT=production` ou hors `LOG_LEVEL=DEBUG`). |
| **2.1** Injection de prompt (chat) | ✅ Corrigé | `chat_api` et `chat_api_stream` : `validate_prompt_safety()` + `sanitize_user_prompt()` appliqués au message utilisateur avant envoi à OpenAI. Patterns FR ajoutés dans `prompt_sanitizer.py` (oublie tout, tu es maintenant, réponds uniquement…). Historique limité à 20 messages. |
| **2.2** Mot de passe reset faible (6 car.) | ✅ Corrigé | `api_reset_password` : critères alignés sur la création de compte (8 caractères min, 1 chiffre, 1 majuscule). |
| **3.3** DEFAULT_ADMIN_PASSWORD | ✅ Corrigé | `raise ValueError` au démarrage si vide ou "admin" en prod (ENVIRONMENT=production). Obligatoire sur Render. |
| **4.1** Logging de données sensibles | ✅ Corrigé | Suppression du log `user.hashed_password` dans `auth_service.authenticate_user`. |
| **1.2** Route sync-cookie sans validation | ✅ Corrigé | Endpoint backend `POST /api/auth/validate-token` ajouté. La route sync-cookie appelle désormais ce endpoint pour valider la signature et l'expiration du token avant de le poser en cookie. Protection contre session hijacking. |
| **2.3** SECRET_KEY auto-générée | ✅ Corrigé | `raise ValueError` au démarrage si SECRET_KEY vide et ENVIRONMENT=production (sauf TESTING=true). Dev/tests : génération auto + warning. |
| **3.2** Protection CSRF | ✅ Corrigé | Endpoint GET /api/auth/csrf (pattern double-submit). Protection reset-password, change-password, delete-account. Désactivé en TESTING. |
| **3.1** DatabaseAdapter.execute_query | ✅ Corrigé | params exigé en dict pour paramètres nommés. TypeError si tuple. Documenté (audit 3.1). |
| **CSP** (audit tier 3.2) | ✅ Corrigé | Content-Security-Policy ajoutée dans next.config.ts (default-src, script-src, style-src, img-src, font-src, connect-src, frame-ancestors, base-uri). 15/02/2026 |
| **Rate limit resend-verification** | ✅ Corrigé | 2 req/min par IP (rate_limit_resend_verification). 15/02/2026 |
| **dangerouslySetInnerHTML** | ✅ Vérifié | Aucune occurrence dans le frontend. |
| **execute_raw_query** | ✅ Vérifié | Non utilisé (legacy). Délègue à execute_query avec params dict. |
| **Monitoring (HIGH #1)** | ✅ Corrigé | `app/core/monitoring.py` : `sentry_sdk.init()` au startup si SENTRY_DSN défini ; endpoint GET `/metrics` pour Prometheus ; middleware `http_requests_total`, `http_request_duration_seconds` (p50/p95/p99). Désactivé en TESTING. 15/02/2026 |

### Corrections en attente

| Faille | Statut | Raison |
|--------|--------|--------|
| — | — | Toutes les corrections identifiées ont été traitées. |

### Fichiers modifiés

- `server/handlers/auth_handlers.py` — `api_validate_token` (POST /api/auth/validate-token)
- `server/routes.py` — Route validate-token
- `server/middleware.py` — validate-token en route publique
- `frontend/app/api/auth/sync-cookie/route.ts` — Appel validate-token avant Set-Cookie
- `app/utils/rate_limit.py` — Décorateurs rate_limit_auth, rate_limit_register
- `app/core/config.py` — Blocage SECRET_KEY (2.3), DEFAULT_ADMIN_PASSWORD (3.3)
- `app/utils/error_handler.py` — `get_safe_error_message()`, durcissement `create_error_response`
- `app/services/auth_service.py` — Suppression log hashed_password
- `server/handlers/auth_handlers.py` — Critères mot de passe reset
- `server/handlers/chat_handlers.py` — Sanitization prompt, messages d'erreur sécurisés
- `server/handlers/user_handlers.py` — Messages d'erreur sécurisés
- `server/handlers/challenge_handlers.py` — Messages d'erreur sécurisés
- `server/handlers/exercise_handlers.py` — Messages d'erreur sécurisés
- `server/handlers/badge_handlers.py` — Messages d'erreur sécurisés
- `server/handlers/recommendation_handlers.py` — Messages d'erreur sécurisés
- `server/middleware.py` — `allow_headers` restreint (4.2), X-CSRF-Token, route csrf publique
- `app/utils/csrf.py` — Validation token double-submit (3.2)
- `server/handlers/auth_handlers.py` — api_get_csrf_token, CSRF sur reset-password
- `server/handlers/user_handlers.py` — CSRF sur change-password, delete-account
- `frontend/lib/api/client.ts` — getCsrfToken()
- `frontend/hooks/useProfile.ts` — X-CSRF-Token sur changement mot de passe
- `frontend/hooks/useSettings.ts` — X-CSRF-Token sur suppression compte
- `frontend/app/reset-password/page.tsx` — CSRF sur reset-password
- `app/services/email_service.py` — Envoi simulé en TESTING (tests auth)
- `app/db/adapter.py` — execute_query: params dict obligatoire, validation (3.1)
- `app/services/enhanced_server_adapter.py` — execute_raw_query: params dict
- `frontend/next.config.ts` — Content-Security-Policy (CSP)
- `app/utils/rate_limit.py` — rate_limit_resend_verification

---

## 8. Proposition de suite — Bénéfice / Risque / Priorité (Février 2026)

Proposition basée sur le rapport coût/bénéfice et le risque de régression. Ordre de priorité recommandé.

### P1 — Haute priorité (impact sécurité majeur, risque limité)

| # | Faille | Bénéfice | Risque | Priorité |
|---|--------|----------|--------|----------|
| 1 | **1.2 sync-cookie** | ~~Empêche le session hijacking~~ ✅ **FAIT** | — | ~~P1~~ |
| 2 | **2.3 SECRET_KEY** | ~~Garantit une SECRET_KEY stable en prod~~ ✅ **FAIT** (13/02/2026) | — | ~~P1~~ |
| 3 | **3.4 Rate limiting** | ~~Protège contre bruteforce~~ ✅ **FAIT** | — | ~~P1~~ |

### P2 — Priorité moyenne (renforce la défense en profondeur)

| # | Faille | Bénéfice | Risque | Priorité |
|---|--------|----------|--------|----------|
| 4 | **3.2 CSRF** | ~~Protège les actions sensibles~~ ✅ **FAIT** (13/02/2026) | — | ~~P2~~ |
| 5 | **4.2 CORS allow_headers** | ~~Réduit la surface d'attaque~~ ✅ **FAIT** (13/02/2026) | — | ~~P2~~ |

### P3 — Priorité basse (durcissement, impact limité à court terme)

| # | Faille | Bénéfice | Risque | Priorité |
|---|--------|----------|--------|----------|
| 6 | **3.1 execute_query** | Force l’usage de paramètres nommés, réduit le risque d’injection SQL par mauvaise utilisation~~ ✅ **FAIT** (13/02/2026) | — | ~~P3~~ |
| 7 | **3.3 DEFAULT_ADMIN_PASSWORD** | ~~Évite un compte admin exploitable~~ ✅ **FAIT** (13/02/2026) | — | ~~P3~~ |

### Ordre d’implémentation recommandé

1. ~~**1.2 sync-cookie**~~ — ✅ **FAIT** (13/02/2026)
2. ~~**3.4 Rate limiting**~~ — ✅ **FAIT** (13/02/2026)
3. ~~**4.2 CORS allow_headers**~~ — ✅ **FAIT** (13/02/2026)
4. ~~**2.3 SECRET_KEY**~~ — ✅ **FAIT** (13/02/2026)
5. ~~**3.2 CSRF**~~ — ✅ **FAIT** (13/02/2026)
6. ~~**3.1 execute_query**~~ — ✅ **FAIT** (13/02/2026)
7. ~~**3.3 DEFAULT_ADMIN_PASSWORD**~~ — ✅ **FAIT** (13/02/2026)

---

## 9. Prochaines étapes (post sync-cookie)

| # | Action | Effort | Criticité |
|---|--------|--------|-----------|
| 1 | ~~**3.4 Rate limiting**~~ — ✅ FAIT | — | — |
| 2 | ~~**4.2 CORS allow_headers**~~ — ✅ FAIT (13/02/2026) | — | — |
| 3 | ~~**2.3 SECRET_KEY**~~ — ✅ FAIT (13/02/2026) | — | — |
| 4 | ~~**3.2 CSRF**~~ — ✅ FAIT (13/02/2026) | — | — |
| 5 | ~~**3.1 execute_query**~~ — ✅ FAIT (13/02/2026) | — | — |

**Validation sync-cookie (1.2) :** ✅ Testé en dev et prod (login → validate-token → sync-cookie).

**Validation rate limiting (3.4) :** ✅ 31 tests passés (auth_flow, user_endpoints, auth_cookies_only). Pas d'effet de bord sur les flux normaux.

**Validation CORS (4.2) :** ✅ 23 tests passés après modification. Navigation manuelle : challenges, exercises, flux SSE AI — aucune erreur CORS en console. Headers autorisés : Content-Type, Authorization, Accept, Accept-Language.

**Validation SECRET_KEY (2.3) :** ✅ En prod sans SECRET_KEY → `ValueError` au démarrage. En dev/tests (TESTING=true ou ENVIRONMENT≠production) → génération auto OK. S'assurer que Render définit `SECRET_KEY` avant déploiement.

**Validation CSRF (3.2) :** ✅ Endpoint GET /api/auth/csrf. Protection reset-password, change-password, delete-account. Désactivé en TESTING. 18 tests auth passés. Déploiement prod OK.

**Validation DEFAULT_ADMIN_PASSWORD (3.3) :** ✅ En prod sans `DEFAULT_ADMIN_PASSWORD` ou égale à "admin" → `ValueError` au démarrage. Variable obligatoire sur Render.

**Validation execute_query (3.1) :** ✅ params dict obligatoire. `TypeError` si tuple. Tests unitaires ajoutés. execute_raw_query non appelé (legacy).

---

## Références

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet - Error Handling](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)
- [OWASP Cheat Sheet - Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
