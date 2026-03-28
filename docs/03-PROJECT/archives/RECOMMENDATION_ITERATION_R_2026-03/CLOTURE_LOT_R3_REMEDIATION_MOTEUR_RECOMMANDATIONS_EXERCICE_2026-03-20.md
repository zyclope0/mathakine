# Clôture lot R3 — Remédiation moteur recommandations **exercice**

> **Date** : 2026-03-20  
> **Verdict** : **GO** (fond technique validé ; périmètre exercice hors défis).  
> **Micro-lot R3b (2026-03-20)** : réalignement **strict du reporting** uniquement — aucun changement runtime, tests inchangés. Ce document remplace toute formulation sur-généralisée selon la vérité active du code.

> **Historique — § 2.2 découverte** : le corps ci-dessous reflète la vérité **au 2026-03-20** (découverte hors `select_top_ranked_exercises`). **Supersédé** par **R6** (2026-03-21) : la découverte passe par le **même pipeline** (`select_top_ranked_exercises`, pénalisation étendue) — voir `app/services/recommendation/recommendation_service.py` et [RECOMMENDATION_R6_EXERCISE_DISCOVERY_AND_REASONS_2026-03-21.md](./RECOMMENDATION_R6_EXERCISE_DISCOVERY_AND_REASONS_2026-03-21.md). Clôture gouvernance itération **R** : [RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md](./RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md).

---

## 1. Objectif R3 (rappel)

Réduire l’instabilité et l’aléa excessif des recommandations **exercice** : ranking déterministe, anti-répétition minimale, sans refonte du moteur ni changement de contrat HTTP public.

**Hors scope R3** : feedback lifecycle, i18n des raisons, recommandations de **défis**, nouvelle API, migrations.

---

## 2. Vérité par branche (à ne pas fusionner abusivement)

### 2.1 Amélioration, progression, réactivation, fallback exercice

Ces branches utilisent **toutes** :

- **pool borné + ranking** Python : pool candidat via `ORDER BY Exercise.id DESC LIMIT MAX_CANDIDATES_TO_RANK`, puis classement déterministe via `select_top_ranked_exercises(...)` (`app/services/recommendation/recommendation_exercise_ranking.py`) ;
- l’**anti-répétition R3** : `penalized_exercise_ids` = exercices déjà présents dans une reco exercice récente (fenêtre 14 j, colonnes existantes de `Recommendation`), collectés **avant** suppression des reco incomplètes.

### 2.2 Découverte (nouveaux types d’exercices)

Cette branche **ne passe pas** par `select_top_ranked_exercises(...)`.

- Sélection **déterministe côté SQL** : `distinct(Exercise.exercise_type)` avec `order_by(Exercise.exercise_type, Exercise.id)` (équivalent produit à un choix stable par type, sans `func.random()` sur les exercices).
- **Pas** d’application directe de `penalized_exercise_ids` sur ce chemin (pas de ranking Python R3 sur ces lignes).
- Le commentaire métier dans le code note explicitement l’absence d’« échantillon global borné » au sens des autres branches — la logique reste celle héritée du lot B4.3 / adaptation R3 « sans random ».

---

## 3. Usages de `random` supprimés ou bornés (formulation exacte)

- **Branches exercice classées ci-dessus (§ 2.1)** : plus de `func.random()` pour la sélection d’exercices ; choix = pool borné + tri Python explicite.
- **Branche découverte (§ 2.2)** : pas de `random()` pour la sélection d’exercices ; ordre SQL stable.
- **Recommandations de défis** : en dehors du périmètre R3 ; le service peut encore utiliser `func.random()` sur la requête des défis — **ce n’est pas** de l’homogénéité « toute la sélection exercice ».

Ne pas écrire que « toute la sélection exercice » suit le même pipeline **pool borné + ranking Python + pénalisation** : la **découverte** est une exception déterministe SQL, stable, sans random, mais **hors** `select_top_ranked_exercises` / **hors** pénalisation R3 directe.

---

## 4. Anti-répétition R3

- **Où** : amélioration, progression, réactivation, fallback (via `penalized_exercise_ids` + `select_top_ranked_exercises`).
- **Découverte** : pas d’intégration de cette pénalisation dans la requête actuelle (réserve résiduelle — § 6).

---

## 5. Tests et gates (baseline citée — pas de rerun imposé pour R3b)

Ces résultats ont été validés lors de la clôture technique R3 ; le micro-lot **R3b** est documentaire uniquement.

| Cible | Commande (raccourci) | Résultat |
|--------|----------------------|----------|
| Reco ciblée | `pytest -q tests/unit/test_recommendation_service.py tests/api/test_recommendation_endpoints.py --maxfail=20 --no-cov` | **21 passed, 1 skipped** |
| Full gate | `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` | **972 passed, 3 skipped** |

---

## 6. Risques résiduels / réserve R3

1. **Fenêtre `MAX_CANDIDATES_TO_RANK`** : exercices pertinents mais hors les *N* derniers `id` ne participent pas au tri Python sur les branches § 2.1.
2. **Tie-break** : clé finale du ranking Python = **`-id`** (parmi équivalents, id le plus élevé d’abord), cohérent avec un pool « récents d’abord » — documenté dans `recommendation_exercise_ranking.py`.
3. **Découverte** : stable et sans `random`, mais **sans** ranking Python R3 ni pénalisation `penalized_exercise_ids` sur le chemin actuel. Un lot ultérieur **optionnel** pourrait aligner la découverte sur le même pipeline si le produit l’exige ; **hors scope** R3 / R3b.

---

## 7. Fichiers runtime concernés par R3 (traceabilité)

- `app/services/recommendation/recommendation_service.py`
- `app/services/recommendation/recommendation_exercise_ranking.py`

*(R3b : aucune modification de ces fichiers.)*

---

## 8. Synthèse R3b

| Affirmation | Statut |
|-------------|--------|
| Toutes les branches « exercice » passent par `select_top_ranked_exercises` | **Faux** — la **découverte** est une exception SQL déterministe. |
| Toutes les branches exercice bénéficient de `penalized_exercise_ids` | **Faux** — pénalisation R3 appliquée via le ranking Python sur § 2.1 seulement. |
| `func.random()` a disparu des branches exercice de sélection (hors défis) | **Vrai** pour les chemins exercice décrits ; les **défis** restent à part. |

**GO R3** maintenu : le cœur R3 est atteint sur les branches concernées ; la **réserve découverte** reste **explicitement** tracée (§ 6 et § 8).
