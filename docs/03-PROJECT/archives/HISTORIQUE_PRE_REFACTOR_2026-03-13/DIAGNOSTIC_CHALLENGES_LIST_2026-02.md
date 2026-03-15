# Diagnostic — GET /api/challenges (liste vide, random_offset, filtres)

**Date :** 22/02/2026  
**Contexte :** Refactor `ORDER BY RANDOM()` → `random_offset` provoque `items=[]` alors que `total=38`. Inquiétude sur la qualité du code et la maintenabilité.

---

## 1. Flux complet (route → handler → DB)

```
GET /api/challenges
    ↓
server/routes/challenges.py  →  endpoint=get_challenges_list
    ↓
server/handlers/challenge_handlers.py  →  get_challenges_list()
    ↓
parse_challenge_list_params(request)  →  p (ListChallengesQuery)
    ↓
app.utils.db_utils.db_session()  →  context manager async
    ↓
EnhancedServerAdapter.get_db_session()  →  SessionLocal()
    ↓
app.db.base.SessionLocal  →  bind=app.db.base.engine
    ↓
challenge_service.list_challenges(db, ...)
challenge_service.count_challenges(db, ...)
```

---

## 2. Point de défaillance #1 : Double engine (fixtures vs app)

| Composant | Engine | Session | Source |
|-----------|--------|---------|--------|
| **Fixtures** (logic_challenge_db) | `get_test_engine()` | `sessionmaker(bind=test_engine)` | `tests/conftest.py` L214-216 |
| **Handlers** (get_challenges_list) | `app.db.base.engine` | `SessionLocal()` | `app/db/base.py` L29, `enhanced_server_adapter.py` L100 |

**Problème :** Deux instances d’engine distinctes, deux pools de connexions, même URL (`TEST_DATABASE_URL` quand `TESTING=true`). En théorie, les deux voient la même base. En pratique, l’unification des engines (fixtures → `app.db.base.engine`) a empiré les résultats (6 échecs au lieu de 5).

**Hypothèse :** Ordre d’initialisation, isolation des transactions ou cleanup des fixtures qui interagissent mal avec le pool de l’app.

---

## 3. Point de défaillance #2 : Incohérence challenge_type (API vs DB)

**Flux du filtre `challenge_type` :**

1. Requête : `GET /api/challenges?challenge_type=sequence`
2. `parse_challenge_list_params` : `normalize_challenge_type("sequence")` → `"SEQUENCE"`
3. `list_challenges(db, challenge_type="SEQUENCE", ...)` et `count_challenges(db, challenge_type="SEQUENCE", ...)`
4. Filtre : `LogicChallenge.challenge_type == "SEQUENCE"`

**Modèle :** `LogicChallengeType` (str, PyEnum) avec `SEQUENCE = "sequence"` (minuscule).

**DB :** `get_enum_value(LogicChallengeType, LogicChallengeType.SEQUENCE)` → `"SEQUENCE"` (via `ENUM_MAPPING`). Les fixtures créent des challenges avec `challenge_type="SEQUENCE"` (majuscule).

**Risque :** SQLAlchemy compare `Enum(LogicChallengeType)` avec la chaîne `"SEQUENCE"`. Selon la config de l’enum (valeurs Python vs PostgreSQL), la comparaison peut échouer ou réussir selon l’environnement.

**Symptôme :** `test_filter_challenges_by_type` échoue avec `0 défis sur 37 total` — la liste est vide alors que le count retourne 37. Soit le filtre de la liste est plus strict, soit le count ne filtre pas correctement.

---

## 4. Point de défaillance #3 : random_offset et état de la query

**Avec `func.random()` (actuel) :**
```python
query.order_by(func.random()).offset(offset).limit(limit).all()
```
→ Une seule requête, pas de `count()` préalable.

**Avec `random_offset` (problématique) :**
```python
total = query.count()
max_offset_val = max(0, total - limit - offset)
random_offset_val = random.randint(0, max_offset_val) if max_offset_val > 0 else 0
return query.order_by(LogicChallenge.id).offset(offset + random_offset_val).limit(limit).all()
```

**Problème possible :** En SQLAlchemy 1.x, `query.count()` peut modifier l’état interne de la query ou de la session. Une requête de count séparée (comme dans `exercise_service`) évite ce risque.

**Observation :** `exercise_service` utilise `random_offset` sans problème. Différence principale : les tests d’exercices n’utilisent pas la même fixture `logic_challenge_db` ni le même chemin (list vs count).

---

## 5. Synthèse des causes probables

| # | Cause | Impact | Priorité |
|---|-------|--------|----------|
| 1 | Double engine (fixtures vs app) | Isolation, visibilité des données | Haute |
| 2 | Incohérence `challenge_type` (SEQUENCE vs sequence) | Filtre `challenge_type` inopérant ou incohérent | Haute |
| 3 | Effet de bord de `query.count()` sur la query | Liste vide avec `random_offset` | Moyenne |

---

## 6. Recommandations

### 6.1 Court terme (stabiliser les tests)

1. **Unifier les engines en test**  
   Faire utiliser `app.db.base.engine` par la fixture `db_session` au lieu de `get_test_engine()`. Si des régressions apparaissent, analyser l’ordre des fixtures et le cleanup.

2. **Corriger le filtre `challenge_type`**  
   S’assurer que la valeur passée à `list_challenges` et `count_challenges` correspond exactement au format attendu par l’enum (vérifier `LogicChallengeType` et les valeurs PostgreSQL).

3. **Adapter `random_offset`**  
   Utiliser une requête de count dédiée (comme dans `exercise_service`) plutôt que `query.count()` sur la même query.

### 6.2 Moyen terme (qualité)

1. **Session unique en test**  
   Un seul point d’entrée pour la session DB en mode test (fixtures + handlers).

2. **Tests de non-régression**  
   Ajouter un test qui vérifie que `list_challenges` et `count_challenges` renvoient des résultats cohérents pour chaque combinaison de filtres.

3. **Documentation des enums**  
   Documenter clairement le mapping API → DB pour `challenge_type` et les autres enums.

---

## 7. Fichiers clés

| Fichier | Rôle |
|---------|------|
| `tests/conftest.py` L214-216 | Fixture `db_session` avec `get_test_engine()` |
| `app/db/base.py` | Engine et `SessionLocal` de l’app |
| `app/utils/db_utils.py` | `db_session()` utilisé par les handlers |
| `app/services/enhanced_server_adapter.py` L92-100 | `get_db_session()` → `SessionLocal()` |
| `app/services/challenge_service.py` L322-355 | `list_challenges`, `count_challenges` |
| `app/core/constants.py` L508-540 | `normalize_challenge_type` |
| `app/utils/db_helpers.py` L58-68 | `ENUM_MAPPING` pour `LogicChallengeType` |
| `app/models/logic_challenge.py` L23-37 | `LogicChallengeType` (valeurs minuscules) |
