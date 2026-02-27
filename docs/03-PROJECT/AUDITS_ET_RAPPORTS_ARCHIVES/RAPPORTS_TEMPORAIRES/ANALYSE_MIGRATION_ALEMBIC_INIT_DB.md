# Analyse : migration du DDL init_database vers Alembic

**Date :** 22/02/2026  
**Objectif :** Évaluer l’ampleur de la tâche pour déplacer tout le DDL de `init_database()` vers Alembic.

---

## Statut (22/02/2026)

| Étape | Statut |
|-------|--------|
| Migration `20260222_add_legacy_tables_exercises_results_userstats.py` | ✅ Créée |
| DDL retiré de `init_database()` (no-op) | ✅ Fait |
| Tests (pytest) | ✅ 404 passent |
| Merge master + push | ✅ Fait |
| Déploiement Render | ✅ Réussi |
| Sanity check prod | ✅ OK (login, exercices, défis, navigation) |
| **Rapport validation** | [VALIDATION_MIGRATION_ALEMBIC_2026-02.md](VALIDATION_MIGRATION_ALEMBIC_2026-02.md) |

---

## 1. État actuel

### 1.1 `init_database()` (server/database.py)

**Depuis 22/02/2026 :** `init_database()` est un no-op (log seulement). Le DDL est dans Alembic (migration 20260222).

| Élément | Source | Détail |
|--------|--------|--------|
| Table `exercises` | `ExerciseQueries.CREATE_TABLE` | CREATE TABLE IF NOT EXISTS + 6 index (idx_exercises_*) |
| Colonne `ai_generated` | ALTER TABLE | ADD COLUMN IF NOT EXISTS |
| UPDATE `ai_generated` | logique métier | Marque les exercices avec préfixe IA |
| Table `results` | `ResultQueries.CREATE_TABLE` | CREATE TABLE IF NOT EXISTS |
| Table `user_stats` | SQL inline | CREATE TABLE IF NOT EXISTS |

**Dépendance :** `exercises.creator_id` → `users(id)` → la table `users` doit exister avant.

### 1.2 Alembic (migrations/versions/)

**Chaîne de migrations (post-migration 22/02) :**
```
... → 20260205_add_missing_tables_and_indexes
  → 20260222_add_legacy_tables (exercises, results, user_stats)
  → 20260206_add_exercises_indexes
  → ... (≈16 migrations) → head
```

**Contenu :** La migration `20260222` crée `exercises`, `results`, `user_stats` + index + `ai_generated`. Les autres migrations créent `user_sessions`, `notifications`, `settings`, etc.

### 1.3 Flux de déploiement (Render, scripts)

1. **Build :** `alembic upgrade head`
2. **Startup :** `python enhanced_server.py` → `init_database()`

L’ordre est bon : Alembic d’abord, puis `init_database()`.

---

## 2. Recensement des chevauchements

| Objet | init_database | Alembic | Risque |
|-------|---------------|---------|--------|
| Table `exercises` | Crée | Non | Aucun chevauchement |
| Index `idx_exercises_*` | 6 index | 20260206_1530, 20260206_1600 (ix_exercises_*) | Noms différents, potentiels doublons fonctionnels |
| Table `results` | Crée | Non (tables_to_keep) | Aucun |
| Table `user_stats` | Crée | Non (tables_to_keep) | Aucun |
| Colonne `ai_generated` | ALTER | Non | Aucun |

**Remarque :** `migrations/env.py` liste `results`, `user_stats` dans `tables_to_keep` pour éviter qu’Alembic les supprime à l’autogenerate, pas pour les créer.

---

## 3. Ampleur de la tâche

### 3.1 Travail à prévoir

| Tâche | Complexité | Remarques |
|-------|------------|-----------|
| Nouvelle migration « init tables legacy » | Moyenne | Créer exercises, results, user_stats avec `IF NOT EXISTS`, idempotent |
| Gérer l’UPDATE `ai_generated` | Faible | Idempotent par définition |
| Aligner les index | Moyenne | Comparer idx_* (init) vs ix_* (Alembic), éviter les doublons |
| Supprimer le DDL de `init_database()` | Faible | Garder un appel vide ou une simple vérification |
| Mise à jour du flux de déploiement | Faible | Déjà `alembic upgrade head` avant startup |

### 3.2 Contraintes et risques

1. **Ordre des migrations**  
   La future migration doit être chaînée après une révision où `users` existe déjà (probablement très tôt dans la chaîne).

2. **Idempotence**  
   Obligatoire : beaucoup de bases ont déjà `exercises`, `results`, `user_stats` via `init_database()`.  
   Utiliser systématiquement `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`.

3. **Doublon d’index**  
   `ExerciseQueries.CREATE_TABLE` définit des `idx_exercises_*` (WHERE is_archived = false).  
   Alembic 20260206_* crée des `ix_exercises_*`. À comparer pour ne pas dupliquer inutilement.

4. **Modèle `Exercise`**  
   `app.models.exercise.Exercise` existe. Vérifier la correspondance colonne par colonne avec la DDL actuelle (creator_id, ai_generated, etc.).

### 3.3 Estimation

| Phase | Durée indicative | Priorité |
|-------|------------------|----------|
| Analyse détaillée des index et des modèles | 1–2 h | Haute |
| Rédaction de la migration idempotente | 2–3 h | Haute |
| Tests sur DB vierge + DB existante | 1–2 h | Haute |
| Suppression du DDL dans `init_database()` | ~30 min | Haute |
| Ajustements et documentation | ~1 h | Moyenne |

**Total :** ~6–9 h selon familiarité avec Alembic.

---

## 4. Recommandation

- La migration est faisable et pertinent pour avoir un seul point d’entrée DDL (Alembic).
- Commencer par une migration dédiée « legacy tables » :
  - créer `exercises` (avec `ai_generated`), `results`, `user_stats`
  - centraliser les index nécessaires
- Une fois validée :
  - retirer le DDL de `init_database()` (ou le réduire à une vérification minimale)
  - documenter le nouveau flux
- Planifier sur 1–2 sprints pour limiter les risques en production.

---

## 6. Préparation avant migration (backup, rollback)

Voir **[PLAN_PREPARATION_MIGRATION_ALEMBIC_DDL.md](PLAN_PREPARATION_MIGRATION_ALEMBIC_DDL.md)** pour :

- Backup BDD (pg_dump)
- Stratégie de rollback
- Checklist pré-migration
- Ordre d’exécution recommandé

---

## 7. Références

- `server/database.py` : `init_database()`
- `app/db/queries.py` : `ExerciseQueries.CREATE_TABLE`, `ResultQueries.CREATE_TABLE`
- `migrations/env.py` : `tables_to_keep`
- `scripts/start_render.sh` : ordre alembic → startup
