# ADR-002 : Chat assistant — accès public sans authentification

**Date :** 2026-03-27
**Statut :** Accepté

---

## Contexte

Mathakine expose un assistant mathématique conversationnel (`/api/chat`). Ce service est implémenté comme un proxy Next.js (`frontend/app/api/chat/route.ts`) qui transmet les requêtes au backend Starlette (`server/routes/chat.py`).

Le backend appelle OpenAI (modèle configuré via `OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE`, défaut `gpt-5-mini`) à chaque requête.

Au moment de l'implémentation initiale, le service a été délibérément rendu accessible sans authentification JWT pour réduire la friction d'onboarding et permettre à des utilisateurs non inscrits de tester l'assistant.

Cette décision implique plusieurs contraintes opérationnelles :

- Chaque requête consomme des tokens OpenAI facturés à l'opérateur.
- Aucun mécanisme de quota par utilisateur n'est applicable sans session.
- La seule protection en place est le rate limiting distribué Redis (`app/utils/rate_limit.py`, règle `chat`), actif uniquement si `REDIS_URL` est défini et `ENVIRONMENT=production`.
- En développement ou si Redis est absent, le fallback in-memory est un store non partagé entre workers Gunicorn, rendant le rate limiting inefficace en charge parallèle.

L'absence d'authentification est référencée comme risque prioritaire P1 dans `CLAUDE.md` (section « Risques prioritaires connus »).

---

## Décision

Le service chat reste accessible sans authentification JWT dans la version actuelle (2.1.x).

Le contrôle de coût repose exclusivement sur le rate limiting Redis (`REDIS_URL` obligatoire en production). Aucun accès anonyme au backend OpenAI n'est autorisé sans rate limiting actif.

La migration vers une route authentifiée est planifiée comme lot distinct, conditionné à la première brique payante (tableau de bord parent/enseignant).

---

## Conséquences

### Positives

- Onboarding sans friction pour les utilisateurs non inscrits.
- Pas de gate d'inscription requis pour tester l'assistant.
- Simplicité d'implémentation du proxy frontend.

### Négatives / Risques

- Exposition directe au coût OpenAI sans plafond par utilisateur : un acteur malveillant ou un bot contournant le rate limiting génère des coûts non bornés.
- Rate limiting inopérant si `REDIS_URL` est absent en production (fallback in-memory non partagé entre workers).
- Aucune traçabilité d'usage par utilisateur (analytics, quotas freemium/payant impossibles sans authentification).
- Incompatible avec une logique de quota d'abonnement (obligation de migrer avant le lancement payant).

### Décisions liées

- `render.yaml` : `REDIS_URL` déclaré `sync: false` (obligatoire, sans valeur par défaut).
- `docs/01-GUIDES/DEPLOYMENT_ENV.md` : `REDIS_URL` listé comme variable requise en production.
- Lot de migration vers route authentifiée : priorité 3 dans `CLAUDE.md` (« Sécurisation route chat »).
