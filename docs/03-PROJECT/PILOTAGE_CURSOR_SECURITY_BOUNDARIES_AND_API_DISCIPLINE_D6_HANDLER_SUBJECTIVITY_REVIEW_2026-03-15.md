# D6 - Handler Subjectivity Review

> Date: 15/03/2026
> Status: closed (2026-03-15)
> Scope: challenge subjective audit findings and define a pragmatic standard

## 1. Mission

Turn the subjective architecture comments from the audit into a precise standard:
- what is acceptable today
- what deserves a future refactor
- what does not count as a defect right now

## 2. Proven Context

The audit claims:
- handlers are still too imperative
- some layers remain anemic / infra-coupled
- large services such as `badge_requirement_engine.py` are hard to maintain

These are partly true observations, but they are not immediate defects in the same category as unsafe defaults or missing request-size limits.

## 3. Analysis Scope (D6)

Verified against code on 15/03/2026 (tree courant):
- `server/handlers/badge_handlers.py` (166 lines)
- `app/services/badge_user_view_service.py` (201 lines)
- `app/services/badge_requirement_engine.py` (766 lines)
- `server/handlers/exercise_handlers.py` (379 lines)

## 4. Acceptable Current State

The following is **acceptable today** and does not require change:

### Handlers

- **badge_handlers.py** : bon exemple de thin handlers — parse → run_db_bound(facade) → JSONResponse, délègue à `BadgeApplicationService`, pas de logique métier.
- **Autres handlers actifs** (ex. `exercise_handlers.py`) : rôle HTTP plus riche — certains utilisent `RedirectResponse`, `TemplateResponse`, `StreamingResponse` ; certains orchestrent plus que les handlers badge. Cela ne constitue pas en soi un défaut immédiat tant que la logique métier principale reste déléguée.
- **Alignement** : `docs/00-REFERENCE/ARCHITECTURE.md` définit « thin HTTP handlers: transport parsing, validation, response mapping ». `badge_handlers.py` respecte ce principe ; d'autres handlers ont un périmètre HTTP élargi par conception.
- **Verdict** : le qualificatif « trop impératif » est vague : des blocs try/except et des appels explicites sont la norme pour des handlers HTTP. Aucun gain prouvé à introduire une couche d’abstraction supplémentaire.

### Services (badge_user_view_service)

- **Pattern** : retour de `Dict[str, Any]` / listes de dicts, usage direct de `Session` et de requêtes SQL/ORM.
- **Justification** : l’API expose du JSON ; des dicts sont un format naturel. L’usage de `Session` est standard pour un service sync.
- **D3** : le fallback `pinned_badge_ids` est désormais explicite (logger.warning, pas de `pass` silencieux).
- **Verdict** : acceptable. Une couche « repository » ou des DTOs riches n’apporteraient pas de gain immédiat démontrable.

### Taille des modules

- **badge_requirement_engine.py** (766 lignes) : module à responsabilité unique (évaluation des critères de badges). La taille est conséquente mais cohérente avec le nombre de types de requirements (attempts_count, logic_attempts_count, mixte, consecutive, etc.).
- **Verdict** : pas un défaut en soi. La décomposition est un candidat de refactor futur, pas une correction urgente.

## 5. Confirmed Future Refactor Candidates

À traiter dans des lots dédiés, avec preuve de gain :

| Candidat | Justification | Priorité |
|----------|---------------|----------|
| `badge_requirement_engine.py` | 766 lignes, plusieurs checkers. Une décomposition par type de requirement (attempts, logic, mixte, etc.) pourrait améliorer la maintenabilité. | Faible, si évolution du domaine badge |
| `auth_service.py`, `exercise_service.py`, `challenge_service.py`, etc. | Déjà listés dans `POINTS_RESTANTS_2026-03-15.md` § 3. | Suivant la roadmap |
| Extraction de repositories | Si un besoin de testabilité ou de réutilisation de requêtes émerge. | Non prioritaire |

## 6. Rejected / Overstated Audit Claims

| Claim | Verdict | Raison |
|-------|---------|--------|
| « Handlers trop impératifs » | **Rejeté comme défaut** | `badge_handlers.py` est thin (parse → delegate → respond). D'autres handlers (ex. `exercise_handlers.py`) ont un rôle HTTP plus riche (RedirectResponse, TemplateResponse, StreamingResponse) ; ce n'est pas un défaut tant que la logique métier reste déléguée. « Impératif » décrit le style normal d'un handler HTTP. |
| « Couches anémiques / infra-couplées » | **Sur-vendu** | Retourner des dicts pour une API JSON est cohérent. Le couplage à SQLAlchemy est le choix standard du projet. « Anémique » sans critère mesurable n’est pas actionnable. |
| « badge_requirement_engine trop gros » | **Partiellement vrai, pas un bug** | Le fichier est volumineux mais structuré (registry de checkers). La taille seule n’est pas un défaut. Décomposition = refactor futur, pas correction. |

## 7. Micro-adjustment Code

**Aucun.** Aucun micro-ajustement n’a été retenu :

- Aucun gain DRY évident dans `badge_handlers.py` : chaque handler a un flux légèrement différent (body, query params, cache, etc.). Une abstraction générique ajouterait de la complexité sans bénéfice mesurable.
- Le `traceback` utilisé dans un handler pour `logger.debug(traceback.format_exc())` est redondant avec `exc_info=True` ailleurs, mais la suppression serait cosmétique et sans impact sur la doctrine.

## 8. Architecture Decision (D6)

- **D6 = doc-only** : la sortie est une clarification documentée, pas un refactor.
- Aucun changement de code. La doctrine ci-dessus reflète l'état actuel du code et définit ce qui est acceptable vs dette future.

## 9. Validation

- Aucun code modifié → pas de pytest obligatoire.
- Revue manuelle : cohérence avec `badge_handlers.py`, `badge_user_view_service.py`, `ARCHITECTURE.md`.

## 10. GO / NO-GO

`GO` : la doctrine est précise, défendable et alignée avec le code réel. Aucun faux refactor.
