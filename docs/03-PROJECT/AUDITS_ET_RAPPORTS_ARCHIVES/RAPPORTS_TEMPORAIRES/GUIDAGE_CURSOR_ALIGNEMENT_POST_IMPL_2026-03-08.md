# Guidage Cursor - Alignement Post-Implementations

> Date : 08/03/2026
> Usage : guide d'execution pour Cursor / Composer apres plusieurs features recentes
> Statut : implemente le 08/03/2026

---

## 0. Resultat

Les 5 lots de hardening definis dans ce guide ont ete appliques :

- Lot 1 : analytics `interleaved` ramenes a une semantique session
- Lot 2 : flux `save=true` durci et UX d'erreur explicite cote frontend
- Lot 3 : duplication adaptive retiree dans `exercise_handlers.py`
- Lot 4 : quality gate Python remis au vert (`black`, UTF-8)
- Lot 5 : hygiene repo finalisee (`frontend/junit.xml`, `.gitignore`, import inutilise)

---

## 1. Objectif

Ce document guide Cursor de facon precise pour remettre le projet dans un etat
plus robuste apres les dernieres implementations (F07, F32, F35, UX dashboard).

Le but n'est pas de "faire un gros refactor". Le but est de corriger les
incoherences a plus forte valeur pour :

- fiabilite des analytics
- robustesse du flux interleaved
- hygiene quality gates
- reduction de duplication
- standardisation minimale sans regression

---

## 2. Contexte factuel a garder en tete

Etat observe sur le repo local `master` au 08/03/2026 :

- `pytest -q --maxfail=20` : 757 passed, 2 skipped
- `frontend`: `npx tsc --noEmit` OK
- `frontend`: `npx vitest run` OK
- `frontend`: `npm run i18n:validate` OK
- `frontend`: `npm run lint` OK avec 1 warning
- `black app/ server/ tests/ --check` : KO

Conclusion :

- le fonctionnel est globalement sain
- la prod est consideree fonctionnelle
- les points a traiter sont surtout de la robustesse, de la qualite de signal
  produit, et de l'hygiene d'industrialisation

---

## 3. Documents a lire avant de coder

Cursor ne doit pas charger toute la documentation. Lire uniquement :

1. `README_TECH.md`
2. `docs/00-REFERENCE/ARCHITECTURE.md`
3. `docs/02-FEATURES/EDTECH_ANALYTICS.md`
4. `docs/02-FEATURES/API_QUICK_REFERENCE.md`
5. `docs/03-PROJECT/IMPLEMENTATION_F32_SESSION_ENTRELACEE.md`
6. `docs/03-PROJECT/IMPLEMENTATION_F35_REDACTION_LOGS_DB.md`

Ne pas partir sur un refactor large sans avoir lu ces fichiers.

---

## 4. Probleme priorises

## P1 - Analytics interleaved semantiquement faussees

Constat :

- le clic Quick Start interleaved est trace une seule fois
- chaque exercice de la session entrelacee emet ensuite un `first_attempt`
  de type `interleaved`
- les agrégats admin comparent donc 1 clic de session a plusieurs submits
  d'exercices

Impact :

- les taux de conversion admin peuvent etre trompeurs
- les chiffres `first_attempt` et `by_type.interleaved` ne correspondent pas a
  une logique "session"
- la lecture produit devient non fiable

Fichiers concernes :

- `frontend/components/dashboard/QuickStartActions.tsx`
- `frontend/hooks/useSubmitAnswer.ts`
- `frontend/lib/analytics/edtech.ts`
- `app/services/analytics_service.py`
- eventuellement tests associes

Decision recommande :

- pour `type="interleaved"`, ne tracer le `first_attempt` qu'une seule fois par
  session, au premier exercice soumis
- conserver `quick_start_click` une seule fois au clic CTA
- ne pas emettre un `first_attempt` interleaved pour chaque exercice suivant

Important :

- ne pas casser la semantique existante pour `exercise` et `challenge`
- ne pas changer le schema DB
- ne pas introduire un nouvel event analytics dans ce lot

Implementation cible :

1. Stocker dans `sessionStorage` un petit etat de session interleaved, par
   exemple :

```json
{
  "plan": ["addition", "division"],
  "completedCount": 0,
  "length": 10,
  "analytics": {
    "firstAttemptTracked": false
  }
}
```

2. Dans `useSubmitAnswer`, n'appeler `trackFirstAttempt("interleaved", ...)`
   qu'au moment du premier submit de la session interleaved.
3. Pour les exercices suivants de la meme session :
   - ne rien emettre cote analytics EdTech
4. Garder le comportement actuel pour `exercise` et `challenge`.

Tests a ajouter ou mettre a jour :

- test unitaire frontend sur la logique analytics interleaved
- verification qu'une session entrelacee ne produit qu'un seul
  `first_attempt` type `interleaved`

Criteres d'acceptation :

- 1 clic interleaved = au plus 1 `first_attempt` interleaved
- pas de regression sur exercice/challenge classiques
- doc analytics mise a jour si la formulation actuelle devient inexacte

---

## P1 - Quality gate Python non propre

Constat :

- `black --check` echoue sur le repo
- `tests/unit/test_adaptive_difficulty_service.py` a un probleme d'encodage
- plusieurs fichiers de tests demandent un reformatage

Impact :

- le gate de formatage n'est pas fiable
- les futurs commits risquent de casser CI ou d'augmenter le bruit

Fichiers deja signales par `black` :

- `tests/unit/test_adaptive_difficulty_service.py`
- `tests/api/test_admin_users_delete.py`
- `tests/unit/utils/test_latex_utils.py`
- `tests/unit/test_exercise_generator.py`
- `tests/unit/test_exercise_service.py`
- `tests/unit/test_logic_challenge_service.py`

Decision recommande :

- phase dediee "hygiene" sans changement metier
- convertir `tests/unit/test_adaptive_difficulty_service.py` en UTF-8 propre
- reformater les autres fichiers avec `black`

Contraintes :

- ne modifier aucun comportement de test
- pas de refactor en meme temps

Criteres d'acceptation :

- `black app/ server/ tests/ --check` passe
- `pytest -q --maxfail=20` reste vert

---

## P2 - Flux interleaved fragile si la sauvegarde d'exercice echoue

Constat :

- `POST /api/exercises/generate` peut retourner `200` meme si la sauvegarde DB
  echoue
- dans ce cas, la reponse peut ne pas contenir `id`
- le flux "Exercice suivant" ne gere pas explicitement ce cas

Impact :

- session entrelacee bloquee silencieusement
- UX fragile en cas d'erreur DB transitoire

Fichiers concernes :

- `server/handlers/exercise_handlers.py`
- `frontend/app/exercises/interleaved/page.tsx`
- `frontend/components/exercises/ExerciseSolver.tsx`

Decision recommande :

- si `save=true` et que la sauvegarde echoue, retourner une erreur HTTP
  explicite au lieu d'un `200` incomplet
- cote frontend, afficher un feedback utilisateur clair et un fallback propre

Implementation cible :

1. Backend :
   - dans `generate_exercise_api`, si `save_to_db` est vrai et que
     `create_generated_exercise` echoue ou ne retourne pas d'id, retourner
     `api_error_response(500, ...)`
   - ne pas continuer silencieusement
2. Frontend entree de session :
   - sur erreur de generation du premier exercice, toast + retour vers
     `/exercises`
3. Frontend exercice suivant :
   - si appel API echoue, afficher un toast
   - conserver la session courante en storage
   - ne pas vider l'etat tant qu'aucun nouvel exercice valide n'est cree

Tests a ajouter :

- test API pour `generate_exercise_api` quand la sauvegarde echoue avec
  `save=true`
- test frontend minimal ou test unitaire de branche d'erreur pour
  `handleNextExercise`

Criteres d'acceptation :

- pas de `200` sans `id` quand `save=true`
- pas de blocage silencieux cote UI

---

## P2 - Duplication de la resolution adaptive et standardisation incomplete

Constat :

- la logique de resolution adaptative `age_group` est dupliquee dans
  `generate_exercise` et `generate_exercise_api`
- les utilitaires de standardisation existent deja mais ne sont pas entierement
  cables (`enum_mapping`, `response_formatters`)

Impact :

- dette DRY
- risque de divergence future entre routes HTML/JSON
- maintenance plus couteuse

Fichiers concernes :

- `server/handlers/exercise_handlers.py`
- `app/utils/enum_mapping.py`
- `app/utils/response_formatters.py`

Decision recommande :

- ne pas lancer un refactor transversal du projet dans ce lot
- faire un refactor cible et a faible risque dans `exercise_handlers.py`

Implementation cible :

1. Extraire une fonction privee dans `server/handlers/exercise_handlers.py`,
   par exemple :

```py
async def _resolve_adaptive_age_group_if_needed(
    request: Request,
    exercise_type_raw: str | None,
    age_group_raw: str | None,
    adaptive: bool,
) -> str | None:
    ...
```

2. Utiliser cette fonction dans :
   - `generate_exercise`
   - `generate_exercise_api`
3. Conserver strictement le comportement actuel.
4. Ne pas toucher aux autres handlers dans ce lot, sauf si necessaire pour
   corriger une regression evidente.

Important :

- scope volontairement limite
- l'objectif est de supprimer la duplication recente, pas de "finir toute
  l'architecture" en une fois

Tests a mettre a jour si besoin :

- tests API deja existants autour de `adaptive=true` sans `age_group`

Criteres d'acceptation :

- une seule implementation de la resolution adaptive dans le handler exercise
- pas de changement de contrat API

---

## P3 - Hygiene repo

Constats :

- `frontend/app/challenges/page.tsx` contient un import inutilise (`cn`)
- `frontend/junit.xml` est un artefact genere versionne
- `.gitignore` contient des lignes corrompues / parasites a nettoyer

Decision recommande :

- corriger ce lot a la fin seulement
- pas melanger avec les fixes metier P1/P2

Implementation cible :

1. supprimer l'import inutilise `cn`
2. retirer `frontend/junit.xml` de l'index git si c'est bien un artefact genere
3. ajouter la bonne regle d'ignore si necessaire
4. nettoyer `.gitignore` sans changer son intention

Important :

- le `.pptx` dans `docs/investor_deck/` peut etre un livrable voulu : ne pas le
  supprimer par automatisme

---

## 5. Ordre d'execution recommande

Ordre strict :

1. corriger P1 analytics interleaved
2. corriger P2 robustesse generate/save + UI
3. corriger P2 duplication adaptive
4. corriger P1 hygiene black/UTF-8
5. corriger P3 hygiene repo
6. relancer tous les checks
7. mettre a jour la documentation touchee

Pourquoi cet ordre :

- analytics et robustesse session ont la plus forte valeur produit
- le DRY recent doit etre traite avant que d'autres features empilent la dette
- l'hygiene de formatage vient ensuite pour remettre le gate au vert

---

## 6. Contraintes pour Cursor

- ne pas faire un refactor global
- ne pas toucher aux zones non liees
- ne pas modifier les schemas DB
- ne pas changer les payloads admin analytics sauf necessite documentee
- ne pas casser les tests existants
- privilegier les petites fonctions privees et les changements cibles
- respecter PowerShell : ne pas utiliser `&&`

---

## 7. Commandes de validation

Depuis `D:\\Mathakine` :

```powershell
git status --short
black app/ server/ tests/ --check
pytest -q --maxfail=20
```

Depuis `D:\\Mathakine\\frontend` :

```powershell
npx tsc --noEmit
npm run lint
npm run i18n:validate
npx vitest run
```

Si tu touches les analytics interleaved, ajouter si possible un test cible avant
le run complet.

---

## 8. Documentation a mettre a jour apres implementation

Mettre a jour seulement si le comportement a change reellement :

- `CHANGELOG.md`
- `README_TECH.md`
- `docs/02-FEATURES/EDTECH_ANALYTICS.md`
- `docs/02-FEATURES/API_QUICK_REFERENCE.md` si contrat modifie
- `docs/INDEX.md` si un nouveau document d'implementation est cree

Si les changements restent purement internes (DRY / black / hygiene), eviter de
sur-documenter.

---

## 9. Definition of done

Le lot est termine si :

- les analytics interleaved ne surcomptent plus les conversions
- le flux interleaved ne peut plus se bloquer silencieusement si `save=true`
- la duplication adaptive recente est retiree
- `black --check` passe
- `pytest`, `tsc`, `lint`, `i18n`, `vitest` passent
- la doc critique touchee est alignee avec le code final
