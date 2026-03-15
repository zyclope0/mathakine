# Lot C1 - Diagnostic Integrity — Compte-rendu final

> Date: 14/03/2026
> Iteration: C - Production Hardening
> Statut: terminé

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `app/core/security.py` | M - sign_diagnostic_state, verify_diagnostic_state |
| `app/services/diagnostic_service.py` | M - state token, check_answer, apply_answer_and_advance |
| `server/handlers/diagnostic_handlers.py` | M - state_token requis, correct_answer ignoré |
| `frontend/hooks/useDiagnostic.ts` | M - adaptation minimale state_token |
| `tests/api/test_diagnostic_endpoints.py` | M - nouveaux tests, contrat state_token |
| `docs/03-PROJECT/PILOTAGE_CURSOR_PRODUCTION_HARDENING_C1_DIAGNOSTIC_INTEGRITY_REPORT_2026-03-14.md` | A - ce document |

---

## 2. Fichiers runtime modifiés

- `app/core/security.py`
- `app/services/diagnostic_service.py`
- `server/handlers/diagnostic_handlers.py`
- `frontend/hooks/useDiagnostic.ts`

---

## 3. Fichiers de test modifiés

- `tests/api/test_diagnostic_endpoints.py`

---

## 4. Endpoints diagnostic réellement touchés

| Endpoint | Modification |
|----------|---------------|
| `POST /api/diagnostic/start` | Retourne `state_token` en plus de `session` |
| `POST /api/diagnostic/question` | Corps : `state_token` (remplace `session`). Retourne `state_token` |
| `POST /api/diagnostic/answer` | Corps : `state_token`, `user_answer` (plus de `correct_answer` ni `session`). Retourne `state_token` |
| `POST /api/diagnostic/complete` | Corps : `state_token` (remplace `session`) |
| `GET /api/diagnostic/status` | Inchangé |

---

## 5. Source de vérité réelle de `correct_answer` après lot

**Backend uniquement.** Le `correct_answer` est :
- généré par `generate_ai_exercise()` dans `generate_question()`
- embarqué dans le `state_token` signé sous `pending.correct_answer`
- lu par `check_answer(state, user_answer)` qui compare à `state["pending"]["correct_answer"]`
- **jamais** lu depuis le corps de la requête client

Le client peut envoyer `correct_answer` — il est ignoré.

---

## 6. Stratégie d'intégrité du state retenue

- **Token signé** : JWT avec `purpose=diagnostic_state`, payload `{session, pending}`, expiration 60 min
- **Vérification** à chaque étape mutante : `/question`, `/answer`, `/complete`
- **Structure** : `{session: {...}, pending: {exercise_type, correct_answer} | null}`
- **Re-signature** après chaque mutation
- **Pas de Redis/DB** : flux stateless, token porteur

---

## 7. Ce qui a été prouvé

- `correct_answer` client n'est plus la source de vérité (test `test_diagnostic_answer_ignores_client_correct_answer`)
- Le state client n'est plus librement falsifiable (token signé requis, rejet 401 si invalide)
- Flux complet start → question → answer → complete fonctionne
- Token invalide rejeté (tests `test_diagnostic_question_rejects_invalid_state_token`, `test_diagnostic_complete_rejects_invalid_state_token`)

---

## 8. Ce qui n'a pas été prouvé

- Robustesse face à un attaquant avec accès à SECRET_KEY
- Expiration du token en conditions réelles
- Charge sous forte concurrence

---

## 9. Résultat run 1

```
7 passed in 9.21s
```

---

## 10. Résultat run 2

```
7 passed in 8.49s
```

---

## 11. Résultat full suite

```
828 passed, 2 skipped in 195.39s
```

---

## 12. Résultat black

```
4 files reformatted (après correction)
All done!
```

---

## 13. Résultat isort

```
(no output - vert)
```

---

## 14. Risques résiduels

- Le frontend a été adapté (useDiagnostic) — périmètre légèrement étendu pour cohérence du flux
- SECRET_KEY partagée avec l'auth : rotation impacte les deux
- Token rejouable pendant sa validité (1 h) — acceptable pour le diagnostic

---

## 15. GO / NO-GO

**GO** - Le lot C1 est clos : flux diagnostic sécurisé, `correct_answer` et state sous contrôle backend, tests et full suite verts.
