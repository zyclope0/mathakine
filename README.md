# 🌟 Mathakine - Plateforme Éducative d'Apprentissage des Mathématiques

[![Tests](https://github.com/mathakine/math-trainer/actions/workflows/tests.yml/badge.svg)](https://github.com/mathakine/math-trainer/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/mathakine/math-trainer/branch/main/graph/badge.svg)](https://codecov.io/gh/mathakine/math-trainer)
[![Version](https://img.shields.io/github/v/release/mathakine/math-trainer)](https://github.com/mathakine/math-trainer/releases)
[![License](https://img.shields.io/github/license/mathakine/math-trainer)](LICENSE)

## 📚 Description du Projet

Mathakine est une plateforme web éducative innovante pour l'apprentissage des mathématiques, spécialement conçue pour les enfants autistes. L'application utilise une interface thématique Star Wars immersive pour créer un environnement d'apprentissage engageant et adapté aux besoins spécifiques de ce public.

**Histoire personnelle** : Créé par un père pour son fils Anakin, 9 ans, passionné par les concours de mathélogique, Mathakine est né du besoin de trouver un outil vraiment interactif et amusant pour s'entraîner aux mathématiques. Ce qui a commencé comme un projet personnel s'est transformé en une mission partagée pour offrir à tous les enfants une expérience d'apprentissage exceptionnelle.

---

## 📖 **Documentation Complète**

### 🚀 **Guides de Démarrage**
- [Installation et Setup](docs/getting-started/README.md) - Guide complet d'installation
- [Premiers Pas](docs/getting-started/README.md#premiers-pas) - Navigation et fonctionnalités de base
- [Configuration](docs/getting-started/README.md#configuration-base-de-données) - SQLite et PostgreSQL

### 🏗️ **Architecture et Technique**
- [Architecture Globale](docs/architecture/README.md) - Vue d'ensemble des composants
- [Documentation API](docs/api/api.md) - 40+ endpoints avec exemples complets
- [Guide Développeur](docs/development/README.md) - Architecture, tests, standards (916 lignes)
- [Tests et CI/CD](docs/development/testing.md) - Système à 4 niveaux avec classification

### 🎨 **Interface et Expérience Utilisateur**
- [Guide UI/UX Complet](docs/ui-ux/ui-ux.md) - Interface Star Wars et accessibilité
- [Composants](docs/ui-ux/ui-ux.md#composants-ui-réutilisables) - Boutons, cartes, modales
- [Accessibilité](docs/ui-ux/ui-ux.md#accessibilité-wcag-21-aa) - WCAG 2.1 AA avec barre d'outils

### ✨ **Fonctionnalités**
- [Fonctionnalités Principales](docs/features/README.md) - 9 types d'exercices + défis logiques
- [Système de Badges](docs/features/BADGE_SYSTEM.md) - Progression et récompenses
- [Tableau de Bord](docs/features/README.md#suivi-de-progression) - Statistiques temps réel

### 📊 **Gestion de Projet**
- [Statut du Projet](docs/project/README.md) - État des fonctionnalités et métriques
- [Roadmap 2025-2026](docs/project/roadmap.md) - Vision et planification future
- [Rapport de Mise à Jour](docs/rapport/rapport-mise-a-jour.md) - Dernière analyse complète (juin 2025)

### 📚 **Documentation Générale**
- [Index Documentation](docs/README.md) - Navigation dans toute la documentation
- [Glossaire](docs/GLOSSARY.md) - Terminologie technique et métier
- [Changelog](docs/CHANGELOG.md) - Historique des versions

---

### Caractéristiques Principales

- **🎯 Apprentissage Adaptatif** : Progression personnalisée selon le niveau et les capacités de l'élève
- **🌌 Interface Immersive** : Thème Star Wars avec effets visuels et sonores adaptés
- **📊 Suivi Détaillé** : Tableaux de bord complets pour élèves, enseignants et parents
- **♿ Accessibilité Avancée** : Support complet pour différents besoins (dyslexie, photosensibilité, etc.)
- **🏆 Système de Motivation** : Progression par rangs Jedi et récompenses virtuelles
- **🔄 CI/CD Intégré** : Système de tests automatisés avec classification intelligente
- **💫 Interface Premium v3.0** : Optimisations ergonomiques avec thème spatial immersif
- **📖 Page "À propos"** : Histoire inspirante de la création de Mathakine et valeurs du projet
- **🎲 Générateurs d'Exercices Étendus** : 9 types d'exercices avec 4 nouveaux domaines (Fractions, Géométrie, Texte, Divers) ⭐ **NOUVEAU**

## 🎲 Types d'Exercices Disponibles

### Exercices Mathématiques Complets

#### Types Arithmétiques (Existants)
- **➕ Addition** : 4 niveaux de difficulté (Initié → Maître)
- **➖ Soustraction** : Calculs avec résultats positifs
- **✖️ Multiplication** : Tables et calculs avancés
- **➗ Division** : Divisions exactes adaptées au niveau
- **🔀 Mixte** : Combinaisons intelligentes des opérations

#### Nouveaux Types (Mai 2025) ⭐
- **🔢 Fractions** : 4 opérations complètes avec module Python `fractions`
  - Progression : fractions simples → dénominateurs différents → calculs complexes → divisions
  - Exemple : `Calcule 5/6 + 3/4 → 19/12`
- **📐 Géométrie** : 5 formes (carré, rectangle, triangle, cercle, trapèze)
  - 3 propriétés : périmètre, aire, diagonale
  - Exemple : `Calcule l'aire d'un triangle avec base=146 et hauteur=105 → 7665.0`
- **🌟 Divers** : 6 catégories de problèmes concrets
  - Monnaie, vitesse, pourcentages, probabilités, séquences
  - Exemple : `Un train roule à 755 km/h pendant 1 heure. Distance ? → 755 km`

### Progression par Niveaux
- **🌱 Initié** : Introduction aux concepts (nombres 1-10)
- **⚔️ Padawan** : Niveau intermédiaire (nombres 10-50)
- **🛡️ Chevalier** : Calculs avancés (nombres 50-100)
- **👑 Maître** : Défis experts (nombres 100-500)

### API REST Complète
```bash
POST /api/exercises/generate
{
  "exercise_type": "fractions",
  "difficulty": "padawan",
  "save": false
}
```

**Résultats de Migration** : 12/12 tests réussis (100%), +50% de types d'exercices, +200% de couverture mathématique

## 🏗️ Architecture Technique

### Stack Technologique

#### Backend
- **Frameworks** : FastAPI 0.115.12 + Starlette 0.31.1
- **ORM** : SQLAlchemy 2.0.40
- **Base de données** : PostgreSQL (production) / SQLite (développement)
- **Authentification** : JWT via python-jose
- **Validation** : Pydantic 2.11.0

#### Frontend
- **Templates** : Jinja2 3.1.2
- **Styles** : CSS personnalisé avec système de variables
- **JavaScript** : Vanilla JS avec modules ES6
- **Accessibilité** : WCAG 2.1 AA compliant

#### Infrastructure
- **Serveur** : Uvicorn 0.23.2 (ASGI)
- **Migrations** : Alembic 1.13.1
- **Tests** : Pytest 7.4.3 avec couverture
- **CI/CD** : GitHub Actions + Docker

## 🚀 Installation et Configuration

### Prérequis
- Python 3.11 ou supérieur
- PostgreSQL 14+ (production) ou SQLite (développement)
- Git

### Installation Locale

```bash
# Cloner le repository
git clone https://github.com/mathakine/math-trainer.git
cd mathakine

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# Installer le système CI/CD (hooks Git)
python scripts/setup_git_hooks.py

# Initialiser la base de données
python mathakine_cli.py init

# Lancer l'application
python mathakine_cli.py run
```

### Configuration Docker

```bash
# Construction de l'image
docker build -t mathakine .

# Lancement avec docker-compose
docker-compose up -d
```

## 🔄 Système CI/CD

### Classification Intelligente des Tests

Le projet utilise un système de classification des tests en 3 niveaux :

#### 🔴 Tests Critiques (BLOQUANTS)
- **Impact** : Bloquent le commit et le déploiement
- **Timeout** : 3 minutes
- **Contenu** : Tests fonctionnels, services core, authentification

#### 🟡 Tests Importants (NON-BLOQUANTS)
- **Impact** : Avertissement, commit autorisé
- **Timeout** : 2 minutes
- **Contenu** : Tests d'intégration, modèles, adaptateurs

#### 🟢 Tests Complémentaires (INFORMATIFS)
- **Impact** : Information seulement
- **Timeout** : 1 minute
- **Contenu** : CLI, initialisation, fonctionnalités secondaires

### Workflow de Développement

1. **Modification du code**
2. **Tests automatiques** (hook pre-commit)
3. **Commit** (si tests critiques passent)
4. **Push** → Pipeline GitHub Actions
5. **Déploiement** (si tous les tests critiques passent)

### Commandes CI/CD

```bash
# Vérification manuelle pre-commit
python scripts/pre_commit_check.py

# Tests par catégorie
python -m pytest tests/functional/ -v      # Critiques
python -m pytest tests/integration/ -v     # Importants
python -m pytest tests/unit/test_cli.py -v # Complémentaires

# Mise à jour automatique des tests
python scripts/update_tests_after_changes.py --auto-create

# Bypass temporaire (non recommandé)
git commit --no-verify
```

Pour plus de détails, consultez le [Guide CI/CD complet](docs/CI_CD_GUIDE.md).

---

## 📱 **Accès à l'Application**

### **Démarrage Local**
```bash
python mathakine_cli.py run
```
🌐 **Interface** : http://localhost:8000  
📖 **API Docs** : http://localhost:8000/docs

### **Compte de Test**
- **Utilisateur** : `test_user`
- **Mot de passe** : `test_password`

---

## 🤝 **Contribution et Support**

### **Pour Contribuer**
1. **Fork** le repository
2. **Lire** le [Guide de Contribution](docs/development/contributing.md)
3. **Respecter** les standards de code et tests
4. **Soumettre** une Pull Request

### **Support**
- **🐛 Issues** : Pour bugs et demandes de fonctionnalités
- **💬 Discussions** : Pour questions générales
- **📖 Documentation** : Guide complet dans [docs/](docs/)

---

**Que la Force des Mathématiques soit avec vous !** ⭐🚀

*Développé avec ❤️ pour l'apprentissage inclusif* 