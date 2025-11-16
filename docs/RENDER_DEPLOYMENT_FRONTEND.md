# 🚀 Configuration Render pour Frontend Next.js - Mathakine

**Date** : Novembre 2025  
**Objectif** : Vérifier et documenter la configuration Render pour déployer le nouveau frontend Next.js

---

## 📋 **RÉSUMÉ EXÉCUTIF**

Le projet utilise maintenant **Next.js 16.0.1** comme frontend principal, ce qui nécessite une configuration Render différente de l'ancien setup Jinja2.

**⚠️ MODIFICATIONS NÉCESSAIRES** : **OUI** - La configuration Render doit être mise à jour pour déployer le frontend Next.js.

**🎯 RECOMMANDATION** : Créer **deux services Render séparés** (backend Python + frontend Node).

---

## 🔍 **ANALYSE DE LA CONFIGURATION ACTUELLE**

### **1. Procfile Actuel**

```bash
web: bash scripts/start_render.sh
```

**Problème** : Le script `start_render.sh` démarre uniquement le backend (`enhanced_server.py`), pas le frontend Next.js.

### **2. Script start_render.sh Actuel**

Le script actuel :
- ✅ Initialise la base de données PostgreSQL
- ✅ Démarre le backend FastAPI (`enhanced_server.py`)
- ❌ **Ne démarre PAS le frontend Next.js**

---

## ✅ **CONFIGURATION REQUISE POUR NEXT.JS**

### **Option 1 : Deux Services Séparés (RECOMMANDÉ)**

Render permet de créer deux services séparés :
1. **Backend Service** : Python/FastAPI
2. **Frontend Service** : Next.js

#### **Backend Service (Python)**

**Build Command** :
```bash
pip install -r requirements.txt
```

**Start Command** :
```bash
python enhanced_server.py
```

**Variables d'Environnement** :
- `DATABASE_URL` (PostgreSQL)
- `SECRET_KEY`
- `LOG_LEVEL=INFO`
- `ENVIRONMENT=production`
- `FRONTEND_URL=https://mathakine-frontend.onrender.com` (URL du frontend)

#### **Frontend Service (Next.js)**

**Build Command** :
```bash
cd frontend && npm install && npm run build
```

**Start Command** :
```bash
cd frontend && npm start
```

**Variables d'Environnement** :
- `NEXT_PUBLIC_API_BASE_URL=https://mathakine-backend.onrender.com` (URL du backend)
- `NEXT_PUBLIC_SITE_URL=https://mathakine-frontend.onrender.com`
- `NODE_ENV=production`

**Port** : Render définit automatiquement `PORT` (Next.js l'utilise automatiquement)

---

### **Option 2 : Service Unique avec Reverse Proxy**

Si vous préférez un seul service, vous pouvez utiliser le backend comme reverse proxy pour servir le frontend Next.js.

**⚠️ COMPLEXITÉ** : Cette option nécessite des modifications au backend pour servir les fichiers statiques Next.js.

**Recommandation** : Utiliser l'Option 1 (deux services séparés).

---

## 🔧 **MODIFICATIONS À APPLIQUER**

### **1. Créer un Nouveau Service Frontend sur Render**

1. **Créer un nouveau service "Web Service"**
   - Nom : `mathakine-frontend`
   - Environnement : `Node`
   - Root Directory : `frontend`

2. **Build Command** :
   ```bash
   npm install && npm run build
   ```

3. **Start Command** :
   ```bash
   npm start
   ```

4. **Variables d'Environnement** :
   ```
   NEXT_PUBLIC_API_BASE_URL=https://mathakine-backend.onrender.com
   NEXT_PUBLIC_SITE_URL=https://mathakine-frontend.onrender.com
   NODE_ENV=production
   ```

### **2. Mettre à Jour le Service Backend**

1. **Modifier les variables d'environnement** :
   ```
   FRONTEND_URL=https://mathakine-frontend.onrender.com
   ```

2. **Vérifier CORS** :
   - S'assurer que `FRONTEND_URL` est dans `BACKEND_CORS_ORIGINS`
   - Vérifier dans `app/core/config.py`

### **3. Mettre à Jour le Procfile (Optionnel)**

Si vous gardez un seul service pour le backend :

**Procfile** :
```bash
web: bash scripts/start_render.sh
```

Le script `start_render.sh` reste inchangé (démarre uniquement le backend).

---

## 📝 **CHECKLIST CONFIGURATION RENDER**

### **Service Backend**

- [ ] Service créé avec environnement Python
- [ ] Build Command : `pip install -r requirements.txt`
- [ ] Start Command : `python enhanced_server.py` ou `bash scripts/start_render.sh`
- [ ] Variables d'environnement :
  - [ ] `DATABASE_URL` (PostgreSQL)
  - [ ] `SECRET_KEY`
  - [ ] `LOG_LEVEL=INFO`
  - [ ] `ENVIRONMENT=production`
  - [ ] `FRONTEND_URL=https://mathakine-frontend.onrender.com`
  - [ ] `OPENAI_API_KEY` (si nécessaire)

### **Service Frontend**

- [ ] Service créé avec environnement Node
- [ ] Root Directory : `frontend`
- [ ] Build Command : `npm install && npm run build`
- [ ] Start Command : `npm start`
- [ ] Variables d'environnement :
  - [ ] `NEXT_PUBLIC_API_BASE_URL=https://mathakine-backend.onrender.com`
  - [ ] `NEXT_PUBLIC_SITE_URL=https://mathakine-frontend.onrender.com`
  - [ ] `NODE_ENV=production`

### **CORS et Sécurité**

- [ ] Backend CORS configuré pour accepter le frontend
- [ ] Frontend configuré avec la bonne URL backend
- [ ] Pas de `localhost` dans les variables d'environnement production

---

## 🔄 **SCRIPT DE DÉMARRAGE ALTERNATIF**

Si vous préférez un seul service qui démarre les deux :

**scripts/start_render_full.sh** :
```bash
#!/bin/bash

# Démarrer le backend en arrière-plan
python enhanced_server.py &
BACKEND_PID=$!

# Attendre que le backend soit prêt
sleep 5

# Démarrer le frontend
cd frontend
npm start

# Si le frontend s'arrête, arrêter aussi le backend
kill $BACKEND_PID
```

**⚠️ NOTE** : Cette approche n'est pas recommandée car :
- Plus complexe à gérer
- Moins de flexibilité (redémarrage indépendant)
- Moins de scalabilité

---

## 📊 **COMPARAISON AVANT/APRÈS**

### **Avant (Jinja2 Legacy)**

- ✅ Un seul service Render
- ✅ Backend sert les templates HTML directement
- ✅ Pas de build séparé nécessaire

### **Après (Next.js)**

- ⚠️ **Deux services recommandés** (backend + frontend)
- ⚠️ Build Next.js nécessaire (`npm run build`)
- ⚠️ Variables d'environnement spécifiques (`NEXT_PUBLIC_*`)
- ⚠️ Configuration CORS entre services

---

## ✅ **RECOMMANDATIONS FINALES**

### **Configuration Recommandée**

1. **Créer deux services Render** :
   - `mathakine-backend` (Python)
   - `mathakine-frontend` (Node)

2. **Backend** :
   - Build : `pip install -r requirements.txt`
   - Start : `python enhanced_server.py`
   - Variables : `FRONTEND_URL` pointant vers le frontend

3. **Frontend** :
   - Build : `npm install && npm run build`
   - Start : `npm start`
   - Variables : `NEXT_PUBLIC_API_BASE_URL` pointant vers le backend

4. **CORS** :
   - Backend autorise le domaine frontend
   - Frontend utilise l'URL backend en production

---

## 📚 **RÉFÉRENCES**

- [Documentation Render](https://render.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Variables d'Environnement](ENVIRONMENT_VARIABLES.md)
- [Audit Production](AUDIT_PRODUCTION_MVP_COMPLET.md)

---

**Dernière mise à jour** : Novembre 2025

