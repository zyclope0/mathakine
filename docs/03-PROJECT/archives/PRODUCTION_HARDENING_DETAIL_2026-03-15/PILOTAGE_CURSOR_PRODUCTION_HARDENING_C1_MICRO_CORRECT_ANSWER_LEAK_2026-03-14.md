# Micro-lot C1 — Suppression fuite `correct_answer`

> Date: 14/03/2026
> Iteration: C - Production Hardening
> Statut: **terminé**

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `server/handlers/diagnostic_handlers.py` | M - correct_answer retiré de la réponse /question, ajouté à /answer |
| `frontend/hooks/useDiagnostic.ts` | M - correct_answer retiré du type, correctAnswerForFeedback depuis /answer |
| `frontend/components/diagnostic/DiagnosticSolver.tsx` | M - utilise correctAnswerForFeedback au lieu de question.correct_answer |
| `tests/api/test_diagnostic_endpoints.py` | M - tests adaptés, preuve /question n'expose plus correct_answer |

---

## 2. Fichiers runtime modifiés

- `server/handlers/diagnostic_handlers.py`
- `frontend/hooks/useDiagnostic.ts`
- `frontend/components/diagnostic/DiagnosticSolver.tsx`

---

## 3. Fichiers de test modifiés

- `tests/api/test_diagnostic_endpoints.py`

---

## 4. Contrat public `/api/diagnostic/question` après correction

**Avant** : `question` contenait `correct_answer`.

**Après** : `question` ne contient plus `correct_answer`. Champs exposés :
- `exercise_type`, `difficulty`, `level_ordinal`
- `question`, `choices`, `explanation`, `hint`
- `question_number`, `max_questions`, `types_remaining`

---

## 5. Où vit `correct_answer` après correction

- **Dans le state_token signé** : `pending.correct_answer` (jamais exposé au client)
- **Dans la réponse `/answer`** : `correct_answer` exposé uniquement après soumission, pour feedback pédagogique (highlight du bon choix, GrowthMindsetHint)

Le client ne peut plus lire la bonne réponse avant d'avoir répondu.

---

## 6. Ce qui a été prouvé

- `/api/diagnostic/question` n'expose plus `correct_answer` (test `test_diagnostic_question_does_not_expose_correct_answer`)
- La correction backend continue d'utiliser la bonne réponse interne au token (test `test_diagnostic_answer_ignores_client_correct_answer`)
- Flux complet fonctionne sans récupérer correct_answer depuis /question (test `test_diagnostic_full_flow_with_state_token` avec mock)

---

## 7. Ce qui n'a pas été prouvé

- Que `explanation` ou `hint` ne révèlent jamais la solution avant réponse (certaines explications du générateur incluent le résultat ; elles sont affichées après soumission, pas avant)

---

## 8. Résultat run 1

```
8 passed in 8.91s
```

---

## 9. Résultat run 2

```
8 passed in 8.78s
```

---

## 10. Résultat full suite

```
829 passed, 2 skipped in 188.35s
```

---

## 11. Résultat black

```
All done! 257 files would be left unchanged.
```

---

## 12. Résultat isort

```
(no output - vert)
```

---

## 13. Risques résiduels

- `correct_answer` exposé dans `/answer` après soumission — acceptable (feedback pédagogique, pas de triche possible avant réponse)
- `explanation` peut contenir le résultat ; affichée uniquement en phase feedback (après réponse)

---

## 14. GO / NO-GO

**GO** — La bonne réponse n'est plus lisible par le client dans le payload public de `/question`. La fuite est fermée.

---

## Addendum — Recâblage frontend feedback + fix typecheck (14/03/2026)

### Fichiers modifiés

- `frontend/hooks/useDiagnostic.ts` — type réponse `/answer` avec `correct_answer?: string`, `setCorrectAnswerForFeedback(res.correct_answer ?? null)`
- `frontend/components/diagnostic/DiagnosticSolver.tsx` — `GrowthMindsetHint` avec spread conditionnel pour `exactOptionalPropertyTypes`

### Runtime frontend modifié

Oui — `useDiagnostic.ts` et `DiagnosticSolver.tsx`.

### Recâblage appliqué

1. **useDiagnostic** : type réponse `/answer` étendu avec `correct_answer?: string` ; `setCorrectAnswerForFeedback(res.correct_answer ?? null)` appelé après `/answer`.
2. **DiagnosticSolver** : `correctAnswer` passé via `{...(typeof correctAnswerForFeedback === "string" ? { correctAnswer: correctAnswerForFeedback } : {})}` pour respecter `exactOptionalPropertyTypes`.

### Résultat tsc

```
(exit 0 — vert)
```

### Résultat lint

```
exit 0 — 1 warning (session unused, préexistant)
```

### Résultat run 1 pytest diagnostic

```
8 passed in 11.95s
```

### Résultat run 2 pytest diagnostic

```
8 passed in 12.23s
```

### Résultat black

```
All done! 257 files would be left unchanged.
```

### Résultat isort

```
(no output — vert)
```

### Risques résiduels

Aucun nouveau — recâblage correct, typecheck vert.

### GO / NO-GO

**GO** — C1 recâblage frontend feedback + fix typecheck clos.
