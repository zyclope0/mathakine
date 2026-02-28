# Plan Clean Code & Contrats de données (DTO)

**Date :** 28/02/2026  
**Référence :** Audit Backend Alpha 2 — Clean code & lisibilité ; Étape 2 Normaliser les contrats  
**Objectif :** Formaliser les entrées/sorties API, éliminer la duplication, différencier les erreurs.  
**Principe :** Étapes committables/testables séparément.

---

## 1. Contexte et constats

### 1.1 Constats audit (Clean code & lisibilité)

| Constat | Impact | Priorité |
|---------|--------|----------|
| Niveaux d'abstraction hétérogènes dans une même fonction | Lisibilité réduite, tests difficiles | P1 |
| Duplication count/select dans les requêtes listes | Maintenance, risque d'incohérence | P1 |
| `except Exception` omniprésent | Erreurs fonctionnelles noyées | P2 |
| Typage permissif (`Any`, `Dict[str, Any]`) | Pas de contrat explicite, bugs à l'exécution | P1 |

### 1.2 Action liée (Étape 2 — Normaliser les contrats)

1. Créer des DTO stricts (Pydantic) : entrées HTTP, sorties API
2. Éliminer `Dict[str, Any]` dans les signatures critiques
3. Standardiser les conversions enum/string dans une couche de mapping dédiée

---

## 2. Plan par priorité — Étapes formelles

### Priorité 1 — Étapes 1 à 3 (Quick wins + fondations)

| Étape | Intitulé | Objectif | Livrables | Critère de validation |
|-------|----------|----------|-----------|------------------------|
| **1.1** | Facteur commun count/select | Éliminer duplication des filtres dans les requêtes listes | Helper `_build_exercise_list_filters(query, params)` ou équivalent ; réutilisation pour count et select | Tests unitaires existants + 1 test de non-régression sur format réponse |
| **1.2** | DTO entrée SubmitAnswer | Contrat explicite pour POST /api/exercises/{id}/attempt | `SubmitAnswerRequest` (Pydantic) avec `answer`, `time_spent` ; validation dans handler | Test API avec payload invalide → 422 |
| **1.3** | DTO sortie ExerciseList | Contrat explicite pour GET /api/exercises | `ExerciseListResponse`, `ExerciseListItem` (Pydantic) ; mapping ORM → Pydantic dans service ou handler | Test structure JSON retournée |

### Priorité 2 — Étapes 4 à 6 (Contrats étendus)

| Étape | Intitulé | Objectif | Livrables | Critère de validation |
|-------|----------|----------|-----------|------------------------|
| **2.1** | DTO ListExercisesQuery | Contrat entrée GET /api/exercises | `ListExercisesQuery` (skip, limit, exercise_type, age_group, search, order, hide_completed) | Handler parse → construit Query ; tests |
| **2.2** | DTO ListChallengesQuery / ChallengeListResponse | Aligner challenges sur le même pattern | `ListChallengesQuery`, `ChallengeListResponse` | Idem |
| **2.3** | Mapping enum/string centralisé | Une seule couche pour normalisation | `app/utils/enum_mapping.py` ou extension `app/core/constants` ; fonctions `to_api_enum()`, `from_api_enum()` | Aucune conversion inline dans handlers |

### Priorité 3 — Étapes 7 à 9 (Robustesse erreurs)

| Étape | Intitulé | Objectif | Livrables | Critère de validation |
|-------|----------|----------|-----------|------------------------|
| **3.1** | Exceptions métier typées | Différencier erreurs fonctionnelles vs techniques | `ExerciseNotFoundError`, `InvalidAnswerError`, etc. ; mapping vers codes HTTP dans handler | Tests unitaires service lèvent bonne exception |
| **3.2** | Remplacer `except Exception` dans handlers critiques | Garder catch-all uniquement au boundary | submit_answer, get_exercise : catch ciblé ; log + 500 seulement si vraiment inattendu | Pas de régression fonctionnelle |
| **3.3** | Réduire `Dict[str, Any]` dans signatures | Typage explicite progressif | `get_exercises_list_for_api` → retour `ExerciseListResponse` ; `submit_answer_result` → retour type dédié | mypy ou vérification manuelle des appels |

### Priorité 4 — Étapes 10+ (Extensions)

| Étape | Intitulé | Objectif |
|-------|----------|----------|
| **4.1** | DTO endpoints admin | `AdminUsersQuery`, `AdminExercisesQuery`, etc. |
| **4.2** | Documenter contrats dans docstrings / OpenAPI | Schémas référencés dans routes |
| **4.3** | Audit mypy sur modules critiques | Typer retours des services |

---

## 3. Ordre d'exécution recommandé

```
1.1 (duplication count/select)     → commit 1
1.2 (SubmitAnswerRequest)          → commit 2
1.3 (ExerciseListResponse)         → commit 3
2.1 (ListExercisesQuery)           → commit 4
2.2 (challenges DTOs)             → commit 5
2.3 (enum mapping)                 → commit 6
3.1 (exceptions métier)             → commit 7
3.2 (except ciblé)                  → commit 8
3.3 (signatures typées)             → commit 9
```

Chaque commit est **indépendant** et **testable** (pytest + tests manuels si nécessaire).

---

## 4. Structure cible des DTO (référence)

```
app/schemas/
  api/
    exercise/
      requests.py   # SubmitAnswerRequest, ListExercisesQuery
      responses.py # ExerciseDetailResponse, ExerciseListResponse, ExerciseListItem
    challenge/
      requests.py  # ListChallengesQuery, SubmitChallengeAnswerRequest
      responses.py # ChallengeListResponse, ChallengeListItem
  common/
    paginated.py   # PaginatedResponse[T] générique
```

Ou, plus léger : extension des `app/schemas/exercise.py` existants avec des classes dédiées API.

---

## 5. Historique des modifications

| Date | Étape | Détail |
|------|-------|--------|
| 28/02/2026 | — | Création du plan |
| 28/02/2026 | 2.1 | `ListExercisesQuery`, `parse_exercise_list_params` ; handler `get_exercises_list` refactoré |
| 28/02/2026 | 2.2 | `ListChallengesQuery` (alias `ChallengeListParams`), `ChallengeListResponse`, `ChallengeListItem` ; handler `get_challenges_list` utilise DTOs |
| 28/02/2026 | 2.3 | `app/utils/enum_mapping.py` : `*_from_api`, `*_to_api` pour exercise_type, difficulty, challenge_type, age_group ; tests unitaires |
| 22/02/2026 | 3.1 | `app/exceptions.py` : `ExerciseNotFoundError`, `ExerciseSubmitError` ; service lève exceptions métier ; handlers catch ciblé |
| 22/02/2026 | 3.2 | Handlers submit_answer, get_exercise : catch `(ExerciseNotFoundError, ExerciseSubmitError)` au lieu de `except Exception` |
| 22/02/2026 | 3.3 | `SubmitAnswerResponse` (Pydantic) ; `submit_answer_result` retourne type dédié ; tests mis à jour |
