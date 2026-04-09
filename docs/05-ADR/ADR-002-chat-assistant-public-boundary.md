# ADR-002 : Chat assistant - accès public sans authentification

**Date :** 2026-03-27  
**Statut :** Superseded (2026-04-06 par `CHAT-AUTH-01`)

---

## Contexte historique

Mathakine exposait initialement un assistant mathématique conversationnel (`/api/chat`, `/api/chat/stream`) sans authentification JWT, via un proxy Next.js côté frontend et des handlers Starlette accessibles hors whitelist publique côté backend.

Cette décision avait été prise pour réduire la friction d'onboarding et permettre à des utilisateurs non inscrits de tester l'assistant.

Elle impliquait :

- un coût OpenAI directement exposé à du trafic anonyme
- l'absence de quota ou traçabilité par utilisateur
- une dépendance forte au rate limiting Redis comme seule barrière opérationnelle

---

## Décision d'origine

Le service chat est resté public dans la version documentée à l'époque, avec contrôle de coût reposant uniquement sur le rate limiting.

Cette ADR capturait cette décision comme vérité active au 27/03/2026.

---

## Ce qui a changé

Cette décision n'est plus la vérité runtime.

Depuis `CHAT-AUTH-01` :

- `POST /api/chat` et `POST /api/chat/stream` exigent une session valide côté backend Starlette
- le proxy Next `frontend/app/api/chat/*` refuse aussi les requêtes sans cookie `access_token`
- le frontend garde le shell assistant visible pour les invités, mais bloque l'envoi et affiche le CTA existant (`guestLimitCta`)

---

## Vérité actuelle

Le chat n'est plus public.

La source de vérité active est désormais :

- `server/routes/chat.py`
- `server/handlers/chat_handlers.py`
- `frontend/app/api/chat/route.ts`
- `frontend/app/api/chat/stream/route.ts`
- `frontend/lib/api/chatProxyRequest.ts`
- `README_TECH.md`
- `.claude/session-plan.md`

---

## Conséquences

### Positives

- coût OpenAI borné à des utilisateurs authentifiés
- meilleure cohérence avec les futures surfaces payantes / quotas
- politique d'accès homogène avec le reste des routes protégées

### Négatives / trade-offs acceptés

- friction d'accès plus élevée pour tester l'assistant
- les invités ne peuvent plus envoyer de messages, seulement voir le shell / CTA

---

## Statut documentaire

Cette ADR est conservée comme photographie historique d'une décision désormais abandonnée.

Elle ne doit plus être lue comme doctrine active.
