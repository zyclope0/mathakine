# 🚀 Guide de Démarrage Rapide - Mathakine

**Bienvenue dans Mathakine !** Ce guide vous permettra de démarrer rapidement avec l'application éducative mathématique pour enfants autistes avec thème Star Wars.

## 📋 Prérequis

### Système
- **Python 3.13+** (recommandé)
- **PostgreSQL 16+** (production) ou **SQLite** (développement)
- **Git** pour le versioning
- **Node.js** (optionnel, pour les outils de développement)

### Environnement
- **Windows 10/11**, **macOS**, ou **Linux**
- **8 GB RAM** minimum
- **2 GB d'espace disque** libre

## ⚡ Installation Rapide

### 1. Cloner le Projet
```bash
git clone https://github.com/votre-repo/mathakine.git
cd mathakine
```

### 2. Environnement Virtuel
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (macOS/Linux)
source venv/bin/activate
```

### 3. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration Base de Données

#### Option A : SQLite (Développement)
```bash
# Initialiser la base de données
python mathakine_cli.py init
```

#### Option B : PostgreSQL (Production)
```bash
# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres PostgreSQL

# Initialiser la base de données
python mathakine_cli.py init --postgres
```

### 5. Démarrer l'Application
```bash
# Démarrage simple
python mathakine_cli.py run

# Ou directement
python enhanced_server.py
```

🎉 **L'application est maintenant accessible sur http://localhost:8000**

## 🔐 Premiers Pas

### Connexion Test
- **Utilisateur** : `test_user`
- **Mot de passe** : `test_password`

### Navigation Principale
- **Accueil** : `/` - Vue d'ensemble et statistiques
- **Exercices** : `/exercises` - Liste des exercices disponibles
- **Tableau de bord** : `/dashboard` - Suivi de progression
- **Profil** : `/profile` - Gestion du compte utilisateur

## 🎮 Fonctionnalités Clés

### Types d'Exercices (9 types disponibles - Version 1.5.0)

**Types Arithmétiques de Base** :
- **Addition** : Opérations d'addition adaptées au niveau
- **Soustraction** : Opérations de soustraction avec valeurs positives
- **Multiplication** : Tables de multiplication
- **Division** : Divisions sans reste
- **Mixte** : Combinaison de plusieurs types

**Nouveaux Types (Mai 2025)** ⭐ :
- **Fractions** : 4 opérations complètes (addition, soustraction, multiplication, division)
- **Géométrie** : Calculs sur 5 formes (carré, rectangle, triangle, cercle, trapèze)
- **Texte** : Questions textuelles avec énoncés élaborés et contextualisés
- **Divers** : 6 catégories (monnaie, vitesse, pourcentages, probabilités, séquences)

**Génération via API** : Tous types accessibles via `/api/exercises/generate`

### Niveaux de Difficulté (Thème Star Wars)
- **Initié** : Niveau facile (nombres 1-10)
- **Padawan** : Niveau intermédiaire (nombres 10-50)
- **Chevalier** : Niveau difficile (nombres 50-100)
- **Maître** : Niveau expert (nombres 100-500)

### Défis Logiques
- **Types** : Visuels, abstraits, patterns, mots
- **Groupes d'âge** : 10-11, 12-13, 14-15 ans
- **Système d'indices** : 3 niveaux progressifs

## 🛠️ Commandes Utiles

### CLI Mathakine
```bash
# Voir toutes les commandes
python mathakine_cli.py --help

# Démarrer le serveur
python mathakine_cli.py run

# Exécuter les tests
python mathakine_cli.py test --all

# Initialiser la base de données
python mathakine_cli.py init

# Ouvrir un shell Python avec contexte
python mathakine_cli.py shell
```

### Tests
```bash
# Tests complets
python tests/unified_test_runner.py --all

# Tests par catégorie
python tests/unified_test_runner.py --unit
python tests/unified_test_runner.py --api
python tests/unified_test_runner.py --functional
```

### Base de Données
```bash
# Basculer entre SQLite et PostgreSQL
python scripts/toggle_database.py

# Migrations Alembic
alembic upgrade head
alembic current
alembic history
```

## 🎯 Prochaines Étapes

### Pour les Développeurs
1. **Lire** : [Guide Développeur](../development/README.md)
2. **Explorer** : [Architecture](../architecture/README.md)
3. **Contribuer** : [Guide de Contribution](../development/contributing.md)

### Pour les Utilisateurs
1. **Découvrir** : [Fonctionnalités](../features/README.md)
2. **Personnaliser** : [Interface Utilisateur](../features/ui-interface.md)
3. **Progresser** : [Système de Recommandations](../features/recommendations.md)

## 🆘 Aide et Support

### Problèmes Courants
- **Port 8000 occupé** : Changer le port dans la configuration
- **Erreur base de données** : Vérifier la connexion PostgreSQL
- **Tests échouent** : Vérifier l'environnement virtuel

### Ressources
- **Documentation** : [Table des Matières](../TABLE_DES_MATIERES.md)
- **Dépannage** : [troubleshooting.md](troubleshooting.md)
- **API** : [Référence API](../development/api-reference.md)

### Contact
- **Issues GitHub** : Pour les bugs et demandes de fonctionnalités
- **Discussions** : Pour les questions générales
- **Email** : Pour le support direct

---

**Que la Force des Mathématiques soit avec vous !** ⭐🚀 