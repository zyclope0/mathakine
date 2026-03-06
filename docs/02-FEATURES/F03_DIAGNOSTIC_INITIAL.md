# F03 — Test de diagnostic initial (IRT adaptatif)

> **Référence technique** — Contexte complet pour développeurs et prompts IA  
> **Date :** 06/03/2026  
> **Statut :** Implémenté (04/03/2026)  
> **Source :** [ROADMAP_FONCTIONNALITES §F03](ROADMAP_FONCTIONNALITES.md), [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md)

---

## 1. Vue d'ensemble

F03 évalue le niveau réel de l'utilisateur en 4 opérations arithmétiques via un algorithme IRT (Item Response Theory) simplifié. Les scores alimentent immédiatement les recommandations et l'adaptation dynamique (F05).

**Fondements scientifiques :**
- Hattie (2009) — Formative assessment (d = 0.90)
- Sweller (1988) — Alignement difficulté/compétence prévient la surcharge cognitive
- Black & Wiliam (1998) — Assessment for learning

---

## 2. Algorithme IRT adaptatif

```
1. Commencer au niveau médian (PADAWAN, ordinal 1)
2. Réponse correcte → niveau +1 (plafonné à GRAND_MAITRE)
3. Réponse incorrecte → niveau -1 (plancher à INITIE)
4. Arrêt d'un type : 2 erreurs consécutives au MÊME niveau → niveau établi
5. Session complète : tous les types terminés OU 10 questions atteintes
```

**Constantes** (dans `app/services/diagnostic_service.py`) :
- `DIAGNOSTIC_TYPES` : addition, soustraction, multiplication, division
- `STARTING_LEVEL_ORDINAL` : 1 (PADAWAN)
- `MAX_QUESTIONS` : 10
- `CONSECUTIVE_ERRORS_TO_STOP` : 2

**État de session** : `DiagnosticSessionState` — dict sérialisable en JSON, stocké côté frontend entre chaque question (backend stateless entre les appels).

---

## 3. Données — Table `diagnostic_results`

| Colonne | Type | Description |
|---------|------|-------------|
| `user_id` | int | Utilisateur |
| `triggered_from` | str | "onboarding" \| "settings" |
| `scores` | JSONB | `{"addition": {"level": 2, "difficulty": "CHEVALIER", "correct": 4, "total": 5}, ...}` |
| `questions_asked` | int | Nombre de questions posées |
| `duration_seconds` | int \| null | Durée totale |
| `completed_at` | timestamp | Date de fin |

**Mapping ordinal → difficulté** : 0=INITIE, 1=PADAWAN, 2=CHEVALIER, 3=MAITRE, 4=GRAND_MAITRE

**Validité** : 30 jours (`_IRT_MAX_AGE_DAYS` dans `adaptive_difficulty_service`). Au-delà, F05 utilise progression ou profil.

---

## 4. Endpoints API

| Méthode | Endpoint | Auth | Body / Params |
|---------|----------|------|---------------|
| GET | `/api/diagnostic/status` | Oui | — |
| POST | `/api/diagnostic/start` | Oui | `{triggered_from?: "onboarding"\|"settings"}` |
| POST | `/api/diagnostic/question` | Oui | `{session}` |
| POST | `/api/diagnostic/answer` | Oui | `{session, exercise_type, user_answer, correct_answer}` |
| POST | `/api/diagnostic/complete` | Oui | `{session, duration_seconds?}` |

Voir [API_QUICK_REFERENCE.md § Diagnostic](API_QUICK_REFERENCE.md).

---

## 5. Fichiers impliqués

| Rôle | Fichier |
|------|---------|
| Service métier | `app/services/diagnostic_service.py` |
| Modèle | `app/models/diagnostic_result.py` |
| Handlers | `server/handlers/diagnostic_handlers.py` |
| Routes | `server/routes/diagnostic.py` |
| Migration | `migrations/versions/20260304_diagnostic.py` |
| Frontend page | `frontend/app/diagnostic/page.tsx` |
| Hook scores IRT | `frontend/hooks/useIrtScores.ts` |
| Settings (section) | Section "Évaluation de niveau" dans Settings |

---

## 6. Intégration avec F05

Le service `adaptive_difficulty_service` utilise `diagnostic_service.get_latest_score()` comme **priorité 1** de sa cascade. Si un diagnostic valide (< 30 jours) existe pour le type demandé, la difficulté est dérivée directement des scores IRT.

---

## 7. Backlog F03-suite

| Lacune | Statut |
|--------|--------|
| Dashboard `has_completed` — message "ton niveau a été établi" | ⏳ Backlog (partiellement couvert par `LevelEstablishedWidget` F05) |
| Génération IA (`/api/ai/generate`) ignore le diagnostic | ⏳ Backlog |

---

## 8. Tests

- `tests/unit/services/test_diagnostic_service.py`
- `tests/integration/test_diagnostic_api.py`
