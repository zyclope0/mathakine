# Flux d'authentification - Mathakine

> Parcours utilisateur et pages associees
> **Date :** 15/02/2026 - **MAJ 09/03/2026** (boundary session/recovery refactoree, revocation post-reset et post-change password)

---

## Vue d'ensemble

```
/register -> /verify-email -> /login -> application protegee
                ^                |
                |                v
POST /api/auth/resend-verification   session cookies + refresh

/forgot-password -> email reset -> /reset-password?token=... -> /login
```

---

## 1. Inscription

**Page :** `/register`
**API :** `POST /api/users/`

Champs principaux :
- `username` - >= 3 caracteres
- `email` - format email valide
- `password` - >= 8 caracteres, avec les regles de force backend
- `full_name` - optionnel

Flux apres succes :
- creation utilisateur via `UserCreate`
- generation du token de verification
- envoi email de verification
- redirection frontend vers `/verify-email?verify=true`

---

## 2. Verification email

**Page :** `/verify-email`
**API :** `GET /api/auth/verify-email?token=...`
**Boundary backend :** `auth_recovery_service.py`

Etats fonctionnels :
- `success` - email verifie
- `already_verified` - lien rejoue
- `invalid` - token invalide
- `expired` - token expire
- `resend` - renvoi manuel via email

Renvoi manuel :
- `POST /api/auth/resend-verification` avec `{email}`
- le flow reste volontairement discret sur l'existence reelle du compte
- un email mal forme ou inexistant retourne le meme message generique de securite

---

## 3. Connexion et session

**Page :** `/login`
**API :** `POST /api/auth/login`
**Boundary backend :** `auth_session_service.py`

Succes :
- `access_token` renvoye dans le body et pose en cookie HttpOnly
- `refresh_token` pose en cookie HttpOnly
- `csrf_token` pose en cookie non HttpOnly (double-submit)
- creation d'une `UserSession` en base
- redirection frontend vers la zone protegee

Compte non verifie :
- le login reste autorise
- `access_scope` reste limite tant que l'email n'est pas verifie

Refresh / bootstrap :
- `POST /api/auth/refresh` accepte le cookie `refresh_token` (ou le body si necessaire)
- `POST /api/auth/validate-token` valide un token frontend avant sync-cookie
- `GET /api/users/me` reconstruit l'utilisateur courant a partir du token valide
- `POST /api/auth/logout` supprime les cookies d'auth

---

## 4. Mot de passe oublie

**Page :** `/forgot-password`
**API :** `POST /api/auth/forgot-password`
**Boundary backend :** `auth_recovery_service.py`

Flux :
1. l'utilisateur saisit son email
2. si le compte existe et est actif, un email de reset est envoye
3. la reponse reste la meme meme si l'email n'existe pas

Objectif securite : ne pas reveler si l'adresse est associee a un compte.

---

## 5. Reinitialisation mot de passe

**Page :** `/reset-password`
**API :** `POST /api/auth/reset-password`
**Body :** `{token, password, password_confirm}`
**Boundary backend :** `auth_recovery_service.py` + `auth_service.py`

Succes :
- mot de passe remplace
- `password_changed_at` mis a jour
- toutes les `UserSession` existantes supprimees
- tous les access / refresh tokens emis avant ce moment sont rejetes via `iat`
- reponse HTTP inchangee : message succes + `success: true`

Effet utilisateur :
- un autre onglet deja ouvert peut encore afficher son etat courant
- des qu'il renavigue ou refait un appel protege, il doit se reconnecter

---

## 6. Changement de mot de passe depuis le profil

**Page :** `/settings` / espace compte
**API :** `PUT /api/users/me/password`
**Boundary backend :** `user_application_service.py` -> `UserService.update_user_password`

Depuis cette iteration, ce flow est aligne sur le reset password :
- mise a jour du hash
- mise a jour de `password_changed_at`
- revocation des sessions existantes
- rejet des anciens access / refresh tokens apres la reponse courante

---

## 7. Sessions actives

**Page :** `/settings` - section sessions actives
**API :**
- `GET /api/users/me/sessions`
- `DELETE /api/users/me/sessions/{id}`

Comportement :
- une `UserSession` est creee a chaque login reussi
- la session courante est marquee `is_current: true`
- la revocation manuelle des sessions reste disponible

---

## Fichiers cles

| Role | Fichier |
|------|---------|
| Hooks auth frontend | `frontend/hooks/useAuth.ts` |
| Client API | `frontend/lib/api/client.ts` |
| Route protegee | `frontend/components/auth/ProtectedRoute.tsx` |
| Pages frontend | `frontend/app/{login,register,verify-email,forgot-password,reset-password}/page.tsx` |
| Handlers backend | `server/handlers/auth_handlers.py`, `server/handlers/user_handlers.py` |
| Session auth | `app/services/auth_session_service.py` |
| Recovery auth | `app/services/auth_recovery_service.py` |
| Moteur auth | `app/services/auth_service.py` |
| Auth runtime | `server/auth.py`, `server/middleware.py` |

---

## Codes HTTP usuels

| Endpoint | Cas d'erreur | Code |
|----------|--------------|------|
| `POST /api/auth/login` | credentials invalides | `401` |
| `POST /api/auth/refresh` | refresh token manquant/invalide/revoque | `401` |
| `GET /api/auth/verify-email` | token invalide ou expire | `400` |
| `POST /api/auth/resend-verification` | email manquant | `400` |
| `POST /api/auth/forgot-password` | erreur d'envoi email | `500` |
| `POST /api/auth/reset-password` | token invalide ou expire | `400` |
| `PUT /api/users/me/password` | mot de passe courant incorrect | `401` |

---

Voir aussi : [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) et [CONFIGURER_EMAIL.md](../01-GUIDES/CONFIGURER_EMAIL.md)
