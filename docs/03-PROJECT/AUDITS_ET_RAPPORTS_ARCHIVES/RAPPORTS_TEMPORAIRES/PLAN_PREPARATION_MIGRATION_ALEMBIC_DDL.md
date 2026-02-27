# Plan de préparation sécurisée — Migration DDL init_database vers Alembic

**Date :** 22/02/2026  
**Objectif :** Sécuriser au maximum l’opération avant de démarrer la migration (Point 3).  
**Référence :** [ANALYSE_MIGRATION_ALEMBIC_INIT_DB.md](ANALYSE_MIGRATION_ALEMBIC_INIT_DB.md)  
**Statut :** Réalisé 22/02/2026

---

## Vue d’ensemble

| Phase | Action | Quand |
|-------|--------|-------|
| 1 | Backup BDD | **Avant toute modification** |
| 2 | Branche Git dédiée | Avant le premier changement de code |
| 3 | Pré-requis et checklist | Validation avant migration |
| 4 | Exécution migration | Étapes ordonnées |
| 5 | Rollback | Si problème détecté |

---

## 1. Backup de la base de données

### 1.1 Environnements à backuper

| Environnement | Base | Méthode |
|---------------|------|---------|
| **Render (test/prod)** | mathakine_test_gii8, mathakine | Dashboard Render → Database → **Export** → Create export (rétention 7 jours) |
| **Local dev** | `mathakine` ou `test_mathakine` | **BDD via Docker** → `docker exec` (voir § 1.2b) ou `pg_dump` si client installé |

### 1.2 Commande pg_dump (PostgreSQL, client installé localement)

```powershell
# Windows PowerShell — backup local
$env:PGPASSWORD = "postgres"
pg_dump -h localhost -U postgres -d mathakine -F c -f backups/mathakine_backup_$(Get-Date -Format 'yyyyMMdd_HHmm').dump

# Ou en SQL plain (plus lisible, plus gros fichier)
pg_dump -h localhost -U postgres -d mathakine -F p -f backups/mathakine_backup_$(Get-Date -Format 'yyyyMMdd_HHmm').sql
```

```bash
# Linux / Git Bash — backup avec DATABASE_URL
pg_dump "$DATABASE_URL" -F c -f backups/mathakine_backup_$(date +%Y%m%d_%H%M).dump
```

### 1.2b Backup local quand la BDD tourne via Docker

Si PostgreSQL est dans un conteneur (ex. `pg-mathakine`), `pg_dump` n'est pas forcément installé sur l'hôte. Utiliser `docker exec` :

```powershell
# Lister les conteneurs Postgres
docker ps --filter "ancestor=postgres"

# Backup — remplacer CONTAINER et DB si besoin (conteneur local type: pg-test, pg-mathakine)
$ts = Get-Date -Format 'yyyyMMdd_HHmm'
cmd /c "docker exec pg-test pg_dump -U postgres -d test_mathakine -F c > backups\mathakine_backup_$ts.dump"
```

*Note :* En local, la BDD s'appelle souvent `test_mathakine` ; le conteneur peut être `pg-test` ou `pg-mathakine`.

**Convention :** stocker les dumps dans `backups/` (déjà dans `.gitignore` — ne pas committer).

### 1.3 Restauration (rollback BDD)

```powershell
# Restaurer un dump custom (-F c)
pg_restore -h localhost -U postgres -d mathakine -c backups/mathakine_backup_YYYYMMDD_HHMM.dump

# Ou SQL plain
psql -h localhost -U postgres -d mathakine -f backups/mathakine_backup_YYYYMMDD_HHMM.sql
```

`-c` = drop objets avant création (attention en prod). Sans `-c`, les données peuvent s’ajouter aux existantes.

---

## 2. Rollback facile — Stratégie multi-niveaux

### Niveau 1 : Rollback BDD seul (si migration Alembic pose problème)

1. Arrêter le serveur.
2. Restaurer le backup : `pg_restore` ou `psql -f`.
3. Remettre la révision Alembic à l’état précédent :
   ```bash
   alembic downgrade -1   # ou alembic downgrade <revision_avant>
   ```
4. Redémarrer le serveur.

### Niveau 2 : Rollback code + BDD (si nouvelle migration + nouveau `init_database`)

1. `git revert` du commit de migration (ou `git checkout` de la branche précédente).
2. Redéployer l’ancienne version (qui appelle encore `init_database()` avec DDL).
3. Si la migration Alembic a déjà été appliquée : `alembic downgrade -1`.
4. Optionnel : restaurer le backup BDD si l’état est incohérent.

### Niveau 3 : Branche Git dédiée (recommandé)

```bash
# Avant de commencer
git checkout -b feat/alembic-legacy-tables-ddl
git push -u origin feat/alembic-legacy-tables-ddl
```

En cas de problème : revenir sur `master` et continuer à utiliser l’ancienne version.

---

## 3. Checklist pré-migration

À valider **avant** de créer la première migration :

- [x] **Backup BDD effectué** — Render : Export dashboard ; Local : `.\scripts\backup_db.ps1` (docker exec pg-test)
- [x] **Branche Git dédiée** — `feat/alembic-legacy-tables-ddl` créée et poussée sur origin
- [x] **Révision Alembic** — Chaîne 20260205 → 20260222 → 20260206 → head
- [x] **Tests** — `pytest tests/` passent
- [x] **Merge master + déploiement Render** — 22/02/2026

### Vérification rapide état BDD

```sql
-- À lancer en psql ou outil graphique
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('exercises', 'results', 'user_stats', 'users');
```

---

## 4. Ordre d’exécution recommandé

| Ordre | Étape | Détail |
|-------|-------|--------|
| 1 | Backup | `pg_dump` de la base concernée |
| 2 | Branche | `git checkout -b feat/alembic-legacy-tables-ddl` |
| 3 | Analyse index | Comparer `ExerciseQueries.CREATE_TABLE` vs migrations 20260206_* |
| 4 | Création migration | Nouvelle migration idempotente (`IF NOT EXISTS`) |
| 5 | Test DB vierge | Nouvelle base → `alembic upgrade head` → vérifier tables |
| 6 | Test DB existante | Base avec données → `alembic upgrade head` → pas de régression |
| 7 | Modifier `init_database()` | Retirer le DDL, garder éventuellement une vérification minimale |
| 8 | Tests | `pytest tests/` |
| 9 | Commit + PR | Revue avant merge |
| 10 | Déploiement test | Sur environnement de staging/test |
| 11 | Déploiement prod | Après validation sur test |

---

## 5. Récapitulatif des commandes utiles

```bash
# Backup
pg_dump "$DATABASE_URL" -F c -f backups/mathakine_backup_$(date +%Y%m%d_%H%M).dump

# État Alembic
alembic current
alembic history -r current:head

# Downgrade (si besoin)
alembic downgrade -1

# Restauration BDD
pg_restore -d "$DATABASE_URL" -c backups/mathakine_backup_YYYYMMDD_HHMM.dump
```

---

## 6. Script de backup (optionnel)

Créer `scripts/backup_db.sh` (ou `.ps1` sous Windows) :

```bash
#!/bin/bash
set -e
mkdir -p backups
TIMESTAMP=$(date +%Y%m%d_%H%M)
DUMP_FILE="backups/mathakine_backup_${TIMESTAMP}.dump"
echo "Backup vers $DUMP_FILE ..."
pg_dump "${DATABASE_URL}" -F c -f "$DUMP_FILE"
echo "✅ Backup terminé: $DUMP_FILE"
```

L’exécuter avant chaque étape sensible.
