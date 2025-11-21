# 🚀 Guide de Déploiement Render - Mathakine

**Date** : Novembre 2025  
**Statut** : Production Ready ✅

---

## 📋 **PRÉREQUIS**

- [ ] Compte Render actif : https://render.com
- [ ] Repository Git connecté à Render
- [ ] Code pushé sur la branche `main` (ou branche de production)

---

## ⚡ **DÉPLOIEMENT RAPIDE (Option 1 : Automatique)**

### **Étape 1 : Déployer via render.yaml**

1. **Pusher le fichier `render.yaml`** sur votre repository Git
2. **Aller sur Render Dashboard** : https://dashboard.render.com
3. **Cliquer sur "New" → "Blueprint"**
4. **Sélectionner votre repository**
5. **Render créera automatiquement** :
   - ✅ Service Backend (Python)
   - ✅ Service Frontend (Next.js)
   - ✅ Base de données PostgreSQL

### **Étape 2 : Configurer les Variables Sensibles**

Render ne peut pas générer automatiquement certaines variables. Vous devez les ajouter manuellement :

#### **Backend Service (`mathakine-backend`)**

1. Aller dans **Dashboard → mathakine-backend → Environment**
2. Ajouter/Vérifier :
   ```
   OPENAI_API_KEY=sk-...  (votre clé OpenAI si vous utilisez l'IA)
   SECRET_KEY=<sera généré automatiquement par Render>
   ```

#### **Frontend Service (`mathakine-frontend`)**

1. Aller dans **Dashboard → mathakine-frontend → Environment**
2. Vérifier que les URLs sont correctes :
   ```
   NEXT_PUBLIC_API_BASE_URL=https://mathakine-backend.onrender.com
   NEXT_PUBLIC_SITE_URL=https://mathakine-frontend.onrender.com
   ```

### **Étape 3 : Déployer**

1. **Render déploiera automatiquement** après la création du Blueprint
2. **Temps estimé** : 10-15 minutes (premier build)
3. **Vérifier les logs** pour voir la progression

---

## 🔧 **DÉPLOIEMENT MANUEL (Option 2 : Si render.yaml ne fonctionne pas)**

### **1️⃣ Créer la Base de Données PostgreSQL**

1. **Dashboard → "New" → "PostgreSQL"**
2. Configuration :
   - **Name** : `mathakine-db`
   - **Database** : `mathakine`
   - **Plan** : Free (1GB)
3. **Créer la base** → Copier le **Internal Database URL**

---

### **2️⃣ Créer le Service Backend**

1. **Dashboard → "New" → "Web Service"**
2. Configuration :
   - **Name** : `mathakine-backend`
   - **Environment** : `Python 3`
   - **Branch** : `main`
   - **Root Directory** : (vide - racine du projet)
   - **Build Command** :
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command** :
     ```bash
     bash scripts/start_render.sh
     ```

3. **Variables d'Environnement** :
   ```
   DATABASE_URL=<Internal Database URL copiée précédemment>
   SECRET_KEY=<générer avec: openssl rand -hex 32>
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   MATH_TRAINER_PROFILE=prod
   FRONTEND_URL=https://mathakine-frontend.onrender.com
   OPENAI_API_KEY=<votre clé si nécessaire>
   ```

4. **Health Check Path** : `/health`
5. **Créer le service**

---

### **3️⃣ Créer le Service Frontend**

1. **Dashboard → "New" → "Web Service"**
2. Configuration :
   - **Name** : `mathakine-frontend`
   - **Environment** : `Node`
   - **Branch** : `main`
   - **Root Directory** : `frontend`
   - **Build Command** :
     ```bash
     npm install && npm run build
     ```
   - **Start Command** :
     ```bash
     npm start
     ```

3. **Variables d'Environnement** :
   ```
   NEXT_PUBLIC_API_BASE_URL=https://mathakine-backend.onrender.com
   NEXT_PUBLIC_SITE_URL=https://mathakine-frontend.onrender.com
   NODE_ENV=production
   ```

4. **Health Check Path** : `/`
5. **Créer le service**

---

## ✅ **VÉRIFICATIONS POST-DÉPLOIEMENT**

### **1. Backend est opérationnel**

```bash
# Test endpoint health
curl https://mathakine-backend.onrender.com/health

# Test API docs
curl https://mathakine-backend.onrender.com/docs
```

**Attendu** : Réponse JSON avec statut `ok`

---

### **2. Frontend est accessible**

```bash
# Test page d'accueil
curl https://mathakine-frontend.onrender.com/
```

**Attendu** : HTML de la page Next.js

---

### **3. Communication Backend ↔ Frontend**

1. **Ouvrir le frontend** : https://mathakine-frontend.onrender.com
2. **Tester une fonctionnalité** qui appelle l'API (ex: login, exercices)
3. **Vérifier dans les logs backend** que les requêtes arrivent

---

## 🐛 **DÉPANNAGE ERREURS COURANTES**

### **Erreur 1 : "Build failed" sur le Frontend**

**Cause** : Dépendances manquantes ou erreurs TypeScript

**Solution** :
```bash
# Tester localement
cd frontend
npm install
npm run build

# Corriger les erreurs TypeScript avant de push
```

---

### **Erreur 2 : "CORS error" dans le navigateur**

**Cause** : Backend refuse les requêtes du frontend

**Solution** :
1. Vérifier que `FRONTEND_URL` est définie dans le backend
2. Vérifier que `FRONTEND_URL` correspond à l'URL exacte du frontend
3. Redémarrer le service backend après modification

---

### **Erreur 3 : "Cannot connect to database"**

**Cause** : `DATABASE_URL` incorrecte

**Solution** :
1. Copier **Internal Database URL** (pas External)
2. Format attendu : `postgresql://user:password@host:port/database`
3. Vérifier dans **Dashboard → Backend → Environment**

---

### **Erreur 4 : Frontend renvoie "API_BASE_URL not defined"**

**Cause** : Variables `NEXT_PUBLIC_*` mal configurées

**Solution** :
1. Vérifier dans **Dashboard → Frontend → Environment**
2. S'assurer que `NEXT_PUBLIC_API_BASE_URL` existe
3. **Rebuild obligatoire** après modification (les variables `NEXT_PUBLIC_*` sont compilées au build)

---

### **Erreur 5 : "Service unavailable" après 15 minutes d'inactivité**

**Cause** : Plan gratuit Render met les services en veille

**Solution** :
- **Accepter le délai** : Premier chargement = 30-60 secondes
- **Upgrader** : Plan Starter ($7/mois) = toujours actif
- **Ping service** : Utiliser un service comme UptimeRobot pour pinger toutes les 5 minutes

---

## 📊 **MONITORING ET LOGS**

### **Voir les logs en temps réel**

1. **Dashboard → Service → Logs**
2. Filtrer par :
   - **Deploy Logs** : Erreurs de build
   - **Runtime Logs** : Erreurs d'exécution

### **Métriques de performance**

- **Dashboard → Service → Metrics**
- Vérifier :
  - CPU Usage
  - Memory Usage
  - Request Rate

---

## 🔄 **MISES À JOUR ET REDÉPLOIEMENT**

### **Déploiement automatique (recommandé)**

1. **Auto-deploy activé** par défaut
2. Chaque `git push` sur `main` redéploie automatiquement
3. Temps de déploiement : 5-10 minutes

### **Déploiement manuel**

1. **Dashboard → Service → Manual Deploy**
2. **Sélectionner la branche**
3. **Cliquer sur "Deploy"**

---

## 🔐 **SÉCURITÉ**

### **Variables sensibles**

- ⚠️ **NE JAMAIS commiter** `.env` ou `.env.local`
- ✅ Définir toutes les clés dans **Render Dashboard → Environment**
- ✅ Utiliser **"Encrypt"** pour les secrets (Render les chiffre automatiquement)

### **HTTPS**

- ✅ **Activé automatiquement** par Render
- ✅ Certificat SSL gratuit via Let's Encrypt
- ✅ Renouvellement automatique

---

## 💰 **COÛTS**

### **Plan Gratuit (Free)**

- ✅ **3 services** inclus (Backend + Frontend + DB)
- ✅ **Illimité** en nombre de requêtes
- ⚠️ **Mise en veille** après 15 minutes d'inactivité
- ⚠️ **750 heures/mois** de runtime (suffit pour un projet personnel)

### **Plan Payant (Starter)**

- ✅ **$7/mois** par service web
- ✅ **Toujours actif** (pas de mise en veille)
- ✅ **Plus de CPU/RAM**

---

## 📚 **RESSOURCES**

- [Documentation Render](https://render.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL on Render](https://render.com/docs/databases)

---

## ✅ **CHECKLIST FINALE**

- [ ] Backend déployé et accessible
- [ ] Frontend déployé et accessible
- [ ] Base de données PostgreSQL créée
- [ ] Variables d'environnement configurées
- [ ] CORS configuré (backend accepte frontend)
- [ ] Health checks passent (vert dans Dashboard)
- [ ] Test login/exercices fonctionne
- [ ] Logs backend/frontend sans erreurs critiques
- [ ] HTTPS actif (cadenas dans navigateur)

---

**🎉 Félicitations ! Mathakine est déployé en production !**

**URL Frontend** : https://mathakine-frontend.onrender.com  
**URL Backend** : https://mathakine-backend.onrender.com  
**API Docs** : https://mathakine-backend.onrender.com/docs

