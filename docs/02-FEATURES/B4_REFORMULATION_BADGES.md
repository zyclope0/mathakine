# B4 — Reformulation des badges existants

> **Date** : 15/02/2026  
> **Contexte** : Lot B du [PLAN_REFONTE_BADGES](PLAN_REFONTE_BADGES.md)  
> **Objectif** : Auditer et reformuler les badges actuels (icône, titre, visuel, objectif) selon les principes psychologiques et le contexte Mathakine (thème Jedi, exercices + défis logiques)

---

## Réconciliation B4 / Challenge

| Dimension | Demande utilisateur | Formalisation PLAN_REFONTE_BADGES | Réalisation B4 |
|-----------|---------------------|-----------------------------------|---------------|
| **Contexte** | « Pense au challenge » — inclure le contexte défis logiques | B4 décrit comme reformulation dans le « contexte du projet » ; pas de mention explicite défis vs exercices | Section 1 documente les 2 piliers (exercices + défis), périmètre B4 = exercices uniquement |
| **Périmètre badges** | Contexte pointu et minutieux | Principes psychologiques + gamification ; schéma requirements = attempts, exercise_type, etc. (exercices) | B4 reformule les 17 badges existants (tous basés sur `Attempt`) ; défis logiques hors périmètre |
| **Évolution** | — | Lot C : moteur générique ; B5+ formulaire admin | Extension future : badges « défi logique » (Lot C ou B5+) avec `LogicChallengeAttempt` |
| **Alignement** | | **PLAN mis à jour 15/02** : § 5.3.1 formalise le périmètre challenge ; B-4 marqué ✅ Fait | Cohérent |

---

## Table des matières

1. [Contexte plateforme et challenge](#1-contexte-plateforme-et-challenge)
2. [État actuel des badges](#2-état-actuel-des-badges)
3. [Matrice de reformulation par badge](#3-matrice-de-reformulation-par-badge)
4. [Spécifications finales par badge](#4-spécifications-finales-par-badge)
5. [Script de mise à jour](#5-script-de-mise-à-jour)

---

## 1. Contexte plateforme et challenge

### 1.1 Deux piliers d'activité Mathakine

| Pilier | Modèle | Table / Champ clé | Description |
|--------|--------|-------------------|-------------|
| **Exercices mathématiques** | `Attempt` | `attempts` | Additions, soustractions, multiplications, divisions — résolution d'exercices générés |
| **Défis logiques** | `LogicChallengeAttempt` | `logic_challenge_attempts` | Suites, motifs, puzzles, énigmes, raisonnement, probabilités, etc. |

**Types de défis logiques** (`LogicChallengeType`) : `sequence`, `pattern`, `visual`, `puzzle`, `riddle`, `deduction`, `probability`, `graph`, `coding`, `chess`, `custom`.

### 1.2 Périmètre actuel des badges (B4)

**Les badges existants sont basés UNIQUEMENT sur les exercices mathématiques** (`Attempt`).  
Le moteur `BadgeService._check_badge_requirements` interroge exclusivement la table `attempts`.

| Aspect | État actuel | Après B4 |
|--------|-------------|----------|
| Source données badges | `Attempt` uniquement | Inchangé — exercices uniquement |
| Défis logiques | Non pris en compte | Restent hors périmètre pour B4 |
| Extension future | — | Lot C ou B5+ : possibilité de badges « défi logique » |

**Implication pour la reformulation** : Les libellés (titre, description, star_wars_title) doivent refléter clairement le périmètre **exercices**. On évite des formulations trop génériques (« résoudre des missions ») qui pourraient suggérer que les défis logiques comptent. On privilégie : « résoudre X exercices », « exercices d’addition », etc.

### 1.3 Thème Jedi et hiérarchie des rangs

| Rang | Niveau | Sens dans la progression |
|------|--------|---------------------------|
| **Youngling** | 1–4 | Débutant, premiers pas |
| **Padawan** | 5–14 | Apprenti en formation |
| **Knight** | 15–29 | Chevronné |
| **Master** | 30–49 | Expert |
| **Grand Master** | 50+ | Sommet de la maîtrise |

Les badges doivent s’aligner sur cette progression : titres Jedi cohérents, vocabulaire (Temple, Maître, Ordre, Padawan, etc.).

### 1.4 Principes psychologiques appliqués

| Principe | Application badges |
|----------|-------------------|
| **Goal-gradient** | Objectif progressif (X/Y), formulation « Plus que X », barre visible |
| **Endowment** | Visuels valorisants pour badges obtenus, option épingler |
| **Scarcity** | Badges or/légendaire = visuels distincts ; « Rare » (&lt;5%) |
| **Social proof** | « X% ont débloqué » — comparaison avec les pairs |
| **Loss aversion** | Streaks (7j, 30j), messages « Tu approches, ne lâche pas ! » |

---

## 2. État actuel des badges

### 2.1 Inventaire par code

| Code | Requirements (JSON) | Catégorie typique | Difficulté |
|------|---------------------|-------------------|-------------|
| `first_steps` | `{"attempts_count": 1}` | progression | bronze |
| `padawan_path` | `{"attempts_count": 10}` | progression | bronze |
| `knight_trial` | `{"attempts_count": 50}` | progression | silver |
| `jedi_master` | `{"attempts_count": 100}` | progression | gold |
| `grand_master` | `{"attempts_count": 200}` | progression | legendary |
| `addition_master` | `{"exercise_type": "addition", "consecutive_correct": 20}` | mastery | silver |
| `subtraction_master` | `{"exercise_type": "soustraction", "consecutive_correct": 15}` | mastery | silver |
| `multiplication_master` | `{"exercise_type": "multiplication", "consecutive_correct": 15}` | mastery | silver |
| `division_master` | `{"exercise_type": "division", "consecutive_correct": 15}` | mastery | silver |
| `speed_demon` | `{"max_time": 5}` | performance | silver |
| `perfect_day` | (logique spéciale) | regularity | gold |
| `perfect_week` | `{"consecutive_days": 7}` | regularity | gold |
| `perfect_month` | `{"consecutive_days": 30}` | regularity | legendary |
| `expert` | `{"min_attempts": 50, "success_rate": 80}` | mastery | silver |
| `perfectionist` | `{"min_attempts": 30, "success_rate": 95}` | mastery | gold |
| `explorer` | (all_types) | discovery | bronze |
| `versatile` | `{"min_per_type": 5}` | discovery | silver |

### 2.2 Limitations du moteur de progression

`_get_badge_progress` ne gère que :
- `attempts_count`
- `min_attempts` + `success_rate`

Les autres types (consecutive, max_time, consecutive_days, all_types, min_per_type) renvoient `(0, 0, 0)`. C’est une limitation connue (Lot C).

---

## 3. Matrice de reformulation par badge

### 3.1 Légende

| Colonne | Signification |
|---------|---------------|
| **Principe** | Principe psychologique dominant |
| **Cat.** | Catégorie (`progression`, `mastery`, `regularity`, `performance`, `discovery`, `special`) |
| **Diff.** | Difficulté (`bronze`, `silver`, `gold`, `legendary`) |
| **Icône** | Emoji ou référence `icon_url` |

### 3.2 Matrice synthétique

| Code | Principe | Cat. | Diff. | Icône |
|------|----------|------|-------|-------|
| `first_steps` | Goal-gradient | progression | bronze | 🌱 |
| `padawan_path` | Goal-gradient | progression | bronze | ⚔️ |
| `knight_trial` | Goal-gradient | progression | silver | 🛡️ |
| `jedi_master` | Goal-gradient + Endowment | progression | gold | 🏆 |
| `grand_master` | Scarcity + Social proof | progression | legendary | 👑 |
| `addition_master` | Mastery (compétence) | mastery | silver | ➕ |
| `subtraction_master` | Mastery | mastery | silver | ➖ |
| `multiplication_master` | Mastery | mastery | silver | ✖️ |
| `division_master` | Mastery | mastery | silver | ➗ |
| `speed_demon` | Performance + Scarcity | performance | silver | ⚡ |
| `perfect_day` | Loss aversion (streak 1j) | regularity | gold | ☀️ |
| `perfect_week` | Loss aversion | regularity | gold | 🔥 |
| `perfect_month` | Loss aversion + Scarcity | regularity | legendary | 💎 |
| `expert` | Mastery (taux réussite) | mastery | silver | 🎯 |
| `perfectionist` | Mastery + Scarcity | mastery | gold | ✨ |
| `explorer` | Discovery (autonomie) | discovery | bronze | 🗺️ |
| `versatile` | Discovery (polyvalence) | discovery | silver | 🌐 |

---

## 4. Spécifications finales par badge

### 4.1 Progression (attempts_count)

#### `first_steps` — Premiers pas au Temple

| Champ | Valeur |
|-------|--------|
| **name** | Premiers pas au Temple |
| **description** | Résous ton premier exercice et fais ton entrée dans l'Ordre. Chaque Maître a débuté ainsi. |
| **star_wars_title** | Youngling du Premier Matin |
| **category** | progression |
| **difficulty** | bronze |
| **points_reward** | 5 |
| **icon_url** | (éventuellement emoji 🌱 ou URL) |
| **Principe** | Goal-gradient — premier palier, gratification immédiate |

---

#### `padawan_path` — Voie du Padawan

| Champ | Valeur |
|-------|--------|
| **name** | Voie du Padawan |
| **description** | Résous 10 exercices. Tu découvres les bases de l'entraînement Jedi. |
| **star_wars_title** | Padawan de la Dizaine |
| **category** | progression |
| **difficulty** | bronze |
| **points_reward** | 10 |
| **Principe** | Goal-gradient — palier accessible, sens de la progression |

---

#### `knight_trial` — Épreuve du Chevalier

| Champ | Valeur |
|-------|--------|
| **name** | Épreuve du Chevalier |
| **description** | Résous 50 exercices et prouve ta constance. L'Ordre te reconnaît comme aspirant chevalier. |
| **star_wars_title** | Aspirant des Cinquante Épreuves |
| **category** | progression |
| **difficulty** | silver |
| **points_reward** | 25 |
| **Principe** | Goal-gradient — effort soutenu, barre X/50 visible |

---

#### `jedi_master` — Maître Jedi

| Champ | Valeur |
|-------|--------|
| **name** | Maître Jedi |
| **description** | Résous 100 exercices. Tu as atteint la maîtrise de l'entraînement régulier. |
| **star_wars_title** | Maître des Cent Épreuves |
| **category** | progression |
| **difficulty** | gold |
| **points_reward** | 50 |
| **Principe** | Goal-gradient + Endowment — badge prestigieux, propriété valorisée |

---

#### `grand_master` — Grand Maître

| Champ | Valeur |
|-------|--------|
| **name** | Grand Maître |
| **description** | Résous 200 exercices. Tu rejoins le cercle restreint des Maîtres les plus assidus de l'Ordre. |
| **star_wars_title** | Grand Maître des Deux Cents |
| **category** | progression |
| **difficulty** | legendary |
| **points_reward** | 100 |
| **Principe** | Scarcity + Social proof — rareté, comparaison avec les pairs |

---

### 4.2 Maîtrise par type (consecutive_correct)

#### `addition_master`

| Champ | Valeur |
|-------|--------|
| **name** | Maître des Additions |
| **description** | Réussis 20 additions consécutives sans erreur. La Force des nombres t'obéit. |
| **star_wars_title** | Gardien des Sommes |
| **category** | mastery |
| **difficulty** | silver |
| **points_reward** | 30 |
| **Principe** | Mastery — compétence démontrée dans un domaine |

---

#### `subtraction_master`

| Champ | Valeur |
|-------|--------|
| **name** | Maître des Soustractions |
| **description** | Réussis 15 soustractions consécutives sans erreur. Le retranchement n'a plus de secret. |
| **star_wars_title** | Maître du Retranchement |
| **category** | mastery |
| **difficulty** | silver |
| **points_reward** | 30 |
| **Principe** | Mastery |

---

#### `multiplication_master`

| Champ | Valeur |
|-------|--------|
| **name** | Maître des Multiplications |
| **description** | Réussis 15 multiplications consécutives sans erreur. Les tables sont ton allié. |
| **star_wars_title** | Gardien des Produits |
| **category** | mastery |
| **difficulty** | silver |
| **points_reward** | 30 |
| **Principe** | Mastery |

---

#### `division_master`

| Champ | Valeur |
|-------|--------|
| **name** | Maître des Divisions |
| **description** | Réussis 15 divisions consécutives sans erreur. La partition des nombres est maîtrisée. |
| **star_wars_title** | Maître de la Partition |
| **category** | mastery |
| **difficulty** | silver |
| **points_reward** | 30 |
| **Principe** | Mastery |

---

### 4.3 Performance et régularité

#### `speed_demon`

| Champ | Valeur |
|-------|--------|
| **name** | Éclair de Vitesse |
| **description** | Résous un exercice correctement en moins de 5 secondes. La Force accélère tes réflexes. |
| **star_wars_title** | Éclair du Temple |
| **category** | performance |
| **difficulty** | silver |
| **points_reward** | 25 |
| **Principe** | Performance + Scarcity — exploit rare |

---

#### `perfect_day`

| Champ | Valeur |
|-------|--------|
| **name** | Journée Parfaite |
| **description** | Réussis tous tes exercices du jour. Une journée sans faille, une étape vers la maîtrise. |
| **star_wars_title** | Jour sans Ombre |
| **category** | regularity |
| **difficulty** | gold |
| **points_reward** | 40 |
| **Principe** | Loss aversion — incite à maintenir la qualité quotidienne |

---

#### `perfect_week`

| Champ | Valeur |
|-------|--------|
| **name** | Semaine Parfaite |
| **description** | Pratique au moins une fois par jour pendant 7 jours consécutifs. La constance forge les Jedi. |
| **star_wars_title** | Gardien de la Semaine Sacrée |
| **category** | regularity |
| **difficulty** | gold |
| **points_reward** | 50 |
| **Principe** | Loss aversion — streak 7j, « ne lâche pas » |

---

#### `perfect_month`

| Champ | Valeur |
|-------|--------|
| **name** | Mois Parfait |
| **description** | Pratique au moins une fois par jour pendant 30 jours consécutifs. Réservé aux plus déterminés. |
| **star_wars_title** | Gardien du Mois des Étoiles |
| **category** | regularity |
| **difficulty** | legendary |
| **points_reward** | 150 |
| **Principe** | Loss aversion + Scarcity — streak 30j, très rare |

---

### 4.4 Maîtrise (taux de réussite)

#### `expert`

| Champ | Valeur |
|-------|--------|
| **name** | Expert |
| **description** | Atteins au moins 80% de réussite sur 50 exercices. La précision est la marque des Jedi confirmés. |
| **star_wars_title** | Jedi de la Précision |
| **category** | mastery |
| **difficulty** | silver |
| **points_reward** | 35 |
| **Principe** | Mastery — compétence mesurée par le taux |

---

#### `perfectionist`

| Champ | Valeur |
|-------|--------|
| **name** | Perfectionniste |
| **description** | Atteins au moins 95% de réussite sur 30 exercices. L'excellence est rare. |
| **star_wars_title** | Maître de l'Excellence |
| **category** | mastery |
| **difficulty** | gold |
| **points_reward** | 60 |
| **Principe** | Mastery + Scarcity — niveau rare, visuel distinct |

---

### 4.5 Découverte

#### `explorer`

| Champ | Valeur |
|-------|--------|
| **name** | Explorateur |
| **description** | Essaie au moins un exercice de chaque type (addition, soustraction, multiplication, division). |
| **star_wars_title** | Explorateur des Quatre Voies |
| **category** | discovery |
| **difficulty** | bronze |
| **points_reward** | 15 |
| **Principe** | Discovery — autonomie, exploration des domaines |

---

#### `versatile`

| Champ | Valeur |
|-------|--------|
| **name** | Polyvalent |
| **description** | Réussis au moins 5 exercices de chaque type. La polyvalence est une force. |
| **star_wars_title** | Padawan des Quatre Arts |
| **category** | discovery |
| **difficulty** | silver |
| **points_reward** | 35 |
| **Principe** | Discovery — polyvalence, pas de spécialisation exclusive |

---

## 5. Script de mise à jour

Le script `scripts/update_badges_b4.py` applique ces reformulations en base via des `UPDATE` sur la table `achievements`, en ciblant chaque badge par son `code`. Les `requirements` ne sont pas modifiés.

**Exécution :**
```bash
python scripts/update_badges_b4.py              # Dry-run (prévisualisation)
python scripts/update_badges_b4.py --execute    # Applique les mises à jour
```

**Note sur les défis logiques** : Ce document et le script B4 portent uniquement sur les badges existants (exercices). Une évolution ultérieure pourra introduire des badges « Défi logique » basés sur `LogicChallengeAttempt`, avec des codes comme `logic_explorer`, `sequence_master`, etc.

**Note visuel / droit d'auteur** : Pour les badges (B4 et futurs B5) — titres et titres honorifiques dans l'*esprit* progression/maîtrise, sans termes Star Wars protégés. Voir [PLAN_REFONTE_BADGES](PLAN_REFONTE_BADGES.md) § 5.3.2.

---

## Références

- [PLAN_REFONTE_BADGES](PLAN_REFONTE_BADGES.md) — Lot B, B4
- [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) — Principes psychologiques
- [BADGES_AUDIT_PAUFINAGE](BADGES_AUDIT_PAUFINAGE.md) — Audit page badges
- `app/services/badge_service.py` — Logique d'attribution
