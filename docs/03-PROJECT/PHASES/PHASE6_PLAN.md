# 📋 PHASE 6 - NOMMAGE ET LISIBILITÉ

**Date** : 20 novembre 2025  
**Approche** : ✅ Méticuleuse 100% + Hyper-structurée  
**Durée** : 2 jours  
**Statut** : 🚀 EN PRÉPARATION

---

## 🎯 OBJECTIF

Améliorer la lisibilité et la maintenabilité du code à 100% :
1. Variables cryptiques → Noms explicites
2. Docstrings manquantes → Documentation complète
3. TODO/FIXME → Nettoyés ou transformés en issues
4. Linting → 100% passant

---

## 📊 MÉTRIQUES CIBLES

| Métrique | Avant | Cible | Validation |
|----------|-------|-------|------------|
| **Variables 1-2 char** | ~200 | 0 | `grep -rn "\b[a-z]\{1,2\}\s*=" app/ server/` |
| **Docstrings** | ~40% | 100% | Script analyse |
| **TODO/FIXME** | ~25 | 0 | `grep -rn "TODO\|FIXME"` |
| **flake8** | ~50 warnings | 0 | `flake8 app/ server/` |
| **black** | Non formaté | 100% | `black --check` |
| **isort** | Non trié | 100% | `isort --check` |

---

## 📝 ÉTAPES

### ÉTAPE 0 : Analyse (30 min)
```bash
# Lancer l'analyse automatique
python scripts/phase6_analyse_variables.py
python scripts/phase6_analyse_docstrings.py
python scripts/phase6_analyse_todos.py
```

### ÉTAPE 1 : Renommage variables (6-8h)
**Catégories prioritaires** :
1. Exceptions (`e` → `{specific}_error`)
2. Sessions DB (`db` → `db_session`)
3. Indices (`idx` → `{entity}_index`)
4. Connexions (`conn` → `db_connection`)
5. Résultats SQL (`row` → `{entity}_row`)

**Ordre de traitement** :
1. `app/core/` (fondations)
2. `app/services/` (services - CRITIQUE)
3. `app/api/endpoints/` (endpoints)
4. `server/` (backend Starlette)
5. `tests/` (après prod)

### ÉTAPE 2 : Docstrings (4-6h)
**Format** : Google Style

**Priorités** :
1. ⭐ **HAUTE** : Endpoints API
2. ⭐ **HAUTE** : Services
3. **MOYENNE** : Modèles
4. **MOYENNE** : Handlers
5. **BASSE** : Fonctions internes

### ÉTAPE 3 : TODO/FIXME (2h)
Pour chaque TODO/FIXME :
- **Obsolète** → Supprimer
- **Valide** → Issue GitHub
- **Critique** → Corriger immédiatement

### ÉTAPE 4 : Linting (3-4h)
```bash
# Auto-fix
black app/ server/
isort app/ server/ --profile black

# Validation
flake8 app/ server/
pylint app/ server/
```

### ÉTAPE 5 : Validation (1h)
- [x] 0 variables cryptiques
- [x] 100% docstrings
- [x] 0 TODO/FIXME
- [x] Linting 100%
- [x] Tests passent
- [x] CI/CD OK

---

## 🚀 LANCEMENT

**Script d'analyse créé** : `scripts/phase6_analyse_variables.py`

**Commande pour démarrer** :
```bash
# Analyse complète
python scripts/phase6_analyse_variables.py

# Voir le plan complet
cat docs/phases/PHASE6_PLAN.md
```

---

**Prêt à démarrer la Phase 6 !** 🎉

