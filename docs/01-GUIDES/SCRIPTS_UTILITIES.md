# Guide — Scripts utilitaires (scripts/)

> Scope : Mathakine — répertoire `scripts/`
> Updated : 2026-03-27

---

## Objectif

Ce guide documente les 17 scripts du répertoire `scripts/`. Chaque script est conçu pour une opération ponctuelle de maintenance, de diagnostic ou de préparation de données. Ils ne font pas partie du pipeline applicatif.

> ⚠️ La plupart de ces scripts modifient des données. Toujours exécuter sur une base de développement ou avec un snapshot préalable en production.

---

## Prérequis

```bash
# Virtualenv activé
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate      # Windows

# Variable d'environnement base cible
export DATABASE_URL=postgresql://user:pass@host:5432/mathakine
# ou pour cibler la base de test
export DATABASE_URL=postgresql://user:pass@host:5432/mathakine_test
```

---

## Catégorie 1 — Données et contenu

### `audit_fix_exercises_db.py` (13.6 KB)

Audit et correction des exercices en base : détecte les exercices avec des champs manquants, des titres incohérents ou des tags invalides, et applique des corrections normalisées.

```bash
# Mode diagnostic uniquement (pas de modification)
python scripts/audit_fix_exercises_db.py --dry-run

# Mode correction
python scripts/audit_fix_exercises_db.py --fix
```

Sortie attendue :
```
[AUDIT] Exercises scanned: 1247
[FIX] Missing difficulty_level fixed: 14
[FIX] Invalid tags normalized: 8
[OK] Audit complete.
```

---

### `audit_fix_challenges_db.py` (9.6 KB)

Même principe que `audit_fix_exercises_db.py` pour les défis logiques.

```bash
python scripts/audit_fix_challenges_db.py --dry-run
python scripts/audit_fix_challenges_db.py --fix
```

---

### `cleanup_test_data_production.py` (19 KB)

Supprime les données de test créées accidentellement en production (users avec email `@test.`, exercices avec titre contenant `[TEST]`, etc.).

```bash
# Toujours dry-run d'abord
python scripts/cleanup_test_data_production.py --dry-run

# Confirmation requise en production
python scripts/cleanup_test_data_production.py --confirm
```

> ⚠️ **Production only.** Ne jamais exécuter sur la base de développement (supprime des données réelles au pattern).

---

### `cleanup_edtech_aberrant_data.py` (3.9 KB)

Supprime les événements edtech aberrants (durées négatives, scores hors bornes, user_id NULL) de la table `edtech_events`.

```bash
python scripts/cleanup_edtech_aberrant_data.py
```

---

### `truncate_edtech_events.py` (1.4 KB)

Vide la table `edtech_events` (TRUNCATE). Utilisé pour reset d'environnement de test ou allègement d'une base de développement gonflée.

```bash
python scripts/truncate_edtech_events.py
```

> ⚠️ Irréversible sans snapshot. Réservé aux environnements non-production ou après export.

---

### `add_pinned_badges_to_test_db.py` (2 KB)

Insère les badges épinglés (pinned) dans la base de test pour les tests manuels de l'interface badges.

```bash
python scripts/add_pinned_badges_to_test_db.py
```

---

### `ensure_dev_users.py` (3.4 KB)

Crée les utilisateurs de développement standard (ObiWan admin, Luke utilisateur) s'ils n'existent pas. Idempotent.

```bash
python scripts/ensure_dev_users.py
```

Sortie attendue :
```
[OK] Admin user ObiWan: already exists
[OK] Regular user Luke: created
```

---

### `reset_onboarding_all_users.py` (961 bytes)

Remet le flag `onboarding_completed` à `False` pour tous les utilisateurs. Utilisé pour tester le flux d'onboarding.

```bash
python scripts/reset_onboarding_all_users.py
```

---

## Catégorie 2 — Base de données

### `backup_db.py` (1.6 KB)

Effectue un `pg_dump` de la base et sauvegarde le fichier localement avec timestamp.

```bash
python scripts/backup_db.py
# Fichier généré : backups/mathakine_YYYYMMDD_HHMMSS.sql
```

---

### `backup_db.ps1` (PowerShell, 2.6 KB)

Version PowerShell du script de backup, pour exécution planifiée sous Windows.

```powershell
.\scripts\backup_db.ps1
```

---

### `check_local_db.py` (3.7 KB)

Vérifie l'état de la base locale : connexion, version PostgreSQL, nombre d'enregistrements par table principale, état des migrations Alembic.

```bash
python scripts/check_local_db.py
```

Sortie attendue :
```
[DB] PostgreSQL 15.x connected
[MIGRATION] Current: 20260327_add_content_difficulty_tier (head)
[TABLES] users: 12, exercises: 1247, logic_challenges: 438
```

---

### `verify_user_deletion.py` (3.9 KB)

Vérifie qu'une suppression d'utilisateur a bien déclenché toutes les cascades (exercices, défis, progress, point_events, badges).

```bash
python scripts/verify_user_deletion.py --user-id <uuid>
```

---

## Catégorie 3 — Maintenance et correctifs

### `fix_recommendations_schema_for_tests.py` (4.4 KB)

Corrige le schéma de la table `recommendations` pour le rendre compatible avec les fixtures de tests (ajout de colonnes manquantes, normalisation des valeurs NULL).

```bash
python scripts/fix_recommendations_schema_for_tests.py
```

Usage : après une migration incomplète en environnement de test, ou pour synchroniser une base de test ancienne.

---

### `debug_challenge_list.py` (996 bytes)

Affiche la liste des défis en base avec leurs métadonnées clés (type, difficulté, is_active, is_archived). Diagnostic rapide.

```bash
python scripts/debug_challenge_list.py
```

---

## Catégorie 4 — Tests et validation

### `test_backend_local.py` (5.8 KB)

Lance une batterie de requêtes HTTP contre le backend local pour valider les endpoints principaux sans passer par pytest. Utile pour un smoke test rapide après démarrage.

```bash
# Backend local requis sur le port configuré
python scripts/test_backend_local.py
```

Sortie attendue :
```
[OK] GET /ready → 200
[OK] POST /api/auth/login → 200
[OK] GET /api/exercises → 200
...
```

---

### `test_sendgrid.py` (2.7 KB)

Envoie un email de test via l'API SendGrid pour valider la configuration email.

```bash
SENDGRID_API_KEY=SG.xxx python scripts/test_sendgrid.py --to test@example.com
```

---

## Catégorie 5 — Déploiement

### `start_render.sh` (849 bytes)

Script de démarrage utilisé par Render (complément ou alternative au `Procfile`). Initialise les variables d'environnement minimales avant de lancer `enhanced_server.py`.

```bash
# Exécution manuelle (debug déploiement)
bash scripts/start_render.sh
```

---

## Référence rapide

| Script | Catégorie | Risque | Idempotent |
|--------|-----------|--------|-----------|
| `audit_fix_exercises_db.py` | Contenu | Moyen | Oui (--dry-run) |
| `audit_fix_challenges_db.py` | Contenu | Moyen | Oui (--dry-run) |
| `cleanup_test_data_production.py` | Contenu | **Élevé** | Oui (--dry-run) |
| `cleanup_edtech_aberrant_data.py` | Contenu | Moyen | Non |
| `truncate_edtech_events.py` | Contenu | **Élevé** | Non |
| `add_pinned_badges_to_test_db.py` | Contenu | Faible | Oui |
| `ensure_dev_users.py` | Contenu | Faible | **Oui** |
| `reset_onboarding_all_users.py` | Contenu | Faible | **Oui** |
| `backup_db.py` | Base | Faible | **Oui** |
| `backup_db.ps1` | Base | Faible | **Oui** |
| `check_local_db.py` | Base | Aucun | **Oui** |
| `verify_user_deletion.py` | Base | Aucun | **Oui** |
| `fix_recommendations_schema_for_tests.py` | Maintenance | Moyen | Non |
| `debug_challenge_list.py` | Maintenance | Aucun | **Oui** |
| `test_backend_local.py` | Tests | Aucun | **Oui** |
| `test_sendgrid.py` | Tests | Aucun | **Oui** |
| `start_render.sh` | Déploiement | Faible | **Oui** |
