# Checklist .env & Render - Environnement de developpement

**Derniere mise a jour :** 06/03/2026  
**Complement a :** [DEPLOYMENT_ENV.md](DEPLOYMENT_ENV.md) (variables prod Render)

> ⚠️ **OBSOLÈTE (section historique)** — La partie « Ton .env actuel » plus bas est un **snapshot local** ; ne pas l’utiliser comme contrat d’équipe.
>
> **À lire en priorité :**
> - [DEPLOYMENT_ENV.md](DEPLOYMENT_ENV.md) — prod Render
> - [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md) — overrides modèles IA (`OPENAI_MODEL_*`)
> - Racine [`../../.env.example`](../../.env.example) + `app/core/config.py` — liste et défauts réels

---

## Contrat generique actuel

### Backend local minimum

- `DATABASE_URL`
- `SECRET_KEY`
- `FRONTEND_URL`
- `OPENAI_API_KEY` si tu utilises `assistant_chat`, `exercises_ai` ou `challenges_ai`

### Frontend local minimum

- `NEXT_PUBLIC_API_BASE_URL` dans `frontend/.env.local` si le frontend tourne separement du backend

### Backend production Render minimum

- `DATABASE_URL`
- `SECRET_KEY`
- `OPENAI_API_KEY`
- `FRONTEND_URL`
- `ENVIRONMENT=production`
- `MATH_TRAINER_PROFILE=prod`
- `REDIS_URL` : requis en production pour le rate limiting distribue
- `DEFAULT_ADMIN_PASSWORD` : requis et fort en production

### Variables IA optionnelles

- `OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE`
- `OPENAI_MODEL_EXERCISES_OVERRIDE`
- `OPENAI_MODEL_CHALLENGES_OVERRIDE`
- `OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE`

Ces variables sont des overrides ops. Elles ne remplacent pas les defauts produit codes.

### Variables legacy a laisser vides en nominal

- `OPENAI_MODEL` — **legacy chat uniquement** (si renseigné + allowlist assistant, peut servir d’override ; sinon ignoré). Le pilotage explicite du chat = `OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE`. Voir `AI_MODEL_GOVERNANCE.md`.
- `OPENAI_MODEL_EXERCISES`
- `OPENAI_MODEL_REASONING`

Ces variables existent pour compatibilite ou transition ; les flux nominaux exercices / défis ne doivent pas en dépendre.

---

## Snapshot local historique (conserve pour trace)

> ⚠️ OBSOLETE - ce qui suit decrit un contexte local ponctuel et non un contrat generique de projet.

## Ton .env actuel (dev local)

| Variable | Statut | Note |
|----------|--------|------|
| DATABASE_URL | OK | Pointe vers Render -> ton serveur local utilise la BDD Render |
| TEST_DATABASE_URL | OK | Pointe vers Docker local -> les tests utilisent la BDD locale |
| SECRET_KEY | OK | Defini |
| LOG_LEVEL | OK | INFO |
| FRONTEND_URL | OK | localhost:3000 pour le dev |
| OPENAI_API_KEY | OK | Defini |
| PORT | OK | 10000 |
| MATH_TRAINER_PROFILE | Attention | `prod` en local -> preferer `dev` pour un vrai contexte local |
| NEXT_PUBLIC_API_BASE_URL | Info | Variable frontend a definir dans `frontend/.env.local` |
| NEXT_PUBLIC_DEMO_MODE | Info | Variable frontend |

## Variables optionnelles (avec valeurs par defaut)

Ces variables ont des valeurs par defaut ; inutile de les mettre dans le `.env` sauf si tu veux changer le comportement :

- `LOG_FILE`, `CACHE_TTL_SECONDS`, `MAX_CONNECTIONS_POOL`, `POOL_RECYCLE_SECONDS`
- `RATE_LIMIT_PER_MINUTE`, `ENABLE_QUERY_CACHE`
- `OPENAI_MODEL` (legacy assistant si non vide et allowlist fail-closed : `gpt-5-mini`, `gpt-5.4`, `gpt-4o-mini`, `gpt-4o` - vide recommande ; defaut assistant = `gpt-5-mini`)
- `OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE` (override ops assistant ; meme allowlist fail-closed ; vide = defaut produit)
- `OPENAI_MODEL_EXERCISES_OVERRIDE` (override ops flux SSE exercices IA ; defaut code = `o4-mini`), `OPENAI_MODEL_EXERCISES` (legacy)
- `OPENAI_MODEL_CHALLENGES_OVERRIDE` (override ops flux SSE defis IA, prioritaire), `OPENAI_MODEL_REASONING` (legacy defis ; non nominal, laisser vide), `OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE` (fallback defis ; defaut code = `gpt-4o-mini`)

## Emails (mot de passe oublie, verification email)

Guide detaille : [CONFIGURER_EMAIL.md](CONFIGURER_EMAIL.md). Sans config : simules en dev, erreur en prod.

Exemple SMTP :

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ton_email@gmail.com
SMTP_PASSWORD=mot_de_passe_application
SMTP_FROM_EMAIL=noreply@mathakine.com
```

Exemple SendGrid :

```env
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@mathakine.com
```

## Variables a configurer sur Render

### Gerees par Render si le service est correctement relie

| Variable | Source |
|----------|--------|
| DATABASE_URL | Injectee par Render si la base est liee au service |
| SECRET_KEY | Obligatoire en prod. Peut etre generee par Render |

### A definir a la main dans Render

| Variable | Valeur | Obligatoire |
|----------|--------|-------------|
| OPENAI_API_KEY | Ta cle API OpenAI | Oui |
| ENVIRONMENT | `production` | Oui |
| MATH_TRAINER_PROFILE | `prod` | Oui |
| FRONTEND_URL | URL frontend de production | Oui |
| LOG_LEVEL | `INFO` | Recommande |
| REDIS_URL | URL Redis de production | Oui |
| DEFAULT_ADMIN_PASSWORD | Secret fort | Oui |

## Resume rapide

**Env local (.env)**
- Tests -> `TEST_DATABASE_URL`
- Serveur local -> `DATABASE_URL`

**Render (production)**
- verifier que `DATABASE_URL` est bien liee a PostgreSQL
- definir `OPENAI_API_KEY`
- definir `REDIS_URL`
- definir `DEFAULT_ADMIN_PASSWORD`
- verifier `SECRET_KEY`
