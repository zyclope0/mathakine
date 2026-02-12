# 🔧 DÉPANNAGE ERREUR "Failed to fetch"

## 🚨 **PROBLÈME**

Erreur `Failed to fetch` lors de la connexion - le frontend ne peut pas atteindre le backend.

## ✅ **SOLUTIONS APPLIQUÉES**

### **1. Amélioration de la gestion d'erreur**

- ✅ Message d'erreur plus explicite avec l'URL du backend
- ✅ Détection des erreurs réseau spécifiques
- ✅ Affichage de l'URL dans les détails de l'erreur

### **2. Configuration de l'URL API**

- ✅ Support de `NEXT_PUBLIC_API_BASE_URL` (recommandé)
- ✅ Fallback vers `NEXT_PUBLIC_API_URL` (ancien)
- ✅ Fallback vers `http://localhost:8000` (par défaut)

## 🔍 **VÉRIFICATIONS À FAIRE**

### **1. Vérifier que le backend est démarré**

```bash
# Dans un terminal séparé
cd D:\Mathakine
python enhanced_server.py
# OU
python mathakine_cli.py run
```

Le backend doit être accessible sur `http://localhost:8000`

### **2. Tester l'endpoint directement**

Ouvrir dans le navigateur ou avec curl :

```bash
# Test de l'endpoint de login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ObiWan","password":"HelloThere123!"}'
```

### **3. Vérifier la configuration CORS**

Le backend doit autoriser `http://localhost:3000` dans `BACKEND_CORS_ORIGINS`.

Vérifier dans `app/core/config.py` :

```python
BACKEND_CORS_ORIGINS: List[str] = [
    "http://localhost:8000",
    "http://localhost:3000",  # ← Doit être présent
    ...
]
```

### **4. Vérifier les variables d'environnement**

Le fichier `frontend/.env.local` doit contenir :

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**Important** : Redémarrer le serveur Next.js après modification de `.env.local` :

```bash
# Arrêter le serveur (Ctrl+C)
# Puis redémarrer
cd frontend
npm run dev
```

## 🛠️ **COMMANDES DE DÉPANNAGE**

### **Vérifier que le backend répond**

```bash
# Test simple
curl http://localhost:8000/api/docs
```

### **Vérifier les logs du backend**

Regarder les logs du serveur backend pour voir si les requêtes arrivent.

### **Vérifier la console navigateur**

Ouvrir les DevTools (F12) → Onglet Network pour voir :

- Si la requête est envoyée
- Le code de statut HTTP
- Les erreurs CORS éventuelles

## 📋 **CHECKLIST DE DÉPANNAGE**

- [ ] Backend démarré sur `http://localhost:8000`
- [ ] Frontend démarré sur `http://localhost:3000`
- [ ] Variable `NEXT_PUBLIC_API_BASE_URL` définie dans `.env.local`
- [ ] Serveur Next.js redémarré après modification `.env.local`
- [ ] CORS configuré pour autoriser `localhost:3000`
- [ ] Pas de firewall bloquant les connexions locales
- [ ] Ports 3000 et 8000 disponibles

## 🎯 **PROCHAINES ÉTAPES**

Si le problème persiste après ces vérifications :

1. Vérifier les logs du backend
2. Vérifier la console navigateur (F12)
3. Tester avec curl/Postman pour isoler le problème
4. Vérifier que les deux serveurs sont sur la même machine
