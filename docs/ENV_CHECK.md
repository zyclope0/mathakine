# Checklist .env & Render – Environnement de développement

## ✅ Ton .env actuel (dev local)

| Variable | Statut | Note |
|----------|--------|------|
| DATABASE_URL | ✅ | Pointe vers Render → ton serveur local utilise la BDD Render |
| TEST_DATABASE_URL | ✅ | Pointe vers Docker local → les tests utilisent la BDD locale |
| SECRET_KEY | ✅ | Défini |
| LOG_LEVEL | ✅ | INFO |
| FRONTEND_URL | ✅ | localhost:3000 pour le dev |
| OPENAI_API_KEY | ✅ | Défini (génération d'exercices IA) |
| PORT | ✅ | 10000 |
| MATH_TRAINER_PROFILE | ⚠️ | = prod → pour le dev local, tu peux passer en `dev` |
| NEXT_PUBLIC_API_BASE_URL | ℹ️ | Variable frontend – à définir dans `frontend/.env.local` |
| NEXT_PUBLIC_DEMO_MODE | ℹ️ | Variable frontend |

---

## 🔧 Variables optionnelles (avec valeurs par défaut)

Ces variables ont des valeurs par défaut, pas besoin de les mettre dans le `.env` sauf si tu veux changer le comportement :

- `LOG_FILE`, `CACHE_TTL_SECONDS`, `MAX_CONNECTIONS_POOL`, `POOL_RECYCLE_SECONDS`
- `RATE_LIMIT_PER_MINUTE`, `ENABLE_QUERY_CACHE`, `OPENAI_MODEL`

---

## 📧 Emails (mot de passe oublié, vérification email)

Guide détaillé : **[docs/01-GUIDES/CONFIGURER_EMAIL.md](01-GUIDES/CONFIGURER_EMAIL.md)** — Sans config : simulés en dev, erreur en prod.

Par défaut, les emails sont simulés si SMTP n’est pas configuré. Pour envoyer de vrais emails (ex. vérification d’email) :

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ton_email@gmail.com
SMTP_PASSWORD=mot_de_passe_application
SMTP_FROM_EMAIL=noreply@mathakine.com
```

Ou avec SendGrid :

```
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@mathakine.com
```

---

## 🌐 Variables à configurer sur Render

Dans le **Dashboard Render** → ton service backend → **Environment** :

### Déjà gérées par Render (si tout est correctement lié)

| Variable | Source |
|----------|--------|
| DATABASE_URL | Injectée par Render si la base est liée au service |
| SECRET_KEY | **Obligatoire** en prod. Peut être générée par Render (`generateValue: true`). Sans elle, l'app ne démarre pas (sécurité 2.3). |

### À définir à la main dans Render

| Variable | Valeur | Obligatoire |
|----------|--------|-------------|
| **OPENAI_API_KEY** | Ta clé API OpenAI | ✅ (pour la génération d’exercices IA) |
| ENVIRONMENT | `production` | ✅ |
| MATH_TRAINER_PROFILE | `prod` | ✅ |
| FRONTEND_URL | `https://mathakine-frontend.onrender.com` (ou ton URL front) | ✅ |
| LOG_LEVEL | `INFO` | Recommandé |

### Exemple pour le service backend

1. Render Dashboard → **mathakine-backend** → **Environment**
2. Vérifier / ajouter :
   - `OPENAI_API_KEY` = `sk-proj-...` (ta clé)
   - `ENVIRONMENT` = `production`
   - `FRONTEND_URL` = `https://mathakine-frontend.onrender.com`
   - `SECRET_KEY` = une chaîne longue et aléatoire si Render ne l’a pas générée

---

## 📋 Résumé rapide

**Env local (.env)**  
- Tests → `TEST_DATABASE_URL` (Docker local)  
- Serveur local → `DATABASE_URL` (Render ou autre selon ton besoin)

**Render (production)**  
- Vérifier que `DATABASE_URL` est bien liée à la base PostgreSQL  
- Définir `OPENAI_API_KEY`  
- **Obligatoire** : `SECRET_KEY` (sans elle, le backend ne démarre pas en prod)  

Ton `.env` actuel est cohérent pour le dev local.  
La seule chose à confirmer sur Render est la présence de `OPENAI_API_KEY`.
