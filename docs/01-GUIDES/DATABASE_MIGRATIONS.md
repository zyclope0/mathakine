# Runbook — Migrations base de données (Alembic)

> Scope : Mathakine backend — PostgreSQL + Alembic
> Updated : 2026-03-27

---

## Objectif

Ce runbook couvre le cycle complet de gestion des migrations Alembic : création, application, vérification et rollback, en développement et en production.

---

## Prérequis

| Condition | Vérification |
|-----------|-------------|
| Virtualenv activé | `which python` → chemin `.venv/` |
| `DATABASE_URL` ou `TEST_DATABASE_URL` défini | `echo $DATABASE_URL` |
| Dépendances installées | `pip show alembic` |
| Base accessible | `python -c "from app.core.db import engine; print(engine.url)"` |

Convention de nommage des fichiers de migration :

```
YYYYMMDD_description_courte.py
ex. : 20260327_add_content_difficulty_tier.py
```

---

## 1. Vérifier l'état courant

```bash
# Révision HEAD actuelle de la base
alembic current

# Historique complet des révisions
alembic history --verbose

# Différence entre HEAD DB et HEAD code
alembic check
```

Sortie attendue (base à jour) :

```
INFO  [alembic.runtime.migration] Running on postgresql://...
20260327_add_content_difficulty_tier (head)
```

---

## 2. Créer une nouvelle migration

```bash
# Migration auto-générée (comparer modèles SQLAlchemy vs schéma DB actuel)
alembic revision --autogenerate -m "description_courte"

# Migration manuelle (contenu vide, à remplir)
alembic revision -m "description_courte"
```

Le fichier généré apparaît dans `migrations/versions/`. **Toujours inspecter le fichier avant application** : les migrations auto-générées peuvent contenir des faux positifs (index non gérés, colonnes de vue, etc.).

Convention de renommage après génération :

```bash
# Le fichier généré a un hash aléatoire : le renommer selon la convention projet
mv migrations/versions/<hash>_description.py migrations/versions/YYYYMMDD_description.py
```

---

## 3. Appliquer les migrations

```bash
# Appliquer jusqu'au HEAD (toutes les migrations en attente)
alembic upgrade head

# Appliquer une révision spécifique
alembic upgrade 20260327_add_content_difficulty_tier

# Appliquer +N révisions depuis l'état actuel
alembic upgrade +2
```

Sortie attendue :

```
INFO  [alembic.runtime.migration] Running upgrade <prev> -> <target>, description
```

---

## 4. Rollback (downgrade)

```bash
# Reculer d'une révision
alembic downgrade -1

# Reculer jusqu'à une révision spécifique
alembic downgrade 20260321_add_point_events_ledger

# Revenir à l'état vide (DANGEREUX — supprime toutes les tables gérées par Alembic)
alembic downgrade base
```

> ⚠️ `downgrade base` en production supprime le schéma complet. Ne jamais exécuter sans snapshot DB préalable.

---

## 5. Procédure de déploiement production (Render)

La migration est exécutée automatiquement par la `buildCommand` dans `render.yaml` :

```yaml
buildCommand: pip install -r requirements.txt && alembic upgrade head
```

Le build Render échoue et interrompt le déploiement si `alembic upgrade head` retourne un code d'erreur non nul. Le service précédent reste actif (déploiement atomique Render).

**Vérification post-déploiement :**

```bash
# Via Render Shell ou connexion directe à la DB prod
alembic current
# Attendu : <dernière révision> (head)
```

---

## 6. Rollback en production

En cas de déploiement raté nécessitant un rollback DB :

```bash
# 1. Identifier la révision cible (révision stable précédente)
alembic history | grep -A1 "$(alembic current | grep -v INFO)"

# 2. Rollback
alembic downgrade -1

# 3. Vérifier
alembic current

# 4. Redéployer le commit précédent (via Render dashboard : Manual Deploy → commit antérieur)
```

> Si la migration modifie des colonnes sans `downgrade` inverse implémenté (common pattern), le rollback DB est impossible sans restauration snapshot. Toujours implémenter `downgrade()` dans les migrations de production.

---

## 7. Troubleshooting

### `alembic.util.exc.CommandError: Can't locate revision identified by '<hash>'`

La base contient un hash de révision inconnu du code (migration orpheline ou conflit de branche).

```bash
# Identifier la révision ghost
alembic current

# Forcer l'état de la table alembic_version
python -c "
from app.core.db import engine
with engine.connect() as conn:
    conn.execute('UPDATE alembic_version SET version_num = \'<revision_cible>\'')
    conn.commit()
"
```

### `sqlalchemy.exc.ProgrammingError: column already exists`

Migration déjà appliquée partiellement. Inspecter `alembic_version` et corriger manuellement ou créer une migration de correction.

### Migration appliquée en CI mais échoue en prod

Cause la plus fréquente : SQLite (CI) vs PostgreSQL (prod). Les migrations utilisant `server_default`, `op.execute()` SQL brut ou des types PostgreSQL-specifiques (ex. `UUID`, `JSONB`) peuvent passer en SQLite mais échouer en PostgreSQL.

Vérification locale avec PostgreSQL :

```bash
TEST_DATABASE_URL=postgresql://... alembic upgrade head
```

### `Target database is not up to date`

```bash
alembic upgrade head
```

---

## 8. Référence rapide

| Commande | Effet |
|----------|-------|
| `alembic current` | Révision courante de la DB |
| `alembic history` | Historique des révisions |
| `alembic check` | Migrations en attente |
| `alembic upgrade head` | Appliquer tout |
| `alembic upgrade +1` | Appliquer une révision |
| `alembic downgrade -1` | Reculer d'une révision |
| `alembic revision --autogenerate -m "desc"` | Générer depuis les modèles |
| `alembic revision -m "desc"` | Migration vide manuelle |

---

## 9. Répertoire des migrations actives

Localisation : `migrations/versions/`

| Fichier | Contenu |
|---------|---------|
| `initial_snapshot.py` | Baseline schéma initial (2025-05-13) |
| `20260321_add_point_events_ledger.py` | Ledger gamification points |
| `20260322_ai_eval_harness_persistence.py` | Persistance evaluation harness IA |
| `20260326_add_users_age_group.py` | Colonne `age_group` table `users` (F42) |
| `20260327_add_content_difficulty_tier.py` | Colonne `difficulty_tier` exercises + logic_challenges (F42) |

Liste complète : `ls migrations/versions/*.py | sort`
