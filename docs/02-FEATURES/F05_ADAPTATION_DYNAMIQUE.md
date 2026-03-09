# F05 â€” Adaptation dynamique de difficultÃ©

> **RÃ©fÃ©rence technique** â€” Contexte complet pour dÃ©veloppeurs et prompts IA  
> **Date :** 06/03/2026  
> **Statut :** ImplÃ©mentÃ© (v3.0.0-alpha.3+)  
> **Source :** [ROADMAP_FONCTIONNALITES Â§F05](ROADMAP_FONCTIONNALITES.md), [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md)

---

## 1. Vue d'ensemble

F05 dÃ©termine le niveau de difficultÃ© adaptÃ© Ã  chaque utilisateur et type d'exercice, puis adapte le mode de rÃ©ponse (QCM vs saisie libre) selon le niveau IRT prouvÃ©.

**Fondements scientifiques :**
- Vygotsky (1978) â€” Zone proximale de dÃ©veloppement (ZPD)
- Bjork (1994) â€” Desirable difficulties
- Csikszentmihalyi (1990) â€” Flow (difficultÃ© â‰ˆ compÃ©tence)

---

## 2. Architecture â€” Cascade de rÃ©solution

La difficultÃ© est rÃ©solue par **cascade de prioritÃ©s** dans `app/services/adaptive_difficulty_service.py` :

| PrioritÃ© | Source | Condition | Retourne |
|----------|--------|-----------|----------|
| 1 | **Diagnostic IRT** (F03) | Diagnostic < 30 jours, type Ã©valuÃ© | `age_group` depuis `diagnostic_results.scores` |
| 2 | **Progression temps rÃ©el** | â‰¥ 5 tentatives sur 7 jours (table `progress`) | `age_group` depuis `mastery_level` |
| 3 | **Profil utilisateur** | `preferred_difficulty` ou `grade_level` | `age_group` mappÃ© |
| 4 | **Fallback** | Aucune donnÃ©e | `GROUP_9_11` (PADAWAN) |

**Ajustement temps rÃ©el** (boost/descente) appliquÃ© aprÃ¨s rÃ©solution :
- `completion_rate > 85 %` ET `streak >= 3` â†’ niveau +1
- `completion_rate < 50 %` ET `streak = 0` â†’ niveau -1

---

## 3. DonnÃ©es â€” Table `diagnostic_results`

| Colonne | Type | Description |
|---------|------|-------------|
| `user_id` | int | Utilisateur |
| `completed_at` | timestamp | Date de fin du diagnostic |
| `triggered_from` | str | "onboarding" \| "settings" |
| `questions_asked` | int | Nombre de questions posÃ©es |
| `duration_seconds` | int \| null | DurÃ©e totale |
| `scores` | JSONB | `{"addition": {"level": 2, "difficulty": "CHEVALIER", "correct": 4, "total": 5}, ...}` |

**Types Ã©valuÃ©s par l'IRT :** `addition`, `soustraction`, `multiplication`, `division`.

**ValiditÃ© :** 30 jours (`_IRT_MAX_AGE_DAYS`). Au-delÃ , la cascade passe au niveau 2 (progression) ou 3 (profil).

---

## 4. Mapping `preferred_difficulty`

Le champ `users.preferred_difficulty` stocke **deux formats** (onboarding vs profil) :

| Valeur stockÃ©e | Origine | MappÃ© vers |
|----------------|---------|------------|
| `"adulte"`, `"9-11"`, `"12-14"`, `"15-17"`, `"6-8"` | Onboarding (age_group) | Ordinal 0â€“4 â†’ `age_group` |
| `"GRAND_MAITRE"`, `"MAITRE"`, etc. | Profil (DifficultyLevel) | Idem |

Voir `_PREF_DIFFICULTY_TO_ORDINAL` dans `adaptive_difficulty_service.py`.

---

## 5. Proxys IRT â€” Types non Ã©valuÃ©s

| Type | Proxy | Logique |
|------|-------|---------|
| `MIXTE` | Oui | Minimum des 4 scores de base (protection surcharge) |
| `FRACTIONS` | Oui | Niveau **division** uniquement (conservateur) |
| `GEOMETRIE`, `TEXTE`, `DIVERS` | Non | Cascade profil/fallback |

---

## 6. Mode de rÃ©ponse â€” QCM vs saisie libre

**RÃ¨gle :** Saisie libre uniquement si niveau IRT = **GRAND_MAITRE** pour ce type.

| OÃ¹ | Comment |
|----|---------|
| **Backend** | GÃ©nÃ¨re **toujours** les `choices` (QCM). Le flag `is_open_answer` dans le JSON est un fallback legacy, **ignorÃ©** par le frontend. |
| **Frontend** | `useIrtScores()` â†’ `resolveIsOpenAnswer(exercise_type)` dÃ©cide d'afficher QCM ou input texte selon les scores IRT. |

**Fichiers :**
- `frontend/hooks/useIrtScores.ts` â€” lit `/api/diagnostic/status`, expose `resolveIsOpenAnswer`, `getIrtLevel`, `isIrtCovered`
- `frontend/components/exercises/ExerciseSolver.tsx` â€” `isOpenAnswer = resolveIsOpenAnswer(exercise.exercise_type)`
- `frontend/components/exercises/ExerciseModal.tsx` â€” idem

**Types sans IRT :** Fallback sur `user.preferred_difficulty` (ex. `"adulte"` â†’ saisie libre).

---

## 7. Fichiers impliquÃ©s

### Backend
| Fichier | RÃ´le |
|---------|------|
| `app/services/adaptive_difficulty_service.py` | Cascade, `resolve_adaptive_difficulty()`, `resolve_irt_level()`, proxys |
| `app/services/diagnostic_service.py` | `get_latest_score()`, format scores IRT |
| `server/handlers/exercise_handlers.py` | Branchement `?adaptive=true` (dÃ©faut), appelle `resolve_adaptive_difficulty` |
| `app/utils/exercise_generator_helpers.py` | Distracteurs QCM calibres par niveau (source de verite) |
| `app/models/diagnostic_result.py` | ModÃ¨le `DiagnosticResult` |

### Frontend
| Fichier | RÃ´le |
|---------|------|
| `frontend/hooks/useIrtScores.ts` | Hook â€” scores IRT, `resolveIsOpenAnswer`, `getIrtLevel` |
| `frontend/components/exercises/ExerciseSolver.tsx` | RÃ©solution exercice (page dÃ©diÃ©e) |
| `frontend/components/exercises/ExerciseModal.tsx` | RÃ©solution exercice (modal) |
| `frontend/components/dashboard/LevelEstablishedWidget.tsx` | Widget "Ton Profil MathÃ©matique" (badges par type) |

### API
| Endpoint | RÃ´le |
|----------|------|
| `GET /api/diagnostic/status` | Retourne `{has_completed, latest: {scores, completed_at, ...}}` â€” consommÃ© par `useIrtScores` |
| `POST /api/exercises/generate` | Param `adaptive=true` (dÃ©faut) â€” rÃ©solution adaptative |
| `POST /api/exercises/generate` | Param `age_group` explicite â€” dÃ©sactive l'adaptation |

---

## 8. Backlog F05-suite

| Item | Statut |
|------|--------|
| `/api/ai/generate` â€” adaptation IRT pour gÃ©nÃ©ration IA (SSE) | â³ Backlog |
| Seuils boost/descente configurables via admin | â³ Backlog |
| [F05-B1] Saisie libre par taux de rÃ©ussite rÃ©el (â‰¥90% sur 5 tentatives) | â³ Backlog |

---

## 9. Tests

- `tests/unit/test_adaptive_difficulty_service.py` â€” 54 tests (cascade, proxys, mapping `preferred_difficulty`, `resolve_irt_level`)

