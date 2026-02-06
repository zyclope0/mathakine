# 🛠️ Scripts Mathakine - Documentation Complète

Ce dossier contient **45+ scripts utilitaires** pour la maintenance, le développement et le déploiement du projet Mathakine. Cette documentation est **exhaustive et à jour** avec tous les scripts réellement présents.

## 📋 Table des Matières

- [🎯 Scripts Principaux](#-scripts-principaux)
- [👥 Gestion des Utilisateurs](#-gestion-des-utilisateurs)
- [🗄️ Base de Données](#️-base-de-données)
- [🔧 Développement & Git](#-développement--git)
- [🧪 Tests & Validation](#-tests--validation)
- [⚙️ Configuration & Environnement](#️-configuration--environnement)
- [🖥️ Scripts PowerShell](#️-scripts-powershell)
- [📊 Analyse & Monitoring](#-analyse--monitoring)

---

## 🎯 Scripts Principaux

### `mathakine_cli.py` (Racine du projet)
**Interface en ligne de commande unifiée pour Mathakine**

```bash
# Démarrer le serveur
python mathakine_cli.py serve

# Gérer la base de données
python mathakine_cli.py migrate
python mathakine_cli.py init-db

# Tests et validation
python mathakine_cli.py test
python mathakine_cli.py check-health
```

**Fonctionnalités** :
- Gestion complète du serveur et de la base de données
- Interface unifiée pour toutes les opérations projet
- Logging avancé et gestion d'erreurs

---

## 👥 Gestion des Utilisateurs

### `create_obiwan_user.py`
**Création de l'utilisateur permanent ObiWan pour les tests et démos**

```bash
# Créer l'utilisateur ObiWan
python scripts/create_obiwan_user.py

# Forcer la recréation
python scripts/create_obiwan_user.py --force

# Mode verbose
python scripts/create_obiwan_user.py --verbose
```

**Fonctionnalités** :
- Création sécurisée avec mot de passe bcrypt
- Validation de l'unicité et gestion des conflits
- Intégration avec le système de nettoyage automatique
- Configuration : `ObiWan` / `HelloThere123!`

### `keep_obiwan_user.py`
**Protection de l'utilisateur ObiWan contre le nettoyage automatique**

```bash
# Marquer ObiWan comme permanent
python scripts/keep_obiwan_user.py

# Vérifier le statut
python scripts/keep_obiwan_user.py --check
```

### `create_test_data.py`
**Génération de données de test pour le développement**

```bash
# Créer un jeu de données complet
python scripts/create_test_data.py

# Créer seulement les utilisateurs
python scripts/create_test_data.py --users-only

# Créer seulement les exercices
python scripts/create_test_data.py --exercises-only
```

### `cleanup_test_data.py`
**Nettoyage intelligent des données de test**

```bash
# Nettoyage standard (préserve ObiWan)
python scripts/cleanup_test_data.py

# Nettoyage complet
python scripts/cleanup_test_data.py --all

# Mode simulation
python scripts/cleanup_test_data.py --dry-run
```

---

## 🗄️ Base de Données

### `generate_migration.py`
**Génération automatique de migrations Alembic**

```bash
# Créer une nouvelle migration
python scripts/generate_migration.py "Add user preferences"

# Migration automatique avec détection des changements
python scripts/generate_migration.py --auto "Model updates"
```

### `init_alembic.py`
**Initialisation d'Alembic pour le projet**

```bash
# Initialiser Alembic
python scripts/init_alembic.py

# Réinitialiser complètement
python scripts/init_alembic.py --reset
```

### `toggle_database.py`
**Basculement entre PostgreSQL et SQLite**

```bash
# Basculer vers SQLite
python scripts/toggle_database.py --sqlite

# Basculer vers PostgreSQL
python scripts/toggle_database.py --postgres
```

### `restore_deleted_tables.sql`
**Script SQL pour restaurer des tables supprimées accidentellement**

```sql
-- Exécuter directement dans psql ou pgAdmin
\i scripts/restore_deleted_tables.sql
```

---

## 🔧 Développement & Git

### `setup_git_hooks.py`
**Installation automatique des hooks Git pour le projet**

```bash
# Installer tous les hooks
python scripts/setup_git_hooks.py

# Désinstaller les hooks
python scripts/setup_git_hooks.py --uninstall
```

**Hooks installés** :
- **pre-commit** : Exécute `pre_commit_check.py` avant chaque commit
- **post-merge** : Vérifie les dépendances après un merge

### `pre_commit_check.py`
**Vérifications automatiques avant commit**

```bash
# Vérification manuelle
python scripts/pre_commit_check.py

# Mode strict (bloque sur warnings)
python scripts/pre_commit_check.py --strict

# Vérifier un fichier spécifique
python scripts/pre_commit_check.py --file app/models/user.py
```

**Vérifications effectuées** :
- Syntaxe Python valide
- Tests critiques
- Normes de codage
- Compatibilité des énumérations

### `install_hooks.py`
**Installation simplifiée des hooks de développement**

```bash
# Installation rapide
python scripts/install_hooks.py
```

---

## 🧪 Tests & Validation

### `check_compatibility.py`
**Vérification et correction des problèmes de compatibilité**

```bash
# Vérification complète
python scripts/check_compatibility.py

# Corriger les énumérations
python scripts/check_compatibility.py --fix-enums

# Corriger Pydantic v1 → v2
python scripts/check_compatibility.py --fix-pydantic

# Mode verbeux
python scripts/check_compatibility.py --verbose
```

**Détecte et corrige** :
- Énumérations sans `.value` pour PostgreSQL
- Migration Pydantic v1 vers v2 (`.dict()` → `.model_dump()`)
- Imports obsolètes

### `update_tests_after_changes.py`
**Mise à jour automatique des tests après modifications du code**

```bash
# Mise à jour intelligente
python scripts/update_tests_after_changes.py

# Création automatique de tests manquants
python scripts/update_tests_after_changes.py --auto-create

# Mode simulation
python scripts/update_tests_after_changes.py --dry-run
```

### `check_test_data.py`
**Validation de l'intégrité des données de test**

```bash
# Vérification rapide
python scripts/check_test_data.py

# Rapport détaillé
python scripts/check_test_data.py --detailed
```

### `analyze_test_cleanup.py`
**Analyse des données avant nettoyage**

```bash
# Analyser les données actuelles
python scripts/analyze_test_cleanup.py

# Rapport avec recommandations
python scripts/analyze_test_cleanup.py --recommend
```

---

## ⚙️ Configuration & Environnement

### `generate_context.py`
**Génération du contexte de projet pour l'IA et la documentation**

```bash
# Générer le contexte complet
python scripts/generate_context.py

# Contexte pour un module spécifique
python scripts/generate_context.py --module app.models

# Format markdown
python scripts/generate_context.py --format markdown
```

### `optimize_performance.py`
**Optimisation des performances du projet**

```bash
# Optimisation complète
python scripts/optimize_performance.py

# Optimiser seulement la base de données
python scripts/optimize_performance.py --db-only

# Optimiser seulement le code
python scripts/optimize_performance.py --code-only
```

### `normalize_css.py`
**Normalisation et optimisation des fichiers CSS**

```bash
# Normaliser tous les CSS
python scripts/normalize_css.py

# Fichier spécifique
python scripts/normalize_css.py --file static/style.css
```

---

## 🖥️ Scripts PowerShell & Batch

### Configuration Environnement (`scripts/utils/`)

#### `env_manager.ps1` / `env_manager.bat`
**Gestionnaire complet des variables d'environnement**

```powershell
# PowerShell
.\scripts\utils\env_manager.ps1 -Action Setup
.\scripts\utils\env_manager.ps1 -Action Validate
```

```cmd
# Batch
scripts\utils\env_manager.bat setup
scripts\utils\env_manager.bat validate
```

#### `check_encoding.py` / `Check-Encoding.ps1`
**Vérification de l'encodage des fichiers**

```bash
# Python
python scripts/utils/check_encoding.py

# PowerShell
.\scripts\utils\Check-Encoding.ps1
```

#### `fix_encoding.py` / `Fix-EnvEncoding.ps1`
**Correction automatique des problèmes d'encodage**

```bash
# Correction Python
python scripts/utils/fix_encoding.py

# Correction PowerShell
.\scripts\utils\Fix-EnvEncoding.ps1
```

### Validation Serveur (`scripts/utils/`)

#### `validate_server_port.bat` / `Validate-ServerPort.ps1`
**Validation et gestion des ports serveur**

```cmd
# Vérifier le port 8000
scripts\utils\validate_server_port.bat 8000
```

```powershell
# PowerShell avec options avancées
.\scripts\utils\Validate-ServerPort.ps1 -Port 8000 -AutoFix
```

### Installation (`scripts/setup/`)

#### `install_and_run.bat`
**Installation complète et démarrage du projet**

```cmd
# Installation et démarrage automatiques
scripts\setup\install_and_run.bat
```

#### `Install-Dependencies.ps1`
**Installation des dépendances PowerShell**

```powershell
# Installation avec vérifications
.\scripts\setup\Install-Dependencies.ps1 -Verify
```

---

## 📊 Analyse & Monitoring

### `fix_test_user_password.py`
**Correction des mots de passe utilisateurs de test**

```bash
# Réinitialiser les mots de passe
python scripts/fix_test_user_password.py

# Utilisateur spécifique
python scripts/fix_test_user_password.py --user obiwan
```

### `keep_test_user.py`
**Gestion de la persistance des utilisateurs de test**

```bash
# Marquer comme permanent
python scripts/keep_test_user.py --permanent

# Vérifier le statut
python scripts/keep_test_user.py --status
```

### `start_render.sh`
**Script de démarrage pour environnement Render (déploiement)**

```bash
# Démarrage production
./scripts/start_render.sh
```

---

## 🔧 Utilisation Avancée

### Scripts de Migration

Pour migrer les données ou la configuration :

```bash
# 1. Vérifier la compatibilité
python scripts/check_compatibility.py --verbose

# 2. Corriger les problèmes
python scripts/check_compatibility.py --fix-enums --fix-pydantic

# 3. Mettre à jour les tests
python scripts/update_tests_after_changes.py --auto-create

# 4. Valider l'intégrité
python scripts/check_test_data.py --detailed
```

### Workflow de Développement

Pour configurer un environnement de développement complet :

```bash
# 1. Installer les hooks Git
python scripts/setup_git_hooks.py

# 2. Créer l'utilisateur de test
python scripts/create_obiwan_user.py

# 3. Générer des données de test
python scripts/create_test_data.py

# 4. Optimiser les performances
python scripts/optimize_performance.py

# 5. Valider la configuration
python scripts/pre_commit_check.py
```

### Maintenance Régulière

Scripts à exécuter régulièrement :

```bash
# Hebdomadaire
python scripts/cleanup_test_data.py
python scripts/optimize_performance.py

# Mensuel
python scripts/analyze_test_cleanup.py --recommend
python scripts/generate_context.py

# Avant release
python scripts/check_compatibility.py
python scripts/update_tests_after_changes.py
```

---

## 📚 Documentation des Modules

- **🔧 Utilitaires** : `scripts/utils/` - 25+ scripts de configuration
- **⚙️ Configuration** : `scripts/setup/` - Scripts d'installation
- **🗄️ Base de données** : `scripts/database/` - Scripts SQL et migrations
- **🖥️ Serveur** : `scripts/server/` - Scripts de gestion serveur

---

## 🆘 Aide et Dépannage

### Problèmes Courants

**Erreur "Module not found"** :
```bash
# S'assurer d'être dans le répertoire racine
cd /path/to/mathakine
python scripts/nom_du_script.py
```

**Problèmes de permissions** :
```bash
# Rendre exécutable (Linux/Mac)
chmod +x scripts/nom_du_script.py

# PowerShell (Windows)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Base de données non accessible** :
```bash
# Vérifier la configuration
python scripts/utils/check_env_vars.py

# Réinitialiser la base
python scripts/toggle_database.py --sqlite
```

### Logs et Debugging

Tous les scripts supportent le mode verbose :
```bash
python scripts/nom_du_script.py --verbose
```

Les logs sont générés dans `logs/` avec rotation automatique.

---

*Documentation mise à jour : 28 mai 2025*  
*Scripts totaux : 45+ | Maintenance : Active* 