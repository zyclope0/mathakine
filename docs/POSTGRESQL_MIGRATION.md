# Guide de migration vers PostgreSQL

Ce document détaille le processus de migration de SQLite vers PostgreSQL pour l'application Mathakine, ainsi que les avantages et considérations associés.

## Pourquoi migrer vers PostgreSQL ?

### Avantages de PostgreSQL par rapport à SQLite

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

## Prérequis

- PostgreSQL 12+ installé (version 17 recommandée)
- Accès administrateur à PostgreSQL
- Python 3.8+ avec les bibliothèques `psycopg2` et `python-dotenv`

## Processus de migration

### 1. Configuration de l'environnement

Assurez-vous que les variables d'environnement suivantes sont correctement définies dans votre fichier `.env` :

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mathakine_test
```

### 2. Exécution de la migration

La migration peut être effectuée en utilisant le script fourni :

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
4. Migration des données avec conversion des types si nécessaire
5. Vérification de l'intégrité des données migrées

### 3. Basculement entre les bases de données

Vous pouvez facilement basculer entre SQLite et PostgreSQL en utilisant l'utilitaire fourni :

```bash
# Sous Windows
scripts/toggle_database.bat

# Sous Linux/MacOS
python scripts/toggle_database.py [sqlite|postgres]
```

## Considérations importantes

### Différences de types de données

PostgreSQL est plus strict que SQLite concernant les types de données. Certaines conversions sont effectuées automatiquement :

| SQLite          | PostgreSQL     | Notes |
|-----------------|----------------|-------|
| INTEGER         | INTEGER        | |
| REAL            | DOUBLE PRECISION | |
| TEXT            | TEXT           | |
| BLOB            | BYTEA          | |
| INTEGER (0/1)   | BOOLEAN        | Pour les colonnes is_*, has_*, active, enabled |

### Performances et optimisation

Pour de meilleures performances avec PostgreSQL :

1. **Indexation** : Ajoutez des index sur les colonnes fréquemment recherchées
2. **Configuration** : Ajustez les paramètres PostgreSQL selon votre charge de travail
3. **Maintenance** : Exécutez régulièrement `VACUUM` et `ANALYZE` pour optimiser les performances

## Validation post-migration

Après la migration, effectuez les vérifications suivantes :

1. Comparaison des décomptes de lignes entre SQLite et PostgreSQL
2. Test des fonctionnalités de l'application avec PostgreSQL
3. Vérification des performances sous charge

## Retour à SQLite (si nécessaire)

En cas de besoin, vous pouvez revenir à SQLite en utilisant l'utilitaire de basculement :

```bash
scripts/toggle_database.bat  # puis sélectionnez SQLite
```

---

*Note : La migration vers PostgreSQL est recommandée pour les environnements de production et de test avancé, tandis que SQLite reste pratique pour le développement local.* 