# Journal des modifications

Ce fichier documente toutes les modifications notables apportées au projet Mathakine.

## [Unreleased]

### Ajouts
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

### Modifications
- 🔄 Refactorisation des relations entre les modèles SQLAlchemy avec cascade="all, delete-orphan"
- 🔄 Standardisation des opérations de suppression dans tous les endpoints API
- 🔄 Personnalisation de l'interface Swagger UI et ReDoc
- 🔄 Amélioration des badges de type d'exercice et de difficulté
- 🔄 Mise à jour de la documentation UI_GUIDE.md avec les nouvelles fonctionnalités
- 🔄 Archivage et nettoyage des documents obsolètes ou temporaires
- 🔄 Organisation des documents dans des dossiers d'archives datés

### Corrections
- 🐛 Correction des potentielles fuites de mémoire lors des suppressions d'entités
- 🐛 Prévention des erreurs d'intégrité référentielle dans la base de données
- 🐛 Correction du défilement automatique indésirable lors du basculement de vue grille/liste
- 🐛 Résolution d'un problème de cache avec le mécanisme de "force redraw"
- 🐛 Correction d'un problème où les exercices archivés (is_archived = true) s'affichaient dans la liste des exercices
- 🐛 Optimisation du contrôle de défilement pour une meilleure expérience utilisateur
- 🐛 Désactivation complète du défilement automatique pour respecter le contrôle utilisateur

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
