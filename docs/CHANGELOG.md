# Journal des modifications

Ce fichier documente toutes les modifications notables apportées au projet Mathakine.

## [Unreleased]

### Ajouts
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
> Dernière mise à jour : 15/06/2025
