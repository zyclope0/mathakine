# F04 - Revisions espacees (algorithme SM-2)

> Reference technique - implementation roadmap
> Date : 2026-03-29
> Statut : [PARTIAL] `F04-P1`..`F04-P5` livres ; extensions hors scope = defis + F23
> Source : [ROADMAP_FONCTIONNALITES §F04](ROADMAP_FONCTIONNALITES.md)

---

## 1. Vue d'ensemble

F04 introduit un systeme de revisions espacees base sur SM-2 pour optimiser la retention a long terme des competences acquises.

Fondements scientifiques retenus :
- Ebbinghaus (1885) : courbe de l'oubli
- Cepeda et al. (2006) : pratique espacee > pratique massee
- Kornell & Bjork (2008) : spacing + interleaving efficaces en mathematiques
- SM-2 : base historique de SuperMemo / Anki

---

## 2. Etat actuel du chantier

### Livre dans `F04-P1`

- table persistante `spaced_repetition_items`
- modele ORM `SpacedRepetitionItem`
- moteur SM-2 pur dans `app/services/spaced_repetition/sm2_engine.py`
- service applicatif `record_exercise_attempt_for_spaced_repetition(...)`
- branchement sur `exercise_attempt_service.submit_answer(...)`
- idempotence par `last_attempt_id`

### Livre dans `F04-P2` / `F04-P3`

- read-model user-level (agregat) consomme via `/api/users/stats` → `spaced_repetition`
- widget dashboard « revisions du jour » (frontend)

### Livre dans `F04-P4`

- `GET /api/users/me/reviews/next` : prochaine carte SR **actionnable** (exercice actif, non archivé), payload review-safe, aucune ecriture SR sur cette route

### Livre dans `F04-P5`

- widget dashboard : CTA **Réviser maintenant** si `due_today_count > 0` ou `overdue_count > 0` → fetch `reviews/next` → redirection `/exercises/{id}?session=spaced-review`
- `ExerciseSolver` : mode `session=spaced-review` (badge contexte, pas d’indice avant réponse, explication affichée après soumission, puis prochaine carte due ou fin de session sobre)
- pas de nouvelle route API ; pas de second solver

### Non livre a ce stade

- integration defis
- integration F23 (SR + IA)

---

## 3. Algorithme SM-2 retenu

Intervalles :
- 1er succes : J+1
- 2e succes : J+3
- 3e succes : J+7
- suivants : intervalle precedent x ease factor

Ease factor :
- initial : `2.5`
- plancher : `1.3`
- plafond : `3.0`
- succes rapide (`quality >= 4`) : `+0.1`
- succes lent (`quality == 3`) : inchange
- echec (`quality < 3`) : `-0.2` et retour a `J+1`

Qualite derivee depuis la tentative exercice :
- incorrect : `0`
- correct et `time_spent <= 60s` : `5`
- correct et `60s < time_spent < 120s` : `4`
- correct et `time_spent >= 120s` : `3`

Invalidite d'entree :
- `quality` hors `0..5` -> `SpacedRepetitionInputError`

---

## 4. Granularite retenue

Une carte SR = un couple `(user_id, exercise_id)`.

Justification :
- cle toujours disponible au moment du `submit_answer`
- alignement naturel avec les tentatives existantes
- pas de collision entre exercices distincts du meme type ou meme tier
- lecture future "revisions du jour" plus simple qu'un agregat par concept encore instable

Decision associee :
- `exercise_id` est `NOT NULL`
- suppression de l'exercice -> suppression des cartes SR associees (`ON DELETE CASCADE`)
- pas de booleen `is_f04_user` stocke sur `users` ; l'etat F04 user-level restera derive

---

## 5. Modele de donnees actif

```sql
spaced_repetition_items (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  exercise_id INT NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
  ease_factor FLOAT NOT NULL,
  interval_days INT NOT NULL,
  next_review_date DATE NOT NULL,
  repetition_count INT NOT NULL,
  last_quality INT NULL,
  last_attempt_id INT NULL, -- correlation idempotente, sans FK
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  UNIQUE (user_id, exercise_id)
)
```

Index utile actuellement :
- `(user_id, next_review_date)` pour les futures lectures "due today"

---

## 6. Integration runtime actuelle

Write path actif :
- `app/services/exercises/exercise_attempt_service.py`
- apres `create_attempt(...)`
- dans un savepoint dedie, pour ne pas casser le flux principal si SR echoue

Regle runtime :
- tentative exercice standard seulement
- pas de handler dedie dans `F04-P1`
- pas de changement frontend dans `F04-P1`

---

## 7. Read-model user-level (`F04-P2`)

Expose dans `/api/users/stats` sous la cle `spaced_repetition` :

```json
{
  "f04_initialized": true,
  "active_cards_count": 12,
  "due_today_count": 3,
  "overdue_count": 1,
  "next_review_date": "2026-03-31"
}
```

Interpretation produit :
- `0 carte` -> F04 non initialise
- `due_today_count > 0` -> revisions a afficher
- `overdue_count > 0` -> utilisateur en retard

Important :
- les compteurs F04 user-level restent alignes sur les cartes **actionnables**
- un exercice inactif ou archive ne doit plus gonfler `due_today_count` / `overdue_count`
- `/api/users/stats` et `GET /api/users/me/reviews/next` racontent donc la meme verite produit

---

## 8. Prochaine revision due (`F04-P4`)

Endpoint : `GET /api/users/me/reviews/next` (auth + acces complet).

Reponse :

- `has_due_review` : `true` uniquement si une carte **actionnable** existe (`next_review_date` <= aujourd'hui UTC, exercice actif et non archive)
- `summary` : meme objet que le bloc `spaced_repetition` de `/api/users/stats`
- `next_review` : `null` si aucune carte actionnable ; sinon un seul item avec `review_item_id`, `exercise_id`, `due_status` (`overdue` \| `due_today`), `next_review_date` (ISO), `exercise` (champs strictement necessaires a l'enonce — **pas** de correction ni d'explication ni d'indice)

Ordre de selection : retard avant « du jour » ; puis `next_review_date` croissante ; puis `review_item_id` croissant.

---

## 9. Experience frontend livree (`F04-P5`)

Point d'entree :
- widget dashboard `Revisions du jour`
- CTA `Reviser maintenant` seulement si une action immediate existe

Comportement :
- fetch `GET /api/users/me/reviews/next`
- stockage temporaire review-safe via `spacedReviewSession`
- redirection `/exercises/{id}?session=spaced-review`
- `ExerciseSolver` reste le solver unique

Decision produit explicite :
- avant soumission : aucun `hint`, aucune `explanation`, aucune correction
- apres soumission : explication affichee pour fournir un feedback pedagogique utile
- suite de session : prochaine carte due si elle existe, sinon fin de session sobre

---

## 10. Reserves documentees (non bloquantes)

Reserves conservees volontairement hors du scope livre :
- analytics : le flux `spaced-review` n'est pas encore distingue partout comme type analytics dedie ; une partie du tracking reste agregee avec `exercise`
- UX : pas encore de compteur `X revisions restantes` dans la session SR
- perimetre : pas d'integration defis dans la file SR
- strategie avancee : pas encore de couplage F23 (`SR + IA`)

Ces points restent des suites bornees, pas des blockers du lot F04 exercice deja livre.

---

## 11. Documentation a realigner

### Mise a jour immediate apres `F04-P1`

- `docs/00-REFERENCE/ARCHITECTURE.md`
  - ajouter le domaine `app/services/spaced_repetition/`
  - mentionner le seam `exercise_attempt_service.submit_answer(...)`
- `docs/00-REFERENCE/DATA_MODEL.md`
  - ajouter `SpacedRepetitionItem`
  - documenter la cardinalite `(user, exercise)`
- `docs/05-ADR/`
  - ADR dedie sur la granularite SR, l'idempotence et la derive user-level

### Reference API

- `docs/02-FEATURES/API_QUICK_REFERENCE.md` — agregat F04 dans `/stats` + `GET /api/users/me/reviews/next`

---

## 12. References

- [ROADMAP_FONCTIONNALITES §F04](ROADMAP_FONCTIONNALITES.md)
- [../00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)
- [../00-REFERENCE/DATA_MODEL.md](../00-REFERENCE/DATA_MODEL.md)
- [../05-ADR/ADR-005-spaced-repetition-foundation.md](../05-ADR/ADR-005-spaced-repetition-foundation.md)
