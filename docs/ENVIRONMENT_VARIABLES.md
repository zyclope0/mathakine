# 🔧 Variables d'Environnement - Mathakine

**Date** : Novembre 2025  
**Version** : 1.0

---

## 📋 **Vue d'Ensemble**

Ce document liste toutes les variables d'environnement requises pour le fonctionnement de Mathakine en développement et en production.

---

## 🎯 **FRONTEND (Next.js)**

### **Variables Obligatoires en Production**

| Variable | Description | Exemple Dev | Exemple Prod | Obligatoire |
|----------|-------------|-------------|--------------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | URL du backend API | `http://localhost:8000` | `https://api.mathakine.com` | ✅ Production |
| `NEXT_PUBLIC_SITE_URL` | URL publique du site | `http://localhost:3000` | `https://mathakine.com` | ✅ Production |
| `NODE_ENV` | Environnement (géré automatiquement) | `development` | `production` | ✅ Auto |

### **Variables Optionnelles**

| Variable | Description | Défaut | Notes |
|----------|-------------|--------|-------|
| `NEXT_PUBLIC_API_URL` | Alternative à `NEXT_PUBLIC_API_BASE_URL` | - | Utilisé si `NEXT_PUBLIC_API_BASE_URL` non défini |

### **Configuration Frontend**

**Fichier** : `frontend/.env.local` (développement) ou variables d'environnement (production)

```bash
# Backend API
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Site URL
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

**⚠️ IMPORTANT** :
- Les variables `NEXT_PUBLIC_*` sont exposées au client (ne jamais mettre de secrets)
- Ne jamais commiter `.env.local` dans Git
- En production, définir ces variables dans votre plateforme de déploiement

---

## 🎯 **BACKEND (Python/FastAPI)**

### **Variables Obligatoires en Production**

| Variable | Description | Exemple Dev | Exemple Prod | Obligatoire |
|----------|-------------|-------------|--------------|-------------|
| `SECRET_KEY` | Clé secrète pour JWT | Généré auto | `votre-cle-secrete-32-caracteres` | ✅ Production |
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://user:pass@localhost/mathakine` | `postgresql://...` | ✅ Production |
| `OPENAI_API_KEY` | Clé API OpenAI (si génération IA) | `sk-...` | `sk-...` | ⚠️ Optionnel |

### **Variables de Configuration**

| Variable | Description | Défaut | Notes |
|----------|-------------|--------|-------|
| `LOG_LEVEL` | Niveau de logging | `INFO` | ⚠️ Ne peut pas être `DEBUG` en production |
| `ENVIRONMENT` | Environnement | `development` | `production` pour prod |
| `MATH_TRAINER_PROFILE` | Profil d'environnement | `dev` | `prod` pour production |
| `FRONTEND_URL` | URL du frontend (pour CORS) | `http://localhost:3000` | Obligatoire en production |
| `POSTGRES_SERVER` | Serveur PostgreSQL | `localhost` | - |
| `POSTGRES_USER` | Utilisateur PostgreSQL | `postgres` | - |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | `postgres` | - |
| `POSTGRES_DB` | Nom de la base de données | `mathakine` | - |

### **Variables de Performance**

| Variable | Description | Défaut | Notes |
|----------|-------------|--------|-------|
| `ENABLE_QUERY_CACHE` | Activer le cache des requêtes | `true` | - |
| `CACHE_TTL_SECONDS` | Durée de vie du cache (secondes) | `300` | 5 minutes |
| `MAX_CONNECTIONS_POOL` | Nombre max de connexions DB | `20` | - |
| `POOL_RECYCLE_SECONDS` | Recyclage des connexions | `3600` | 1 heure |

### **Variables de Sécurité**

| Variable | Description | Défaut | Notes |
|----------|-------------|--------|-------|
| `RATE_LIMIT_PER_MINUTE` | Limite de requêtes par minute | `60` | - |
| `MAX_CONTENT_LENGTH` | Taille max du contenu (bytes) | `16777216` | 16MB |
| `SECURE_HEADERS` | Activer les headers de sécurité | `true` | - |

### **Configuration Backend**

**Fichier** : `.env` (développement) ou variables d'environnement (production)

```bash
# Sécurité (OBLIGATOIRE en production)
SECRET_KEY=votre-cle-secrete-tres-longue-et-securisee

# Base de données (OBLIGATOIRE en production)
DATABASE_URL=postgresql://user:password@host:5432/mathakine

# Environnement
ENVIRONMENT=production
MATH_TRAINER_PROFILE=prod
LOG_LEVEL=INFO

# Frontend (pour CORS)
FRONTEND_URL=https://mathakine.com

# OpenAI (optionnel)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

**⚠️ IMPORTANT** :
- `SECRET_KEY` : Générer une clé forte (32+ caractères) en production
- `LOG_LEVEL` : Ne jamais mettre `DEBUG` en production (forcé à `INFO` automatiquement)
- `DATABASE_URL` : Utiliser PostgreSQL en production (pas SQLite)

---

## 🔒 **SÉCURITÉ**

### **Variables Sensibles (Ne JAMAIS Commiter)**

- ✅ `SECRET_KEY`
- ✅ `OPENAI_API_KEY`
- ✅ `DATABASE_URL` (contient mot de passe)
- ✅ `POSTGRES_PASSWORD`
- ✅ Toute variable contenant des secrets

### **Vérification Git**

```bash
# Vérifier qu'aucun secret n'est commité
git ls-files | grep -E "\.env|\.local"

# Devrait retourner uniquement :
# - .env.example
# - frontend/.env.example
# - sample.env (si présent)
```

---

## 🚀 **DÉPLOIEMENT**

### **Render.com**

Dans le dashboard Render, définir :

**Backend** :
```
SECRET_KEY=<générer une clé forte>
DATABASE_URL=<URL PostgreSQL fournie par Render>
ENVIRONMENT=production
MATH_TRAINER_PROFILE=prod
LOG_LEVEL=INFO
FRONTEND_URL=https://mathakine.onrender.com
OPENAI_API_KEY=<votre clé>
```

**Frontend** :
```
NEXT_PUBLIC_API_BASE_URL=https://mathakine-backend.onrender.com
NEXT_PUBLIC_SITE_URL=https://mathakine.onrender.com
NODE_ENV=production
```

### **Vercel**

Dans le dashboard Vercel, définir les mêmes variables que pour Render.

---

## ✅ **VALIDATION**

### **Checklist Avant Production**

- [ ] `SECRET_KEY` défini et fort (32+ caractères)
- [ ] `DATABASE_URL` pointe vers PostgreSQL (pas SQLite)
- [ ] `LOG_LEVEL` = `INFO` (pas `DEBUG`)
- [ ] `NEXT_PUBLIC_API_BASE_URL` défini et ne contient pas `localhost`
- [ ] `NEXT_PUBLIC_SITE_URL` défini
- [ ] `FRONTEND_URL` défini pour CORS
- [ ] Aucun secret dans Git (vérifier avec `git ls-files`)
- [ ] `.env.example` présent et à jour

---

## 📚 **RÉFÉRENCES**

- [Guide Déploiement](development/operations.md)
- [Guide Sécurité](architecture/security.md)
- [Audit Production](AUDIT_PRODUCTION_MVP_COMPLET.md)

---

**Dernière mise à jour** : Novembre 2025

