# Guide de sécurité pour les migrations Alembic en production

Ce document décrit les bonnes pratiques et procédures pour gérer les migrations Alembic en production de manière sécurisée dans le projet Mathakine.

## Risques liés aux migrations en production

Les migrations de base de données en production présentent plusieurs risques :

1. **Perte de données** : Les opérations comme `DROP TABLE`, `DROP COLUMN`, ou les modifications de type de données peuvent entraîner une perte irréversible de données.

2. **Temps d'arrêt** : Les migrations longues peuvent bloquer des tables et provoquer des temps d'arrêt.

3. **Incompatibilité** : Les migrations peuvent créer des incompatibilités entre la base de données et le code applicatif.

4. **Erreurs irréversibles** : Sans sauvegarde adéquate, certaines erreurs ne peuvent pas être facilement corrigées.

## Outils de sécurité pour les migrations

Le projet Mathakine intègre trois scripts principaux pour sécuriser les migrations Alembic :

### 1. `alembic_backup.py`

Ce script crée une sauvegarde complète de la base de données avant toute migration :

```bash
python scripts/alembic_backup.py
```

Caractéristiques :
- Création d'une sauvegarde complète avec horodatage
- Vérification automatique de l'intégrité de la sauvegarde
- Gestion automatique des anciennes sauvegardes (conservation des 5 plus récentes)
- Vérification de l'espace disque disponible

### 2. `safe_migrate.py`

Ce script est l'outil principal pour appliquer des migrations de manière sécurisée :

```bash
python scripts/safe_migrate.py [--force] [--dry-run] [--sql] [--target REVISION]
```

Options :
- `--dry-run` : Simule la migration sans l'appliquer
- `--force` : Force l'exécution même si des opérations risquées sont détectées
- `--sql` : Génère le SQL sans l'exécuter
- `--target` : Spécifie la révision cible (par défaut: "head")

Fonctionnalités :
- Analyse les migrations à appliquer pour détecter des opérations risquées
- Effectue automatiquement une sauvegarde avant d'appliquer les migrations
- Journalise en détail chaque étape du processus
- Protège les tables critiques contre les suppressions accidentelles

### 3. `restore_from_backup.py`

En cas de problème, ce script permet de restaurer rapidement la base de données :

```bash
python scripts/restore_from_backup.py [--backup INDEX] [--force] [--reset-to REVISION]
```

Options :
- `--backup` : Index de la sauvegarde à restaurer
- `--force` : Restaure sans demander de confirmation
- `--reset-to` : Révision Alembic à définir après la restauration

Fonctionnalités :
- Liste les sauvegardes disponibles avec leurs métadonnées
- Restaure complètement la base de données
- Permet de réinitialiser la table `alembic_version` à une révision spécifique

## Procédure sécurisée pour les migrations en production

Pour appliquer des migrations en production de manière sécurisée, suivez ces étapes :

### Étape 1 : Préparation

1. **Relire la migration** : Vérifiez manuellement que les changements sont corrects en relisant le fichier de migration.

2. **Créer une sauvegarde manuelle** (en plus de celle automatique) :
   ```bash
   python scripts/alembic_backup.py
   ```

3. **Simuler la migration** :
   ```bash
   python scripts/safe_migrate.py --dry-run
   ```

4. **Générer le SQL** pour vérification :
   ```bash
   python scripts/safe_migrate.py --sql
   ```

### Étape 2 : Application

1. **Planifier une fenêtre de maintenance** si possible

2. **Appliquer la migration** :
   ```bash
   python scripts/safe_migrate.py
   ```

3. **Vérifier les journaux** pour s'assurer que tout s'est bien passé

### Étape 3 : Vérification

1. **Vérifier l'état d'Alembic** :
   ```bash
   alembic current
   ```

2. **Valider la cohérence** en exécutant des tests sur l'application

### Étape 4 : En cas d'erreur

Si la migration échoue ou cause des problèmes :

1. **Restaurer la sauvegarde** :
   ```bash
   python scripts/restore_from_backup.py
   ```

2. **Identifier le problème** dans les logs

3. **Corriger la migration** et recommencer le processus

## Tables protégées

Les tables suivantes sont considérées comme critiques et sont spécialement protégées contre les suppressions accidentelles :

- `results`
- `statistics`
- `user_stats`
- `schema_version`
- `exercises`
- `users`
- `attempts`

## Opérations considérées comme risquées

Le script `safe_migrate.py` détecte automatiquement ces opérations :

- Suppression de table (`op.drop_table`)
- Suppression de colonne (`op.drop_column`)
- Modification de colonne pour ajouter `NOT NULL` (`op.alter_column` avec `not_nullable=True`)
- Renommage de table (`op.rename_table`)
- Instructions SQL `DROP`, `TRUNCATE` ou `ALTER TABLE ... DROP CONSTRAINT` directes

## Bonnes pratiques

1. **Jamais de migration directe en production** : Toujours utiliser `safe_migrate.py`

2. **Tester les migrations** dans un environnement de développement ou de test avant la production

3. **Migrer graduellement** : Privilégier plusieurs petites migrations à une seule grosse

4. **Éviter les migrations à risque** aux heures de pointe

5. **Créer manuellement les migrations pour les tables sensibles** plutôt que d'utiliser l'autogénération

6. **Documenter les migrations complexes** avec des commentaires détaillés

7. **Vérifier les modifications manuellement** avant de les appliquer

## Résumé du workflow sécurisé

```
1. Créer une migration → 2. Vérifier et tester → 3. Simuler (--dry-run) → 
4. Sauvegarder → 5. Appliquer prudemment → 6. Vérifier → 7. Valider
```

En cas de problème à n'importe quelle étape : restaurer à partir de la sauvegarde, corriger, et recommencer.

## Responsabilité

Seuls les administrateurs système ou développeurs expérimentés devraient appliquer des migrations en production. Chaque migration doit être planifiée, testée et validée avant d'être appliquée. 