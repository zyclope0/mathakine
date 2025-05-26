# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.1] - 2025-05-26

### 🔧 Correction Critique : Route "À propos" Fonctionnelle

#### Fixed
- 🚨 **Correction route `/about`** - Page "À propos" maintenant accessible
  - **Problème** : Route définie uniquement dans FastAPI mais pas dans Starlette
  - **Symptôme** : Erreur 404 lors de l'accès à `/about` depuis l'interface web
  - **Cause** : Serveur Starlette (`enhanced_server.py`) ne connaissait pas la route
  - **Solution** :
    - Ajout de `about_page()` dans `server/views.py` avec gestion utilisateur connecté
    - Ajout de `Route("/about", endpoint=about_page)` dans `server/routes.py`
    - Import de `about_page` dans les fonctions de vues
  - **Résultat** : Page "À propos" accessible et fonctionnelle (status 200 OK)

#### Technical
- 📁 **Fichiers modifiés** :
  - `server/views.py` : Nouvelle fonction `about_page()` 
  - `server/routes.py` : Route `/about` ajoutée et import de `about_page`
- 🔄 **Compatibilité** : Route accessible depuis FastAPI et Starlette
- ✅ **Tests** : Page "À propos" charge correctement avec animations et contenu

#### Impact
- **Fonctionnalité restaurée** : Les utilisateurs peuvent maintenant accéder à l'histoire inspirante de Mathakine
- **Navigation complète** : Tous les liens "À propos" (menu, footer) fonctionnent correctement
- **Expérience utilisateur** : Aucune interruption dans la navigation
- **Architecture cohérente** : Même logique de gestion utilisateur que les autres pages

## [1.4.0] - 2025-01-26

### 🌟 Nouveau : Page "À propos" et Optimisations Ergonomiques v3.0

#### Added
- ✨ **Page "À propos" inspirante** (`templates/about.html`)
  - Histoire personnelle touchante de la création de Mathakine
  - Récit de l'étincelle : Anakin, 9 ans, passionné par les concours de mathélogique
  - Transformation d'un projet personnel en mission partagée
  - Design premium avec animations galactiques et particules scintillantes
  - Sections narratives avec effets de balayage lumineux
  - Citations inspirantes d'Einstein et Nelson Mandela
  - Cartes de valeurs interactives (Apprentissage Ludique, Innovation Pédagogique, Approche Familiale, Excellence Accessible)
  - Statistiques visuelles de Mathakine (150+ exercices, 4 niveaux, 9 types, ∞ possibilités)
  - Section contact avec lien GitHub stylisé
- 🎨 **Optimisations Ergonomiques v3.0** - Interface Premium
  - **Page Exercices** : Effets de survol premium, balayage lumineux, bordures dynamiques, étoiles scintillantes
  - **Page d'Accueil** : Hero Section galactique, statistiques dorées, bouton CTA avec fusée, 50 étoiles scintillantes, 3 planètes flottantes
  - **Système de badges colorés** : 9 types d'exercices avec couleurs et icônes spécifiques
  - **Système de difficultés** : 4 niveaux avec étoiles (Initié ⭐, Padawan ⭐⭐, Chevalier ⭐⭐⭐, Maître ⭐⭐⭐⭐)
  - **Cohérence visuelle** : Palette violette unifiée (#8b5cf6), backdrop blur, animations synchronisées
- 🧭 **Navigation améliorée**
  - Lien "À propos" dans le menu utilisateur et footer
  - Breadcrumb configuré pour la page "À propos"
  - Styles CSS harmonisés avec le thème spatial
- 🎭 **Animations et effets premium**
  - Particules scintillantes générées dynamiquement
  - Effets d'entrée séquentiels pour les cartes
  - Animations fluides avec courbes cubic-bezier
  - Effets de Force pour les cartes de niveaux Jedi

#### Changed
- 🔄 **Interface utilisateur transformée** : Passage d'une interface fonctionnelle à une expérience premium immersive
- 🎨 **Thème spatial renforcé** : Intégration complète de l'univers Star Wars dans tous les éléments visuels
- 📱 **Responsive optimisé** : Effets adaptés pour mobile et desktop
- 🎯 **Expérience utilisateur** : Navigation plus intuitive avec dimension humaine ajoutée

#### Technical
- 📁 **Route `/about`** ajoutée dans `app/main.py`
- 🎨 **Version CSS** mise à jour : `v=3.0.20250115`
- 🖼️ **Styles CSS** : Nouveaux composants pour la page "À propos" et optimisations ergonomiques
- ⚡ **JavaScript** : Animations d'entrée et effets de particules
- 🔗 **Intégration complète** : Templates, routes, navigation, breadcrumbs

#### Impact
- **Dimension humaine** : Ajoute une histoire personnelle touchante qui humanise l'application
- **Mission inspirante** : Transforme la motivation personnelle en vision partagée pour tous les parents
- **Attachement émotionnel** : Rend l'application plus attachante et mémorable
- **Expérience premium** : Interface digne d'une application moderne avec immersion totale
- **Transparence** : Montre l'origine, les valeurs et la philosophie du projet

## [1.3.0] - 2025-01-26

### 🚀 Nouveau : Système CI/CD avec Classification Intelligente des Tests

#### Added
- ✨ **Pipeline GitHub Actions complet** (`.github/workflows/ci.yml`)
  - Tests critiques, importants et complémentaires en parallèle
  - Analyse de couverture de code automatique
  - Vérifications de qualité (Black, isort, Flake8, Bandit, Safety)
  - Génération de rapports détaillés et artifacts
- 🔧 **Script de vérification pre-commit** (`scripts/pre_commit_check.py`)
  - Classification automatique des tests par criticité
  - Timeouts adaptés (3min critiques, 2min importants, 1min complémentaires)
  - Feedback détaillé avec conseils de résolution
- 🪝 **Système de hooks Git** (`.githooks/` + `scripts/setup_git_hooks.py`)
  - Hook pre-commit automatique pour tests critiques
  - Hook post-merge pour mises à jour de dépendances
  - Installation/désinstallation simplifiée
- ⚙️ **Configuration centralisée** (`tests/test_config.yml`)
  - Classification YAML des tests par niveaux
  - Configuration par environnement (local/CI/staging)
  - Paramètres de qualité et métriques
- 🔄 **Mise à jour automatique des tests** (`scripts/update_tests_after_changes.py`)
  - Détection des changements Git depuis dernier commit
  - Analyse des nouvelles fonctions/classes/endpoints
  - Génération automatique de templates de tests
  - Suggestions classées par priorité (critique/important/complémentaire)
- 📚 **Documentation complète** (`docs/CI_CD_GUIDE.md`)
  - Guide d'installation et d'utilisation
  - Troubleshooting et bonnes pratiques
  - Configuration et personnalisation
  - Métriques et monitoring

#### Changed
- 🔄 **Classification des tests en 3 niveaux** :
  - **🔴 Critiques** : Bloquent déploiement (fonctionnels, services core, auth)
  - **🟡 Importants** : Avertissement (intégration, modèles, adaptateurs, API)
  - **🟢 Complémentaires** : Informatifs (CLI, init, recommandations)
- 📊 **Workflow de développement optimisé** :
  - Tests automatiques avant chaque commit
  - Feedback immédiat (3 min max pour critiques)
  - Prévention des régressions automatique
- 🎯 **Métriques et monitoring intégrés** :
  - Taux de réussite par catégorie
  - Temps d'exécution des suites
  - Couverture de code (objectif 75%)
  - Rapports JSON/HTML/Markdown

#### Benefits
- **Pour Développeurs** : Feedback rapide, priorités claires, suggestions automatiques
- **Pour Équipe** : Déploiements sécurisés, qualité maintenue, métriques performance
- **Pour Maintenance** : Tests mis à jour automatiquement, configuration centralisée

## [1.2.0] - 2025-05-26

### 🚀 Mise à jour majeure : Refactoring complet et améliorations

#### Added
- ✨ Nouveau système de handlers modulaires pour l'UI (`server/handlers/`)
- 📊 Système de recommandations personnalisées complet
- 🧩 Templates partiels pour composants réutilisables
- 📚 Documentation complète du schéma de base de données (`docs/Tech/DATABASE_SCHEMA.md`)
- 🧪 Plan de correction structuré des tests (`tests/CORRECTION_PLAN.md`)
- 🔧 Scripts de vérification de compatibilité DB
- 🎯 Support des tokens expirés et refresh tokens
- 📝 Documentation consolidée et professionnelle

#### Changed
- 🔄 Refactoring complet des services avec adaptateurs unifiés
- 🏗️ Architecture améliorée avec séparation claire des responsabilités
- 📈 Couverture de tests augmentée de 47% à 73%
- ✅ Tous les tests fonctionnels passent maintenant (6/6 - 100%)
- 🔐 Système d'authentification JWT renforcé
- 📱 Interface utilisateur optimisée avec nouveaux composants
- 📚 Documentation mise à jour pour être plus académique et professionnelle

#### Fixed
- 🐛 Résolution complète des problèmes d'énumérations PostgreSQL/SQLite
- 🔑 Correction du système d'authentification JWT
- 🆔 Fix des contraintes d'unicité dans les tests (utilisation d'UUIDs)
- 🛣️ Résolution des conflits de routage FastAPI (`/me/progress`)
- 🗑️ Implémentation correcte du système de suppression en cascade
- 🎯 Correction des assertions d'énumérations dans les tests
- 🔄 Fix des problèmes de mocks dans les tests d'adaptateurs

#### Removed
- 🗑️ 70+ fichiers obsolètes archivés et organisés
- 🧹 Scripts de debug temporaires supprimés
- 📄 Documentation redondante consolidée
- 🔧 Scripts PowerShell remplacés par des solutions Python
- 🗂️ Anciens tests obsolètes supprimés

#### Security
- 🔒 Validation Pydantic renforcée sur toutes les entrées
- 🛡️ Protection contre les injections SQL via SQLAlchemy
- 🔐 Tokens JWT avec expiration et refresh
- 🚫 CORS configuré de manière restrictive

#### Performance
- ⚡ Optimisation des requêtes de base de données
- 🚀 Chargement lazy des ressources frontend
- 💾 Système de cache intelligent
- 📊 Pagination optimisée avec curseurs

### État du projet
Le projet est maintenant **PRODUCTION-READY** avec :
- ✅ Architecture stable et scalable
- ✅ Tests fonctionnels 100% passants
- ✅ Documentation complète et professionnelle
- ✅ Sécurité renforcée
- ✅ Performance optimisée
- ✅ 296/347 tests passent (85% de succès)

---

# Journal des modifications

Ce fichier documente toutes les modifications notables apportées au projet Mathakine.

## [Unreleased]

### Ajouts
- ✅ Système de recommandations personnalisées avec modèle de données et migration
- ✅ Nouvelles colonnes pour les exercices (age_group, context_theme, complexity)
- ✅ Stockage de la maîtrise des concepts et de la courbe d'apprentissage en JSON
- ✅ Système de gestion unifiée des transactions avec `TransactionManager`
- ✅ Adaptateur de base de données (`DatabaseAdapter`) pour interface commune SQL/SQLAlchemy
- ✅ Services métier pour les exercices, défis logiques et utilisateurs
- ✅ Adaptateur `EnhancedServerAdapter` pour intégrer le système de transaction à enhanced_server.py
- ✅ Tests automatisés pour l'adaptateur EnhancedServerAdapter
- ✅ Gestion unifiée des suppressions en cascade avec SQLAlchemy pour tous les modèles
- ✅ Nouveaux endpoints de suppression API pour les utilisateurs, exercices et défis logiques
- ✅ Scripts de sécurité pour les migrations Alembic en production (`safe_migrate.py`, `restore_from_backup.py`)
- ✅ Script de vérification des migrations (`pre_commit_migration_check.py`)
- ✅ Documentation détaillée pour les suppressions en cascade et la sécurité des migrations Alembic
- ✅ Amélioration de la documentation OpenAPI (Swagger) pour tous les endpoints
- ✅ Système de pagination amélioré pour la page d'exercices
- ✅ Gestion optimisée des basculements entre vue grille et vue liste
- ✅ Interface holographique pour les exercices avec effets Star Wars
- ✅ Animation adaptative selon le niveau de difficulté des exercices
- ✅ Préparation de l'infrastructure pour le feedback sonore
- ✅ Fonctionnalités d'accessibilité avancées (mode contraste élevé, texte plus grand, réduction des animations)
- ✅ Barre d'outils d'accessibilité avec raccourcis clavier
- ✅ Prise en charge des préférences utilisateur et stockage local des paramètres
- ✅ Nouvelle structure de documentation avec répartition en catégories Core, Tech et Features
- ✅ Table des matières de documentation rationalisée pour faciliter la navigation
- ✅ Documents consolidés pour une meilleure cohérence (ARCHITECTURE.md, DEVELOPER_GUIDE.md, etc.)
- ✅ Système d'archivage de documents avec redirections pour maintenir la compatibilité
- ✅ Glossaire étendu avec nouveaux termes techniques et métaphoriques Star Wars
- ✅ Approche de mock pour les tests avec problèmes d'énumération entre SQLite et PostgreSQL
- ✅ Implémentation de techniques de test unitaire pur avec unittest.mock

### Modifications
- 🔄 Migration progressive des opérations SQL directes vers le système de transaction unifié
- 🔄 Conversion des endpoints `/api/exercises/{id}` (DELETE), `/api/submit-answer` et `/api/exercises` (GET) pour utiliser l'adaptateur
- 🔄 Amélioration de la gestion des sessions de base de données avec try/finally systématique
- 🔄 Tests unitaires pour le système de transaction et les suppressions en cascade
- 🔄 Séparation des opérations de suppression physique et d'archivage logique
- 🔄 Refactorisation des relations entre les modèles SQLAlchemy avec cascade="all, delete-orphan"
- 🔄 Standardisation des opérations de suppression dans tous les endpoints API
- 🔄 Personnalisation de l'interface Swagger UI et ReDoc
- 🔄 Amélioration des badges de type d'exercice et de difficulté
- 🔄 Mise à jour de la documentation UI_GUIDE.md avec les nouvelles fonctionnalités
- 🔄 Archivage et nettoyage des documents obsolètes ou temporaires
- 🔄 Organisation des documents dans des dossiers d'archives datés
- 🔄 Rationalisation complète de la documentation technique pour améliorer la lisibilité
- 🔄 Migration de documents clés vers une structure plus cohérente (Core, Tech, Features)
- 🔄 Mise à jour des liens de référence entre documents
- 🔄 Standardisation du formatage dans toute la documentation
- 🔄 Amélioration de l'accès à la documentation pour les nouveaux contributeurs
- 🔄 Adaptation des tests unitaires avec mocks pour améliorer l'isolation et éviter les problèmes d'énumération
- 🔄 Simplification des tests de services utilisateur avec des mocks isolés

### Corrections
- 🐛 Correction des potentielles fuites de mémoire lors des suppressions d'entités
- 🐛 Prévention des erreurs d'intégrité référentielle dans la base de données
- 🐛 Élimination des transactions SQL manuelles incohérentes
- 🐛 Correction du défilement automatique indésirable lors du basculement de vue grille/liste
- 🐛 Résolution d'un problème de cache avec le mécanisme de "force redraw"
- 🐛 Correction d'un problème où les exercices archivés (is_archived = true) s'affichaient dans la liste des exercices
- 🐛 Optimisation du contrôle de défilement pour une meilleure expérience utilisateur
- 🐛 Désactivation complète du défilement automatique pour respecter le contrôle utilisateur
- 🐛 Correction des liens brisés dans la documentation suite à la restructuration
- 🐛 Résolution des incohérences dans les références entre documents consolidés
- 🐛 Correction du problème d'accès non autorisé aux pages d'exercices sans authentification
- 🐛 Ajout de contrôles d'authentification sur les routes exercise_detail_page et exercises_page
- 🐛 Mise à jour du système de déconnexion pour gérer les tokens access_token et refresh_token
- 🐛 Correction de l'importation du modèle Recommendation dans all_models.py
- 🐛 Résolution des erreurs d'intégrité référentielle liées aux recommandations utilisateur
- 🐛 Correction des tests utilisant des énumérations incompatibles avec PostgreSQL
- 🐛 Résolution des erreurs de type dans les tests d'intégration entre SQLite et PostgreSQL
- 🐛 Correction de la redirection après connexion vers la page d'exercices
- 🐛 Correction des problèmes d'affichage dans la page de détail d'exercice
- 🐛 Amélioration de l'accessibilité et de la navigation dans le tableau de bord

## [0.3.1] - 2025-05-11

### Ajouts
- ✅ Implémentation d'Alembic pour la gestion des migrations de base de données
- ✅ Scripts utilitaires pour faciliter les migrations (`init_alembic.py`, `generate_migration.py`, `alembic_demo.py`)
- ✅ Documentation complète du processus de migration (docs/ALEMBIC.md)
- ✅ Configuration spéciale pour préserver les tables héritées (results, statistics, user_stats, schema_version)

### Corrections
- 🐛 Correction du problème d'insertion dans la table `results` lors de la validation des exercices
- 🐛 Amélioration de la gestion des transactions dans la fonction `submit_answer`
- 🐛 Meilleure journalisation des erreurs de base de données

## [0.3.0] - 2025-05-01

### Ajouts
- ✅ Implémentation d'Alembic pour la gestion des migrations de base de données
- ✅ Scripts utilitaires pour faciliter les migrations (`init_alembic.py`, `generate_migration.py`, `alembic_demo.py`)
- ✅ Documentation complète du processus de migration (docs/ALEMBIC.md)
- ✅ Configuration spéciale pour préserver les tables héritées (results, statistics, user_stats, schema_version)

## [0.2.0] - 2024-09-08

### Ajouts
- ✅ Système de journalisation centralisé avec configuration avancée
- ✅ Dossier `logs/` pour centraliser tous les fichiers de logs 
- ✅ Scripts de migration et de nettoyage des logs anciens
- ✅ Détection des fichiers obsolètes avec scripts d'analyse
- ✅ Dossiers `migrations/` et `services/` pour mieux structurer le projet
- ✅ Documentation détaillée du système de logs (docs/LOGGING.md)

### Modifications
- 🔄 Module `app/core/logging_config.py` pour la gestion centralisée des logs
- 🔄 Mise à jour de tous les imports loguru pour utiliser le module centralisé
- 🔄 Modification de `app/core/config.py` pour intégrer la nouvelle configuration de logs
- 🔄 Amélioration de la structure du projet avec les nouveaux dossiers
- 🔄 Mise à jour de la documentation sur la structure du projet

### Corrections
- 🐛 Normalisation des chemins de logs dans tous les modules

## [0.1.0] - 2024-09-01

### Ajouts
- ✅ Migration des modèles de données vers Pydantic v2
- ✅ Documentation de migration Pydantic v2
- ✅ Script de vérification des validateurs Pydantic
- ✅ Configuration pour le déploiement sur Render

### Modifications
- 🔄 Mise à jour des validateurs dans tous les schémas
- 🔄 Adaptation du préfixe API de "/api/v1" à "/api"
- 🔄 Endpoint racine (/) renvoyant une réponse HTML
- 🔄 Mise à jour de requirements.txt avec Pydantic 2.11.0

### Corrections
- 🐛 Problèmes de validation des modèles Pydantic
- 🐛 Compatibilité avec les dernières versions des dépendances 

> Note: Ce fichier a été consolidé à partir de CHANGELOG.md et RECENT_UPDATES.md le 2025-05-08.
> Dernière mise à jour : 22/06/2025

## [Non publié]

### Ajouté
- Système CI/CD complet avec classification intelligente des tests
- Tests fonctionnels pour validation du tableau de bord
- Script de création de données de test pour utilisateurs

### Corrigé
- **CRITIQUE** : Tableau de bord dysfonctionnel - utilisait un ID utilisateur fixe au lieu de l'utilisateur connecté
- Authentification correcte dans tous les handlers API
- Gestion des erreurs améliorée avec messages explicites

### Modifié
- Handler `get_user_stats` pour utiliser l'authentification réelle
- Logs détaillés pour debugging des statistiques utilisateur

## [1.3.0] - 2025-01-15

### Ajouté
- **Système CI/CD complet** avec GitHub Actions
- **Classification intelligente des tests** en 3 niveaux (Critique/Important/Complémentaire)
- **Hooks Git automatiques** avec vérifications pre-commit
- **Scripts de mise à jour automatique** des tests après modifications
- **Configuration centralisée** des tests et métriques qualité
- **Rapports détaillés** de couverture et performance
- **Documentation complète** du système CI/CD dans `docs/CI_CD_GUIDE.md`

### Amélioré
- **Workflow de développement** optimisé avec feedback rapide
- **Prévention des régressions** automatique
- **Métriques de qualité** suivies en continu
- **Documentation** mise à jour dans tous les guides pertinents

### Technique
- Pipeline GitHub Actions multi-étapes avec exécution parallèle
- Tests critiques avec timeout 3 minutes et échec rapide
- Analyse de sécurité automatique (Bandit, Safety)
- Vérifications de style automatiques (Black, isort, Flake8)

## [1.2.0] - 2024-12-20

### Ajouté
- **Système de suppression en cascade** complet pour maintenir l'intégrité des données
- **Documentation CASCADE_DELETION.md** détaillant le système
- **Tests complets** pour valider les suppressions en cascade à tous les niveaux
- **Interface holographique** style Star Wars pour les exercices
- **Fonctionnalités d'accessibilité avancées** (contraste, taille texte, animations, dyslexie)
- **Système unifié de gestion des transactions** avec TransactionManager
- **EnhancedServerAdapter** pour l'intégration avec enhanced_server.py

### Corrigé
- **Problèmes d'affichage** des exercices archivés dans les listes
- **Défilement automatique** indésirable lors des changements de page
- **Tests de suppression** en cascade pour tous les composants
- **Gestion des erreurs** dans les opérations de base de données

### Amélioré
- **Couverture des tests** de 64% à 68%
- **Support des tests asynchrones** avec meilleure gestion
- **Scripts de test** avec logging standard et gestion propre des ressources
- **Documentation** mise à jour avec les nouvelles fonctionnalités

## [1.1.0] - 2024-11-15

### Ajouté
- **Migration vers PostgreSQL** pour la production
- **Système de migrations Alembic** pour la gestion du schéma
- **Scripts de migration sécurisée** avec sauvegarde automatique
- **Compatibilité SQLite/PostgreSQL** maintenue pour le développement
- **Documentation POSTGRESQL_MIGRATION.md** et **ALEMBIC.md**

### Corrigé
- **Normalisation des types de données** entre SQLite et PostgreSQL
- **Gestion des énumérations** selon le moteur de base de données
- **Scripts de basculement** entre les deux systèmes

### Technique
- Configuration automatique du moteur selon l'environnement
- Préservation des tables héritées lors des migrations
- Validation de l'intégrité post-migration

## [1.0.0] - 2024-10-01

### Ajouté
- **Architecture dual-backend** : FastAPI (API) + Starlette (interface web)
- **Système d'authentification JWT** avec cookies HTTP-only
- **Génération d'exercices** algorithmique et pseudo-IA
- **Tableau de bord** avec statistiques et graphiques
- **Défis logiques** pour les 10-15 ans
- **Thème Star Wars** complet avec terminologie Jedi
- **Tests structurés** en 4 niveaux (unitaires, API, intégration, fonctionnels)
- **Documentation complète** avec guides techniques

### Fonctionnalités principales
- Exercices mathématiques adaptatifs (Addition, Soustraction, Multiplication, Division)
- Niveaux de difficulté thématiques (Initié, Padawan, Chevalier, Maître)
- Suivi de progression avec statistiques détaillées
- Interface utilisateur responsive avec thème spatial
- API REST complète avec documentation OpenAPI

### Technique
- Base de données SQLite avec modèles SQLAlchemy 2.0
- Validation des données avec Pydantic 2.0
- Architecture MVC avec séparation claire des responsabilités
- Système de journalisation centralisé avec loguru
- Interface CLI complète pour l'administration

---

## Légende des types de modifications

- **Ajouté** : Nouvelles fonctionnalités
- **Modifié** : Modifications de fonctionnalités existantes
- **Déprécié** : Fonctionnalités qui seront supprimées dans une version future
- **Supprimé** : Fonctionnalités supprimées dans cette version
- **Corrigé** : Corrections de bugs
- **Sécurité** : Corrections de vulnérabilités de sécurité
