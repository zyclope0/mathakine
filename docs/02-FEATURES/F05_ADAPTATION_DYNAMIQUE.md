# F05 — Adaptation dynamique de difficulté

> **Référence technique** — Contexte complet pour développeurs et prompts IA  
> **Date :** 06/03/2026  
> **Statut :** Implémenté (v3.0.0-alpha.3+)  
> **Source :** [ROADMAP_FONCTIONNALITES §F05](ROADMAP_FONCTIONNALITES.md), [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md)

---

## 1. Vue d'ensemble

F05 détermine le niveau de difficulté adapté à chaque utilisateur et type d'exercice, puis adapte le mode de réponse (QCM vs saisie libre) selon le niveau IRT prouvé.

**Fondements scientifiques :**
- Vygotsky (1978) — Zone proximale de développement (ZPD)
- Bjork (1994) — Desirable difficulties
- Csikszentmihalyi (1990) — Flow (difficulté ≈ compétence)

---

## 2. Architecture — Cascade de résolution

La difficulté est résolue par **cascade de priorités** dans `app/services/adaptive_difficulty_service.py` :

| Priorité | Source | Condition | Retourne |
|----------|--------|-----------|----------|
| 1 | **Diagnostic IRT** (F03) | Diagnostic < 30 jours, type évalué | `age_group` depuis `diagnostic_results.scores` |
| 2 | **Progression temps réel** | ≥ 5 tentatives sur 7 jours (table `progress`) | `age_group` depuis `mastery_level` |
| 3 | **Profil utilisateur** | `preferred_difficulty` ou `grade_level` | `age_group` mappé |
| 4 | **Fallback** | Aucune donnée | `GROUP_9_11` (PADAWAN) |

**Ajustement temps réel** (boost/descente) appliqué après résolution :
- `completion_rate > 85 %` ET `streak >= 3` → niveau +1
- `completion_rate < 50 %` ET `streak = 0` → niveau -1

---

## 3. Données — Table `diagnostic_results`

| Colonne | Type | Description |
|---------|------|-------------|
| `user_id` | int | Utilisateur |
| `completed_at` | timestamp | Date de fin du diagnostic |
| `triggered_from` | str | "onboarding" \| "settings" |
| `questions_asked` | int | Nombre de questions posées |
| `duration_seconds` | int \| null | Durée totale |
| `scores` | JSONB | `{"addition": {"level": 2, "difficulty": "CHEVALIER", "correct": 4, "total": 5}, ...}` |

**Types évalués par l'IRT :** `addition`, `soustraction`, `multiplication`, `division`.

**Validité :** 30 jours (`_IRT_MAX_AGE_DAYS`). Au-delà, la cascade passe au niveau 2 (progression) ou 3 (profil).

---

## 4. Mapping `preferred_difficulty`

Le champ `users.preferred_difficulty` stocke **deux formats** (onboarding vs profil) :

| Valeur stockée | Origine | Mappé vers |
|----------------|---------|------------|
| `"adulte"`, `"9-11"`, `"12-14"`, `"15-17"`, `"6-8"` | Onboarding (age_group) | Ordinal 0–4 → `age_group` |
| `"GRAND_MAITRE"`, `"MAITRE"`, etc. | Profil (DifficultyLevel) | Idem |

Voir `_PREF_DIFFICULTY_TO_ORDINAL` dans `adaptive_difficulty_service.py`.

---

## 5. Proxys IRT — Types non évalués

| Type | Proxy | Logique |
|------|-------|---------|
| `MIXTE` | Oui | Minimum des 4 scores de base (protection surcharge) |
| `FRACTIONS` | Oui | Niveau **division** uniquement (conservateur) |
| `GEOMETRIE`, `TEXTE`, `DIVERS` | Non | Cascade profil/fallback |

---

## 6. Mode de réponse — QCM vs saisie libre

**Règle :** Saisie libre uniquement si niveau IRT = **GRAND_MAITRE** pour ce type.

| Où | Comment |
|----|---------|
| **Backend** | Génère **toujours** les `choices` (QCM). Le flag `is_open_answer` dans le JSON est un fallback legacy, **ignoré** par le frontend. |
| **Frontend** | `useIrtScores()` → `resolveIsOpenAnswer(exercise_type)` décide d'afficher QCM ou input texte selon les scores IRT. |

**Fichiers :**
- `frontend/hooks/useIrtScores.ts` — lit `/api/diagnostic/status`, expose `resolveIsOpenAnswer`, `getIrtLevel`, `isIrtCovered`
- `frontend/components/exercises/ExerciseSolver.tsx` — `isOpenAnswer = resolveIsOpenAnswer(exercise.exercise_type)`
- `frontend/components/exercises/ExerciseModal.tsx` — idem

**Types sans IRT :** Fallback sur `user.preferred_difficulty` (ex. `"adulte"` → saisie libre).

---

## 7. Fichiers impliqués

### Backend
| Fichier | Rôle |
|---------|------|
| `app/services/adaptive_difficulty_service.py` | Cascade, `resolve_adaptive_difficulty()`, `resolve_irt_level()`, proxys |
| `app/services/diagnostic_service.py` | `get_latest_score()`, format scores IRT |
| `server/handlers/exercise_handlers.py` | Branchement `?adaptive=true` (défaut), appelle `resolve_adaptive_difficulty` |
| `server/exercise_generator_helpers.py` | Distracteurs QCM calibrés par niveau |
| `app/models/diagnostic_result.py` | Modèle `DiagnosticResult` |

### Frontend
| Fichier | Rôle |
|---------|------|
| `frontend/hooks/useIrtScores.ts` | Hook — scores IRT, `resolveIsOpenAnswer`, `getIrtLevel` |
| `frontend/components/exercises/ExerciseSolver.tsx` | Résolution exercice (page dédiée) |
| `frontend/components/exercises/ExerciseModal.tsx` | Résolution exercice (modal) |
| `frontend/components/dashboard/LevelEstablishedWidget.tsx` | Widget "Ton Profil Mathématique" (badges par type) |

### API
| Endpoint | Rôle |
|----------|------|
| `GET /api/diagnostic/status` | Retourne `{has_completed, latest: {scores, completed_at, ...}}` — consommé par `useIrtScores` |
| `POST /api/exercises/generate` | Param `adaptive=true` (défaut) — résolution adaptative |
| `POST /api/exercises/generate` | Param `age_group` explicite — désactive l'adaptation |

---

## 8. Backlog F05-suite

| Item | Statut |
|------|--------|
| `/api/ai/generate` — adaptation IRT pour génération IA (SSE) | ⏳ Backlog |
| Seuils boost/descente configurables via admin | ⏳ Backlog |
| [F05-B1] Saisie libre par taux de réussite réel (≥90% sur 5 tentatives) | ⏳ Backlog |

---

## 9. Tests

- `tests/unit/test_adaptive_difficulty_service.py` — 54 tests (cascade, proxys, mapping `preferred_difficulty`, `resolve_irt_level`)
