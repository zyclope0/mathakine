# Plan F42-Completion - Refonte difficulte globale Mathakine

**Date initiale :** 2026-03-26
**Derniere mise a jour :** 2026-03-28 (F42 clos + F43-A1/F43-A2 livres ; suites contractuelles legacy sequencees)
**Source :** audit code consolide + debat 4 agents + revue croisee
**Execution :** Cursor Composer
**Validation :** `/octo:review` apres chaque lot

---

## 1. Etat reel (verite terrain 2026-03-28)

| Couche | Etat initial | Etat reel apres lots |
|--------|-------------|----------------------|
| BDD / persistance | OK | **DONE** - `users.age_group`, `difficulty_tier` sur exercises + logic_challenges |
| Recommandation | OK | **DONE** - filtre tier +-1 exercices, score-penalty defis (design choice documente) |
| Types frontend API | OK | **DONE** - `difficulty_tier` type Exercise + Challenge |
| Generation exercices (local) | PARTIEL | **DONE** - `build_exercise_generation_profile()` + `pedagogical_band_override` + tier recalcule |
| Generation exercices (OpenAI) | PARTIEL | **DONE** - `calibration_desc` injecte dans le prompt |
| Adaptive second axe exercices | PARTIEL | **DONE** - `AdaptiveGenerationContext`, `resolve_adaptive_context()`, separation age / bande |
| Fallback band cold-start | ANALYSE | **STABLE** - fallback reste `learning` ; tout changement demande une decision produit explicite |
| Generation defis / contexte user | PARTIEL | **DONE** - `challenge_generation_context.py` lit le contexte user F42 via `build_recommendation_user_context()` |
| SSE defis difficulty_tier (chemin normal) | MANQUANT | **DONE** - `_persist_challenge_sync()` retourne `difficulty_tier` |
| SSE defis difficulty_tier (chemin erreur) | MANQUANT | **DONE** - `normalize_generated_challenge()` accepte et retourne `difficulty_tier` |
| Evaluation / progression (bridge) | NON | **DONE** - `mastery_tier_bridge.py` : `mastery_to_tier()`, `enrich_diagnostic_scores_f42()`, `canonical_age_group_with_fallback()` |
| Admin list exercices + defis | NON | **DONE** - `admin_content_service.py` expose `difficulty_tier` + `difficulty_rating` |
| Schema GenerateExerciseResult | INCOMPLET | **DONE** - `difficulty_tier: Optional[int]` |
| Destarwarisation exercices backend | PARTIEL | **DONE** - `SpatialNarratives`, tags IA neutralises |
| Destarwarisation schemas (docstrings) | NON | **DONE** - docstrings cibles neutralisees ; dette `star_wars_title` documentee |
| Destarwarisation i18n (exercise copy) | NON | **DONE** - copy exercice-facing neutralisee |
| Gamification cleanup labels publics | NON | **DONE** - labels publics neutralises sur profil/dashboard/leaderboard/badges |
| Extension ladder 5 -> 8 buckets | NON | **DONE** - backend + frontend + i18n alignes sur 8 buckets canoniques |
| Cleanup final Star Wars visible | NON | **DONE** - surfaces visibles principales nettoyees ; dettes techniques legacy assumees |

---

## 2. Regles non negociables

1. **Lire avant d'ecrire** - auditer les fichiers reels avant toute modification.
2. **Un lot = un commit.**
3. **Diff strictement borne** - aucun changement hors scope.
4. **RGPD mineurs (critique)** : les libelles de rang du classement public doivent rester bases sur la progression (`XP/points`), jamais sur `age_group`.
5. **`preferred_difficulty`** : ne pas supprimer brutalement. Introduire un helper de normalisation (`canonical_age_group(user)`) puis deprecier progressivement.
6. **`DifficultyLevels`** (`INITIE/PADAWAN/...`) : ne pas renommer tant que la boucle evaluation/progression n'est pas stabilisee.
7. **Champ technique legacy** : `jedi_rank` peut rester un identifiant technique temporaire si les labels publics sont neutralises cote affichage.

---

## 3. Sequencage reel

```text
[DONE] F42-C1A         : Generation exercices (local + OpenAI + diagnostic feeder)
[DONE] F42-C1B         : Destarwarisation UI/i18n exercices hors gamification publique
[DONE] F42-C2          : Evaluation / progression (bridge mastery -> tier)
[DONE] F42-C3A         : Defis personnalises par contexte utilisateur
[DONE] F42-C3B         : Gamification/theme cleanup + surfaces stales + labels publics
[DONE] F42-C3C         : Extension ladder publique 5 -> 8 buckets (backend + UI + i18n)
[DONE] F42-C4          : Cleanup final des traces Star Wars encore visibles
[DONE] F42-ADMIN-CHECK : Controle end-to-end admin
[DONE] F42-P1          : Fix SSE `difficulty_tier` sur les chemins erreur challenge
[DONE] F42-P3          : UI coherence niveau/rang sur profile + dashboard progression
[DONE] F42-P4          : Recalibrage progression points -> level -> rank (best effort)
[DONE] F42-P5          : Analyse et suppression progressive de `LEVEL_TITLES`
[DONE] F42-P2          : Dette technique post-debat (fallback decision, cache, safeguard, instrumentation)
[DONE] F43-A1          : Observabilite post-F42 (logs tier/source + endpoint admin cohortes)
[DONE] F43-A2          : Cleanup residuel legacy wording / Swagger / user schema
```

---

## 4. Statut restant

Le bloc F42 est maintenant **termine**.
Les premiers suivis post-F42 sont egalement **livres** :
- `F43-A1` : observabilite empirique (logs structures + endpoint admin read-only)
- `F43-A2` : cleanup residuel legacy wording / Swagger / user schema

Les suites logiques sont maintenant hors perimetre F42 :
- `F43-A3` : migration contractuelle additive `jedi_rank` -> `progression_rank`
- `F43-A4` : migration contractuelle additive `star_wars_title` -> `thematic_title`
- instrumentation / analytics plus large
- nouveaux chantiers fonctionnels

---

## 5. Dette technique assumee (hors perimetre)

| Item | Raison du report |
|------|------------------|
| `star_wars_title: Optional[str]` dans `ChallengeBadgeEarned` | Champ nullable ; migration de contrat optionnelle |
| Cache mastery (P2b) | Pas urgent < quelques centaines users simultanes |
| Migration DB `difficulty_tier` sur tentatives/progress | Seulement apres validation couche service |
| Filtre dur reco defis (vs score penalty) | Design choice documente - asymetrie intentionnelle |
| Dashboard parent/enseignant labels age dedies | Produit payant, lot separe |
| Filtre leaderboard par groupe d'age (`F40-v2`) | Depend clarification produit post-F42 et validation UX/RGPD |
| Renommage physique champs API legacy (`jedi_rank`, `star_wars_title`, etc.) | A traiter uniquement via migration contractuelle additive dediee (`F43-A3` / `F43-A4`) |
| Extension matrice F42 (5eme groupe age, 4eme bande) | Pas avant besoin utilisateur reel valide |
| `LEVEL_TITLES` | **Traite** via F42-P5 - retire du payload public ; reliquats doc/historiques acceptables |

---

## 6. Points de vigilance post-debat

### Risques identifies par le debat 4 agents (2026-03-27)

| Risque | Priorite | Action |
|--------|----------|--------|
| Fallback band `learning` en cold-start | Decision produit ouverte | Etat reel actuel : fallback neutre = `learning` ; ne changer que via F42-P2 |
| `difficulty_tier` absent chemins erreur SSE challenge | **CORRIGE** P1b | `normalize_generated_challenge()` |
| Double affichage niveau/rang (`LEVEL_TITLES` vs bucket) | **CORRIGE** P3 | bucket = seule verite publique de rang |
| Progression compte trop lineaire | **CORRIGE** P4 | courbe points -> niveau par paliers ; badges realignes sur `total_points` |
| Cache mastery absent | **CORRIGE** P2 | cache TTL + invalidation sur ecriture Progress |
| Safeguard bridge silencieux | **CORRIGE** P2 | clamp + warning dans `mastery_to_tier()` |
| Seuils bandes pedagogiques non valides empiriquement | Moyen terme | instrumenter taux de reussite / tier |
| Double query Progress chemin IRT | Acceptable | faible risque multi-worker, surveiller |
| Observabilite runtime tiers / progression | **CORRIGE** F43-A1 | logs `f43_exercise_attempt`, `f43_adaptive_context`, endpoint admin read-only |

### Validite pedagogique

Le debat scientifique (Hattie, Vygotsky, Sweller, Deci & Ryan, Siegler) confirme :
- la matrice 4x3 est **approximative mais viable**
- les seuils `mastery -> bande` sont des **stipulations pragmatiques**, pas une calibration empirique
- l'age comme premier axe simplifie la variabilite intra-age, mais reste acceptable pour un MVP
- l'action cle restante est d'instrumenter les taux de reussite par tier en production

---

## 7. Gate standard

### Backend
```powershell
D:\Mathakine\.venv\Scripts\python.exe -m pytest tests\ -q --tb=short --maxfail=20 --no-cov --ignore=tests\api\test_admin_auth_stability.py
D:\Mathakine\.venv\Scripts\python.exe -m black <fichiers touches> --check
D:\Mathakine\.venv\Scripts\python.exe -m isort <fichiers touches> --check-only
D:\Mathakine\.venv\Scripts\python.exe -m flake8 --select=E9,F63,F7,F82 <fichiers touches>
```

### Frontend
```powershell
cd D:\Mathakine\frontend && npm run lint
cd D:\Mathakine\frontend && npx tsc --noEmit
cd D:\Mathakine\frontend && npx prettier --check <fichiers touches>
```
