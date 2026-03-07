# Flux d'authentification — Mathakine

> Parcours utilisateur et pages associées  
> **Date :** 15/02/2026 — **MAJ 06/03/2026** (sessions, flux auth clarifié, login non vérifié, B1/B2 backend)

---

## Vue d'ensemble

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  /register  │ ──▶ │ /verify-email   │ ──▶ │   /login    │
│  Inscription │     │ (token=xxx)     │     │ Connexion   │
└─────────────┘     └──────────────────┘     └─────────────┘
                                                    │
                                                    ▼
┌──────────────────┐     ┌─────────────────┐     ┌─────────────┐
│ /reset-password  │ ◀── │ /forgot-password │     │   App       │
│ (token=xxx)      │     │ Demande reset    │     │ Connecté    │
└──────────────────┘     └─────────────────┘     └─────────────┘
```

---

## 1. Inscription (Register)

**Page :** `/register`  
**API :** `POST /api/users/` (crée le compte)

| Champ | Validation |
|-------|------------|
| username | ≥ 3 caractères |
| email | Format email valide |
| password | ≥ 8 caractères, 1 chiffre, 1 majuscule |
| confirmPassword | Doit égaler password |
| full_name | Optionnel |

**Flux après succès :** Redirection vers `/verify-email?verify=true` (sans token) — l'utilisateur doit cliquer sur le lien reçu par email.

**États d'erreur :** email/username déjà utilisé → message d'erreur affiché. Si `registration_enabled=false` (admin config) → 403, inscriptions désactivées.

---

## 2. Vérification email (Verify Email)

**Page :** `/verify-email`  
**API :** `GET /api/auth/verify-email?token=xxx`  
**Service :** `AuthService.verify_email_token` (refactoré 26/02)

| Paramètre URL | Rôle |
|---------------|------|
| `token` | Token envoyé par email (obligatoire pour vérifier) |

**États de la page :**
| État | Déc déclencheur | Action utilisateur |
|------|-----------------|-------------------|
| `loading` | Token présent, requête en cours | — |
| `success` | Vérification réussie | Lien vers /login |
| `error` | Token invalide | Lien renvoi (avec email) |
| `expired` | Token expiré | Lien renvoi |
| `resend` | Pas de token | Formulaire email pour renvoyer |

**Renvoi email :** `POST /api/auth/resend-verification` avec `{email}`.

---

## 3. Connexion (Login)

**Page :** `/login`  
**API :** `POST /api/auth/login`

| Champ | Rôle |
|-------|------|
| username | Identifiant (pas email) |
| password | Mot de passe |

**Query params :**
- `registered=true` — Affiche message "Inscription réussie, vérifiez votre email"
- `verify=true` — Affiche message "Email vérifié, connectez-vous"

**Compte non vérifié :**

- le login reste autorisé
- l'utilisateur reçoit un `access_scope` limité tant que l'email n'est pas vérifié
- l'UX peut toujours proposer le renvoi via `POST /api/auth/resend-verification`

**Succès :**

- `access_token` renvoyé dans le body et posé en cookie HttpOnly de compatibilité
- `refresh_token` posé en cookie HttpOnly
- création d'une `UserSession` en base via `authenticate_user_with_session()`
- redirection frontend vers `/dashboard`

---

## 4. Mot de passe oublié (Forgot Password)

**Page :** `/forgot-password`  
**API :** `POST /api/auth/forgot-password`

| Champ | Validation |
|-------|------------|
| email | Format email valide |

**Flux :**  
1. Utilisateur entre son email  
2. Backend envoie email avec lien `https://.../reset-password?token=xxx`  
3. Page affiche message de confirmation (même si email inconnu — sécurité)

---

## 5. Réinitialisation mot de passe (Reset Password)

**Page :** `/reset-password`  
**API :** `POST /api/auth/reset-password`  
**Service :** `AuthService.reset_password_with_token` (refactoré 26/02)

| Paramètre | Source |
|-----------|--------|
| token | Query `?token=xxx` (obligatoire) |
| password | Formulaire |
| password_confirm | Formulaire |

**Validation :** Mot de passe ≥ 8 caractères (le backend impose aussi chiffre + majuscule).

**États :**
| État | Déc déclencheur |
|------|-----------------|
| `form` | Token présent, formulaire affiché |
| `loading` | Requête en cours |
| `success` | Redirection vers /login après 2s |
| `error` | Token manquant ou expiré / erreur API |

**CSRF :** Le header `X-CSRF-Token` est automatiquement injecté par `apiRequest()` (lecture du cookie `csrf_token` posé au login). Centralisé via `CsrfMiddleware` depuis l'audit H6 (02/03/2026) — plus d'appel explicite à `getCsrfToken()` dans les composants.

---

## Fichiers clés

| Rôle | Fichier |
|------|---------|
| Hook auth | `frontend/hooks/useAuth.ts` |
| Client API | `frontend/lib/api/client.ts` |
| Route protégée | `frontend/components/auth/ProtectedRoute.tsx` |
| Pages | `frontend/app/{login,register,verify-email,forgot-password,reset-password}/page.tsx` |
| Backend handlers | `server/handlers/auth_handlers.py`, `server/handlers/user_handlers.py` |
| Logique métier | `app/services/auth_service.py` (verify_email_token, reset_password_with_token, authenticate_user_with_session, create_registered_user_with_verification) |

**Note Next.js (15/02)** : Les pages `reset-password` et `verify-email` utilisent `useSearchParams()` pour lire le token dans l'URL. Elles sont enveloppées dans un boundary `<Suspense>` afin de respecter les exigences de l'App Router (prerender).

---

## Erreurs courantes et debugging

| Symptôme | Cause possible |
|----------|----------------|
| Compte non vérifié après login | Accès limité tant que l'email n'est pas vérifié ; proposer le renvoi de verification |
| Cookie non envoyé | Domaine différent (prod) → sync via `sync-cookie` |
| Token expiré (verify/reset) | Lien trop ancien → renvoyer l'email |
| 401 après login | Refresh token manquant ou expiré → se reconnecter |

### Codes HTTP — Auth

| Endpoint | Cas d'erreur | Code |
|----------|--------------|------|
| `POST /api/auth/refresh` | Token/cookie manquant | **401** Unauthorized |
| `POST /api/auth/refresh` | Token expiré ou invalide | **401** Unauthorized |

→ Voir [CONFIGURER_EMAIL](../01-GUIDES/CONFIGURER_EMAIL.md) pour la configuration des envois d'email.

---

## 6. Sessions actives et paramètres plateforme

### Sessions actives
- **Page** : `/settings` — section « Sessions actives »
- **API** : `GET /api/users/me/sessions` (liste avec `is_current: true` sur la session courante)
- **Révocation** : `DELETE /api/users/me/sessions/{id}` — marque la session inactive
- **Création** : Une `UserSession` est créée à chaque login réussi

### Inscriptions désactivées
- **Paramètre** : `registration_enabled=false` (table `settings`, admin `/admin/config`)
- **Comportement** : `POST /api/users/` renvoie **403** si inscriptions désactivées
- **Message** : Erreur affichée sur la page `/register`

### Mode maintenance
- **Paramètre** : `maintenance_mode=true` (table `settings`)
- **Backend** : Middleware 503 sur toutes les routes sauf `/health`, `/metrics`, `/api/admin/*`, `/api/auth/login`, refresh, validate-token
- **Frontend** : Overlay blocant (`MaintenanceOverlay.tsx`) sauf sur `/login` et `/admin` — lien « Accès admin » vers `/login`
