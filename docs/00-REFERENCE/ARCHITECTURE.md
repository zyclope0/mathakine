# Architecture - Mathakine

> Reference architecture globale (backend + frontend)
> Derniere mise a jour : 11/03/2026

---

## 1. Vue systeme

Mathakine est structure en 3 couches :

1. `frontend/` (Next.js 16) : interface utilisateur, pages, hooks React Query, i18n FR/EN.
2. `server/` (Starlette) : couche HTTP (routes, handlers, auth, middleware, SSE/proxy).
3. `app/` (domaine) : logique metier, services applicatifs, repositories, generateurs, modeles SQLAlchemy, schemas.

Flux principal :

```text
Browser -> Next.js (frontend) -> Starlette routes/handlers -> app/services -> app/repositories -> PostgreSQL
```

---

## 2. Principes d'architecture

- Separation stricte : handler HTTP mince, logique metier dans `app/services`, acces data isole dans `app/repositories`.
- Source de verite API : `server/routes/` + handlers associes.
- Transactions : les flux mutateurs sont portes par les services proprietaires.
- i18n et UX : le frontend pilote l'affichage ; le backend preserve des contrats stables.
- Securite : auth Cookie/Bearer, CSRF middleware, redaction des secrets dans les logs DB (F35), revocation auth via `password_changed_at` + `iat`.

---

## 3. Domaines fonctionnels

Backend (`app/services` + `server/handlers`) :

- Authentification, verification et recovery utilisateur
- Exercices, tentatives et session entrelacee
- Defis logiques et progression
- Recommendations adaptatives
- Badges et progression badges
- Analytics EdTech (Quick Start / first attempt)
- Administration (users, content, moderation, config, reports)

Fonctionnalites recentes importantes :

- F07 : timeline progression (`GET /api/users/me/progress/timeline`)
- F32 : session entrelacee (`GET /api/exercises/interleaved-plan`)
- F35 : redaction URL DB au log de demarrage (`redact_database_url_for_log`)
- 09/03 : iteration backend `exercise/auth/user` cloturee et archivee
- 11/03 : iteration backend `challenge/admin/badge` cloturee et archivee

---

## 4. Frontend (synthese)

- App Router Next.js (`frontend/app`)
- Composants par domaine (`frontend/components/*`)
- Hooks metier (`frontend/hooks/*`)
- Client API centralise (`frontend/lib/api/client.ts`)
- Stores UI (Zustand), data serveur (React Query), i18n (`frontend/messages`)

Reference detaillee frontend :
- [ARCHITECTURE Frontend](../04-FRONTEND/ARCHITECTURE.md)

---

## 5. Backend (synthese)

- `server/routes/` : declaration des endpoints
- `server/handlers/` : adaptation HTTP (parse, validation transport, reponse)
- `app/services/` : orchestration metier et facades applicatives
- `app/repositories/` : acces data isole pour les flux refactores
- `app/generators/` : source de verite de la generation d'exercices
- `app/models/` : ORM SQLAlchemy
- `app/db/` : session, engine, adapter, transactions

Boundaries refactorees et stabilisees au 11/03/2026 :

- `exercise` : `exercise_generation_service.py`, `exercise_attempt_service.py`, `exercise_query_service.py`, `exercise_stream_service.py`
- `auth` : `auth_session_service.py`, `auth_recovery_service.py`
- `user` : `user_application_service.py`
- `challenge` : `challenge_query_service.py`, `challenge_attempt_service.py`, `challenge_stream_service.py`
- `admin` : `admin_read_service.py`, `admin_application_service.py`
- `badge` : `badge_application_service.py`

Compatibilite :

- `server/exercise_generator*.py` restent presents comme couches de re-export vers `app/generators` et `app/utils`
- ils ne sont plus la source de verite a faire evoluer

Reference technique complete :
- [README_TECH racine](../../README_TECH.md)

Audit architecture backend :
- [AUDIT_ARCHITECTURE_BACKEND_2026-03](../03-PROJECT/AUDIT_ARCHITECTURE_BACKEND_2026-03.md)

---

## 6. Contrats API a connaitre

- `POST /api/exercises/generate` : `exercise_type` requis, `age_group` optionnel, `adaptive` supporte.
- `GET /api/exercises/interleaved-plan` : plan entrelace, `409 not_enough_variety` si varietes insuffisantes.
- `GET /api/users/me/progress/timeline` : points 7j/30j + resume.
- `POST /api/auth/reset-password` : revoque les anciens access/refresh tokens et les sessions existantes.
- `PUT /api/users/me/password` : aligne la revocation sur le meme mecanisme que le reset password.

Reference API complete :
- [API_QUICK_REFERENCE](../02-FEATURES/API_QUICK_REFERENCE.md)

---

## 7. Documentation canonique

- Vue technique globale : [README_TECH](../../README_TECH.md)
- Flux auth : [AUTH_FLOW](../02-FEATURES/AUTH_FLOW.md)
- Index documentation : [docs/INDEX](../INDEX.md)
- Architecture frontend detaillee : [04-FRONTEND/ARCHITECTURE](../04-FRONTEND/ARCHITECTURE.md)

