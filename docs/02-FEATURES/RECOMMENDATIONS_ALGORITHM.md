# Algorithme de recommandations — Mathakine

> Scope : `app/services/recommendation/`
> Updated : 2026-03-27

---

## Architecture

```
recommendation_service.py          Orchestrateur principal (RecommendationService)
recommendation_user_context.py     Contexte utilisateur (age_group, tier cible, niveaux)
recommendation_exercise_ranking.py Classement et sélection des exercices candidats
recommendation_exercise_reasons.py Codes raison i18n (reco.exercise.*)
```

**Point d'entrée backend** : `RecommendationService.generate_recommendations(db, user_id)`
**Point d'entrée API** : `GET /api/recommendations` → `get_recommendations_for_api_sync()`

---

## Contexte utilisateur

Avant toute sélection, le service construit le contexte via `build_recommendation_user_context()` :

| Champ | Source | Rôle |
|-------|--------|------|
| `age_group` | `users.age_group` (F42) | Détermine le profil pédagogique |
| `target_difficulty_tier` | `compute_user_target_difficulty_tier(age_group, mastery)` | Tier 1-12 cible (matrice F42) |
| `current_level` | `users.current_level` | Niveau de compte |
| `preferred_difficulty` | `users.preferred_difficulty` | Niveau legacy (INITIE…) |
| `mastery` | dernier Progress IA par type d'exercice | Source de la bande pédagogique |

---

## Algorithme exercices (R1–R4)

Les exercices sont sélectionnés par **pré-filtre SQL dur** sur le tier, puis classés.

### Pré-filtre tier (F42)

```python
exercise_tier_filter_expression(target_tier, difficulty_level)
# → OR(
#     Exercise.difficulty_tier IS NULL,          ← exercices legacy sans tier
#     Exercise.difficulty_tier BETWEEN tier-1 AND tier+1
#   )
```

Fenêtre : `tier ±1` (3 valeurs sur 12). Les exercices sans `difficulty_tier` (legacy) passent toujours le filtre pour ne pas vider le pool.

### Catégories de recommandation

| Code | Condition déclencheur | Logique de sélection |
|------|-----------------------|----------------------|
| `improvement` | taux de réussite < 70% sur le type | tier cible, type d'exercice courant |
| `progression` | taux de réussite ≥ 70%, prochain niveau disponible | tier cible + 1, type suivant |
| `maintenance` | exercices déjà bien maîtrisés | tier courant, variété de types |
| `discovery` | types non encore pratiqués | tier cible, types nouveaux |
| `fallback` | pool vide après tous les filtres | tier ±1 relaxé, tous types |

### Classement final

`select_top_ranked_exercises()` : parmi les candidats filtrés (max `MAX_CANDIDATES_TO_RANK`), trie par score composite (taux de réussite, fraîcheur, diversité de types) et retourne les N meilleurs.

---

## Algorithme défis (R5)

Les défis utilisent une approche **différente** : pas de pré-filtre SQL strict sur le tier, mais un **score de pertinence** calculé en Python sur le pool filtré par âge.

### Pré-filtre pool (SQL)

```python
# Filtre obligatoire : actif, non archivé, groupe d'âge compatible
filter(
    LogicChallenge.is_active.is_(True),
    LogicChallenge.is_archived.is_(False),
    OR(LogicChallenge.age_group == db_age_group,
       LogicChallenge.age_group == AgeGroup.ALL_AGES),
    NOT EXISTS(réussis récemment)
)
```

### Fonction de score

```python
def _score_challenge_for_recommendation(ch, profile, user_target_tier):
    dr = ch.difficulty_rating  # 1.0–5.0

    if profile == "onboarding":    score = (4.6 - dr) * 3.5        # préfère facile
    elif profile == "stretch":     score = (4.2 - min(dr, 4.0)) * 2.8
    elif profile == "explorer":    score = (dr - 2.0) * 1.2        # préfère difficile
    else:                          score = (5.0 - abs(dr - 3.0)) * 2.0

    # Bonus complétion partielle / type varié
    if ch récemment tenté sans réussir: score += 6.0 ou 2.0

    # Pénalité tier (F42) — si tier connu
    if user_target_tier and ch.difficulty_tier:
        dist = abs(ch.difficulty_tier - user_target_tier)
        score -= dist * 0.35

    return score
```

Le tri final est par `(-score, -id)` ; les 4 meilleurs sont retenus.

---

## Asymétrie exercices / défis — design choice documenté

| Aspect | Exercices | Défis |
|--------|-----------|-------|
| Filtre tier | **Pré-filtre SQL dur** `BETWEEN tier-1 AND tier+1` | **Pénalité de score** `dist * 0.35` |
| Explication | Pool large, filtre efficace en base | Pool plus restreint (~quelques centaines), scoring Python acceptable |
| Conséquence | Un défi hors-tier peut toujours apparaître si son score est suffisamment haut | Un exercice hors-tier `±1` n'apparaît jamais (sauf legacy sans tier) |
| Risque | Faible : les exercices legacy sans tier passent toujours | Faible : la pénalité `0.35/tier` est atténuée par les bonus comportementaux |

Cette asymétrie est **intentionnelle** et résulte de la différence de taille de pool entre exercices (>1000) et défis (~400). Elle est acceptée comme design choice dans ADR-004.

---

## Codes raison i18n

Les recommandations exposent un champ `reason_code` traduit côté client par `useRecommendationsReason.ts`.

### Exercices

| Code | Signification |
|------|--------------|
| `reco.exercise.improvement` | Exercice à améliorer (< 70%) |
| `reco.exercise.progression` | Prochaine étape de progression |
| `reco.exercise.maintenance` | Consolidation d'une compétence maîtrisée |
| `reco.exercise.discovery` | Nouveau type à découvrir |
| `reco.exercise.fallback` | Recommandation de repli |

### Défis

| Code | Signification |
|------|--------------|
| `reco.challenge.onboarding` | Premier défi (profil nouveau) |
| `reco.challenge.gentle_progress` | Progression douce |
| `reco.challenge.skill_stretch` | Défi de dépassement |
| `reco.challenge.variety` | Variété de types |

---

## Limitations connues

- Le filtre exercices legacy (sans `difficulty_tier`) dilue la précision pédagogique du pré-filtre.
- La pénalité tier sur les défis (`0.35/tier`) peut être contrebalancée par un fort bonus comportemental : un défi 3 tiers au-dessus peut remonter si l'utilisateur l'a tenté plusieurs fois sans succès.
- La fenêtre `±1` exercices est un paramètre fixe non configurable : une progression rapide peut créer un délai avant que le tier cible soit recalculé.
- Le classement défis (`_score_challenge_for_recommendation`) n'est pas couvert par des tests unitaires dédiés au scoring.
