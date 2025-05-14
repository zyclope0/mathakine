# Guide complet du système de base de données - Mathakine

Ce document décrit l'architecture de base de données complète du projet Mathakine, incluant les environnements supportés, les migrations avec Alembic et les procédures de sécurité.

## 1. Vue d'ensemble du système de base de données

Le projet Mathakine supporte deux systèmes de gestion de base de données :
- **SQLite** - Utilisé principalement pour le développement local
- **PostgreSQL** - Recommandé pour les environnements de production

### Architecture de la base de données

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  Modèles SQLAlchemy  ◄──┼──►  Base de données  ◄──┼──►  Migrations Alembic │
│                   │     │                   │     │                   │
└───────────────────┘     └───────────────────┘     └───────────────────┘
```

### Tables principales

- **users** - Utilisateurs de l'application
- **exercises** - Exercices mathématiques
- **attempts** - Tentatives de résolution
- **progress** - Progression des utilisateurs
- **logic_challenges** - Défis logiques 

### Tables héritées (à préserver)

- **results** - Résultats d'exercices (héritage)
- **statistics** - Statistiques par session (héritage)
- **user_stats** - Statistiques utilisateur (héritage)
- **schema_version** - Version du schéma (héritage)

## 2. Migration vers PostgreSQL

### 2.1 Pourquoi migrer vers PostgreSQL ?

#### Avantages par rapport à SQLite

1. **Performances accrues**
   - Meilleure gestion des requêtes complexes
   - Optimisation pour les grands volumes de données
   - Index plus sophistiqués

2. **Concurrence**
   - Support des accès simultanés multiples
   - Verrouillage au niveau des lignes (et non de la base entière)
   - Idéal pour les applications multi-utilisateurs

3. **Scalabilité**
   - Capacité à gérer de grands volumes de données
   - Support de la réplication et du clustering
   - Performances maintenues avec la croissance de l'application

4. **Fonctionnalités avancées**
   - Transactions ACID complètes
   - Contraintes d'intégrité avancées
   - Types de données riches
   - Procédures stockées et triggers

### 2.2 Prérequis

- PostgreSQL 12+ installé (version 17 recommandée)
- Accès administrateur à PostgreSQL
- Python 3.8+ avec les bibliothèques `psycopg2` et `python-dotenv`

### 2.3 Processus de migration

#### Configuration de l'environnement

Configurez les variables d'environnement dans `.env` :

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mathakine_test
```

#### Exécution de la migration

```bash
# Sous Windows
scripts/migrate_to_postgres.bat

# Sous Linux/MacOS
python scripts/migrate_to_postgres.py
```

Le script effectue les opérations suivantes :
1. Connexion à la base de données SQLite existante
2. Création de la base de données PostgreSQL si elle n'existe pas
3. Conversion du schéma SQLite vers PostgreSQL
4. Migration des données avec conversion des types
5. Vérification de l'intégrité des données migrées

#### Basculement entre les bases de données

Utilitaire pour basculer facilement entre SQLite et PostgreSQL :

```bash
python scripts/toggle_database.py [sqlite|postgres]
```

### 2.4 Migration sur Render (Hébergement cloud)

#### Création d'une base PostgreSQL sur Render

1. Dans le tableau de bord Render, créez une nouvelle base de données PostgreSQL
2. Configurez selon vos besoins (nom, région, plan)
3. Notez les informations de connexion fournies

#### Migration des données vers Render

```bash
python scripts/migrate_to_render.py
```

#### Configuration du service web Render

Ajoutez la variable d'environnement `DATABASE_URL` avec la valeur de l'URL externe fournie par Render.

### 2.5 Considérations importantes

#### Différences de types de données

PostgreSQL est plus strict que SQLite concernant les types :

| SQLite          | PostgreSQL     | Notes |
|-----------------|----------------|-------|
| INTEGER         | INTEGER        | |
| REAL            | DOUBLE PRECISION | |
| TEXT            | TEXT           | |
| BLOB            | BYTEA          | |
| INTEGER (0/1)   | BOOLEAN        | Pour les colonnes is_*, has_*, active, enabled |

#### Optimisation des performances

Pour de meilleures performances avec PostgreSQL :

```bash
# Outil d'optimisation automatique
python scripts/optimize_postgres.py
```

Ce script :
- Crée des index sur les colonnes fréquemment utilisées
- Exécute VACUUM ANALYZE sur toutes les tables
- Génère un rapport d'état de la base de données

## 3. Gestion des migrations avec Alembic

### 3.1 Configuration d'Alembic

La structure des migrations est organisée comme suit :

- `alembic.ini` - Configuration principale
- `migrations/` - Dossier contenant tous les scripts
  - `env.py` - Logique de migration personnalisée
  - `versions/` - Versions de migrations
    - `initial_snapshot.py` - État initial
    - `20250513_baseline.py` - Point de départ

### 3.2 Commandes Alembic principales

#### Afficher l'état actuel
```bash
alembic current  # Version actuelle
alembic history  # Historique des migrations
```

#### Marquer comme migrée
```bash
alembic stamp head  # Marquer la base comme à jour
```

#### Créer une nouvelle migration
```bash
alembic revision --autogenerate -m "Description de la migration"
```

#### Appliquer/annuler des migrations
```bash
alembic upgrade head            # Appliquer toutes les migrations
alembic upgrade <revision_id>   # Appliquer jusqu'à une révision spécifique
alembic downgrade -1            # Annuler la dernière migration
alembic downgrade <revision_id> # Revenir à une révision spécifique
```

### 3.3 Protection des tables héritées

Le fichier `migrations/env.py` est configuré pour protéger les tables héritées contre la suppression accidentelle lors des migrations autogénérées :

```python
def include_object(object, name, type_, reflected, compare_to):
    # Protéger les tables héritées
    if type_ == "table" and name in ["results", "statistics", "user_stats", "schema_version"]:
        if object.metadata.requires_fallback:
            return False
    return True
```

## 4. Sécurité des migrations en production

### 4.1 Risques liés aux migrations en production

1. **Perte de données** : Opérations comme `DROP TABLE`, `DROP COLUMN`, etc.
2. **Temps d'arrêt** : Migrations longues bloquant des tables
3. **Incompatibilité** : Entre base de données et code
4. **Erreurs irréversibles** : Sans sauvegarde adéquate

### 4.2 Outils de sécurité fournis

#### Script de sauvegarde
```bash
python scripts/alembic_backup.py
```
- Crée une sauvegarde complète avec horodatage
- Vérifie l'intégrité automatiquement
- Gère les anciennes sauvegardes (5 plus récentes)

#### Script de migration sécurisée
```bash
python scripts/safe_migrate.py [--force] [--dry-run] [--sql] [--target REVISION]
```
- Analyse les migrations pour détecter les opérations risquées
- Effectue une sauvegarde automatique
- Journalise en détail chaque étape
- Protège les tables critiques

#### Script de restauration
```bash
python scripts/restore_from_backup.py [--backup INDEX] [--force] [--reset-to REVISION]
```
- Liste les sauvegardes disponibles
- Restaure complètement la base de données
- Permet de réinitialiser à une révision spécifique

### 4.3 Procédure sécurisée pour les migrations en production

#### Étape 1 : Préparation
1. **Relire la migration** pour vérifier les changements
2. **Créer une sauvegarde manuelle**
3. **Simuler la migration** avec `--dry-run`
4. **Générer le SQL** pour vérification avec `--sql`

#### Étape 2 : Application
1. **Planifier une fenêtre de maintenance** si possible
2. **Appliquer la migration** avec `safe_migrate.py`
3. **Vérifier les journaux**

#### Étape 3 : Vérification
1. **Vérifier l'état d'Alembic** avec `alembic current`
2. **Valider la cohérence** en exécutant des tests

#### Étape 4 : En cas d'erreur
1. **Restaurer la sauvegarde**
2. **Identifier le problème** dans les logs
3. **Corriger la migration** et recommencer

### 4.4 Opérations considérées comme risquées

Le script `safe_migrate.py` détecte automatiquement :
- Suppression de table (`op.drop_table`)
- Suppression de colonne (`op.drop_column`)
- Modification de colonne pour ajouter `NOT NULL` 
- Renommage de table (`op.rename_table`)
- Instructions SQL `DROP`, `TRUNCATE` ou `ALTER TABLE ... DROP CONSTRAINT`

## 5. Résolution des problèmes courants

### 5.1 Problèmes avec PostgreSQL

| Problème | Cause possible | Solution |
|----------|----------------|----------|
| Échec de connexion | Mauvaises informations de connexion | Vérifier les variables d'environnement |
| Erreur de permission | Droits insuffisants | `GRANT ALL PRIVILEGES ON DATABASE mathakine_test TO utilisateur` |
| Tables manquantes | Schéma incorrect | Réexécuter les migrations |

### 5.2 Problèmes avec Alembic

| Problème | Cause possible | Solution |
|----------|----------------|----------|
| "Target database is not up to date" | Base non synchronisée | `alembic stamp head` |
| "Can't locate revision" | Révision inexistante | Vérifier les valeurs `revision` et `down_revision` |
| "Multiple head revisions" | Branches multiples | `alembic merge <revision1> <revision2>` |
| Tables manquantes après migration | Mauvaise protection | Restaurer sauvegarde et vérifier `include_object` |

### 5.3 Test de connexion

```bash
# Test de connexion SQLite
python check_db_connection.py sqlite

# Test de connexion PostgreSQL
python check_db_connection.py postgres

# Test de connexion Render
python test_render_connection.py
```

## 6. Bonnes pratiques

1. **Toujours vérifier les migrations générées** avant application
2. **Faire des sauvegardes régulières**
3. **Tester les migrations** dans un environnement de développement
4. **Éviter de modifier les migrations existantes** déjà appliquées
5. **Créer manuellement les migrations** pour les tables sensibles
6. **Jamais de migration directe en production** - Utiliser `safe_migrate.py`
7. **Migrer graduellement** - Privilégier plusieurs petites migrations
8. **Documenter les migrations complexes** par des commentaires détaillés

## 7. Workflow de développement recommandé

1. Développer localement avec SQLite pour la rapidité
2. Tester régulièrement avec PostgreSQL pour garantir la compatibilité
3. Utiliser Alembic pour toutes les modifications de schéma
4. Vérifier manuellement toutes les migrations autogénérées
5. En production, utiliser uniquement les scripts sécurisés

---

*Ce document consolide les informations de POSTGRESQL_MIGRATION.md, ALEMBIC.md et ALEMBIC_SÉCURITÉ.md* 