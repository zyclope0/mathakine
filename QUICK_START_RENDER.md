# ⚡ Quick Start - Déploiement Render en 5 Minutes

**Pour utilisateurs pressés** - Guide ultra-rapide 🚀

---

## 🎯 **CE QU'IL FAUT SAVOIR**

✅ **Deux services séparés** : Backend (Python) + Frontend (Next.js)  
✅ **Fichier `render.yaml`** : Automatise tout  
✅ **15 minutes** : Temps de déploiement complet

---

## 📦 **ÉTAPE 1 : Commit les fichiers**

```bash
git add render.yaml DEPLOY_RENDER_GUIDE.md
git commit -m "feat: Add Render deployment"
git push origin main
```

---

## 🌐 **ÉTAPE 2 : Créer le Blueprint sur Render**

1. Aller sur : https://dashboard.render.com
2. Cliquer : **"New" → "Blueprint"**
3. Sélectionner votre repository GitHub/GitLab
4. Cliquer : **"Apply"**

➡️ **Render crée automatiquement** :
- ✅ Backend (mathakine-backend)
- ✅ Frontend (mathakine-frontend)
- ✅ Database (mathakine-db)

---

## 🔑 **ÉTAPE 3 : Ajouter les secrets (2 minutes)**

### **Backend Service**

Dashboard → **mathakine-backend** → **Environment** → Ajouter :

```
OPENAI_API_KEY=sk-...
```

*(Seulement si vous utilisez l'IA pour générer des exercices)*

### **Frontend Service**

Dashboard → **mathakine-frontend** → **Environment** → Vérifier :

```
NEXT_PUBLIC_API_BASE_URL=https://mathakine-backend.onrender.com
NEXT_PUBLIC_SITE_URL=https://mathakine-frontend.onrender.com
```

*(Devrait être déjà configuré automatiquement)*

---

## ⏳ **ÉTAPE 4 : Attendre le déploiement**

- **Backend** : 5-8 minutes
- **Frontend** : 8-12 minutes
- **Total** : ~15 minutes

**Voir la progression** : Dashboard → Services → Logs

---

## ✅ **ÉTAPE 5 : Tester**

### **Test 1 : Backend**

```bash
curl https://mathakine-backend.onrender.com/health
```

**Attendu** : `{"status":"ok"}`

### **Test 2 : Frontend**

Ouvrir dans un navigateur :
```
https://mathakine-frontend.onrender.com
```

**Attendu** : Page d'accueil Mathakine

### **Test 3 : Login**

1. Aller sur le frontend
2. Créer un compte / Se connecter
3. Tester les exercices

**Attendu** : Tout fonctionne ✅

---

## 🐛 **PROBLÈMES COURANTS**

### **"Build failed" sur Frontend**

**Cause** : Erreurs TypeScript

**Solution** :
```bash
cd frontend
npm run build
# Corriger les erreurs affichées
git add .
git commit -m "fix: TypeScript errors"
git push
```

---

### **"CORS error" dans le navigateur**

**Cause** : Backend refuse les requêtes du frontend

**Solution** :
1. Dashboard → **mathakine-backend** → **Environment**
2. Vérifier que `FRONTEND_URL` existe et est correct
3. **Manual Deploy** pour redémarrer

---

### **"Service unavailable" après 15 min**

**Cause** : Plan gratuit = mise en veille après inactivité

**Solution** :
- **Accepter** : Premier chargement = 30-60 secondes
- **Upgrader** : Plan Starter ($7/mois) = toujours actif

---

## 💰 **COÛTS**

### **Plan Gratuit (Free)**

- ✅ **0€/mois**
- ✅ 3 services inclus
- ⚠️ Mise en veille après 15 minutes
- ⚠️ Premier chargement lent (30-60s)

### **Plan Starter**

- 💵 **$7/mois** par service web
- ✅ Toujours actif (pas de veille)
- ✅ Plus rapide

**Recommandation** : Commencer par Free, upgrader si nécessaire

---

## 📚 **DOCUMENTS COMPLETS**

- **Guide détaillé** : `DEPLOY_RENDER_GUIDE.md`
- **Problèmes résolus** : `PROBLEMES_DEPLOIEMENT_RESOLUS.md`
- **Documentation technique** : `RENDER_DEPLOYMENT_FRONTEND.md`

---

## 🎉 **C'EST TOUT !**

**Temps total** : 5 minutes (configuration) + 15 minutes (build)

**URLs finales** :
- Frontend : https://mathakine-frontend.onrender.com
- Backend : https://mathakine-backend.onrender.com
- API Docs : https://mathakine-backend.onrender.com/docs

---

**Besoin d'aide ?** → Voir `DEPLOY_RENDER_GUIDE.md` pour le guide complet

