# Iteration B - Contracts, Decomposition & CI Hardening

> Date: 11/03/2026
> Statut: actif
> Strategie: quality-first, max-effort
> Protocole: `CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md`

---

## Objectif

Cette iteration ne vise plus seulement le wiring. Elle vise a transformer les facades de transition en use cases defendables, a durcir les contrats et a faire de la CI un vrai garde-fou.

Priorites:

1. supprimer `Tuple` et `Dict[str, Any]` comme contrats dominants
2. introduire des DTO/resultats metier types
3. decouper les hotspots encore trop gros
4. traiter les hotspots SQL/perf les plus couteux
5. durcir couverture et typing module par module

## Faux positifs a eviter

- croire qu'une facade applicative suffit a elle seule a faire un use case propre
- lancer mypy strict partout d'un coup
- ouvrir `challenge_validator.py` sans lot dedie

## Lots de l'iteration B

### B1 - Challenge use cases
- `PILOTAGE_CURSOR_BACKEND_CONTRACTS_LOT1_CHALLENGE_USE_CASES_2026-03-11.md`

### B2 - Admin and badge use cases
- `PILOTAGE_CURSOR_BACKEND_CONTRACTS_LOT2_ADMIN_BADGE_USE_CASES_2026-03-11.md`

### B3 - Hotspot decomposition
- `PILOTAGE_CURSOR_BACKEND_CONTRACTS_LOT3_HOTSPOT_DECOMPOSITION_2026-03-11.md`

### B4 - SQL performance
- `PILOTAGE_CURSOR_BACKEND_CONTRACTS_LOT4_SQL_PERFORMANCE_2026-03-11.md`

### B5 - CI and typing hardening
- `PILOTAGE_CURSOR_BACKEND_CONTRACTS_LOT5_CI_TYPING_2026-03-11.md`

## Gate d'iteration

Pour considerer l'iteration B terminee:
- les contrats dominants des zones ciblees sont types
- les tuples `(result, err, code)` ont disparu des facades ciblees
- les hotspots majeurs ont ete decomposes ou explicitement isoles
- un vrai seuil couverture et un plan mypy sont actifs

## Exemple de cible

```py
class SubmitChallengeAttemptCommand(BaseModel):
    challenge_id: int
    user_id: int
    user_solution: str
    time_spent: float | None
    hints_used_count: int

class SubmitChallengeAttemptResult(BaseModel):
    is_correct: bool
    explanation: str | None
    new_badges: list[BadgeEarned]
    progress_notification: ProgressNotification | None
    hints_remaining: int | None
```

Cette cible remplace:
- `Dict[str, Any]`
- tuples heterogenes
- erreurs non standardisees

## Compte-rendu attendu

Chaque lot doit dire:
- quels contrats ont ete types
- quels tuples ont ete supprimes
- quels hotspots ont ete reduits
- quelle preuve CI/typing a ete ajoutee
