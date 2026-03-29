# ADR-005 : Fondation spaced repetition (F04)

**Date :** 2026-03-29
**Statut :** Accepte

---

## Contexte

F04 introduit des revisions espacees basees sur SM-2.

Le lot `F04-P1` a livre :
- la persistance SQLAlchemy `spaced_repetition_items`
- un moteur SM-2 pur
- un write path branche uniquement sur `submit_answer(...)` pour les exercices

Depuis, l'exercice scope complet `F04-P2` a `F04-P5` a ete livre :
- read-model user-level derive
- widget dashboard `Revisions du jour`
- endpoint read-only `GET /api/users/me/reviews/next`
- flux frontend `Reviser maintenant` dans le solver existant

---

## Decision

### 1. Granularite

Une carte SR = un couple `(user_id, exercise_id)`.

Cette granularite est retenue car :
- la cle est toujours disponible au `submit_answer`
- elle evite les collisions d'un agregat trop large (`type + tier`, etc.)
- elle reste lisible pour un futur widget "revisions du jour"

### 2. Semantique de suppression

`exercise_id` est `NOT NULL` avec `ON DELETE CASCADE`.

La suppression de l'exercice supprime la carte SR associee.
Nous n'acceptons pas de carte orpheline ou de `exercise_id = NULL` pour cette granularite.

### 3. Etat user-level

L'etat F04 utilisateur reste derive.

Nous ne stockons pas de flag de type :
- `is_f04_user`
- `has_spaced_repetition`

Les futures surfaces user-level devront recalculer cet etat depuis `spaced_repetition_items`.

### 4. Idempotence

L'idempotence applicative est portee par `last_attempt_id`.

Ce champ reste sans FK vers `attempts` afin d'eviter :
- les contraintes artificielles d'ordre de flush
- les fragilites de tests unitaires

### 5. Boundary runtime

Le write path SR est non bloquant pour le flux principal de tentative.

`submit_answer(...)` appelle la mise a jour SR dans un savepoint dedie :
- si SR reussit, la carte est mise a jour
- si SR echoue, la tentative utilisateur reste validee

Ce choix privilegie la robustesse du flux d'apprentissage principal.

### 6. Actionable read truth

Les lectures user-level F04 doivent rester alignees sur des cartes **actionnables** seulement.

Concretement :
- les compteurs user-level ignorent les exercices inactifs ou archives
- `GET /api/users/stats` et `GET /api/users/me/reviews/next` doivent rester coherents entre eux

### 7. Retrieval-first with post-answer feedback

La session `spaced-review` suit la regle produit suivante :
- avant reponse : pas de spoiler (`correct_answer`, `hint`, `explanation`)
- apres reponse : feedback explicatif autorise

Cette decision vise a proteger l'effort de rappel tout en gardant une boucle pedagogique utile apres soumission.

---

## Consequences

### Positives

- modele simple et coherent
- seam backend borne
- moteur SM-2 testable independamment
- future lecture "due today" simple a calculer

### Negatives / compromis

- pas encore d'integration defis
- suppression d'un exercice = perte des cartes SR associees
- analytics du mode `spaced-review` pas encore totalement distingues d'un exercice standard
- pas encore de compteur de session `X revisions restantes`

---

## Etat actuel

Depuis cette ADR, les livrables suivants ont ete poses :
- `F04-P2` : read-model user-level derive (`f04_initialized`, `active_cards_count`, `due_today_count`, `overdue_count`, `next_review_date`) expose via `/api/users/stats`
- `F04-P3` : widget dashboard `Revisions du jour`
- `F04-P4` : `GET /api/users/me/reviews/next` (lecture seule, prochaine carte actionnable, payload review-safe)
- `F04-P5` : flux frontend `Reviser maintenant` -> solver existant en mode `?session=spaced-review`

Les documents actifs realignes sont :
- `docs/02-FEATURES/API_QUICK_REFERENCE.md`
- `docs/02-FEATURES/F04_REVISIONS_ESPACEES.md`

Extensions encore hors de cette ADR de fondation :
- integration defis
- couplage futur avec F23 (SR + IA)
