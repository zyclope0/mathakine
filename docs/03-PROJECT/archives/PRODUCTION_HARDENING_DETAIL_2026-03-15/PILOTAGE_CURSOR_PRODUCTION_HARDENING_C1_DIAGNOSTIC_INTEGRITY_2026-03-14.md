# Lot C1 - Diagnostic Integrity

> Date: 14/03/2026
> Iteration: C - Production Hardening
> Priorite: P1 critique metier
> Statut: **terminé** — voir `PILOTAGE_CURSOR_PRODUCTION_HARDENING_C1_DIAGNOSTIC_INTEGRITY_REPORT_2026-03-14.md`

## 1. Mission

Rendre le flux diagnostic fiable cote backend:

- ne plus faire confiance au `correct_answer` envoye par le client
- ne plus faire confiance a un etat de session diagnostic librement modifiable

## 2. Contexte actuel prouve

Le flux actuel est stateless cote backend jusqu'a `/complete`.

Dans `server/handlers/diagnostic_handlers.py`:

- `/api/diagnostic/answer` compare `user_answer` a `correct_answer` fourni par le frontend
- le commentaire dit explicitement que le backend "ne revalide pas"
- `/api/diagnostic/complete` persiste une `session` fournie par le client

Dans `app/services/diagnostic_service.py`:

- l'etat de session est un `dict` JSON serialisable
- aucune preuve d'integrite de ce state n'est attachee aux appels suivants

Conclusion:
- un client peut biaiser le niveau final et les scores en envoyant un `correct_answer`
  ou une `session` modifies

## 3. Faux positifs a eviter

- penser que le probleme est seulement UX
- corriger seulement le frontend
- signer uniquement `correct_answer` mais laisser la session libre
- stocker tout en base sans justification alors qu'un state signe peut suffire

## 4. Risque production exact

Risque principal:
- integrite metier du diagnostic non garantie

Impact concret:
- scores, niveaux et recommandations post-diagnostic falsifiables
- perte de confiance dans les donnees de diagnostic

## 5. Decision d'architecture imposee

Decision recommandee pour ce lot:

- conserver un flux stateless apparent
- introduire un `state_token` signe cote serveur
- embarquer dans ce token le state diagnostic necessaire et les bonnes reponses
- verifier la signature a chaque etape mutante du flux
- recalculer cote backend si la reponse de l'utilisateur est correcte

Cette decision est preferee a un stockage serveur complet car:

- elle garde un lot borne
- elle evite d'ouvrir d'emblee Redis/DB session pour le diagnostic
- elle ferme deja la falsification naive du flux

## 6. Ce qui est mal place

- `correct_answer` recu du client dans `/answer`
- `session` librement recopiee du client jusqu'a `/complete`

## 7. Ce qui est duplique ou fragile

- logique de confiance implicite dans les payloads frontend
- absence de preuve d'integrite entre les appels `/start`, `/question`, `/answer`, `/complete`

## 8. Decoupage cible

Handlers:

- parsing HTTP
- validation body
- verification du state signe
- appel service

Service diagnostic:

- creation du state logique
- serialisation signee du state
- verification du state signe
- evaluation correcte/incorrecte cote backend
- persistence finale

## 9. Exemples avant / apres

### Avant

```py
is_correct = str(user_answer).strip().lower() == str(correct_answer).strip().lower()
diagnostic_svc._apply_answer(session, exercise_type, is_correct)
```

### Apres

```py
state = diagnostic_svc.verify_state_token(state_token)
is_correct = diagnostic_svc.check_answer(state, exercise_type, user_answer)
diagnostic_svc.apply_answer(state, exercise_type, is_correct)
next_state_token = diagnostic_svc.sign_state_token(state)
```

## 10. Fichiers a lire avant toute modification

- `D:\\Mathakine\\server\\handlers\\diagnostic_handlers.py`
- `D:\\Mathakine\\app\\services\\diagnostic_service.py`
- `D:\\Mathakine\\app\\core\\security.py`
- `D:\\Mathakine\\tests\\api\\test_diagnostic_endpoints.py`

## 11. Scope autorise

- `server/handlers/diagnostic_handlers.py`
- `app/services/diagnostic_service.py`
- helper de signature/verif strictement necessaire
- schemas/DTO diagnostic strictement necessaires
- tests diagnostic

## 12. Scope interdit

- refactor recommendation
- refactor frontend diagnostic large
- stockage Redis de session
- ouverture d'un lot anti-abus dans ce lot

## 13. Checks exacts

1. `git status --short`
2. `git diff --name-only`
3. `pytest -q tests/api/test_diagnostic_endpoints.py --maxfail=20`
4. relancer exactement la meme commande
5. si runtime backend touche:
   - `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py`
6. `black app/ server/ tests/ --check`
7. `isort app/ server/ --check-only --diff`

## 14. Exigences de validation

- prouver que `correct_answer` client n'est plus la source de verite
- prouver que le state client n'est plus librement falsifiable
- lister les endpoints diagnostic reellement touches
- pas de GO si la verif integrite reste partielle

## 15. Stop conditions

- si la signature du state impose d'ouvrir un chantier auth/session global
- si le lot deborde vers un stockage distribue complet
- dans ce cas: STOP, documenter pourquoi, ne pas bricoler

## 16. Format de compte-rendu final

1. Fichiers modifies
2. Fichiers runtime modifies
3. Fichiers de test modifies
4. Endpoints reellement touches
5. Source de verite reelle de `correct_answer` apres lot
6. Strategie d'integrite du state retenue
7. Ce qui a ete prouve
8. Ce qui n'a pas ete prouve
9. Resultat run 1
10. Resultat run 2
11. Resultat full suite
12. Resultat black
13. Resultat isort
14. Risques residuels
15. GO / NO-GO

