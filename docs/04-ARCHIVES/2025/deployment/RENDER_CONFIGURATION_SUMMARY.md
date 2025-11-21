# ⚡ Résumé Configuration Render - Frontend Next.js

**Date** : Novembre 2025  
**Statut** : ⚠️ **MODIFICATIONS NÉCESSAIRES**

---

## 🎯 **RÉSUMÉ RAPIDE**

**OUI**, vous devez modifier la configuration Render pour déployer le nouveau frontend Next.js.

**Solution** : Créer **deux services Render séparés** (backend + frontend).

---

## ✅ **ACTIONS À EFFECTUER SUR RENDER**

### **1. Créer le Service Frontend**

Dans le dashboard Render :

1. **Nouveau Service** → **Web Service**
2. **Nom** : `mathakine-frontend`
3. **Environnement** : `Node`
4. **Root Directory** : `frontend`
5. **Build Command** : `npm install && npm run build`
6. **Start Command** : `npm start`

### **2. Variables d'Environnement Frontend**

Dans les paramètres du service frontend :

```
NEXT_PUBLIC_API_BASE_URL=https://mathakine-backend.onrender.com
NEXT_PUBLIC_SITE_URL=https://mathakine-frontend.onrender.com
```

**⚠️ IMPORTANT** :
- Remplacer `mathakine-backend` et `mathakine-frontend` par les vrais noms de vos services Render
- Ne pas mettre `localhost` en production (le build échouera)
- `NODE_ENV` et `PORT` sont gérés automatiquement par Render
- Les variables `NEXT_PUBLIC_*` doivent être définies **AVANT** le build (dans les Environment Variables du service)

### **3. Mettre à Jour le Service Backend**

Dans les paramètres du service backend existant :

**Ajouter/Modifier** :
```
FRONTEND_URL=https://mathakine-frontend.onrender.com
```

**⚠️ IMPORTANT** :
- Cette variable est utilisée pour CORS dans `app/core/config.py`
- Remplacer `mathakine-frontend` par le vrai nom de votre service frontend

---

## 📋 **CHECKLIST RAPIDE**

### **Service Frontend (NOUVEAU)**

- [ ] Service créé avec environnement **Node**
- [ ] Root Directory : **`frontend`**
- [ ] Build Command : **`npm install && npm run build`**
- [ ] Start Command : **`npm start`**
- [ ] Variable `NEXT_PUBLIC_API_BASE_URL` définie (URL backend)
- [ ] Variable `NEXT_PUBLIC_SITE_URL` définie (URL frontend)

### **Service Backend (EXISTANT)**

- [ ] Variable `FRONTEND_URL` mise à jour (URL frontend)
- [ ] Vérifier que CORS accepte le domaine frontend

---

## 🔍 **VÉRIFICATIONS POST-DÉPLOIEMENT**

1. **Frontend accessible** : `https://mathakine-frontend.onrender.com`
2. **Backend accessible** : `https://mathakine-backend.onrender.com`
3. **API fonctionne** : Le frontend peut appeler le backend
4. **Pas d'erreurs CORS** : Vérifier la console navigateur
5. **Pas d'erreurs 404** : Toutes les routes fonctionnent

---

## 📚 **DOCUMENTATION COMPLÈTE**

Pour plus de détails, voir :
- [Guide Complet Render](RENDER_DEPLOYMENT_FRONTEND.md)
- [Variables d'Environnement](ENVIRONMENT_VARIABLES.md)

---

**Dernière mise à jour** : Novembre 2025

