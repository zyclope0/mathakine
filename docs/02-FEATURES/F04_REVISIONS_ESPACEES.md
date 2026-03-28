# F04 - Revisions espacees (algorithme SM-2)

> Reference technique - implementation roadmap
> Date : 2026-03-29
> Statut : [PARTIAL] `F04-P1` backend livre ; `F04-P2` read-model user-level a venir
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

### Non livre a ce stade

- read-model user-level F04
- endpoint public ou user-level pour exposer l'etat F04
- widget dashboard "revisions du jour"
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

## 7. Read-model cible pour `F04-P2`

Le prochain lot backend doit exposer un etat user-level derive, sans champ stocke sur `users`.

Payload cible :

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

---

## 8. Documentation a realigner

### Mise a jour immediate apres `F04-P1`

- `docs/00-REFERENCE/ARCHITECTURE.md`
  - ajouter le domaine `app/services/spaced_repetition/`
  - mentionner le seam `exercise_attempt_service.submit_answer(...)`
- `docs/00-REFERENCE/DATA_MODEL.md`
  - ajouter `SpacedRepetitionItem`
  - documenter la cardinalite `(user, exercise)`
- `docs/05-ADR/`
  - ADR dedie sur la granularite SR, l'idempotence et la derive user-level

### Mise a jour a faire quand `F04-P2` existera

- `docs/02-FEATURES/API_QUICK_REFERENCE.md`
  - documenter l'endpoint ou la surface API exposee pour le read-model F04
- toute doc technique qui decrit les handlers/services users si un nouveau handler ou endpoint est ajoute
- toute doc dashboard si le payload F04 est consomme ensuite par une UI

---

## 9. References

- [ROADMAP_FONCTIONNALITES §F04](ROADMAP_FONCTIONNALITES.md)
- [../00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)
- [../00-REFERENCE/DATA_MODEL.md](../00-REFERENCE/DATA_MODEL.md)
- [../05-ADR/ADR-005-spaced-repetition-foundation.md](../05-ADR/ADR-005-spaced-repetition-foundation.md)
