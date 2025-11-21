# Guide d'utilisation d'Alembic pour Mathakine

Ce document explique comment utiliser Alembic pour gérer les migrations de base de données dans le projet Mathakine.

## Contexte

Mathakine utilise PostgreSQL comme base de données principale et Alembic pour gérer les migrations. La base de données contient des tables héritées du projet original (results, statistics, user_stats, schema_version) qui doivent être préservées lors des migrations.

## Configuration

- Le fichier `alembic.ini` contient la configuration principale d'Alembic
- Le dossier `migrations` contient les scripts de migration
- Le fichier `migrations/env.py` contient la logique de migration personnalisée
- Le dossier `migrations/versions` contient les versions successives de migrations

## Structure des migrations

Les migrations sont organisées comme suit:

1. `initial_snapshot` - Migration initiale qui documente l'état initial de la base de données
2. `20250513_baseline` - Migration de base qui sert de point de départ pour les migrations futures

## Comment utiliser Alembic

### Initialiser la base de données

La base de données est déjà initialisée et contient les tables nécessaires. Vous n'avez pas besoin de créer de nouvelles tables.

### Marquer la base de données comme migrée

Pour indiquer à Alembic que votre base de données est à jour avec les migrations existantes:

```bash
alembic stamp head
```

### Créer une nouvelle migration

Lorsque vous modifiez les modèles SQLAlchemy, vous devez créer une nouvelle migration:

```bash
alembic revision --autogenerate -m "Description de la migration"
```

Vérifiez ensuite le fichier généré dans `migrations/versions/` pour vous assurer qu'il ne contient pas d'opérations non désirées, comme la suppression des tables héritées.

### Appliquer les migrations

Pour appliquer toutes les migrations non appliquées:

```bash
alembic upgrade head
```

Pour appliquer une migration spécifique:

```bash
alembic upgrade <revision_id>
```

### Annuler une migration

Pour annuler la dernière migration:

```bash
alembic downgrade -1
```

Pour revenir à une migration spécifique:

```bash
alembic downgrade <revision_id>
```

### Vérifier l'état des migrations

Pour voir les migrations appliquées et en attente:

```bash
alembic history
alembic current
```

## Tables héritées à préserver

Les tables suivantes sont des tables héritées qui ne doivent pas être supprimées lors des migrations:

- `results` - Résultats d'exercices
- `statistics` - Statistiques par session
- `user_stats` - Statistiques utilisateur
- `schema_version` - Version du schéma

Le fichier `migrations/env.py` a été configuré pour ignorer ces tables lors de la génération des migrations qui tenteraient de les supprimer.

## Bonnes pratiques

1. **Toujours vérifier les migrations générées** avant de les appliquer, particulièrement pour s'assurer qu'elles ne suppriment pas les tables héritées.

2. **Faire des sauvegardes régulières** de la base de données avant d'appliquer des migrations importantes.

3. **Tester les migrations** dans un environnement de développement avant de les appliquer en production.

4. **Éviter de modifier les migrations existantes** après qu'elles aient été appliquées.

5. Si vous devez ajouter des colonnes aux tables héritées, créez une migration manuelle au lieu d'utiliser l'autogénération:

   ```python
   def upgrade():
       op.add_column('results', sa.Column('new_column', sa.String(), nullable=True))
   
   def downgrade():
       op.drop_column('results', 'new_column')
   ```

## Résolution des problèmes courants

### "Target database is not up to date"

Si vous obtenez cette erreur, cela signifie que la base de données n'est pas synchronisée avec les migrations:

```bash
alembic stamp head
```

### "Can't locate revision identified by..."

Si une migration fait référence à une révision inexistante, vérifiez les valeurs `revision` et `down_revision` dans les fichiers de migration.

### "Multiple head revisions are present"

Si vous avez plusieurs branches de migration, vous devez les fusionner:

```bash
alembic merge <revision1> <revision2>
```

### Tables manquantes après migration

Si des tables disparaissent après une migration, restaurez votre sauvegarde et vérifiez que la fonction `include_object` dans `migrations/env.py` ignore correctement les tables à préserver. 