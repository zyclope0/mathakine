# Schéma de la base de données Mathakine

Ce document décrit la structure de la base de données PostgreSQL 16 utilisée par l'application Mathakine (anciennement Math Trainer).

## Tables principales

### users
Table des utilisateurs de l'application.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| username | VARCHAR | NOT NULL | Nom d'utilisateur |
| email | VARCHAR | NOT NULL | Email de l'utilisateur |
| hashed_password | VARCHAR | NOT NULL | Mot de passe hashé |
| full_name | VARCHAR | NULL | Nom complet |
| role | VARCHAR(10) | NULL | Rôle utilisateur (PADAWAN, MAÎTRE, GARDIEN, ARCHIVISTE) |
| is_active | BOOLEAN | NULL | Indique si le compte est actif |
| created_at | TIMESTAMP | NULL | Date de création du compte |
| updated_at | TIMESTAMP | NULL | Date de dernière mise à jour |
| grade_level | INTEGER | NULL | Niveau scolaire |
| learning_style | VARCHAR | NULL | Style d'apprentissage préféré |
| preferred_difficulty | VARCHAR | NULL | Niveau de difficulté préféré |
| preferred_theme | VARCHAR | NULL | Thème préféré |
| accessibility_settings | VARCHAR | NULL | Paramètres d'accessibilité |

### exercises
Table des exercices mathématiques.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| title | VARCHAR | NOT NULL | Titre de l'exercice |
| creator_id | INTEGER | NULL | ID de l'utilisateur créateur, clé étrangère vers users.id |
| exercise_type | VARCHAR | NOT NULL | Type d'exercice |
| difficulty | VARCHAR | NOT NULL | Niveau de difficulté |
| tags | VARCHAR | NULL | Tags pour la catégorisation |
| question | TEXT | NOT NULL | Énoncé de la question |
| correct_answer | VARCHAR | NOT NULL | Réponse correcte |
| choices | JSON | NULL | Choix possibles (pour QCM) |
| explanation | TEXT | NULL | Explication de la solution |
| hint | TEXT | NULL | Indice |
| image_url | VARCHAR | NULL | URL d'une image associée |
| audio_url | VARCHAR | NULL | URL d'un fichier audio associé |
| is_active | BOOLEAN | NULL | Indique si l'exercice est actif |
| is_archived | BOOLEAN | NULL | Indique si l'exercice est archivé |
| view_count | INTEGER | NULL | Nombre de vues |
| created_at | TIMESTAMP | NULL | Date de création |
| updated_at | TIMESTAMP | NULL | Date de dernière mise à jour |

### attempts
Table des tentatives de résolution d'exercices.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| user_id | INTEGER | NOT NULL | ID de l'utilisateur, clé étrangère vers users.id |
| exercise_id | INTEGER | NOT NULL | ID de l'exercice tenté, clé étrangère vers exercises.id |
| user_answer | VARCHAR | NOT NULL | Réponse donnée par l'utilisateur |
| is_correct | BOOLEAN | NOT NULL | Indique si la réponse est correcte |
| time_spent | DOUBLE PRECISION | NULL | Temps passé en secondes |
| attempt_number | INTEGER | NULL | Numéro de la tentative |
| hints_used | INTEGER | NULL | Nombre d'indices utilisés |
| device_info | VARCHAR | NULL | Informations sur l'appareil utilisé |
| created_at | TIMESTAMP | NULL | Date de la tentative |

### progress
Table de progression des utilisateurs.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| user_id | INTEGER | NOT NULL | ID de l'utilisateur, clé étrangère vers users.id |
| exercise_type | VARCHAR | NOT NULL | Type d'exercice |
| difficulty | VARCHAR | NOT NULL | Niveau de difficulté |
| total_attempts | INTEGER | NULL | Nombre total de tentatives |
| correct_attempts | INTEGER | NULL | Nombre de tentatives correctes |
| average_time | DOUBLE PRECISION | NULL | Temps moyen de résolution |
| completion_rate | DOUBLE PRECISION | NULL | Taux de complétion |
| streak | INTEGER | NULL | Série actuelle |
| highest_streak | INTEGER | NULL | Meilleure série |
| mastery_level | INTEGER | NULL | Niveau de maîtrise |
| awards | JSON | NULL | Récompenses obtenues |
| strengths | VARCHAR | NULL | Points forts identifiés |
| areas_to_improve | VARCHAR | NULL | Domaines à améliorer |
| recommendations | VARCHAR | NULL | Recommandations |
| last_updated | TIMESTAMP | NULL | Date de dernière mise à jour |

## Défis logiques

### logic_challenges
Table des défis de logique.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| title | VARCHAR | NOT NULL | Titre du défi |
| creator_id | INTEGER | NULL | ID de l'utilisateur créateur, clé étrangère vers users.id |
| challenge_type | VARCHAR(11) | NOT NULL | Type de défi logique |
| age_group | VARCHAR(11) | NOT NULL | Tranche d'âge cible |
| description | TEXT | NOT NULL | Description du défi |
| visual_data | JSON | NULL | Données visuelles (diagrammes, images) |
| correct_answer | VARCHAR | NOT NULL | Réponse correcte |
| solution_explanation | TEXT | NOT NULL | Explication de la solution |
| hint_level1 | TEXT | NULL | Indice de niveau 1 |
| hint_level2 | TEXT | NULL | Indice de niveau 2 |
| hint_level3 | TEXT | NULL | Indice de niveau 3 |
| difficulty_rating | DOUBLE PRECISION | NULL | Niveau de difficulté |
| estimated_time_minutes | INTEGER | NULL | Temps estimé en minutes |
| success_rate | DOUBLE PRECISION | NULL | Taux de réussite |
| image_url | VARCHAR | NULL | URL d'une image associée |
| source_reference | VARCHAR | NULL | Référence à la source |
| tags | VARCHAR | NULL | Tags pour la catégorisation |
| is_template | BOOLEAN | NULL | Indique si c'est un modèle |
| generation_parameters | JSON | NULL | Paramètres de génération |
| is_active | BOOLEAN | NULL | Indique si le défi est actif |
| is_archived | BOOLEAN | NULL | Indique si le défi est archivé |
| view_count | INTEGER | NULL | Nombre de vues |
| created_at | TIMESTAMP | NULL | Date de création |
| updated_at | TIMESTAMP | NULL | Date de dernière mise à jour |

### logic_challenge_attempts
Table des tentatives de résolution des défis logiques.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| user_id | INTEGER | NOT NULL | ID de l'utilisateur, clé étrangère vers users.id |
| challenge_id | INTEGER | NOT NULL | ID du défi, clé étrangère vers logic_challenges.id |
| user_answer | VARCHAR | NOT NULL | Réponse donnée par l'utilisateur |
| is_correct | BOOLEAN | NOT NULL | Indique si la réponse est correcte |
| time_spent | DOUBLE PRECISION | NULL | Temps passé en secondes |
| hint_level1_used | BOOLEAN | NULL | Indique si l'indice niveau 1 a été utilisé |
| hint_level2_used | BOOLEAN | NULL | Indique si l'indice niveau 2 a été utilisé |
| hint_level3_used | BOOLEAN | NULL | Indique si l'indice niveau 3 a été utilisé |
| attempt_number | INTEGER | NULL | Numéro de la tentative |
| notes | TEXT | NULL | Notes sur la tentative |
| created_at | TIMESTAMP | NULL | Date de la tentative |

## Tables de configuration

### settings
Table des paramètres de l'application.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| key | VARCHAR | NOT NULL | Clé du paramètre |
| value | VARCHAR | NULL | Valeur du paramètre |
| value_json | JSON | NULL | Valeur JSON du paramètre |
| description | VARCHAR | NULL | Description du paramètre |
| category | VARCHAR | NULL | Catégorie du paramètre |
| is_system | BOOLEAN | NULL | Indique si c'est un paramètre système |
| is_public | BOOLEAN | NULL | Indique si le paramètre est public |
| created_at | TIMESTAMP | NULL | Date de création |
| updated_at | TIMESTAMP | NULL | Date de dernière mise à jour |

## Tables héritées

### results
Table historique des résultats d'exercices.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| exercise_id | INTEGER | NOT NULL | ID de l'exercice |
| is_correct | BOOLEAN | NOT NULL | Indique si la réponse est correcte |
| attempt_count | INTEGER | NULL | Nombre de tentatives, par défaut 1 |
| time_spent | REAL | NULL | Temps passé |
| created_at | TIMESTAMP | NULL | Date de création, par défaut CURRENT_TIMESTAMP |

### statistics
Table historique des statistiques par session.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| user_id | INTEGER | NULL | ID de l'utilisateur |
| session_id | VARCHAR(255) | NOT NULL | ID de la session |
| exercise_type | VARCHAR(50) | NOT NULL | Type d'exercice |
| difficulty | VARCHAR(50) | NOT NULL | Niveau de difficulté |
| total_attempts | INTEGER | NOT NULL | Nombre total de tentatives, par défaut 0 |
| correct_attempts | INTEGER | NOT NULL | Nombre de tentatives correctes, par défaut 0 |
| avg_time | REAL | NOT NULL | Temps moyen de résolution, par défaut 0 |
| last_updated | TIMESTAMP | NULL | Date de dernière mise à jour, par défaut CURRENT_TIMESTAMP |

### user_stats
Table historique des statistiques des utilisateurs.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| exercise_type | VARCHAR(50) | NOT NULL | Type d'exercice |
| difficulty | VARCHAR(50) | NOT NULL | Niveau de difficulté |
| total_attempts | INTEGER | NULL | Nombre total de tentatives, par défaut 0 |
| correct_attempts | INTEGER | NULL | Nombre de tentatives correctes, par défaut 0 |
| last_updated | TIMESTAMP | NULL | Date de dernière mise à jour, par défaut CURRENT_TIMESTAMP |

### schema_version
Table de version du schéma.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| version | INTEGER | NOT NULL | Numéro de version du schéma |

## Relations entre les tables

### Clés étrangères
- `exercises.creator_id` → `users.id`
- `attempts.user_id` → `users.id`
- `attempts.exercise_id` → `exercises.id`
- `progress.user_id` → `users.id`
- `logic_challenges.creator_id` → `users.id`
- `logic_challenge_attempts.user_id` → `users.id`
- `logic_challenge_attempts.challenge_id` → `logic_challenges.id` 