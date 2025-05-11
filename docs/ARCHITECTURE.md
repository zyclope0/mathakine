# Architecture de Mathakine

Ce document décrit l'architecture technique du projet Mathakine, une application d'apprentissage des mathématiques avec thème Star Wars pour les enfants autistes.

## Vue d'ensemble

Mathakine est structuré comme une application web moderne avec une séparation claire entre le backend (API REST) et le frontend. Cette documentation se concentre sur l'architecture du backend.

```
mathakine-backend/
├── app/                     # Code principal de l'application
│   ├── api/                 # API REST
│   ├── core/                # Configuration et utilitaires
│   ├── db/                  # Accès à la base de données
│   ├── models/              # Modèles de données SQLAlchemy
│   ├── schemas/             # Schémas Pydantic
│   └── services/            # Services métier
├── docs/                    # Documentation
├── scripts/                 # Scripts utilitaires
├── static/                  # Fichiers statiques
├── templates/               # Templates Jinja2
├── tests/                   # Tests automatisés
├── mathakine_cli.py         # Interface en ligne de commande
├── Dockerfile               # Configuration Docker
├── requirements.txt         # Dépendances Python
└── Procfile                 # Configuration pour Render/Heroku
```

## Architecture Backend

### API REST (app/api/)

L'API REST est organisée selon les principes RESTful avec une séparation claire des endpoints par domaine fonctionnel :

```
app/api/
├── __init__.py
├── api.py                   # Routeur API principal
├── deps.py                  # Dépendances FastAPI
└── endpoints/               # Endpoints organisés par domaine
    ├── __init__.py
    ├── exercises.py         # Endpoints pour les exercices
    └── users.py             # Endpoints pour les utilisateurs
```

Chaque module d'endpoints contient :
- Des routes CRUD pour la ressource concernée
- Des validations des entrées
- Des opérations spécifiques au domaine

**Améliorations récentes** :
- Restructuration pour une meilleure séparation des préoccupations
- Utilisation des nouveaux gestionnaires lifespan de FastAPI
- Standardisation des réponses API

### Modèles de données (app/models/)

Les modèles de données sont implémentés avec SQLAlchemy et représentent la structure de la base de données :

```
app/models/
├── __init__.py
├── all_models.py            # Import de tous les modèles
├── attempt.py               # Tentatives d'exercices
├── exercise.py              # Exercices mathématiques
├── logic_challenge.py       # Défis logiques
├── progress.py              # Progression des utilisateurs
├── settings.py              # Paramètres système
└── user.py                  # Utilisateurs
```

**Améliorations récentes** :
- Mise à jour pour compatibilité avec SQLAlchemy 2.0
- Ajout du modèle LogicChallenge pour les défis de logique avancés
- Amélioration des relations entre modèles

### Schémas Pydantic (app/schemas/)

Les schémas Pydantic servent à la validation des données et à la sérialisation :

```
app/schemas/
├── __init__.py
├── all_schemas.py           # Import de tous les schémas
├── common.py                # Schémas communs (pagination, réponses)
├── exercise.py              # Schémas d'exercices
├── logic_challenge.py       # Schémas de défis logiques
└── user.py                  # Schémas d'utilisateurs
```

**Améliorations récentes** :
- Mise à jour pour compatibilité avec Pydantic 2.0+
- Standardisation des schémas de réponse
- Ajout de la validation pour les nouveaux types de données

### Services (app/services/)

Les services contiennent la logique métier de l'application :

```
app/services/
├── __init__.py
├── auth_service.py          # Service d'authentification
├── db_init_service.py       # Service d'initialisation de la base de données
├── exercise_service.py      # Service de gestion des exercices
└── user_service.py          # Service de gestion des utilisateurs
```

**Améliorations récentes** :
- Création d'un service dédié pour l'initialisation de la base de données
- Séparation des responsabilités pour une meilleure maintenance
- Implémentation de la génération de données de test

### Configuration et Base de Données (app/core/ et app/db/)

La configuration et l'accès à la base de données sont gérés par ces modules :

```
app/core/
├── __init__.py
├── config.py                # Configuration de l'application
└── security.py              # Sécurité (hachage, JWT)

app/db/
├── __init__.py
├── base.py                  # Configuration SQLAlchemy
└── init_db.py               # Initialisation de la base de données
```

**Améliorations récentes** :
- Mise à jour du système de configuration avec pydantic-settings
- Amélioration de la gestion des connexions à la base de données
- Support de SQLite avec future migration vers PostgreSQL

## Interface en Ligne de Commande (CLI)

Le fichier `mathakine_cli.py` fournit une interface en ligne de commande complète pour gérer l'application :

```
mathakine_cli.py             # Interface CLI principale
```

Commandes disponibles :
- `run` : Démarrer l'application
- `init` : Initialiser la base de données
- `test` : Exécuter les tests
- `validate` : Valider l'application
- `shell` : Démarrer un shell Python interactif
- `setup` : Configurer l'environnement de développement

**Améliorations récentes** :
- Développement d'un CLI complet pour la gestion de l'application
- Support de différents environnements de développement
- Facilitation de l'initialisation et des tests

## Déploiement

### Docker

Le `Dockerfile` a été modernisé pour supporter les dernières versions de Python :

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installation des dépendances spécifiques à Python 3.13
RUN pip install --no-cache-dir sqlalchemy>=2.0.27 fastapi>=0.100.0 pydantic>=2.0.0 pydantic-settings

# Copier le reste des fichiers du projet
COPY . .

# Exposer le port utilisé par l'application
EXPOSE 8081

# Définir les variables d'environnement pour la production
ENV MATH_TRAINER_DEBUG=false
ENV MATH_TRAINER_PROFILE=prod
ENV MATH_TRAINER_PORT=8081

# Commande pour démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
```

### Render

Le script de démarrage pour Render a été amélioré pour assurer une initialisation correcte de la base de données :

```bash
#!/bin/bash

# Script de démarrage pour Render
# Ce script initialise la base de données et démarre le serveur

# S'assurer que nous sommes dans le bon répertoire
cd /opt/render/project/src

# Activer l'environnement virtuel s'il existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Installer les dépendances spécifiques à Python 3.13
pip install sqlalchemy>=2.0.27 fastapi>=0.100.0 pydantic>=2.0.0 pydantic-settings

# Configurer les variables d'environnement
export MATH_TRAINER_DEBUG=false
export MATH_TRAINER_PROFILE=prod

# Initialiser la base de données
python -c "from app.db.init_db import create_tables; create_tables()"

# Démarrer le serveur
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Compatibilité Python 3.13

Des efforts significatifs ont été faits pour assurer la compatibilité avec Python 3.13 :

1. **Mise à jour des dépendances** :
   - SQLAlchemy 2.0.40
   - FastAPI 0.115.12
   - Pydantic 2.11.4
   - pydantic-settings pour la gestion des configurations

2. **Corrections de code** :
   - Utilisation des new-style asynccontextmanager pour FastAPI
   - Correction des changements d'API dans SQLAlchemy
   - Adaptation aux nouvelles conventions de Pydantic

3. **Améliorations de sécurité** :
   - Utilisation des meilleures pratiques pour la validation des entrées
   - Mise en œuvre de middleware de sécurité

Pour plus de détails sur la compatibilité, voir [validation/COMPATIBILITY.md](validation/COMPATIBILITY.md).

## Évolution future

L'architecture est conçue pour permettre les évolutions suivantes :

1. **Migration de base de données** :
   - Passage de SQLite à PostgreSQL pour une meilleure scalabilité
   - Support de migrations avec Alembic

2. **Microservices** :
   - Décomposition potentielle en services spécialisés
   - API Gateway pour la gestion des requêtes

3. **Intégration d'IA** :
   - Génération d'exercices par IA
   - Analyse prédictive des performances des utilisateurs

4. **Interface utilisateur** :
   - API prête pour l'intégration avec un frontend moderne
   - Support pour applications mobiles

## Normalisation et intégrité des données

Une attention particulière a été portée à la normalisation des données pour assurer la cohérence et l'intégrité entre les différentes tables de la base de données.

### Problèmes identifiés et résolus

1. **Incohérence des formats** :
   - Problème : Variantes de casse (majuscules/minuscules) et formats pour les types d'exercices et niveaux de difficulté
   - Solution : Normalisation systématique dans les fonctions de soumission et traitement des données

2. **Doublons dans les statistiques** :
   - Problème : Entrées multiples pour les mêmes combinaisons type/difficulté dans la table `user_stats`
   - Solution : Mécanisme de fusion des statistiques et prévention des doublons futurs

### Mécanismes de normalisation

1. **Normalisation à la source** :
   - Fonctions `normalize_exercise_type()` et `normalize_difficulty()` dans le traitement des données
   - Conversion des valeurs en minuscules et mappage vers des formats standardisés

2. **Correction des données existantes** :
   - Script `fix_database.py` pour identifier et corriger les inconsistances
   - Interface de ligne de commande pour l'exécution de corrections manuelles

3. **Validation continue** :
   - Tests automatisés (`test_normalization.py`) pour vérifier l'intégrité des données
   - Fonction `check_data_normalization()` dans `db_check.py` pour des audits réguliers

### Structure des tables et normalisation

```
# Table exercises
id INTEGER PRIMARY KEY
title TEXT
question TEXT
correct_answer TEXT
choices TEXT (JSON)
explanation TEXT
exercise_type TEXT       # Normalisé: 'addition', 'subtraction', 'multiplication', 'division'
difficulty TEXT          # Normalisé: 'easy', 'medium', 'hard'
is_archived INTEGER
created_at TIMESTAMP

# Table results
id INTEGER PRIMARY KEY
exercise_id INTEGER
is_correct INTEGER
time_spent REAL
attempt_date TIMESTAMP
FOREIGN KEY (exercise_id) REFERENCES exercises(id)

# Table user_stats
id INTEGER PRIMARY KEY
exercise_type TEXT       # Normalisé: 'addition', 'subtraction', 'multiplication', 'division'
difficulty TEXT          # Normalisé: 'easy', 'medium', 'hard'
total_attempts INTEGER
correct_attempts INTEGER
last_updated TIMESTAMP
```

Cette normalisation garantit que les statistiques dans le tableau de bord sont correctement mises à jour après la complétion des exercices et que les données restent cohérentes à travers l'application.

Pour plus de détails sur les problèmes résolus et les mécanismes de normalisation, consultez [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md).

Pour les détails complets sur les plans futurs, voir [docs/PROJECT_STATUS.md](PROJECT_STATUS.md) et [docs/IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).

---
*Dernière mise à jour: 22/07/2024* 