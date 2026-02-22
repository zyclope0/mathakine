# Analyse : migration du DDL init_database vers Alembic

**Date :** 22/02/2026  
**Objectif :** Évaluer l’ampleur de la tâche pour déplacer tout le DDL de `init_database()` vers Alembic.

---

## 1. État actuel

### 1.1 `init_database()` (server/database.py)

Depuis la refactor du 22/02/2026, `init_database()` utilise déjà SQLAlchemy (plus de psycopg2 direct pour l’init). Il exécute :

| Élément | Source | Détail |
|--------|--------|--------|
| Table `exercises` | `ExerciseQueries.CREATE_TABLE` | CREATE TABLE IF NOT EXISTS + 6 index (idx_exercises_*) |
| Colonne `ai_generated` | ALTER TABLE | ADD COLUMN IF NOT EXISTS |
| UPDATE `ai_generated` | logique métier | Marque les exercices avec préfixe IA |
| Table `results` | `ResultQueries.CREATE_TABLE` | CREATE TABLE IF NOT EXISTS |
| Table `user_stats` | SQL inline | CREATE TABLE IF NOT EXISTS |

**Dépendance :** `exercises.creator_id` → `users(id)` → la table `users` doit exister avant.

### 1.2 Alembic (migrations/versions/)

**Chaîne de migrations :**
```
initial_snapshot (pass) 
  → 20250513_baseline (pass) 
  → 20250107_add_enum_values 
  → 20260205_add_missing_tables_and_indexes (user_sessions, notifications)
  → 20260206_1530_add_exercises_indexes
  → 20260206_1600_add_exercises_missing_indexes
  → ... (≈16 migrations)
```

**Contenu des migrations :**
- Ne créent pas les tables `exercises`, `results`, `user_stats`
- Ajoutent des index sur `exercises` (ix_exercises_*, parfois doublons avec init_database)
- Créent `user_sessions`, `notifications`, `settings`, etc.

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

## 5. Références

- `server/database.py` : `init_database()`
- `app/db/queries.py` : `ExerciseQueries.CREATE_TABLE`, `ResultQueries.CREATE_TABLE`
- `migrations/env.py` : `tables_to_keep`
- `scripts/start_render.sh` : ordre alembic → startup
