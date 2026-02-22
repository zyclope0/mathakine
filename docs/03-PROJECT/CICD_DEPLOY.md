# CI/CD, smoke test, migrations et rollback

**Dernière mise à jour :** Février 2026  
**Contexte :** CI automatique, déploiement Render, migrations Alembic

---

## 1. CI automatique (push/PR)

Le workflow **CI (Tests + Lint)** (`.github/workflows/tests.yml`) se déclenche sur :

- `push` et `pull_request` vers `main`, `master`, `develop`

### Jobs exécutés

| Job   | Actions                                        |
|-------|-------------------------------------------------|
| test  | Backend : pytest (coverage), flake8, black, isort |
| lint  | Backend : flake8, black, isort                  |
| frontend | TypeScript, ESLint, Vitest, build Next.js     |

**Gate :** Les tests et le lint doivent passer avant merge.

### Lint bloquant

- `flake8` : erreurs critiques uniquement (`E9,F63,F7,F82`)
- `black` : vérification formatage
- `isort` : vérification tri des imports

Corriger en local avant de pousser :

```bash
black app/ server/
isort app/ server/
```

---

## 2. Smoke test post-déploiement

Render effectue un **health check** à chaque déploiement.

### Backend

| Paramètre    | Valeur   | Rôle                                   |
|-------------|----------|----------------------------------------|
| healthCheckPath | `/health` | Render appelle `GET /health` pour valider le déploiement |

Si `/health` ne répond pas 2xx, Render considère le déploiement comme échoué et ne bascule pas le trafic.

### Test manuel

```bash
# Backend
curl -s https://mathakine-backend.onrender.com/health

# Frontend (page principale)
curl -s -o /dev/null -w "%{http_code}" https://mathakine-frontend.onrender.com/
```

---

## 3. Migrations (Alembic)

### Déploiement automatique

Le `buildCommand` du backend (render.yaml) exécute :

```bash
pip install -r requirements.txt && alembic upgrade head
```

Les migrations sont appliquées **à chaque build** avant le démarrage du serveur.

### Créer une nouvelle migration

```bash
alembic revision -m "description_courte"
# Éditer migrations/versions/<fichier>.py
alembic upgrade head
```

### Vérifier l'état

```bash
alembic current
alembic history -r current:head
```

---

## 4. Rollback manuel

### 4.1 Rollback code ( Render )

1. **Dashboard Render** → Service (backend ou frontend) → **Deploys**
2. Cliquer sur un déploiement antérieur réussi
3. **Manual Deploy** → **Rollback to this deploy**

### 4.2 Rollback migration Alembic

Si une migration pose problème après déploiement :

1. **Backup BDD** (Recommandé avant toute manipulation)  
   - Render : Dashboard → Database → **Export** → Create export  
   - Voir [PLAN_PREPARATION_MIGRATION_ALEMBIC_DDL.md](PLAN_PREPARATION_MIGRATION_ALEMBIC_DDL.md) (backup local)

2. **Downgrade une révision**
   ```bash
   alembic downgrade -1
   # ou vers une révision spécifique
   alembic downgrade <revision_parente>
   ```

3. **Sur Render** : lancer Alembic depuis un shell (Dashboard → Shell) avec `DATABASE_URL` déjà configuré, ou inclure `alembic downgrade -1` dans un script exécuté manuellement.

### 4.3 Rollback code + BDD

Si le nouveau code dépend de la nouvelle migration :

1. Rollback déploiement Render (ancienne version du code)
2. Downgrade Alembic si la migration a déjà été appliquée : `alembic downgrade -1`
3. Optionnel : restaurer un dump si l’état de la BDD est incohérent (voir PLAN_PREPARATION)

---

## 5. Références

| Doc | Contenu |
|-----|---------|
| [DEPLOYMENT_ENV.md](../01-GUIDES/DEPLOYMENT_ENV.md) | Variables d'environnement, checklist pré-déploiement |
| [PLAN_PREPARATION_MIGRATION_ALEMBIC_DDL.md](PLAN_PREPARATION_MIGRATION_ALEMBIC_DDL.md) | Backup, procédures détaillées rollback BDD |
| [DEPLOIEMENT_2026-02-06.md](AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/DEPLOIEMENT_2026-02-06.md) | Exemple de rapport déploiement |
