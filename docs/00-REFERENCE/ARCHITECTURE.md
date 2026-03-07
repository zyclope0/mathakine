# Architecture - Mathakine

> Reference architecture globale (backend + frontend)  
> Derniere mise a jour : 07/03/2026

---

## 1. Vue systeme

Mathakine est structure en 3 couches:

1. `frontend/` (Next.js 16): interface utilisateur, pages, hooks React Query, i18n FR/EN.
2. `server/` (Starlette): couche HTTP (routes, handlers, auth, middleware, SSE/proxy).
3. `app/` (domaine): logique metier, services, modeles SQLAlchemy, schemas.

Flux principal:

```text
Browser -> Next.js (frontend) -> Starlette routes/handlers -> app/services -> PostgreSQL
```

---

## 2. Principes d'architecture

- Separation stricte: handler HTTP mince, logique metier dans `app/services`.
- Source de verite API: `server/routes/` + handlers associes.
- Transactions: flux mutateurs portes par les services proprietaires.
- i18n et UX: front pilote l'affichage, backend renvoie des contrats stables.
- Securite: auth Cookie/Bearer, CSRF middleware, redaction des secrets dans les logs DB (F35).

---

## 3. Domaines fonctionnels

Backend (`app/services` + `server/handlers`):

- Authentification et sessions utilisateur
- Exercices et tentatives
- Defis logiques et progression
- Recommendations adaptatives
- Badges et progression badges
- Analytics EdTech (Quick Start / first attempt)
- Administration (users, content, moderation, config, reports)

Fonctionnalites recentes:

- F07: timeline progression (`GET /api/users/me/progress/timeline`)
- F32: session entrelacee (`GET /api/exercises/interleaved-plan`)
- F35: redaction URL DB au log de demarrage (`redact_database_url_for_log`)

---

## 4. Frontend (synthese)

- App Router Next.js (`frontend/app`)
- Composants par domaine (`frontend/components/*`)
- Hooks metier (`frontend/hooks/*`)
- Client API centralise (`frontend/lib/api/client.ts`)
- Stores UI (Zustand), data serveur (React Query), i18n (`frontend/messages`)

Reference detaillee frontend:
- [ARCHITECTURE Frontend](../04-FRONTEND/ARCHITECTURE.md)

---

## 5. Backend (synthese)

- `server/routes/`: declaration des endpoints
- `server/handlers/`: adaptation HTTP (parse/validation/reponse)
- `app/services/`: orchestration metier
- `app/models/`: ORM SQLAlchemy
- `app/db/`: session/engine/adapter

Reference technique complete:
- [README_TECH racine](../../README_TECH.md)

Audit architecture backend:
- [AUDIT_ARCHITECTURE_BACKEND_2026-03](../03-PROJECT/AUDIT_ARCHITECTURE_BACKEND_2026-03.md)

---

## 6. Contrats API a connaitre

- `POST /api/exercises/generate`: `exercise_type` requis, `age_group` optionnel, `adaptive` supporte.
- `GET /api/exercises/interleaved-plan`: plan entrelace, `409 not_enough_variety` si varietes insuffisantes.
- `GET /api/users/me/progress/timeline`: points 7j/30j + resume.

Reference API complete:
- [API_QUICK_REFERENCE](../02-FEATURES/API_QUICK_REFERENCE.md)

---

## 7. Documentation canonique

- Vue technique globale: [README_TECH](../../README_TECH.md)
- Index documentation: [docs/INDEX](../INDEX.md)
- Architecture frontend detaillee: [04-FRONTEND/ARCHITECTURE](../04-FRONTEND/ARCHITECTURE.md)

