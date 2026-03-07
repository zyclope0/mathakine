# 🧪 Guide : Tester les Modifications de Sécurité

**Date** : 30 Novembre 2025  
**Objectif** : Vérifier les effets de bord des corrections de sécurité (Phases 1-2)

---

## 🎯 Vue d'Ensemble

Ce guide explique comment lancer le serveur en mode test pour vérifier que les modifications de sécurité fonctionnent correctement et n'ont pas d'effets de bord.

---

## ⚙️ Configuration pour les Tests

### Variables d'Environnement Requises

Créez un fichier `.env` à la racine du projet (ou utilisez les variables d'environnement système) :

```bash
# Base de données (utiliser la base de test)
DATABASE_URL=postgresql://postgres:postgres@localhost/mathakine_test
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost/mathakine_test

# Mode développement (pour tester les nouvelles fonctionnalités)
MATH_TRAINER_DEBUG=true
MATH_TRAINER_PROFILE=dev
LOG_LEVEL=DEBUG

# Sécurité - Mode développement (relaxé pour les tests)
REQUIRE_STRONG_DEFAULT_ADMIN=false  # Pas de validation stricte en dev
RUN_STARTUP_MIGRATIONS=true  # Activer les migrations pour les tests

# Frontend - Mode démo (pour voir les credentials)
NEXT_PUBLIC_DEMO_MODE=true  # Afficher les credentials démo

# Ports
PORT=8000
MATH_TRAINER_PORT=8000
```

---

## 🚀 Méthode 1 : Lancer le Serveur Backend (Recommandé)

### Option A : Via `enhanced_server.py` (Serveur complet)

```bash
# Windows PowerShell
python enhanced_server.py

# Ou avec variables d'environnement explicites
$env:MATH_TRAINER_DEBUG="true"
$env:RUN_STARTUP_MIGRATIONS="true"
$env:REQUIRE_STRONG_DEFAULT_ADMIN="false"
python enhanced_server.py
```

**Résultat attendu** :
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

### Option B : Avec variables d'environnement

```bash
# Windows PowerShell
$env:RUN_STARTUP_MIGRATIONS="true"
python enhanced_server.py
```

---

## 🧪 Tests à Effectuer

### ✅ Test 1 : Vérifier les Logs (SEC-1.1)

**Objectif** : Vérifier qu'aucun mot de passe ni hash n'apparaît dans les logs

**Actions** :
1. Lancer le serveur avec `LOG_LEVEL=DEBUG`
2. Effectuer un login avec un utilisateur de test
3. Vérifier les logs dans la console

**Résultat attendu** :
```
✅ Logs génériques uniquement :
   - "Vérification du mot de passe en cours..."
   - "Hash de mot de passe généré avec succès"
   - "Utilisateur trouvé: ObiWan"

❌ Ne doit PAS apparaître :
   - "Mot de passe en clair: ..."
   - "Hash à comparer: ..."
   - "Hash généré: $2b$12$..."
   - "Hash stocké: ..."
```

**Commande de vérification** :
```bash
python scripts/security/check_sensitive_logs.py
```

---

### ✅ Test 2 : Vérifier le Fallback Refresh Token Legacy (SEC-1.2)

**Objectif** : Vérifier que le fallback legacy reste strictement borné :

- aucun refresh token ne doit être recréé à partir d'un access token invalide
- aucun refresh token ne doit être recréé à partir d'un access token trop ancien
- seul un access token legacy encore exploitable peut servir de compatibilité transitoire

**Actions** :
1. Lancer le serveur
2. Se connecter avec un utilisateur
3. Attendre que l'access_token expire (ou le modifier manuellement)
4. Essayer de rafraîchir le token sans refresh_token

**Résultat attendu** :
```
✅ Sans refresh_token et sans access_token legacy exploitable :
   retour 401

❌ Ne doit PAS créer un nouveau refresh_token à partir d'un access_token invalide
❌ Ne doit PAS créer un nouveau refresh_token à partir d'un access_token expiré depuis trop longtemps
```

**Test manuel** :
```bash
# 1. Login pour obtenir un access_token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ObiWan","password":"HelloThere123!"}'

# 2. Essayer de refresh SANS refresh_token
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json"
```

**Lecture attendue** :

- si aucun cookie/access token legacy valable n'est présent, le backend renvoie `401`
- le fallback ne doit pas contourner l'expiration réelle ni recréer un token pour un utilisateur introuvable/inactif

---

### ✅ Test 3 : Vérifier localStorage (SEC-1.3)

**Objectif** : Vérifier qu'aucun refresh_token n'est stocké dans localStorage

**Actions** :
1. Lancer le serveur backend
2. Lancer le frontend (`npm run dev` dans `frontend/`)
3. Ouvrir le navigateur → DevTools → Application → Local Storage
4. Se connecter avec un utilisateur
5. Vérifier localStorage

**Résultat attendu** :
```
✅ localStorage ne contient PAS de clé "refresh_token"
✅ Le refresh_token est uniquement dans les cookies HTTP-only
```

**Commande de vérification** :
```bash
python scripts/security/check_localstorage_refresh.py
```

**Test manuel dans le navigateur** :
```javascript
// Dans la console du navigateur
console.log(localStorage.getItem('refresh_token')); // Doit retourner null
console.log(document.cookie); // Doit contenir refresh_token (cookie HTTP-only)
```

---

### ✅ Test 4 : Vérifier les Credentials Démo (SEC-1.4)

**Objectif** : Vérifier que les credentials démo sont conditionnés par `DEMO_MODE`

**Actions** :
1. Lancer le frontend avec `NEXT_PUBLIC_DEMO_MODE=true`
2. Aller sur `/login`
3. Vérifier que les credentials sont affichés
4. Relancer avec `NEXT_PUBLIC_DEMO_MODE=false`
5. Vérifier que les credentials sont masqués

**Résultat attendu** :
```
✅ Si DEMO_MODE=true : Credentials affichés (ObiWan / HelloThere123!)
✅ Si DEMO_MODE=false : Credentials masqués, bouton "Remplir automatiquement" visible
```

**Commande de vérification** :
```bash
python scripts/security/check_demo_credentials.py
```

---

### ✅ Test 5 : Vérifier le Mot de Passe Admin (SEC-2.1)

**Objectif** : Vérifier que la validation du mot de passe admin fonctionne

**Actions** :
1. Lancer le serveur avec `REQUIRE_STRONG_DEFAULT_ADMIN=true`
2. Définir `DEFAULT_ADMIN_PASSWORD=admin` (8 caractères)
3. Vérifier que le serveur refuse de démarrer

**Résultat attendu** :
```
✅ Exception levée :
   ValueError: DEFAULT_ADMIN_PASSWORD doit faire au moins 16 caractères en production.
   Actuellement: 8 caractères.
```

**Test** :
```bash
# Windows PowerShell
$env:REQUIRE_STRONG_DEFAULT_ADMIN="true"
$env:DEFAULT_ADMIN_PASSWORD="admin"
python enhanced_server.py
# Doit lever une ValueError
```

---

### ✅ Test 6 : Vérifier les Migrations au Boot (SEC-2.2)

**Objectif** : Vérifier que les migrations sont conditionnées

**Actions** :
1. Lancer le serveur avec `RUN_STARTUP_MIGRATIONS=false`
2. Vérifier les logs
3. Relancer avec `RUN_STARTUP_MIGRATIONS=true`
4. Vérifier les logs

**Résultat attendu** :
```
✅ Si RUN_STARTUP_MIGRATIONS=false :
   "RUN_STARTUP_MIGRATIONS=false: Migrations désactivées (production)"

✅ Si RUN_STARTUP_MIGRATIONS=true :
   "RUN_STARTUP_MIGRATIONS=true: Initialisation DB et migrations activées"
   "Vérification des colonnes de vérification email..."
```

**Commande de vérification** :
```bash
python scripts/security/check_startup_migrations.py
```

---

## 🔍 Script de Test Automatisé

Créez un script pour tester tous les points automatiquement :

```bash
# scripts/test_security_modifications.py
#!/usr/bin/env python3
"""
Script pour tester automatiquement les modifications de sécurité.
"""

import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

def run_check(script_name, description):
    """Exécute un script de vérification"""
    print(f"\n{'='*80}")
    print(f"🔍 {description}")
    print(f"{'='*80}")
    script_path = project_root / "scripts" / "security" / script_name
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    """Point d'entrée principal"""
    print("="*80)
    print("🧪 TESTS AUTOMATISÉS - MODIFICATIONS DE SÉCURITÉ")
    print("="*80)
    
    checks = [
        ("check_sensitive_logs.py", "Vérification des logs sensibles"),
        ("check_fallback_refresh.py", "Vérification du fallback refresh token"),
        ("check_localstorage_refresh.py", "Vérification localStorage refresh_token"),
        ("check_demo_credentials.py", "Vérification des credentials démo"),
        ("check_startup_migrations.py", "Vérification des migrations au boot"),
    ]
    
    results = []
    for script, description in checks:
        success = run_check(script, description)
        results.append((description, success))
    
    print("\n" + "="*80)
    print("📊 RÉSULTATS")
    print("="*80)
    
    for description, success in results:
        status = "✅ PASSE" if success else "❌ ÉCHEC"
        print(f"{status} : {description}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n✅ Tous les tests de sécurité passent !")
        return 0
    else:
        print("\n❌ Certains tests ont échoué. Vérifiez les détails ci-dessus.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 🚀 Commandes Rapides

> Si vous n'avez pas de dossier local `scripts/security/`, utilisez les procédures manuelles décrites plus haut. Les commandes ci-dessous correspondent à une automatisation optionnelle.

### Windows PowerShell

```powershell
# 1. Configurer les variables d'environnement
$env:MATH_TRAINER_DEBUG="true"
$env:RUN_STARTUP_MIGRATIONS="true"
$env:REQUIRE_STRONG_DEFAULT_ADMIN="false"
$env:DATABASE_URL="postgresql://postgres:postgres@localhost/mathakine_test"

# 2. Lancer le serveur
python enhanced_server.py

# 3. Dans un autre terminal, lancer les vérifications
python scripts/security/check_sensitive_logs.py
python scripts/security/check_fallback_refresh.py
python scripts/security/check_localstorage_refresh.py
python scripts/security/check_demo_credentials.py
python scripts/security/check_startup_migrations.py
```

### Linux/Mac

```bash
# 1. Configurer les variables d'environnement
export MATH_TRAINER_DEBUG=true
export RUN_STARTUP_MIGRATIONS=true
export REQUIRE_STRONG_DEFAULT_ADMIN=false
export DATABASE_URL="postgresql://postgres:postgres@localhost/mathakine_test"

# 2. Lancer le serveur
python enhanced_server.py

# 3. Dans un autre terminal, lancer les vérifications
python scripts/security/check_sensitive_logs.py
python scripts/security/check_fallback_refresh.py
python scripts/security/check_localstorage_refresh.py
python scripts/security/check_demo_credentials.py
python scripts/security/check_startup_migrations.py
```

---

## 📋 Checklist de Test Complète

### Avant de Lancer le Serveur
- [ ] Base de données de test configurée (`TEST_DATABASE_URL`)
- [ ] Variables d'environnement définies
- [ ] Scripts de vérification disponibles

### Pendant le Test
- [ ] Serveur démarre sans erreur
- [ ] Logs ne contiennent pas de mots de passe/hash
- [ ] Fallback refresh token legacy borné et sans contournement d'expiration
- [ ] localStorage ne contient pas refresh_token
- [ ] Credentials démo conditionnés par DEMO_MODE
- [ ] Mot de passe admin validé si REQUIRE_STRONG_DEFAULT_ADMIN=true
- [ ] Migrations conditionnées par RUN_STARTUP_MIGRATIONS

### Tests Fonctionnels
- [ ] Login fonctionne
- [ ] Refresh token fonctionne (via cookies uniquement)
- [ ] Logout fonctionne
- [ ] Compte ObiWan fonctionne toujours

---

## 🐛 Dépannage

### Le serveur ne démarre pas

**Erreur** : `ValueError: DEFAULT_ADMIN_PASSWORD doit faire au moins 16 caractères`

**Solution** :
```bash
# En développement, désactiver la validation
export REQUIRE_STRONG_DEFAULT_ADMIN=false
# Ou définir un mot de passe fort
export DEFAULT_ADMIN_PASSWORD="MonMotDePasseSuperFort123!"
```

---

### Les migrations ne s'exécutent pas

**Erreur** : Tables manquantes

**Solution** :
```bash
# Activer les migrations au boot
export RUN_STARTUP_MIGRATIONS=true
# Ou exécuter manuellement
python -c "from app.db.init_db import create_tables_with_test_data; create_tables_with_test_data()"
```

---

### Le refresh token ne fonctionne pas

**Erreur** : 401 Unauthorized lors du refresh

**Vérifications** :
1. Vérifier que les cookies sont bien envoyés (`credentials: 'include'`)
2. Vérifier que le refresh_token est dans les cookies (DevTools → Application → Cookies)
3. Vérifier que le backend reçoit bien le cookie (logs)

---

## 📝 Notes Importantes

1. **Mode Développement** : Utilisez `REQUIRE_STRONG_DEFAULT_ADMIN=false` et `RUN_STARTUP_MIGRATIONS=true` pour faciliter les tests
2. **Mode Production** : Utilisez `REQUIRE_STRONG_DEFAULT_ADMIN=true` et `RUN_STARTUP_MIGRATIONS=false`
3. **Base de Test** : Assurez-vous d'utiliser `TEST_DATABASE_URL` et non `DATABASE_URL` pour éviter d'affecter la production

---

**Dernière mise à jour** : 30 Novembre 2025

