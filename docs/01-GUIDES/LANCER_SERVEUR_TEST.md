# 🚀 Guide Rapide : Lancer le Serveur en Mode Test

**Date** : 30 Novembre 2025  
**Objectif** : Démarrer rapidement le serveur pour tester les modifications de sécurité

---

## ⚡ Démarrage Rapide (Windows PowerShell)

### Option 1 : Script Automatique (Recommandé)

```powershell
# Lancer directement avec le script de test
scripts\start_server_test.bat
```

### Option 2 : Commande Manuelle

```powershell
# 1. Configurer les variables d'environnement
$env:MATH_TRAINER_DEBUG="true"
$env:RUN_STARTUP_MIGRATIONS="true"
$env:REQUIRE_STRONG_DEFAULT_ADMIN="false"

# 2. Lancer le serveur
python enhanced_server.py
```

---

## ✅ Vérification des Dépendances

Si vous avez l'erreur `ModuleNotFoundError: No module named 'loguru'` :

```powershell
# Installer les dépendances principales
python -m pip install loguru python-dotenv starlette uvicorn

# Ou installer toutes les dépendances (peut prendre du temps)
python -m pip install -r requirements.txt
```

**Note** : Si `pillow` pose problème, ce n'est pas bloquant pour démarrer le serveur.

---

## 🔍 Vérifier que le Serveur Fonctionne

Une fois le serveur lancé, vous devriez voir :

```
========================================
ENHANCED_SERVER.PY - Serveur complet démarré sur le port 8000
Serveur avec interface graphique complète
========================================
INFO:     Starting Mathakine server on 0.0.0.0:8000 (debug=True)
INFO:     RUN_STARTUP_MIGRATIONS=true: Initialisation DB et migrations activées
INFO:     Mathakine server started successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Accéder au serveur** : `http://localhost:8000`

---

## 🧪 Tests Rapides

### 1. Vérifier les Logs Sensibles

```powershell
python scripts/security/check_sensitive_logs.py
```

### 2. Tester le Login

1. Ouvrir `http://localhost:8000/login`
2. Se connecter avec `ObiWan` / `HelloThere123!`
3. Vérifier dans la console qu'aucun mot de passe n'apparaît dans les logs

### 3. Vérifier les Cookies

1. Ouvrir DevTools (F12) → Application → Cookies
2. Vérifier que `refresh_token` est présent (HTTP-only)
3. Vérifier que `refresh_token` n'est PAS dans localStorage

---

## 🐛 Dépannage

### Erreur : `ModuleNotFoundError: No module named 'loguru'`

**Solution** :
```powershell
python -m pip install loguru
```

### Erreur : `ModuleNotFoundError: No module named 'dotenv'`

**Solution** :
```powershell
python -m pip install python-dotenv
```

### Erreur : Port déjà utilisé

**Solution** :
```powershell
# Utiliser un autre port
$env:PORT="8001"
python enhanced_server.py
```

### Erreur : Base de données non accessible

**Solution** :
```powershell
# Vérifier que PostgreSQL est démarré
# Ou utiliser SQLite pour les tests rapides
$env:DATABASE_URL="sqlite:///./test.db"
```

---

## 📝 Variables d'Environnement Utiles

```powershell
# Mode développement
$env:MATH_TRAINER_DEBUG="true"
$env:RUN_STARTUP_MIGRATIONS="true"
$env:REQUIRE_STRONG_DEFAULT_ADMIN="false"

# Base de données
$env:DATABASE_URL="postgresql://postgres:postgres@localhost/mathakine_test"
$env:TEST_DATABASE_URL="postgresql://postgres:postgres@localhost/mathakine_test"

# Port
$env:PORT="8000"
```

---

## 🎯 Prochaines Étapes

Une fois le serveur lancé :

1. ✅ Vérifier que les logs ne contiennent pas de mots de passe
2. ✅ Tester le login/logout
3. ✅ Vérifier que le refresh token fonctionne (cookies uniquement)
4. ✅ Vérifier que les credentials démo sont conditionnés

Pour plus de détails, voir : [TESTER_MODIFICATIONS_SECURITE.md](TESTER_MODIFICATIONS_SECURITE.md)

---

**Dernière mise à jour** : 30 Novembre 2025

